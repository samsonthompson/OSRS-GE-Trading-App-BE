import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# Path to your trades JSON file
TRADES_JSON = 'analysis/backtesting/data/trades_ma_14.json'  # Change period as needed

# Load trades
with open(TRADES_JSON, 'r') as f:
    trades = json.load(f)

# Extract exit dates and cumulative profits
exit_dates = [datetime.strptime(trade['exit_date'], '%Y-%m-%d') for trade in trades]
cumulative_profits = [trade['cumulative_profit'] for trade in trades]

# Plot equity curve
plt.figure(figsize=(12, 6))
plt.plot(exit_dates, cumulative_profits, marker='o', markersize=3, linewidth=1)
plt.title('Equity Curve (MA 14)')
plt.xlabel('Exit Date')
plt.ylabel('Cumulative Profit')

# Set major x-ticks to yearly
plt.gca().xaxis.set_major_locator(mdates.YearLocator())
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

# Optionally, add vertical lines for each year
for year in set([d.year for d in exit_dates]):
    plt.axvline(datetime(year, 1, 1), color='gray', linestyle='--', alpha=0.2)

plt.grid(True)
plt.tight_layout()
plt.show()
