import json
import requests

def fetch_historical_data(item_id):
    url = f"https://api.weirdgloop.org/exchange/history/osrs/last90d?id={item_id}"
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

def write_data_to_file(data, filename):
    try:
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)
        print(f"Data successfully written to {filename}")
    except Exception as e:
        print(f"An error occurred while writing to file: {e}")

def main():
    # Example item ID for Abyssal Whip
    item_id = 4151
    
    # Fetch the historical data
    historical_data = fetch_historical_data(item_id)
    
    if historical_data:
        # Write the data to a JSON file
        write_data_to_file(historical_data, 'historical_data.json')

if __name__ == "__main__":
    main()
