"""End-to-end ETL orchestration."""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.config import PROCESSED_DATA_DIR, PROJECT_ROOT
from src.extract import extract
from src.load import get_row_count, load
from src.transform import transform

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


def run_pipeline(
    save_processed: bool = True,
    include_incoming: bool = True,
    skip_load: bool = False,
) -> dict:
    """Execute extract -> transform -> load and return run summary."""
    started_at = datetime.now(timezone.utc)

    raw_df = extract(include_incoming=include_incoming)
    cleaned_df = transform(raw_df)

    processed_path: Path | None = None
    if save_processed and not cleaned_df.empty:
        PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = started_at.strftime("%Y%m%d_%H%M%S")
        processed_path = PROCESSED_DATA_DIR / f"listings_clean_{timestamp}.csv"
        cleaned_df.to_csv(processed_path, index=False)
        logger.info("Saved processed file: %s", processed_path)

    loaded_rows = 0
    total_rows = None
    if not skip_load:
        loaded_rows = load(cleaned_df)
        total_rows = get_row_count()

    summary = {
        "started_at": started_at.isoformat(),
        "raw_rows": len(raw_df),
        "clean_rows": len(cleaned_df),
        "loaded_rows": loaded_rows,
        "total_rows_in_db": total_rows,
        "processed_file": str(processed_path) if processed_path else None,
    }
    logger.info("Pipeline summary: %s", summary)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Tehran Real Estate ETL Pipeline")
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Skip writing processed CSV output",
    )
    parser.add_argument(
        "--skip-load",
        action="store_true",
        help="Run extract/transform only (no database load)",
    )
    parser.add_argument(
        "--incoming-only",
        action="store_true",
        help="Process only files in data/incoming/",
    )
    args = parser.parse_args()

    sys.path.insert(0, str(PROJECT_ROOT))

    if args.incoming_only:
        from src.config import INCOMING_DATA_DIR, RAW_DATA_DIR

        raw_df = extract(
            raw_dir=INCOMING_DATA_DIR,
            incoming_dir=INCOMING_DATA_DIR,
            include_incoming=False,
        )
        cleaned_df = transform(raw_df)
        loaded_rows = 0 if args.skip_load else load(cleaned_df)
        logger.info(
            "Incoming-only run: raw=%s clean=%s loaded=%s",
            len(raw_df),
            len(cleaned_df),
            loaded_rows,
        )
        return 0

    run_pipeline(
        save_processed=not args.no_save,
        skip_load=args.skip_load,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
