"""Load step: upsert cleaned data into PostgreSQL."""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from src.config import DATABASE_URL

logger = logging.getLogger(__name__)

UPSERT_SQL = """
INSERT INTO listings (
    record_hash, area_sqm, rooms, parking, warehouse, elevator,
    address, price_rial, price_toman, price_usd, price_per_sqm,
    build_year, source_file
) VALUES (
    :record_hash, :area_sqm, :rooms, :parking, :warehouse, :elevator,
    :address, :price_rial, :price_toman, :price_usd, :price_per_sqm,
    :build_year, :source_file
)
ON CONFLICT (record_hash) DO UPDATE SET
    area_sqm = EXCLUDED.area_sqm,
    rooms = EXCLUDED.rooms,
    parking = EXCLUDED.parking,
    warehouse = EXCLUDED.warehouse,
    elevator = EXCLUDED.elevator,
    address = EXCLUDED.address,
    price_rial = EXCLUDED.price_rial,
    price_toman = EXCLUDED.price_toman,
    price_usd = EXCLUDED.price_usd,
    price_per_sqm = EXCLUDED.price_per_sqm,
    build_year = EXCLUDED.build_year,
    source_file = EXCLUDED.source_file,
    updated_at = NOW();
"""


def get_engine(database_url: str | None = None) -> Engine:
    return create_engine(database_url or DATABASE_URL, pool_pre_ping=True)


def wait_for_database(engine: Engine, retries: int = 30, delay_seconds: float = 2.0) -> None:
    """Block until PostgreSQL accepts connections."""
    import time

    for attempt in range(1, retries + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection established")
            return
        except Exception as exc:
            logger.warning("DB not ready (attempt %s/%s): %s", attempt, retries, exc)
            time.sleep(delay_seconds)
    raise ConnectionError("Could not connect to PostgreSQL")


def _row_to_params(row: pd.Series) -> dict[str, Any]:
    build_year = row.get("build_year")
    if pd.isna(build_year):
        build_year = None
    else:
        build_year = int(build_year)

    return {
        "record_hash": row["record_hash"],
        "area_sqm": float(row["area_sqm"]),
        "rooms": int(row["rooms"]),
        "parking": bool(row["parking"]),
        "warehouse": bool(row["warehouse"]),
        "elevator": bool(row["elevator"]),
        "address": row["address"],
        "price_rial": int(row["price_rial"]),
        "price_toman": int(row["price_toman"]),
        "price_usd": float(row["price_usd"]) if pd.notna(row.get("price_usd")) else None,
        "price_per_sqm": int(row["price_per_sqm"]),
        "build_year": build_year,
        "source_file": row.get("source_file"),
    }


def load(df: pd.DataFrame, database_url: str | None = None) -> int:
    """Upsert transformed rows into PostgreSQL. Returns rows processed."""
    if df.empty:
        logger.warning("No rows to load")
        return 0

    engine = get_engine(database_url)
    wait_for_database(engine)

    params = [_row_to_params(row) for _, row in df.iterrows()]
    with engine.begin() as conn:
        conn.execute(text(UPSERT_SQL), params)

    logger.info("Loaded %s rows into listings", len(params))
    return len(params)


def get_row_count(database_url: str | None = None) -> int:
    engine = get_engine(database_url)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM listings"))
        return int(result.scalar_one())
