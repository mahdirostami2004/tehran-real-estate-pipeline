"""Airflow DAG: generate mock data -> ETL pipeline."""

from __future__ import annotations

from datetime import datetime, timedelta
import sys
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def _generate_mock_data(**_: object) -> None:
    from src.data_generator import write_incoming_file

    write_incoming_file(count=50)


def _run_etl(**_: object) -> None:
    from src.etl_pipeline import run_pipeline

    run_pipeline(save_processed=True, include_incoming=True)


default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="tehran_real_estate_etl",
    default_args=default_args,
    description="Daily ETL for Tehran real estate listings",
    schedule_interval="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["real-estate", "etl"],
) as dag:
    generate_mock_data = PythonOperator(
        task_id="generate_mock_data",
        python_callable=_generate_mock_data,
    )

    run_etl = PythonOperator(
        task_id="run_etl_pipeline",
        python_callable=_run_etl,
    )

    generate_mock_data >> run_etl
