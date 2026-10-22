import argparse
import json
import math
import os
import time
from collections import defaultdict, deque
from datetime import UTC, datetime
from pathlib import Path
from urllib.request import Request, urlopen

from db.connection import get_connection

EXCHANGE_STATUS_API_URL = "https://api.weirdgloop.org/exchange"
BULK_DUMP_API_URL = "https://chisel.weirdgloop.org/gazproj/gazbot/os_dump.json"
DEFAULT_SOURCE = "weirdgloop_dump"
ANOMALY_PRICE_CAP = 2_147_483_646


def fetch_json(url: str) -> dict | list:
    request = Request(url, headers={"User-Agent": "OSRS-GE-Trading-App/1.0"})
    with urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


def load_exchange_last_updated() -> datetime:
    payload = fetch_json(EXCHANGE_STATUS_API_URL)
    osrs_value = payload.get("osrs")
    if not osrs_value:
        return datetime.now(tz=UTC)
    if isinstance(osrs_value, str) and osrs_value.endswith("Z"):
        osrs_value = osrs_value[:-1] + "+00:00"
    return datetime.fromisoformat(osrs_value)


def load_latest_snapshot() -> tuple[datetime, dict[int, dict], dict[int, dict]]:
    snapshot_ts = load_exchange_last_updated()
    payload = fetch_json(BULK_DUMP_API_URL)
    latest_by_id: dict[int, dict] = {}
    mapping_by_id: dict[int, dict] = {}

    for item_id_text, row in payload.items():
        item_id = int(item_id_text)
        price = row.get("price")
        volume = row.get("volume")
        latest_by_id[item_id] = {
            "high": price,
            "low": price,
            "highVolume": volume,
            "lowVolume": volume,
        }
        mapping_by_id[item_id] = {
            "name": row.get("name"),
            "examine": row.get("examine"),
            "icon": row.get("icon"),
            "icon_large": row.get("icon"),
            "members": row.get("members"),
        }

    return snapshot_ts, latest_by_id, mapping_by_id


def apply_schema() -> None:
    schema_path = Path(__file__).resolve().parent.parent / "db" / "schema.sql"
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(schema_path.read_text(encoding="utf-8"))
        conn.commit()


def upsert_items(conn, mapping_by_id: dict[int, dict], latest_by_id: dict[int, dict]) -> None:
    with conn.cursor() as cur:
        for item_id in latest_by_id:
            mapping = mapping_by_id.get(item_id, {})
            cur.execute(
                """
                INSERT INTO items (item_id, item_name, examine, icon, icon_large, members, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT (item_id)
                DO UPDATE SET
                    item_name = EXCLUDED.item_name,
                    examine = EXCLUDED.examine,
                    icon = EXCLUDED.icon,
                    icon_large = EXCLUDED.icon_large,
                    members = EXCLUDED.members,
                    updated_at = NOW()
                """,
                (
                    item_id,
                    mapping.get("name"),
                    mapping.get("examine"),
                    mapping.get("icon"),
                    mapping.get("icon_large"),
                    mapping.get("members"),
                ),
            )


def insert_snapshots(conn, snapshot_ts: datetime, latest_by_id: dict[int, dict], source: str) -> None:
    rejected = 0
    accepted = 0
    with conn.cursor() as cur:
        for item_id, row in latest_by_id.items():
            high_price = row.get("high")
            low_price = row.get("low")
            if high_price is None and low_price is None:
                rejected += 1
                continue
            if high_price is not None and high_price < 0:
                rejected += 1
                continue
            if low_price is not None and low_price < 0:
                rejected += 1
                continue
            cur.execute(
                """
                INSERT INTO price_snapshots (
                    item_id, snapshot_ts, high_price, low_price, high_volume, low_volume, source
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (item_id, snapshot_ts, source) DO NOTHING
                """,
                (
                    item_id,
                    snapshot_ts,
                    high_price,
                    low_price,
                    row.get("highVolume"),
                    row.get("lowVolume"),
                    source,
                ),
            )
            accepted += 1
    return {"accepted_snapshots": accepted, "rejected_snapshots": rejected}


def _signal_from_ratio(ratio: float) -> str:
    if ratio > 0.01:
        return "buy"
    if ratio < -0.01:
        return "sell"
    return "hold"


def _compute_anomaly_flags(prices: deque[float], current_price: float, latest_volume: int | None) -> tuple[bool, bool]:
    jump_flag = False
    bot_dump_flag = False

    if current_price >= ANOMALY_PRICE_CAP:
        jump_flag = True

    if len(prices) >= 2:
        prior = prices[-2]
        if prior > 0:
            pct_move = (current_price - prior) / prior
            if abs(pct_move) >= 0.15:
                jump_flag = True
            if pct_move <= -0.20 and latest_volume is not None and latest_volume > 0:
                bot_dump_flag = True

    return jump_flag, bot_dump_flag


def compute_and_upsert_ma5_signals(conn, source: str, as_of_ts: datetime) -> dict:
    inserted = 0
    jump_flags = 0
    bot_dump_flags = 0
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT item_id, snapshot_ts, high_price, low_price, low_volume
            FROM price_snapshots
            WHERE source = %s AND snapshot_ts <= %s
            ORDER BY item_id, snapshot_ts ASC
            """,
            (source, as_of_ts),
        )
        rows = cur.fetchall()

    history: dict[int, deque[float]] = defaultdict(lambda: deque(maxlen=5))
    latest_state: dict[int, tuple[datetime, float, float, bool, bool]] = {}

    for item_id, snapshot_ts, high_price, low_price, low_volume in rows:
        if high_price is None and low_price is None:
            continue

        if high_price is None:
            close_price = float(low_price)
        elif low_price is None:
            close_price = float(high_price)
        else:
            close_price = float((high_price + low_price) / 2)

        prices = history[item_id]
        prices.append(close_price)
        if len(prices) < 5:
            continue

        ma5 = sum(prices) / 5
        ratio = (close_price - ma5) / ma5 if ma5 else 0.0
        signal = _signal_from_ratio(ratio)
        jump_flag, bot_dump_flag = _compute_anomaly_flags(prices, close_price, low_volume)
        latest_state[item_id] = (snapshot_ts, close_price, ma5, signal, jump_flag or bot_dump_flag)

    with conn.cursor() as cur:
        for item_id, (signal_ts, close_price, ma5, signal, anomaly_flag) in latest_state.items():
            price_vs_ma5 = 0.0 if math.isclose(ma5, 0) else (close_price - ma5) / ma5
            cur.execute(
                """
                INSERT INTO signals_ma5 (
                    item_id, signal_ts, close_price, ma5, price_vs_ma5, signal, jump_flag, bot_dump_flag
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (item_id, signal_ts)
                DO UPDATE SET
                    close_price = EXCLUDED.close_price,
                    ma5 = EXCLUDED.ma5,
                    price_vs_ma5 = EXCLUDED.price_vs_ma5,
                    signal = EXCLUDED.signal,
                    jump_flag = EXCLUDED.jump_flag,
                    bot_dump_flag = EXCLUDED.bot_dump_flag
                """,
                (
                    item_id,
                    signal_ts,
                    round(close_price, 2),
                    round(ma5, 2),
                    round(price_vs_ma5, 6),
                    signal,
                    anomaly_flag,
                    anomaly_flag and signal == "sell",
                ),
            )
            inserted += 1
            if anomaly_flag:
                jump_flags += 1
            if anomaly_flag and signal == "sell":
                bot_dump_flags += 1

    return {
        "signals_written": inserted,
        "jump_flags": jump_flags,
        "bot_dump_flags": bot_dump_flags,
    }


def run_ingest_cycle(source: str = DEFAULT_SOURCE) -> dict:
    apply_schema()
    snapshot_ts, latest_by_id, mapping_by_id = load_latest_snapshot()

    with get_connection() as conn:
        upsert_items(conn, mapping_by_id, latest_by_id)
        snapshot_stats = insert_snapshots(conn, snapshot_ts, latest_by_id, source)
        signal_stats = compute_and_upsert_ma5_signals(conn, source, snapshot_ts)
        conn.commit()

    return {
        "snapshot_ts": snapshot_ts.isoformat(),
        "items_seen": len(latest_by_id),
        "source": source,
        **snapshot_stats,
        **signal_stats,
    }


def run_scheduler(interval_seconds: int) -> None:
    while True:
        started = datetime.now(tz=UTC).isoformat()
        try:
            result = run_ingest_cycle()
            print(json.dumps({"status": "ok", "started_at": started, **result}, indent=2))
        except Exception as exc:
            print(json.dumps({"status": "error", "started_at": started, "error": str(exc)}, indent=2))
        time.sleep(interval_seconds)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest latest OSRS prices and compute MA(5) signals.")
    parser.add_argument("--run-once", action="store_true", help="Run one ingestion cycle and exit.")
    parser.add_argument(
        "--interval-seconds",
        type=int,
        default=int(os.getenv("INGEST_INTERVAL_SECONDS", "86400")),
        help="Schedule interval for daemon mode. Defaults to daily.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.run_once:
        print(json.dumps(run_ingest_cycle(), indent=2))
        return
    run_scheduler(args.interval_seconds)


if __name__ == "__main__":
    main()

