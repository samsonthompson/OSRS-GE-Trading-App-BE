import json
import os

# Path to enriched data (update as needed)
# From analysis/backtesting/dual_MA_crossover to project root is ../../../
ENRICHED_DATA_PATH = os.path.join(os.path.dirname(__file__), '../../../historical_data_327_enriched.json')
BACKTEST_DIR = os.path.dirname(__file__)

# Define pairs of (short, long) MA periods to test
MA_PAIRS = [
    (5, 20),
    (7, 90),
    (14, 90),
    (20, 90),
    (14, 180),
    (20, 180),
    (90, 180),
    (90, 365),
    # Add more as needed
]

def load_enriched_data(path=ENRICHED_DATA_PATH):
    with open(path, 'r') as f:
        return json.load(f)

def compute_max_drawdown(equity_curve):
    peak = float('-inf')
    max_dd = 0.0
    for point in equity_curve:
        equity = point.get('equity', 0.0)
        if equity > peak:
            peak = equity
        drawdown = peak - equity
        if drawdown > max_dd:
            max_dd = drawdown
    return max_dd

def get_ma(row, period):
    return row['indicators']['ma'].get(str(period))

def run_dual_ma_backtest(data, short_period, long_period):
    position = None
    entry_price = 0
    trades = []
    prev_short = None
    prev_long = None
    cumulative = 0
    equity_curve = []
    for row in data:
        short_ma = get_ma(row, short_period)
        long_ma = get_ma(row, long_period)
        price = row['price']
        date = row['date']
        if short_ma is None or long_ma is None or price is None:
            prev_short, prev_long = short_ma, long_ma
            # Even if we can't trade, record equity for this day
            equity_curve.append({
                'date': date,
                'equity': cumulative if position is None else cumulative + (price - entry_price)
            })
            continue
        # Detect crossovers
        if prev_short is not None and prev_long is not None:
            # Bullish crossover: short MA crosses above long MA
            if position is None and prev_short < prev_long and short_ma > long_ma:
                position = 'long'
                entry_price = price
                entry_date = date
            # Bearish crossover: short MA crosses below long MA
            elif position == 'long' and prev_short > prev_long and short_ma < long_ma:
                exit_price = price
                exit_date = date
                profit = exit_price - entry_price
                trades.append({
                    'entry_date': entry_date,
                    'entry_price': entry_price,
                    'exit_date': exit_date,
                    'exit_price': exit_price,
                    'profit': profit
                })
                cumulative += profit
                position = None
        # Record equity for this day
        equity_curve.append({
            'date': date,
            'equity': cumulative if position is None else cumulative + (price - entry_price)
        })
        prev_short, prev_long = short_ma, long_ma
    # Close any open position at the end
    if position == 'long':
        exit_price = data[-1]['price']
        exit_date = data[-1]['date']
        profit = exit_price - entry_price
        trades.append({
            'entry_date': entry_date,
            'entry_price': entry_price,
            'exit_date': exit_date,
            'exit_price': exit_price,
            'profit': profit
        })
        cumulative += profit
    # Add cumulative profit to each trade
    running = 0
    for trade in trades:
        running += trade['profit']
        trade['cumulative_profit'] = running
    total_profit = running
    return trades, total_profit, equity_curve

def save_trades_json(trades, short_period, long_period):
    filename = os.path.join(BACKTEST_DIR, f"trades_ma_{short_period}_{long_period}.json")
    with open(filename, 'w') as f:
        json.dump(trades, f, indent=2)

def save_equity_curve_json(equity_curve, short_period, long_period):
    filename = os.path.join(BACKTEST_DIR, f"equity_curve_ma_{short_period}_{long_period}.json")
    with open(filename, 'w') as f:
        json.dump(equity_curve, f, indent=2)

def main():
    data = load_enriched_data()
    summary = []
    for short, long in MA_PAIRS:
        trades, total_profit, equity_curve = run_dual_ma_backtest(data, short, long)
        save_trades_json(trades, short, long)
        save_equity_curve_json(equity_curve, short, long)
        # Derived metrics
        num_trades = len(trades)
        num_wins = sum(1 for t in trades if t['profit'] > 0)
        num_losses = sum(1 for t in trades if t['profit'] < 0)
        win_rate = (num_wins / num_trades) if num_trades > 0 else 0.0
        gross_profit = sum(t['profit'] for t in trades if t['profit'] > 0)
        gross_loss = -sum(t['profit'] for t in trades if t['profit'] < 0)
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else float('inf') if gross_profit > 0 else 0.0
        average_profit_per_trade = (total_profit / num_trades) if num_trades > 0 else 0.0
        max_drawdown = compute_max_drawdown(equity_curve)
        summary.append({
            'short_ma': short,
            'long_ma': long,
            'num_trades': num_trades,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'avg_profit_per_trade': average_profit_per_trade,
            'max_drawdown': max_drawdown,
            'total_profit': total_profit,
            'first_trade': trades[0] if trades else None,
            'last_trade': trades[-1] if trades else None
        })
    # Save summary JSON
    summary_path = os.path.join(BACKTEST_DIR, 'ma_crossover_summary.json')
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)

if __name__ == "__main__":
    main()
