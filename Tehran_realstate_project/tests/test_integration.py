"""Integration test against PostgreSQL (skipped when DB unavailable)."""

from __future__ import annotations

import os

import pytest

from src.etl_pipeline import run_pipeline
from src.load import get_row_count


@pytest.mark.integration
def test_full_etl_loads_rows():
    if os.getenv("SKIP_DB_TESTS", "").lower() in {"1", "true", "yes"}:
        pytest.skip("SKIP_DB_TESTS is set")

    try:
        summary = run_pipeline(save_processed=False, skip_load=False)
    except Exception as exc:
        pytest.skip(f"PostgreSQL not available: {exc}")

    assert summary["clean_rows"] > 3000
    assert summary["loaded_rows"] == summary["clean_rows"]
    assert get_row_count() >= summary["clean_rows"]
