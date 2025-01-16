import pandas as pd
import json

def calculate_bollinger_bands(prices, window):
    moving_avg = prices.rolling(window=window).mean()
    std_dev = prices.rolling(window=window).std()
    upper_band = moving_avg + (2 * std_dev)
    lower_band = moving_avg - (2 * std_dev)
    return moving_avg, upper_band, lower_band

def calculate_rsi(prices, window):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def load_price_data_from_json(file_path, item_id):
    with open(file_path, 'r') as file:
        data = json.load(file)
    item_data = data.get(str(item_id), [])
    prices = [float(entry.get('price', 0)) for entry in item_data]
    return pd.Series(prices)

def analyze_with_multiple_windows(prices, windows=[14, 30, 90]):
    current_price = prices.iloc[-1]
    
    print("\nCurrent Price: {:.2f}".format(current_price))
    print("\nAnalysis for different time windows:")
    print("-" * 50)
    
    for window in windows:
        ma, upper, lower = calculate_bollinger_bands(prices, window)
        rsi = calculate_rsi(prices, window)
        
        print(f"\n{window}-day indicators:")
        print(f"Moving Average: {ma.iloc[-1]:.2f}")
        print(f"Upper Band: {upper.iloc[-1]:.2f}")
        print(f"Lower Band: {lower.iloc[-1]:.2f}")
        print(f"RSI: {rsi.iloc[-1]:.2f}")
        
        # Print trading signals
        if current_price > upper.iloc[-1]:
            print(f"Signal: Price above {window}-day upper band - Consider Selling")
        elif current_price < lower.iloc[-1]:
            print(f"Signal: Price below {window}-day lower band - Consider Buying")
        
        if rsi.iloc[-1] > 70:
            print(f"Signal: {window}-day RSI indicates overbought")
        elif rsi.iloc[-1] < 30:
            print(f"Signal: {window}-day RSI indicates oversold")

def main():
    file_path = 'historical_data_453.json'
    item_id = 453
    
    prices = load_price_data_from_json(file_path, item_id)
    analyze_with_multiple_windows(prices)

if __name__ == "__main__":
    main()
