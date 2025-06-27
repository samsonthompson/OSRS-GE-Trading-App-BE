import json
from datetime import datetime, timezone

def get_bulk_data_timestamps(json_path='osrs_bulk_data.json'):
    with open(json_path, 'r') as f:
        data = json.load(f)
    # Extract and convert timestamps
    def to_iso(ts):
        if ts is None:
            return None
        return datetime.fromtimestamp(int(float(ts)), tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    return {
        "Jagex Timestamp": to_iso(data.get('%JAGEX_TIMESTAMP%')),
        "Update Detected": to_iso(data.get('%UPDATE_DETECTED%'))
    }

# Example usage:
timestamps = get_bulk_data_timestamps()
print(timestamps)
