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

# Calculate multiple moving averages
df['ma_14'] = df['price'].rolling(window=14).mean()
df['ma_30'] = df['price'].rolling(window=30).mean()
df['ma_90'] = df['price'].rolling(window=90).mean()
df['ma_100'] = df['price'].rolling(window=100).mean()
df['ma_180'] = df['price'].rolling(window=180).mean()
df['ma_365'] = df['price'].rolling(window=365).mean()

# Prepare output: convert timestamp to ISO date+time and NaN to None
output_records = []
for _, row in df.iterrows():
    record = {
        'id': row['id'],
        'price': row['price'],
        'volume': row['volume'] if not pd.isna(row['volume']) else None,
        'date': row['datetime'].strftime('%Y-%m-%dT%H:%M:%S'),
        'ma_14': row['ma_14'] if not pd.isna(row['ma_14']) else None,
        'ma_30': row['ma_30'] if not pd.isna(row['ma_30']) else None,
        'ma_90': row['ma_90'] if not pd.isna(row['ma_90']) else None,
        'ma_100': row['ma_100'] if not pd.isna(row['ma_100']) else None,
        'ma_180': row['ma_180'] if not pd.isna(row['ma_180']) else None,
        'ma_365': row['ma_365'] if not pd.isna(row['ma_365']) else None,
    }
    output_records.append(record)

output_path = 'historical_data_327_with_ma.json'
with open(output_path, 'w') as f:
    json.dump({item_id: output_records}, f, indent=2)
print(f"Saved DataFrame with multiple moving averages and ISO date+time to {output_path}")

# Print first few rows from 2023 onwards
print(df[(df['datetime'] > '2023-01-01')][['datetime', 'price', 'ma_14', 'ma_30', 'ma_90', 'ma_100', 'ma_180', 'ma_365']].head(15))

# Plot macro view
plt.figure(figsize=(14,7))
plt.plot(df['datetime'], df['price'], label='Price', alpha=0.5)
plt.plot(df['datetime'], df['ma_14'], label='14-day MA')
plt.plot(df['datetime'], df['ma_30'], label='30-day MA')
plt.plot(df['datetime'], df['ma_90'], label='90-day MA')
plt.plot(df['datetime'], df['ma_100'], label='100-day MA')
plt.plot(df['datetime'], df['ma_180'], label='180-day MA', linewidth=2)
plt.plot(df['datetime'], df['ma_365'], label='365-day MA', linewidth=2)
plt.legend()
plt.title('Macro View: Price and Multiple Moving Averages')
plt.xlabel('Date')
plt.ylabel('Price')
plt.show()
