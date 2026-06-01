"""Transform step: clean and enrich listing data."""

from __future__ import annotations

import hashlib
import logging
import re

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

MIN_AREA_SQM = 20
MAX_AREA_SQM = 1000
MIN_PRICE_PER_SQM = 1_000_000
MAX_PRICE_PER_SQM = 500_000_000
MIN_ROOMS = 0
MAX_ROOMS = 10


def _parse_numeric(value: object) -> float | None:
    """Parse numbers that may contain commas or whitespace."""
    if pd.isna(value):
        return None
    if isinstance(value, (int, float, np.integer, np.floating)):
        return float(value)
    text = str(value).strip().replace(",", "")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _parse_bool(value: object) -> bool:
    if pd.isna(value):
        return False
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    return text in {"true", "1", "yes", "t"}


def _fix_swapped_area_price(row: pd.Series) -> pd.Series:
    """
    Some rows have price values in the Area column (e.g. '3,310,000,000').
    Detect and swap when Area looks like a price and Price looks like area.
    """
    area = _parse_numeric(row.get("Area"))
    price = _parse_numeric(row.get("Price"))

    area_looks_like_price = area is not None and area >= 1_000_000
    price_looks_like_area = price is not None and price <= MAX_AREA_SQM

    if area_looks_like_price and price_looks_like_area:
        row = row.copy()
        row["Area"], row["Price"] = price, area
    return row


def _compute_record_hash(row: pd.Series) -> str:
    payload = "|".join(
        [
            str(row["area_sqm"]),
            str(row["rooms"]),
            str(row["parking"]),
            str(row["warehouse"]),
            str(row["elevator"]),
            str(row["address"]).strip().lower(),
            str(row["price_rial"]),
            str(row.get("source_file", "")),
        ]
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def rial_to_toman(price_rial: float) -> int:
    """Convert Iranian Rial to Toman (1 Toman = 10 Rials)."""
    return int(round(price_rial / 10))


def compute_price_per_sqm(price_rial: float, area_sqm: float) -> int:
    """Compute price per square meter in Rial."""
    return int(round(price_rial / area_sqm))


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Clean raw listings and produce analytics-ready records."""
    if df.empty:
        return df

    working = df.copy()
    working = working.apply(_fix_swapped_area_price, axis=1)

    working["area_sqm"] = working["Area"].map(_parse_numeric)
    working["rooms"] = pd.to_numeric(working["Room"], errors="coerce")
    working["parking"] = working["Parking"].map(_parse_bool)
    working["warehouse"] = working["Warehouse"].map(_parse_bool)
    working["elevator"] = working["Elevator"].map(_parse_bool)
    working["address"] = working["Address"].astype(str).str.strip()
    working["price_rial"] = working["Price"].map(_parse_numeric)
    working["price_usd"] = working["Price(USD)"].map(_parse_numeric)
    working["source_file"] = working.get("source_file", "unknown")

    if "build_year" not in working.columns:
        working["build_year"] = pd.NA

    before = len(working)

    working = working.dropna(subset=["area_sqm", "rooms", "price_rial", "address"])
    working = working[working["address"].str.lower() != "nan"]
    working = working[
        (working["area_sqm"] >= MIN_AREA_SQM)
        & (working["area_sqm"] <= MAX_AREA_SQM)
        & (working["rooms"] >= MIN_ROOMS)
        & (working["rooms"] <= MAX_ROOMS)
        & (working["price_rial"] > 0)
    ]

    if working.empty:
        return pd.DataFrame(
            columns=[
                "record_hash",
                "area_sqm",
                "rooms",
                "parking",
                "warehouse",
                "elevator",
                "address",
                "price_rial",
                "price_toman",
                "price_usd",
                "price_per_sqm",
                "build_year",
                "source_file",
            ]
        )

    working["price_toman"] = (working["price_rial"] / 10).round().astype(int)
    working["price_per_sqm"] = (
        (working["price_rial"] / working["area_sqm"]).round().astype(int)
    )

    working = working[
        (working["price_per_sqm"] >= MIN_PRICE_PER_SQM)
        & (working["price_per_sqm"] <= MAX_PRICE_PER_SQM)
    ]

    working["record_hash"] = working.apply(_compute_record_hash, axis=1)
    working = working.drop_duplicates(subset=["record_hash"], keep="first")

    cleaned = working[
        [
            "record_hash",
            "area_sqm",
            "rooms",
            "parking",
            "warehouse",
            "elevator",
            "address",
            "price_rial",
            "price_toman",
            "price_usd",
            "price_per_sqm",
            "build_year",
            "source_file",
        ]
    ].reset_index(drop=True)

    logger.info(
        "Transform complete: %s -> %s rows (removed %s)",
        before,
        len(cleaned),
        before - len(cleaned),
    )
    return cleaned
