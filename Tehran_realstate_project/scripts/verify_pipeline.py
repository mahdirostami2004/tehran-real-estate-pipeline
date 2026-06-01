#!/usr/bin/env python3
"""Verify ETL pipeline end-to-end: transform stats + optional DB check."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import RAW_DATA_DIR
from src.etl_pipeline import run_pipeline
from src.load import get_engine, get_row_count, wait_for_database
from sqlalchemy import text


def main() -> int:
    print("=== Tehran Real Estate Pipeline Verification ===\n")

    raw_file = RAW_DATA_DIR / "TehranHouse.csv"
    if not raw_file.exists():
        print(f"FAIL: Missing dataset at {raw_file}")
        return 1
    print(f"OK  : Raw dataset found ({raw_file})")

    summary = run_pipeline(save_processed=True, skip_load=True)
    print(f"OK  : Extracted {summary['raw_rows']} rows")
    print(f"OK  : Transformed to {summary['clean_rows']} clean rows")
    print(f"OK  : Processed CSV -> {summary['processed_file']}")

    try:
        engine = get_engine()
        wait_for_database(engine, retries=5, delay_seconds=2)
        loaded = run_pipeline(save_processed=False, skip_load=False)
        count = get_row_count()
        with engine.connect() as conn:
            avg_pps = conn.execute(
                text("SELECT ROUND(AVG(price_per_sqm)) FROM listings")
            ).scalar_one()
            top_area = conn.execute(
                text(
                    """
                    SELECT address, ROUND(AVG(price_per_sqm)) AS avg_pps, COUNT(*) AS n
                    FROM listings
                    GROUP BY address
                    ORDER BY avg_pps DESC
                    LIMIT 3
                    """
                )
            ).fetchall()

        print(f"OK  : Loaded {loaded['loaded_rows']} rows this run")
        print(f"OK  : Total rows in DB: {count}")
        print(f"OK  : Average price_per_sqm: {avg_pps:,} Rial")
        print("OK  : Top 3 neighborhoods by avg price/m²:")
        for row in top_area:
            print(f"      - {row[0]}: {row[1]:,} ({row[2]} listings)")
    except Exception as exc:
        print(f"WARN: Database check skipped ({exc})")
        print("      Run: sudo usermod -aG docker $USER && newgrp docker")
        print("      Then: make up && make verify")

    print("\n=== Verification complete ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
