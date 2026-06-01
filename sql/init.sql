-- Optional database for Apache Airflow metadata (docker profile: airflow)
SELECT 'CREATE DATABASE airflow'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'airflow')\gexec

-- Schema for Tehran real estate listings
CREATE TABLE IF NOT EXISTS listings (
    id              SERIAL PRIMARY KEY,
    record_hash     VARCHAR(64) NOT NULL UNIQUE,
    area_sqm        NUMERIC(10, 2) NOT NULL CHECK (area_sqm > 0),
    rooms           SMALLINT NOT NULL CHECK (rooms >= 0),
    parking         BOOLEAN NOT NULL DEFAULT FALSE,
    warehouse       BOOLEAN NOT NULL DEFAULT FALSE,
    elevator        BOOLEAN NOT NULL DEFAULT FALSE,
    address         VARCHAR(255) NOT NULL,
    price_rial      BIGINT NOT NULL CHECK (price_rial > 0),
    price_toman     BIGINT NOT NULL CHECK (price_toman > 0),
    price_usd       NUMERIC(14, 2),
    price_per_sqm   BIGINT NOT NULL CHECK (price_per_sqm > 0),
    source_file      build_year      SMALLINT,
   VARCHAR(255),
    ingested_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_listings_address ON listings (address);
CREATE INDEX IF NOT EXISTS idx_listings_price_per_sqm ON listings (price_per_sqm);
CREATE INDEX IF NOT EXISTS idx_listings_rooms ON listings (rooms);
CREATE INDEX IF NOT EXISTS idx_listings_ingested_at ON listings (ingested_at);

-- View for dashboard consumers (Power BI, etc.)
CREATE OR REPLACE VIEW vw_listings_analytics AS
SELECT
    id,
    area_sqm,
    rooms,
    parking,
    warehouse,
    elevator,
    address,
    price_toman,
    price_usd,
    price_per_sqm,
    build_year,
    source_file,
    ingested_at
FROM listings;

COMMENT ON TABLE listings IS 'Cleaned Tehran residential property listings from ETL pipeline';
