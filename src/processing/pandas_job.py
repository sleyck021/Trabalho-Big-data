# src/processing/pandas_job.py
import os
import pandas as pd
from minio import Minio
from io import BytesIO

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000").replace("http://", "").replace("https://", "")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minio")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minio123")

client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False,
)

def read_parquet_from_minio(bucket, path):
    """Lê arquivo Parquet do MinIO"""
    response = client.get_object(bucket, path)
    return pd.read_parquet(BytesIO(response.read()))

def write_parquet_to_minio(df, bucket, path):
    """Escreve DataFrame como Parquet no MinIO"""
    parquet_buffer = BytesIO()
    df.to_parquet(parquet_buffer, index=False)
    parquet_buffer.seek(0)
    
    client.put_object(
        bucket,
        path,
        parquet_buffer,
        length=len(parquet_buffer.getvalue()),
        content_type='application/octet-stream'
    )
    print(f"✅ Escrito: s3://{bucket}/{path}")

def run():
    print("🔄 Iniciando processamento...")
    
    # BRONZE: Leitura do RAW e tipagem
    print("\n📦 Processando camada BRONZE...")
    df_raw = read_parquet_from_minio("raw", "vendas/vendas.parquet")
    
    df_bronze = df_raw.copy()
    df_bronze['order_date'] = pd.to_datetime(df_bronze['order_date'])
    df_bronze['quantity'] = df_bronze['quantity'].astype(int)
    df_bronze['unit_price'] = df_bronze['unit_price'].astype(float)
    
    write_parquet_to_minio(df_bronze, "bronze", "vendas/data.parquet")
    
    # SILVER: Limpeza e enriquecimento
    print("\n🔧 Processando camada SILVER...")
    df_silver = df_bronze[
        (df_bronze['quantity'] > 0) & 
        (df_bronze['unit_price'] > 0)
    ].dropna(subset=['order_id', 'order_date', 'customer_id', 'store_id', 'product_id'])
    
    df_silver['total_value'] = (df_silver['quantity'] * df_silver['unit_price']).round(2)
    
    write_parquet_to_minio(df_silver, "silver", "vendas/data.parquet")
    
    # GOLD: KPIs por data e cidade
    print("\n🏆 Processando camada GOLD - Daily City...")
    df_gold_daily_city = df_silver.groupby(['order_date', 'city', 'state']).agg({
        'total_value': 'sum',
        'quantity': 'sum'
    }).reset_index()
    df_gold_daily_city.columns = ['order_date', 'city', 'state', 'revenue', 'units']
    
    write_parquet_to_minio(df_gold_daily_city, "gold", "vendas_daily_city/data.parquet")
    
    # GOLD: KPIs por produto
    print("\n🏆 Processando camada GOLD - By Product...")
    df_gold_product = df_silver.groupby(['product_id', 'city', 'state']).agg({
        'total_value': 'sum',
        'quantity': 'sum'
    }).reset_index()
    df_gold_product.columns = ['product_id', 'city', 'state', 'revenue', 'units']
    
    write_parquet_to_minio(df_gold_product, "gold", "vendas_by_product/data.parquet")
    
    print("\n✨ Processamento concluído com sucesso!")
    print(f"\n📊 Estatísticas:")
    print(f"   - Registros Bronze: {len(df_bronze)}")
    print(f"   - Registros Silver: {len(df_silver)}")
    print(f"   - KPIs Daily/City: {len(df_gold_daily_city)}")
    print(f"   - KPIs Por Produto: {len(df_gold_product)}")

if __name__ == "__main__":
    run()
