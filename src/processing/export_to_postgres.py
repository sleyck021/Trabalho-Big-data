# src/processing/export_to_postgres.py
import os
import pandas as pd
from minio import Minio
from io import BytesIO
from sqlalchemy import create_engine

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000").replace("http://", "").replace("https://", "")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minio")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minio123")

# PostgreSQL
PG_HOST = os.getenv("PG_HOST", "postgres")
PG_USER = os.getenv("PG_USER", "airflow")
PG_PASS = os.getenv("PG_PASS", "airflow")
PG_DB = os.getenv("PG_DB", "airflow")

client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)

def read_parquet_from_minio(bucket, path):
    """Lê arquivo Parquet do MinIO"""
    response = client.get_object(bucket, path)
    return pd.read_parquet(BytesIO(response.read()))

def export_to_postgres():
    print("🔄 Exportando dados Gold para PostgreSQL...")
    
    # Conexão com SQLAlchemy
    engine = create_engine(f"postgresql://{PG_USER}:{PG_PASS}@{PG_HOST}:5432/{PG_DB}")
    
    # Vendas diárias por cidade
    print("\n📊 Exportando vendas_daily_city...")
    df_daily_city = read_parquet_from_minio("gold", "vendas_daily_city/data.parquet")
    df_daily_city.to_sql('vendas_daily_city', engine, if_exists='replace', index=False)
    print(f"✅ {len(df_daily_city)} registros exportados para tabela 'vendas_daily_city'")
    
    # Vendas por produto
    print("\n📊 Exportando vendas_by_product...")
    df_by_product = read_parquet_from_minio("gold", "vendas_by_product/data.parquet")
    df_by_product.to_sql('vendas_by_product', engine, if_exists='replace', index=False)
    print(f"✅ {len(df_by_product)} registros exportados para tabela 'vendas_by_product'")
    
    # Silver para análises detalhadas
    print("\n📊 Exportando dados silver...")
    df_silver = read_parquet_from_minio("silver", "vendas/data.parquet")
    df_silver.to_sql('vendas_detalhadas', engine, if_exists='replace', index=False)
    print(f"✅ {len(df_silver)} registros exportados para tabela 'vendas_detalhadas'")
    
    engine.dispose()
    print("\n✨ Exportação concluída! Dados disponíveis no PostgreSQL para o Metabase.")

if __name__ == "__main__":
    export_to_postgres()
