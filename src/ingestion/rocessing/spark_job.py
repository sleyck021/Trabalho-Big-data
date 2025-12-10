# src/processing/spark_job.py
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, round as spark_round, sum as spark_sum

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio:9000")

def spark():
    return (SparkSession.builder
        .appName("VendasPipeline")
        .config("spark.hadoop.fs.s3a.endpoint", MINIO_ENDPOINT.replace("http://", ""))
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
        .getOrCreate())

def write_parquet(df, path):
    df.write.mode("overwrite").parquet(path)

def run():
    sp = spark()

    # RAW leitura (CSV)
    raw_csv = "s3a://raw/vendas/vendas.csv"

    df_raw = (sp.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(raw_csv))

    # BRONZE: tipagem e datas
    df_bronze = (df_raw
        .withColumn("order_date", to_date(col("order_date")))
        .withColumn("quantity", col("quantity").cast("int"))
        .withColumn("unit_price", col("unit_price").cast("double")))

    write_parquet(df_bronze, "s3a://bronze/vendas")

    # SILVER: limpeza e métricas simples
    df_silver = (df_bronze
        .filter(col("quantity") > 0)
        .filter(col("unit_price") > 0)
        .withColumn("total_value", spark_round(col("quantity") * col("unit_price"), 2))
        .dropna(subset=["order_id", "order_date", "customer_id", "store_id", "product_id"])
    )

    write_parquet(df_silver, "s3a://silver/vendas")

    # GOLD: KPIs por data e cidade
    df_gold_daily_city = (df_silver
        .groupBy("order_date", "city", "state")
        .agg(
            spark_sum("total_value").alias("revenue"),
            spark_sum("quantity").alias("units")
        ))

    write_parquet(df_gold_daily_city, "s3a://gold/vendas_daily_city")

    # GOLD: KPIs por produto
    df_gold_product = (df_silver
        .groupBy("product_id", "city", "state")
        .agg(
            spark_sum("total_value").alias("revenue"),
            spark_sum("quantity").alias("units")
        ))

    write_parquet(df_gold_product, "s3a://gold/vendas_by_product")

    sp.stop()

if __name__ == "__main__":
    run()
