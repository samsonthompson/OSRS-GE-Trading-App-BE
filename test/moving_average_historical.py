import json
import pandas as pd
import matplotlib.pyplot as plt

# Load your historical data (replace with your actual file and item_id)
with open('historical_data_327.json') as f:
    data = json.load(f)

item_id = '327'  # Change as needed
item_history = data[item_id]

# Convert to DataFrame
df = pd.DataFrame(item_history)
df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')

# Calculate long-term moving averages
df['ma_180'] = df['price'].rolling(window=180).mean()
df['ma_365'] = df['price'].rolling(window=365).mean()

# Save DataFrame with moving averages to JSON for full inspection, matching original structure
output_path = 'historical_data_327_with_ma.json'
# Only keep relevant columns for output
output_records = df[['id', 'price', 'volume', 'timestamp', 'ma_180', 'ma_365']].to_dict(orient='records')
with open(output_path, 'w') as f:
    json.dump({item_id: output_records}, f, indent=2)
print(f"Saved DataFrame with 180/365-day moving averages to {output_path}")

# Print first few rows from 2023 onwards
print(df[(df['datetime'] > '2023-01-01')][['datetime', 'price', 'ma_180', 'ma_365']].head(15))

# Plot macro view
plt.figure(figsize=(14,7))
plt.plot(df['datetime'], df['price'], label='Price', alpha=0.5)
plt.plot(df['datetime'], df['ma_180'], label='180-day MA', linewidth=2)
plt.plot(df['datetime'], df['ma_365'], label='365-day MA', linewidth=2)
plt.legend()
plt.title('Macro View: Price and Long-Term Moving Averages')
plt.xlabel('Date')
plt.ylabel('Price')
plt.show()
