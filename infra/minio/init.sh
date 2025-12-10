#!/bin/sh

echo "Aguardando MinIO iniciar..."
sleep 10

mc alias set local http://minio:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD"
mc mb local/raw || true
mc mb local/bronze || true
mc mb local/silver || true
mc mb local/gold || true
mc anonymous set download local/raw || true

echo "Buckets criados com sucesso!"
