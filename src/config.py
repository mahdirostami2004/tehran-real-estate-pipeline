"""Shared configuration loaded from environment variables."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

POSTGRES_USER = os.getenv("POSTGRES_USER", "tehran_estate")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "change_me_secure_password")
POSTGRES_DB = os.getenv("POSTGRES_DB", "tehran_real_estate")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

RAW_DATA_DIR = PROJECT_ROOT / os.getenv("RAW_DATA_DIR", "data/raw")
PROCESSED_DATA_DIR = PROJECT_ROOT / os.getenv("PROCESSED_DATA_DIR", "data/processed")
INCOMING_DATA_DIR = PROJECT_ROOT / os.getenv("INCOMING_DATA_DIR", "data/incoming")

DATABASE_URL = (
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

EXPECTED_COLUMNS = [
    "Area",
    "Room",
    "Parking",
    "Warehouse",
    "Elevator",
    "Address",
    "Price",
    "Price(USD)",
]
