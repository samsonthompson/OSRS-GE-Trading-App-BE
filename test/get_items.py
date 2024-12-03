import requests

def get_osrs_item_data(category, alpha, page):
    url = f"https://secure.runescape.com/m=itemdb_oldschool/api/catalogue/items.json?category={category}&alpha={alpha}&page={page}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        data = response.json()
        print(data)
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")

# Example usage: Get items in category 1 (Ammo) starting with 'c' on page 1
category_id = 1
alpha = 'c'
page = 1

get_osrs_item_data(category_id, alpha, page)
