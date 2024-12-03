import requests


categories = {
0: "Miscellaneous",
1: "Ammo",
2: "Arrows",
3: "Bolts",
4: "Construction materials",
5: "Construction products",
6: "Cooking ingredients",
7: "Costumes",
8: "Crafting materials",
9: "Familiars",
10: "Farming produce",
11: "Fletching materials",
12: "Food and Drink",
13: "Herblore materials",
14: "Hunting equipment",
15: "Hunting Produce",
16: "Jewellery",
17: "Mage armour",
18: "Mage weapons",
19: "Melee armour - low level",
20: "Melee armour - mid level",
21: "Melee armour - high level",
22: "Melee weapons - low level",
23: "Melee weapons - mid level",
24: "Melee weapons - high level",
25: "Mining and Smithing",
26: "Potions",
27: "Prayer armour",
28: "Prayer materials",
29: "Range armour",
30: "Range weapons",
31: "Runecrafting",
32: "Runes, Spells and Teleports",
33: "Seeds",
34: "Summoning scrolls",
35: "Tools and containers",
36: "Woodcutting product",
37: "Pocket items",
38: "Stone spirits",
39: "Salvage",
40: "Firemaking products",
41: "Archaeology materials",
42: "Wood spirits",
43: "Necromancy armour",
}


def fetch_all_items_for_category(category_id):
    all_items = []
    page = 1
    while True:
        url = f"https://secure.runescape.com/m=itemdb_oldschool/api/catalogue/items.json?category={category_id}&alpha=a&page={page}"
        response = requests.get(url)
        
        # Check if the response is successful and is JSON
        if response.status_code != 200:
            print(f"Failed to fetch data for category {category_id}, page {page}")
            print(f"Response content: {response.content}")
            break

        try:
            data = response.json()
        except ValueError as e:
            print(f"Error parsing JSON: {e}")
            print(f"Response content: {response.content}")
            break

        items = data.get('items', [])
        if not items:
            break  # No more items to fetch

        all_items.extend(items)
        page += 1

    return all_items


def main():
    for category_id, category_name in categories.items():
        print(f"Fetching data for category: {category_name} (ID: {category_id})")
        items = fetch_all_items_for_category(category_id)
        print(f"Basic API info for category {category_name}:")
        print(f"Total items: {len(items)}")
        
        if items:
            print(f"Example item: {items[0]}")
        else:
            print("No items found.")
        
        print("\n")


if __name__ == "__main__":
    main()
