import json
from pathlib import Path

HISTORY_PATH = Path(__file__).resolve().parent.parent / "historical_data_327.json"

with HISTORY_PATH.open(encoding="utf-8") as history_file:
    historical_data = json.load(history_file)


def five_day_moving_average(historical_data):
    rows = next(iter(historical_data.values()))
    last_five_prices = [row["price"] for row in rows[-5:]]
    latest_price = last_five_prices[-1]
    ma5 = sum(last_five_prices) / 5
    ratio = (latest_price - ma5) / ma5 if ma5 else 0

    if ratio > 0.01:
        signal = "buy"
    elif ratio < -0.01:
        signal = "sell"
    else:
        signal = "hold"

    return {
        "price": latest_price,
        "ma5": ma5,
        "signal": signal,
    }


if __name__ == "__main__":
    print(five_day_moving_average(historical_data))
