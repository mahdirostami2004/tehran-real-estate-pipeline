"""Unit tests for ETL transform logic."""

from __future__ import annotations

import pandas as pd
import pytest

from src.transform import (
    compute_price_per_sqm,
    rial_to_toman,
    transform,
)


class TestPriceConversions:
    def test_rial_to_toman(self):
        assert rial_to_toman(10) == 1
        assert rial_to_toman(1_850_000_000) == 185_000_000

    def test_price_per_sqm(self):
        assert compute_price_per_sqm(1_850_000_000, 62) == 29_838_710


class TestTransform:
    def test_basic_cleaning(self):
        raw = pd.DataFrame(
            [
                {
                    "Area": 63,
                    "Room": 1,
                    "Parking": True,
                    "Warehouse": True,
                    "Elevator": True,
                    "Address": "Shahran",
                    "Price": 1_850_000_000.0,
                    "Price(USD)": 61666.67,
                    "source_file": "test.csv",
                }
            ]
        )
        cleaned = transform(raw)
        assert len(cleaned) == 1
        assert cleaned.iloc[0]["price_toman"] == 185_000_000
        assert cleaned.iloc[0]["price_per_sqm"] == 29_365_079
        assert cleaned.iloc[0]["address"] == "Shahran"

    def test_swapped_area_price_fixed(self):
        raw = pd.DataFrame(
            [
                {
                    "Area": " 3,310,000,000 ",
                    "Room": 2,
                    "Parking": True,
                    "Warehouse": True,
                    "Elevator": True,
                    "Address": "Pardis",
                    "Price": 95.0,
                    "Price(USD)": 30000.0,
                    "source_file": "test.csv",
                }
            ]
        )
        cleaned = transform(raw)
        assert len(cleaned) == 1
        assert cleaned.iloc[0]["area_sqm"] == 95.0

    def test_outlier_removed(self):
        raw = pd.DataFrame(
            [
                {
                    "Area": 10,
                    "Room": 1,
                    "Parking": False,
                    "Warehouse": False,
                    "Elevator": False,
                    "Address": "Too Small",
                    "Price": 100_000_000.0,
                    "Price(USD)": 3333.33,
                    "source_file": "test.csv",
                }
            ]
        )
        cleaned = transform(raw)
        assert cleaned.empty

    def test_missing_address_dropped(self):
        raw = pd.DataFrame(
            [
                {
                    "Area": 80,
                    "Room": 2,
                    "Parking": True,
                    "Warehouse": True,
                    "Elevator": True,
                    "Address": None,
                    "Price": 2_000_000_000.0,
                    "Price(USD)": 66666.67,
                    "source_file": "test.csv",
                }
            ]
        )
        cleaned = transform(raw)
        assert cleaned.empty
