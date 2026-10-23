import json
from pathlib import Path

BULK_DATA_PATH = Path(__file__).resolve().parent.parent / "osrs_bulk_data.json"

with BULK_DATA_PATH.open(encoding="utf-8") as bulk_file:
    osrs_bulk_data = json.load(bulk_file)

name_to_id = {}

for item in osrs_bulk_data.values():
    if isinstance(item, dict):
        name_to_id[item["name"]] = item["id"]


def get_item_id(item_name):
    return name_to_id[item_name]
