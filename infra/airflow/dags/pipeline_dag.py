# infra/airflow/dags/pipeline_dag.py
from datetime import datetime, timedelta
import os
from airflow import DAG
from airflow.operators.python import PythonOperator

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
PROJECT_SRC = "/opt/project/src"
DATASETS_DIR = "/opt/project/datasets"

def task_ingest():
    import sys
    sys.path.append(f"{PROJECT_SRC}/ingestion")
    from ingest_to_minio import main
    main()

def task_process():
    import sys
    sys.path.append(f"{PROJECT_SRC}/processing")
    from spark_job import run
    run()

def task_check_gold():
    # Validação mínima: checar se gold tem arquivos
    from minio import Minio
    client = Minio("minio:9000", access_key="minio", secret_key="minio123", secure=False)
    objs = list(client.list_objects("gold", prefix="vendas_daily_city", recursive=True))
    assert len(objs) > 0, "Gold vazio!"

with DAG(
    dag_id="pipeline_vendas",
    start_date=datetime(2024, 11, 1),
    schedule_interval="@daily",
    catchup=False,
    default_args={
        "owner": "data-team",
        "retries": 1,
        "retry_delay": timedelta(minutes=2)
    },
    tags=["vendas", "lakehouse"]
) as dag:

    ingest = PythonOperator(
        task_id="ingest_to_raw",
        python_callable=task_ingest
    )

    process = PythonOperator(
        task_id="process_bronze_silver_gold",
        python_callable=task_process
    )

    check = PythonOperator(
        task_id="check_gold_non_empty",
        python_callable=task_check_gold
    )

    ingest >> process >> check
