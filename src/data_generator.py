"""Generate synthetic listing records for pipeline demos and Airflow schedules."""

from __future__ import annotations

import argparse
import logging
import random
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.config import INCOMING_DATA_DIR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

ADDRESSES = [
    "Saadat Abad",
    "Shahrake Gharb",
    "Velenjak",
    "Narmak",
    "Punak",
    "Pardis",
    "Shahran",
    "Gheitarieh",
    "West Ferdows Boulevard",
    "Zafar",
    "Moniriyeh",
    "Andisheh",
    "Parand",
    "Shahr-e-Ziba",
]

USD_RATE = 30_000  # approximate Rial per USD for mock data


def generate_records(count: int = 50, seed: int | None = None) -> pd.DataFrame:
    """Create random listings compatible with extract/transform pipeline."""
    rng = random.Random(seed)

    rows = []
    for _ in range(count):
        area = rng.randint(45, 180)
        rooms = min(rng.randint(1, 4), max(1, area // 35))
        price_rial = area * rng.randint(25_000_000, 90_000_000)
        price_usd = round(price_rial / USD_RATE, 2)
        build_year = rng.randint(1375, 1402)

        rows.append(
            {
                "Area": area,
                "Room": rooms,
                "Parking": rng.choice([True, False]),
                "Warehouse": rng.choice([True, True, False]),
                "Elevator": rng.choice([True, False]),
                "Address": rng.choice(ADDRESSES),
                "Price": float(price_rial),
                "Price(USD)": price_usd,
                "build_year": build_year,
            }
        )

    return pd.DataFrame(rows)


def write_incoming_file(count: int = 50, output_dir: Path | None = None) -> Path:
    """Write generated records to data/incoming for incremental ETL runs."""
    output_dir = output_dir or INCOMING_DATA_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = output_dir / f"mock_listings_{timestamp}.csv"
    df = generate_records(count=count, seed=int(timestamp[-6:]))
    df.to_csv(path, index=False)
    logger.info("Wrote %s mock records to %s", len(df), path)
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate mock Tehran listing CSV files")
    parser.add_argument("--count", type=int, default=50, help="Number of records")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=INCOMING_DATA_DIR,
        help="Directory for generated CSV",
    )
    args = parser.parse_args()
    write_incoming_file(count=args.count, output_dir=args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
