# src/api/main.py
import os
import io
import pandas as pd
from fastapi import FastAPI
from minio import Minio

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minio")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minio123")

client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)
app = FastAPI(title="Vendas API", version="1.0.0")

def read_parquet(bucket: str, prefix: str):
    # Lê múltiplos arquivos parquet do prefixo
    objects = client.list_objects(bucket, prefix=prefix, recursive=True)
    dfs = []
    for obj in objects:
        if obj.object_name.endswith(".parquet"):
            resp = client.get_object(bucket, obj.object_name)
            data = io.BytesIO(resp.read())
            dfs.append(pd.read_parquet(data))
            resp.close()
            resp.release_conn()
    if not dfs:
        return pd.DataFrame()
    return pd.concat(dfs, ignore_index=True)

@app.get("/v1/revenue/city")
def revenue_city():
    df = read_parquet("gold", "vendas_daily_city")
    # Retorna top 20
    return df.sort_values("revenue", ascending=False).head(20).to_dict(orient="records")

@app.get("/v1/revenue/product")
def revenue_product():
    df = read_parquet("gold", "vendas_by_product")
    return df.sort_values("revenue", ascending=False).head(20).to_dict(orient="records")
