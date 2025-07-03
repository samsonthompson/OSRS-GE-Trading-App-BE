import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load your historical data (replace with your actual file and item_id)
with open('historical_data_327.json') as f:
    data = json.load(f)

item_id = '327'  # Change as needed
item_history = data[item_id]

# Convert to DataFrame
df = pd.DataFrame(item_history)
df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')

# Periods to calculate
periods = [5, 7, 14, 20, 90, 180, 365]

# Calculate moving averages, stds, and Bollinger Bands for each period
for period in periods:
    df[f'ma_{period}'] = df['price'].rolling(window=period).mean()
    df[f'std_{period}'] = df['price'].rolling(window=period).std()
    df[f'bollinger_upper_{period}'] = df[f'ma_{period}'] + 2 * df[f'std_{period}']
    df[f'bollinger_lower_{period}'] = df[f'ma_{period}'] - 2 * df[f'std_{period}']

# Add RSI calculation for selected periods
rsi_periods = [7, 14]
def calculate_rsi(series, period):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi
for period in rsi_periods:
    df[f'rsi_{period}'] = calculate_rsi(df['price'], period)

def get_scalar(val):
    if isinstance(val, (np.ndarray, pd.Series)):
        return round(float(val.item()), 2) if val.size > 0 else None
    return round(float(val), 2) if pd.notna(val) else None

# Prepare output in Option 4 nested format
output_records = []
for _, row in df.iterrows():
    # Ensure row['datetime'] is a scalar Timestamp
    dt = row['datetime']
    if isinstance(dt, np.ndarray):
        dt = pd.to_datetime(dt[0])
    indicators = {
        'ma': {str(period): get_scalar(row[f'ma_{period}']) for period in periods},
        'std': {str(period): get_scalar(row[f'std_{period}']) for period in periods},
        'bollinger': {
            str(period): {
                'upper': get_scalar(row[f'bollinger_upper_{period}']),
                'lower': get_scalar(row[f'bollinger_lower_{period}'])
            } for period in periods
        },
        'rsi': {str(period): get_scalar(row[f'rsi_{period}']) for period in rsi_periods}
    }
    record = {
        'date': dt.strftime('%Y-%m-%d'),
        'price': get_scalar(row['price']),
        'indicators': indicators
    }
    output_records.append(record)

output_path = 'historical_data_327_enriched.json'
with open(output_path, 'w') as f:
    json.dump(output_records, f, indent=2)
print(f"Saved enriched data with nested indicators to {output_path}")

# Plot macro view (keep this section for now)
plt.figure(figsize=(14,7))
plt.plot(df['datetime'], df['price'], label='Price', alpha=0.5)
for period in periods:
    plt.plot(df['datetime'], df[f'ma_{period}'], label=f'{period}-day MA')
plt.legend()
plt.title('Macro View: Price and Multiple Moving Averages')
plt.xlabel('Date')
plt.ylabel('Price')
plt.show()
