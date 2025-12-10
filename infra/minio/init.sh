# infra/minio/init.sh
#!/bin/sh
set -e

mc alias set local http://minio:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD"
mc mb local/raw
mc mb local/bronze
mc mb local/silver
mc mb local/gold
mc anonymous set download local/raw
