import json
from datetime import datetime, timezone

def get_bulk_data_and_timestamp(json_path='osrs_bulk_data.json'):
    with open(json_path, 'r') as f:
        data = json.load(f)
    # Extract special timestamp keys
    jagex_timestamp = data.get('%JAGEX_TIMESTAMP%')
    update_detected = data.get('%UPDATE_DETECTED%')
    # Remove special keys from the main data if needed
    item_data = {k: v for k, v in data.items() if not k.startswith('%')}

    # Convert timestamps to readable format if they exist
    def to_readable(ts):
        if ts is None:
            return None
        # If float, convert to int (for seconds)
        ts = int(float(ts))
        return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()

    jagex_timestamp_readable = to_readable(jagex_timestamp)
    update_detected_readable = to_readable(update_detected)

    return item_data, jagex_timestamp_readable, update_detected_readable

# Example usage:
items, jagex_ts, update_ts = get_bulk_data_and_timestamp()
print(f"Jagex Timestamp: {jagex_ts}")
print(f"Update Detected: {update_ts}")
print(f"Total number of items: {len(items)}")
