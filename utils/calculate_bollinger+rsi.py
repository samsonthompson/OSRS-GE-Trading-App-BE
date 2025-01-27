import pandas as pd
import json
from prediction_tracker import PredictionTracker

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
    
    # Create dictionary to store all analysis data
    analysis_data = {
        'current_price': current_price,
        'ma_14': None, 'ma_30': None, 'ma_90': None,
        'rsi_14': None, 'rsi_30': None, 'rsi_90': None,
        'upper_14': None, 'lower_14': None,
        'upper_30': None, 'lower_30': None,
        'upper_90': None, 'lower_90': None,
        'signal_14': '', 'signal_30': '', 'signal_90': ''
    }
    
    for window in windows:
        ma, upper, lower = calculate_bollinger_bands(prices, window)
        rsi = calculate_rsi(prices, window)
        
        # Store values
        analysis_data[f'ma_{window}'] = ma.iloc[-1]
        analysis_data[f'rsi_{window}'] = rsi.iloc[-1]
        analysis_data[f'upper_{window}'] = upper.iloc[-1]
        analysis_data[f'lower_{window}'] = lower.iloc[-1]
        
        # Generate signals
        signal = ''
        if current_price > upper.iloc[-1]:
            signal = "Sell"
        elif current_price < lower.iloc[-1]:
            signal = "Buy"
        elif rsi.iloc[-1] > 70:
            signal = "Sell (RSI)"
        elif rsi.iloc[-1] < 30:
            signal = "Buy (RSI)"
        analysis_data[f'signal_{window}'] = signal
    
    return analysis_data

def main():
    file_path = 'historical_data_453.json'
    item_id = 453
    
    prices = load_price_data_from_json(file_path, item_id)
    analysis_data = analyze_with_multiple_windows(prices)
    
    # Initialize tracker and record prediction
    tracker = PredictionTracker()
    prediction_id = tracker.record_prediction(item_id, analysis_data)
    
    # Print analysis
    print(f"\nPrediction ID: {prediction_id}")
    print(f"Current Price: {analysis_data['current_price']:.2f}")
    
    for window in [14, 30, 90]:
        print(f"\n{window}-day indicators:")
        print(f"Moving Average: {analysis_data[f'ma_{window}']:.2f}")
        print(f"Upper Band: {analysis_data[f'upper_{window}']:.2f}")
        print(f"Lower Band: {analysis_data[f'lower_{window}']:.2f}")
        print(f"RSI: {analysis_data[f'rsi_{window}']:.2f}")
        if analysis_data[f'signal_{window}']:
            print(f"Signal: {analysis_data[f'signal_{window}']}")

if __name__ == "__main__":
    main()
