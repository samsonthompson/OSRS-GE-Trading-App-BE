import json
import os

# Path to enriched data (update as needed)
# From analysis/backtesting/bollinger-bands to project root is ../../../
ENRICHED_DATA_PATH = os.path.join(os.path.dirname(__file__), '../../../historical_data_327_enriched.json')
BACKTEST_DIR = os.path.dirname(__file__)

BB_PERIODS = [5, 7, 14, 20, 90, 180, 365]
STD_DEV = 2

def load_enriched_data(path=ENRICHED_DATA_PATH):
    """Load enriched historical data from JSON file."""
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

def get_bollinger(row, period):
    """Get Bollinger Bands (upper, lower) for a given period. Returns (None, None) if not present."""
    b = row['indicators']['bollinger'].get(str(period), {})
    return b.get('upper'), b.get('lower')

def run_bollinger_backtest(data, period):
    position = None  # None = out, 'long' = in
    entry_price = 0
    trades = []
    prev_price = None
    prev_upper = None
    prev_lower = None
    cumulative = 0
    equity_curve = []
    for row in data:
        price = row['price']
        upper, lower = get_bollinger(row, period)
        date = row['date']
        if price is None or upper is None or lower is None:
            equity_curve.append({'date': date, 'equity': cumulative if position is None else cumulative + (price - entry_price)})
            prev_price, prev_upper, prev_lower = price, upper, lower
            continue
        # Buy: price crosses below lower band
        if position is None and prev_price is not None and prev_lower is not None:
            if prev_price > prev_lower and price < lower:
                position = 'long'
                entry_price = price
                entry_date = date
        # Sell: price crosses above upper band
        elif position == 'long' and prev_price is not None and prev_upper is not None:
            if prev_price < prev_upper and price > upper:
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
        equity_curve.append({'date': date, 'equity': cumulative if position is None else cumulative + (price - entry_price)})
        prev_price, prev_upper, prev_lower = price, upper, lower
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

def print_backtest_summary(period, trades, total_profit):
    print(f"\nBollinger Period: {period}")
    print(f"Number of trades: {len(trades)}")
    print(f"Total profit: {total_profit:.2f}")
    if trades:
        print(f"First trade: {trades[0]}")
        print(f"Last trade: {trades[-1]}")

def save_trades_json(trades, period):
    filename = os.path.join(BACKTEST_DIR, f"trades_bollinger_{period}.json")
    with open(filename, 'w') as f:
        json.dump(trades, f, indent=2)

def save_equity_curve_json(equity_curve, period):
    filename = os.path.join(BACKTEST_DIR, f"equity_curve_bollinger_{period}.json")
    with open(filename, 'w') as f:
        json.dump(equity_curve, f, indent=2)

def main():
    data = load_enriched_data()
    summary = []
    for period in BB_PERIODS:
        trades, total_profit, equity_curve = run_bollinger_backtest(data, period)
        print_backtest_summary(period, trades, total_profit)
        save_trades_json(trades, period)
        save_equity_curve_json(equity_curve, period)
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
            'bollinger_period': period,
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
    summary_path = os.path.join(BACKTEST_DIR, 'bollinger_summary.json')
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)

if __name__ == "__main__":
    main()
