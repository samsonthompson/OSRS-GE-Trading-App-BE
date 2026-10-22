CREATE TABLE IF NOT EXISTS items (
    item_id INTEGER PRIMARY KEY,
    item_name TEXT,
    examine TEXT,
    icon TEXT,
    icon_large TEXT,
    members BOOLEAN,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS price_snapshots (
    id BIGSERIAL PRIMARY KEY,
    item_id INTEGER NOT NULL REFERENCES items(item_id),
    snapshot_ts TIMESTAMPTZ NOT NULL,
    high_price INTEGER,
    low_price INTEGER,
    high_volume BIGINT,
    low_volume BIGINT,
    source TEXT NOT NULL DEFAULT 'weirdgloop_latest',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_price_snapshot UNIQUE (item_id, snapshot_ts, source)
);

CREATE INDEX IF NOT EXISTS idx_price_snapshots_item_ts
    ON price_snapshots (item_id, snapshot_ts DESC);

CREATE TABLE IF NOT EXISTS signals_ma5 (
    id BIGSERIAL PRIMARY KEY,
    item_id INTEGER NOT NULL REFERENCES items(item_id),
    signal_ts TIMESTAMPTZ NOT NULL,
    close_price NUMERIC(14, 2) NOT NULL,
    ma5 NUMERIC(14, 2) NOT NULL,
    price_vs_ma5 NUMERIC(14, 6) NOT NULL,
    signal TEXT NOT NULL CHECK (signal IN ('buy', 'sell', 'hold')),
    jump_flag BOOLEAN NOT NULL DEFAULT FALSE,
    bot_dump_flag BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_signal_ma5 UNIQUE (item_id, signal_ts)
);

CREATE INDEX IF NOT EXISTS idx_signals_ma5_item_ts
    ON signals_ma5 (item_id, signal_ts DESC);
