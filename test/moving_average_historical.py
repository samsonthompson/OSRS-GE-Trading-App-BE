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

# Calculate 7-day moving average
df['ma_7'] = df['price'].rolling(window=7).mean()

# Print first few rows
print(df[['datetime', 'price', 'ma_7']].head(15))

# Plot
plt.figure(figsize=(12,6))
plt.plot(df['datetime'], df['price'], label='Price')
plt.plot(df['datetime'], df['ma_7'], label='7-day MA')
plt.legend()
plt.title('Price and 7-day Moving Average')
plt.xlabel('Date')
plt.ylabel('Price')
plt.show()
