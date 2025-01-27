import json
import requests

def fetch_historical_data(item_id):
    url = f"https://api.weirdgloop.org/exchange/history/osrs/all?id={item_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")
    return None

def main():
    # Example item ID for Coal (453)
    item_id = 2

    
    # Fetch all historical data for the item
    all_data = fetch_historical_data(item_id)
    
    if all_data:
        # Save the data to a JSON file
        file_name = f"historical_data_{item_id}.json"
        with open(file_name, 'w') as file:
            json.dump(all_data, file, indent=4)
        print(f"Data for item ID {item_id} has been saved to {file_name}")

if __name__ == "__main__":
    main()