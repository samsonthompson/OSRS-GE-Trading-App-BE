import requests
import json
from datetime import datetime, timezone

def fetch_historical_data(item_id):
    url = f"https://api.weirdgloop.org/exchange/history/osrs/all?id={item_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    item_id = 327  # Example item ID
    all_data = fetch_historical_data(item_id)
    print("Raw API response:")
    print(json.dumps(all_data, indent=2))

    if all_data is not None:
        # Print the first 5 entries with human-readable timestamps
        item_history = all_data.get(str(item_id), [])
        print("\nFirst 5 entries with readable timestamps:")
        for entry in item_history[:5]:
            ts = entry['timestamp']
            date_str = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            print(f"Timestamp: {ts} -> {date_str}, Price: {entry['price']}, Volume: {entry['volume']}")
    else:
        print("No data returned from API.")

if __name__ == "__main__":
    main()
