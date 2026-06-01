"""Unit tests for extract module."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.extract import discover_csv_files, extract


def test_discover_csv_files(tmp_path: Path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    (raw_dir / "a.csv").write_text("Area,Room\n1,1\n")
    (raw_dir / "b.txt").write_text("not csv")

    files = discover_csv_files(raw_dir=raw_dir, include_incoming=False)
    assert len(files) == 1
    assert files[0].name == "a.csv"


def test_extract_concatenates_files(tmp_path: Path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    pd.DataFrame({"Area": [60], "Room": [2], "Price": [1e9]}).to_csv(
        raw_dir / "one.csv", index=False
    )
    pd.DataFrame({"Area": [70], "Room": [3], "Price": [2e9]}).to_csv(
        raw_dir / "two.csv", index=False
    )

    df = extract(raw_dir=raw_dir, include_incoming=False)
    assert len(df) == 2
    assert set(df["source_file"]) == {"one.csv", "two.csv"}
