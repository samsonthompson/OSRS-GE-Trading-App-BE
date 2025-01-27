import requests
from datetime import datetime

def fetch_bulk_data():
    url = "https://chisel.weirdgloop.org/gazproj/gazbot/os_dump.json"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
        
        # Get the current timestamp
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Print the total number of items with a timestamp
        total_items = len(data)
        print(f"[{current_time}] Total number of items: {total_items}")
        
        # Find pricing for Onyx ring
        onyx_ring = None
        for item_id, item_data in data.items():
            if isinstance(item_data, dict) and item_data.get("name") == "Onyx ring":
                onyx_ring = item_data
                break
        
        if onyx_ring:
            print(f"[{current_time}] Onyx Ring Price: {onyx_ring['price']}")
        else:
            print(f"[{current_time}] Onyx Ring not found.")
    
    except requests.exceptions.HTTPError as http_err:
        print(f"[{current_time}] HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"[{current_time}] Other error occurred: {err}")

fetch_bulk_data()
