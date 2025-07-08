import json
import os

# Path to enriched data (update as needed)
ENRICHED_DATA_PATH = os.path.join(os.path.dirname(__file__), '../../../historical_data_327_enriched.json')
BACKTEST_DIR = os.path.dirname(__file__)

RSI_PERIODS = [7, 14]  # Use the periods present in your enriched data
RSI_BUY = 30
RSI_SELL = 70

def load_enriched_data(path=ENRICHED_DATA_PATH):
    with open(path, 'r') as f:
        return json.load(f)

def get_rsi(row, period):
    return row['indicators']['rsi'].get(str(period))

def run_rsi_backtest(data, period, buy_level=RSI_BUY, sell_level=RSI_SELL):
    position = None
    entry_price = 0
    trades = []
    cumulative = 0
    equity_curve = []
    for row in data:
        rsi = get_rsi(row, period)
        price = row['price']
        date = row['date']
        if rsi is None or price is None:
            equity_curve.append({'date': date, 'equity': cumulative if position is None else cumulative + (price - entry_price)})
            continue
        # Buy signal
        if position is None and rsi < buy_level:
            position = 'long'
            entry_price = price
            entry_date = date
        # Sell signal
        elif position == 'long' and rsi > sell_level:
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

def save_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def print_backtest_summary(period, trades, total_profit):
    print(f"\nRSI Period: {period}")
    print(f"Number of trades: {len(trades)}")
    print(f"Total profit: {total_profit:.2f}")
    if trades:
        print(f"First trade: {trades[0]}")
        print(f"Last trade: {trades[-1]}")

def main():
    data = load_enriched_data()
    summary = []
    for period in RSI_PERIODS:
        trades, total_profit, equity_curve = run_rsi_backtest(data, period)
        save_json(trades, os.path.join(BACKTEST_DIR, f'trades_rsi_{period}.json'))
        save_json(equity_curve, os.path.join(BACKTEST_DIR, f'equity_curve_rsi_{period}.json'))
        print_backtest_summary(period, trades, total_profit)
        summary.append({
            'rsi_period': period,
            'num_trades': len(trades),
            'total_profit': total_profit,
            'first_trade': trades[0] if trades else None,
            'last_trade': trades[-1] if trades else None
        })
    save_json(summary, os.path.join(BACKTEST_DIR, 'rsi_summary.json'))

if __name__ == "__main__":
    main()
