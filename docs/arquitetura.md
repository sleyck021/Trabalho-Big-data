# Arquitetura do Pipeline

- **Ingestão:** Airflow + Python → MinIO (Raw)
- **Processamento:** Spark → MinIO (Bronze, Silver, Gold)
- **Armazenamento:** MinIO (Data Lake compatível com S3)
- **Visualização:** Metabase
- **API:** FastAPI para servir KPIs

Fluxo: `datasets → ingestion → raw → spark → bronze/silver/gold → dashboards/API`
