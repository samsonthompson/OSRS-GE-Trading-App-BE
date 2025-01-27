import json
from datetime import datetime, UTC

def analyze_timestamps(data):
    # Extract timestamps
    timestamps = [entry['timestamp'] for entry in data]
    
    # Calculate first and last timestamps
    first_timestamp = timestamps[0]
    last_timestamp = timestamps[-1]
    first_date = datetime.fromtimestamp(first_timestamp / 1000, UTC).strftime('%Y-%m-%d %H:%M:%S')
    last_date = datetime.fromtimestamp(last_timestamp / 1000, UTC).strftime('%Y-%m-%d %H:%M:%S')
    
    # Calculate total time range
    total_days = (last_timestamp - first_timestamp) / (1000 * 86400)  
    # Convert ms to days
    total_weeks = total_days / 7 
    
    # Calculate interval between data points
    intervals = [timestamps[i] - timestamps[i - 1] for i in range(1, len(timestamps))]
    avg_interval_days = (sum(intervals) / len(intervals)) / (1000 * 86400) 
    
    print(f"\nData Range Summary:")
    print(f"First entry: {first_date}")
    print(f"Last entry: {last_date}")
    print(f"Total time span: {total_days:.1f} days ({total_weeks:.1f} weeks)")
    print(f"Average interval between entries: {avg_interval_days:.1f} days")

def main():
    with open('historical_data.json', 'r') as file:
        historical_data = json.load(file)
    
    for item_id, data in historical_data.items():
        print(f"\nAnalyzing item ID: {item_id}")
        analyze_timestamps(data)

if __name__ == "__main__":
    main()
