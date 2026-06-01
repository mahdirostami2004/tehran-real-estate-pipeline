"""Extract step: read CSV files from raw and incoming directories."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from src.config import EXPECTED_COLUMNS, INCOMING_DATA_DIR, RAW_DATA_DIR

logger = logging.getLogger(__name__)


def discover_csv_files(
    raw_dir: Path | None = None,
    incoming_dir: Path | None = None,
    include_incoming: bool = True,
) -> list[Path]:
    """Find CSV files in raw and optional incoming folders."""
    raw_dir = raw_dir or RAW_DATA_DIR
    incoming_dir = incoming_dir or INCOMING_DATA_DIR

    files: list[Path] = sorted(raw_dir.glob("*.csv"))
    if include_incoming and incoming_dir.exists():
        files.extend(sorted(incoming_dir.glob("*.csv")))

    return files


def read_csv_file(path: Path) -> pd.DataFrame:
    """Read a single CSV and attach source metadata."""
    logger.info("Reading %s", path)
    df = pd.read_csv(path)
    df["source_file"] = path.name
    return df


def extract(
    raw_dir: Path | None = None,
    incoming_dir: Path | None = None,
    include_incoming: bool = True,
) -> pd.DataFrame:
    """
    Extract listings from all discovered CSV files.

    Architecture note: swap this module later for API/scraping sources
    without changing transform/load stages.
    """
    files = discover_csv_files(raw_dir, incoming_dir, include_incoming)
    if not files:
        logger.warning("No CSV files found in %s", raw_dir)
        return pd.DataFrame(columns=EXPECTED_COLUMNS + ["source_file"])

    frames = [read_csv_file(path) for path in files]
    combined = pd.concat(frames, ignore_index=True)
    logger.info("Extracted %s rows from %s file(s)", len(combined), len(files))
    return combined
