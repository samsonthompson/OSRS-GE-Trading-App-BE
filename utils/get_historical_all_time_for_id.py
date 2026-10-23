import json
from urllib.request import Request, urlopen
from datetime import UTC, datetime


item_id = 327

def get_historical_all_time_for_id_timestamp(item_id):
    url = f"https://api.weirdgloop.org/exchange/history/osrs/all?id={item_id}"
    request = Request(url, headers={"User-Agent": "OSRS-GE-Trading-App/1.0"})
    with urlopen(request) as response:
        data = json.loads(response.read().decode("utf-8"))
    history = data[str(item_id)]
    first = history[0]

    print(first.keys())
    print(first)   
    return data

get_historical_all_time_for_id_timestamp(item_id)