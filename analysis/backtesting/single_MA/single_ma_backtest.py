import json
import os

# Path to enriched data (update as needed)
ENRICHED_DATA_PATH = os.path.join(os.path.dirname(__file__), '../../historical_data_327_enriched.json')
BACKTEST_DIR = os.path.dirname(__file__)

MA_PERIODS = [5, 7, 14, 20, 90, 180, 365]

def load_enriched_data(path=ENRICHED_DATA_PATH):
    """Load enriched historical data from JSON file."""
    with open(path, 'r') as f:
        return json.load(f)

def get_ma(row, period):
    """Get moving average for a given period from a row. Returns None if not present."""
    return row['indicators']['ma'].get(str(period))

def get_rsi(row, period):
    """Get RSI for a given period from a row. Returns None if not present."""
    return row['indicators']['rsi'].get(str(period))

def get_macd(row):
    """Get MACD value from a row. Returns None if not present."""
    return row['indicators']['macd'].get('macd')

def get_bollinger(row, period):
    """Get Bollinger Bands (upper, lower) for a given period. Returns (None, None) if not present."""
    b = row['indicators']['bollinger'].get(str(period), {})
    return b.get('upper'), b.get('lower')

# Example signal function (to be expanded)
def ma_signal(row, period):
    ma = get_ma(row, period)
    price = row['price']
    if ma is None or price is None:
        return None  # Not enough data
    return 1 if price > ma else -1  # Example: 1=buy, -1=sell

def run_single_ma_backtest(data, period):
    position = None  # None = out, 'long' = in
    entry_price = 0
    trades = []
    prev_price = None
    prev_ma = None
    for row in data:
        price = row['price']
        ma = get_ma(row, period)
        if price is None or ma is None:
            prev_price, prev_ma = price, ma
            continue
        # Detect crossover
        if prev_price is not None and prev_ma is not None:
            # Price crosses above MA (buy signal)
            if position is None and prev_price < prev_ma and price > ma:
                position = 'long'
                entry_price = price
                entry_date = row['date']
            # Price crosses below MA (sell signal)
            elif position == 'long' and prev_price > prev_ma and price < ma:
                exit_price = price
                exit_date = row['date']
                trades.append({
                    'entry_date': entry_date,
                    'entry_price': entry_price,
                    'exit_date': exit_date,
                    'exit_price': exit_price,
                    'profit': exit_price - entry_price
                })
                position = None
        prev_price, prev_ma = price, ma
    # Close any open position at the end
    if position == 'long':
        exit_price = data[-1]['price']
        exit_date = data[-1]['date']
        trades.append({
            'entry_date': entry_date,
            'entry_price': entry_price,
            'exit_date': exit_date,
            'exit_price': exit_price,
            'profit': exit_price - entry_price
        })
    # Add cumulative profit to each trade
    cumulative = 0
    for trade in trades:
        cumulative += trade['profit']
        trade['cumulative_profit'] = cumulative
    total_profit = cumulative
    return trades, total_profit

def print_backtest_summary(period, trades, total_profit):
    print(f"\nMA Period: {period}")
    print(f"Number of trades: {len(trades)}")
    print(f"Total profit: {total_profit:.2f}")
    if trades:
        print(f"First trade: {trades[0]}")
        print(f"Last trade: {trades[-1]}")

def save_trades_json(trades, period):
    filename = os.path.join(BACKTEST_DIR, f"trades_ma_{period}.json")
    with open(filename, 'w') as f:
        json.dump(trades, f, indent=2)

def main():
    data = load_enriched_data()
    summary = []
    for period in MA_PERIODS:
        trades, total_profit = run_single_ma_backtest(data, period)
        print_backtest_summary(period, trades, total_profit)
        save_trades_json(trades, period)
        summary.append({
            'ma_period': period,
            'num_trades': len(trades),
            'total_profit': total_profit,
            'first_trade': trades[0] if trades else None,
            'last_trade': trades[-1] if trades else None
        })
    # Save summary JSON
    summary_path = os.path.join(BACKTEST_DIR, 'ma_summary.json')
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)

if __name__ == "__main__":
    main()