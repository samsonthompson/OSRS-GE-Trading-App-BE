import json
import urllib.request

def fetch_bulk_data(url):
    try:
        # Create a request object with a User-Agent header
        request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(request) as response:
            data = json.loads(response.read().decode())
            return data
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def write_data_to_file(data, filename):
    try:
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)
        print(f"Data successfully written to {filename}")
    except Exception as e:
        print(f"An error occurred while writing to file: {e}")

def main():
    # URL for the OSRS bulk data JSON dump
    osrs_bulk_data_url = "https://chisel.weirdgloop.org/gazproj/gazbot/os_dump.json"
    
    # Fetch the data
    data = fetch_bulk_data(osrs_bulk_data_url)
    
    if data:
        # Write the data to a file
        write_data_to_file(data, 'osrs_bulk_data.json')

if __name__ == "__main__":
    main()