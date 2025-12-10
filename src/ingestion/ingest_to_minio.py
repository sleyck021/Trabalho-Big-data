# src/ingestion/ingest_to_minio.py
import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from minio import Minio
from minio.error import S3Error

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minio")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minio123")

client = Minio(
    MINIO_ENDPOINT.replace("http://", "").replace("https://", ""),
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False,
)

def upload_file(bucket: str, object_name: str, file_path: str, content_type: str):
    client.fput_object(bucket, object_name, file_path, content_type=content_type)
    print(f"Uploaded {file_path} to s3://{bucket}/{object_name}")

def to_parquet(df: pd.DataFrame, path: str):
    table = pa.Table.from_pandas(df)
    pq.write_table(table, path)

def main():
    os.makedirs("/tmp/stage", exist_ok=True)
    src_path = "/opt/project/datasets/vendas.csv"
    df = pd.read_csv(src_path, parse_dates=["order_date"], comment='#')
    # Upload CSV ao raw
    upload_file("raw", "vendas/vendas.csv", src_path, "text/csv")
    # Também gerar Parquet no raw
    parquet_path = "/tmp/stage/vendas.parquet"
    to_parquet(df, parquet_path)
    upload_file("raw", "vendas/vendas.parquet", parquet_path, "application/octet-stream")

if __name__ == "__main__":
    main()
