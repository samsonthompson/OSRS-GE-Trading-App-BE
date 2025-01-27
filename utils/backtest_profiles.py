import pandas as pd
import json
from .calculate_indicators import calculate_bollinger_bands, calculate_rsi, calculate_signal_strength

class TradingProfile:
    def __init__(self, name, timeframe_weights, indicator_weights):
        self.name = name
        self.timeframe_weights = timeframe_weights
        self.indicator_weights = indicator_weights

# Define different trading profiles
TRADING_PROFILES = {
    'day_trader': TradingProfile(
        'Day Trader',
        timeframe_weights={14: 0.5, 30: 0.3, 90: 0.2},
        indicator_weights={
            14: {'bollinger': 0.4, 'rsi': 0.4, 'ma': 0.2},
            30: {'bollinger': 0.3, 'rsi': 0.4, 'ma': 0.3},
            90: {'bollinger': 0.2, 'rsi': 0.3, 'ma': 0.5}
        }
    ),
    'swing_trader': TradingProfile(
        'Swing Trader',
        timeframe_weights={14: 0.2, 30: 0.5, 90: 0.3},
        indicator_weights={
            14: {'bollinger': 0.3, 'rsi': 0.5, 'ma': 0.2},
            30: {'bollinger': 0.4, 'rsi': 0.4, 'ma': 0.2},
            90: {'bollinger': 0.5, 'rsi': 0.2, 'ma': 0.3}
        }
    ),
    'position_trader': TradingProfile(
        'Position Trader',
        timeframe_weights={14: 0.1, 30: 0.3, 90: 0.6},
        indicator_weights={
            14: {'bollinger': 0.2, 'rsi': 0.3, 'ma': 0.5},
            30: {'bollinger': 0.3, 'rsi': 0.3, 'ma': 0.4},
            90: {'bollinger': 0.4, 'rsi': 0.2, 'ma': 0.4}
        }
    )
}

class BacktestEngine:
    def __init__(self, prices, profile):
        self.prices = prices
        self.profile = profile
        self.results = []

    def run_backtest(self, initial_capital=1000000):
        capital = initial_capital
        position = 0
        trades = []
        
        # We need enough data for our longest timeframe (90 days)
        for i in range(90, len(self.prices)):
            slice_prices = self.prices[:i+1]
            signal = self.calculate_aggregate_signal(slice_prices)
            
            current_price = self.prices[i]
            
            # Trading logic
            if signal > 70 and position <= 0:  # Strong buy
                position = capital // current_price
                capital -= position * current_price
                trades.append({
                    'type': 'BUY',
                    'price': current_price,
                    'quantity': position,
                    'signal': signal,
                    'timestamp': i
                })
            elif signal < -70 and position > 0:  # Strong sell
                capital += position * current_price
                trades.append({
                    'type': 'SELL',
                    'price': current_price,
                    'quantity': position,
                    'signal': signal,
                    'timestamp': i
                })
                position = 0

        # Calculate final position value
        final_capital = capital + (position * self.prices[-1])
        roi = ((final_capital - initial_capital) / initial_capital) * 100
        
        return {
            'initial_capital': initial_capital,
            'final_capital': final_capital,
            'roi': roi,
            'trades': trades,
            'profile_name': self.profile.name
        }

    def calculate_aggregate_signal(self, prices):
        final_signals = []
        
        for window in [14, 30, 90]:
            if len(prices) >= window:
                ma, upper, lower = calculate_bollinger_bands(prices, window)
                rsi = calculate_rsi(prices, window)
                
                signal_strength = calculate_signal_strength(
                    prices.iloc[-1],
                    ma.iloc[-1],
                    upper.iloc[-1],
                    lower.iloc[-1],
                    rsi.iloc[-1],
                    self.profile.indicator_weights[window]
                )
                
                final_signals.append(signal_strength * self.profile.timeframe_weights[window])
        
        return sum(final_signals)

def run_all_profiles(file_path, item_id):
    # Load price data
    with open(file_path, 'r') as file:
        data = json.load(file)
    prices = pd.Series([float(entry['price']) for entry in data[str(item_id)]])
    
    results = []
    
    # Run backtest for each profile
    for profile in TRADING_PROFILES.values():
        engine = BacktestEngine(prices, profile)
        result = engine.run_backtest()
        results.append(result)
        
        print(f"\nResults for {profile.name}:")
        print(f"ROI: {result['roi']:.2f}%")
        print(f"Final Capital: {result['final_capital']:.2f}")
        print(f"Number of trades: {len(result['trades'])}")
    
    return results

if __name__ == "__main__":
    results = run_all_profiles('historical_data_453.json', 453) 