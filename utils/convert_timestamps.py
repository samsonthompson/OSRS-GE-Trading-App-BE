import json
from datetime import datetime

def analyze_timestamps(data):
    # Print the structure of data for debugging
    print("Data structure:", data)
    
    # Extract timestamps
    timestamps = [entry['timestamp'] for entry in data]  # Access the 'timestamp' key directly
    human_readable_dates = [datetime.utcfromtimestamp(ts / 1000).strftime('%Y-%m-%d %H:%M:%S') for ts in timestamps]
    
    # Calculate intervals between timestamps
    intervals = [timestamps[i] - timestamps[i - 1] for i in range(1, len(timestamps))]
    
    # Print the first few timestamps and intervals
    print("First few timestamps and their human-readable dates:")
    for ts, date in zip(timestamps[:5], human_readable_dates[:5]):
        print(f"Timestamp: {ts}, Date: {date}")
    
    print("\nIntervals between timestamps (in seconds):")
    print(intervals[:5])

def main():
    # Load the historical data from the JSON file
    with open('historical_data.json', 'r') as file:
        historical_data = json.load(file)
    
    # Analyze the timestamps
    for item_id, data in historical_data.items():
        print(f"\nAnalyzing data for item ID: {item_id}")
        analyze_timestamps(data)

if __name__ == "__main__":
    main()
