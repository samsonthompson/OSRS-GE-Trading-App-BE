import json
import sys
import matplotlib.pyplot as plt
from datetime import datetime
import os

# Usage: python plot_equity_curve.py [path/to/equity_curve.json]

def plot_equity_curve(json_path):
    with open(json_path, 'r') as f:
        equity_curve = json.load(f)
    dates = [datetime.strptime(point['date'], '%Y-%m-%d') for point in equity_curve]
    equity = [point['equity'] for point in equity_curve]
    plt.figure(figsize=(12, 6))
    plt.plot(dates, equity, marker='o', markersize=2, linewidth=1)
    plt.title(f'Equity Curve\n{os.path.basename(json_path)}')
    plt.xlabel('Date')
    plt.ylabel('Equity')
    plt.grid(True)
    plt.tight_layout()
    plt.gcf().autofmt_xdate()
    plt.show()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        json_path = sys.argv[1]
    else:
        # Default to a sample file if none provided
        json_path = 'analysis/backtesting/equity_curve_ma_14_90.json'
        print(f"No file provided. Using default: {json_path}")
    plot_equity_curve(json_path)
