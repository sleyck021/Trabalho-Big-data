markdown
# 🚀 Projeto de Ciência de Dados e Big Data – Pipeline de Vendas

Este projeto implementa um pipeline completo de **Ciência de Dados/Big Data**, cobrindo ingestão, processamento, armazenamento em Data Lake e visualização de KPIs.  
A solução foi construída com **Airflow, Spark, MinIO e Metabase**, refletindo práticas reais de engenharia de dados.

---

## 📌 Objetivo

- Demonstrar domínio técnico em coleta, processamento e análise de dados.
- Estruturar um fluxo robusto com camadas **Raw → Bronze → Silver → Gold**.
- Disponibilizar insights via dashboards e API.
- Garantir documentação clara e repositório organizado.

---

## 📂 Estrutura do Repositório

├── README.md # Guia geral do projeto
├── docs/ # Documentação detalhada
│ ├── arquitetura.md
│ ├── dados.md
│ ├── execucao.md
│ └── decisoes-tecnicas.md
├── infra/ # Infraestrutura (Docker, configs)
│ ├── docker-compose.yml
│ ├── minio/init.sh
│ ├── airflow/Dockerfile
│ ├── airflow/requirements.txt
│ └── spark/spark-defaults.conf
├── src/ # Código-fonte
│ ├── ingestion/ingest_to_minio.py
│ ├── processing/spark_job.py
│ └── api/main.py
├── notebooks/ # Análises exploratórias
│ └── 01_exploracao.ipynb
└── vendas.csv
---

## ⚙️ Tecnologias Utilizadas

- **Airflow** → Orquestração de tarefas
- **Spark** → Processamento distribuído
- **MinIO** → Data Lake compatível com S3
- **Metabase** → Visualização de KPIs
- **FastAPI** → API opcional para servir dados
- **Docker Compose** → Infraestrutura containerizada

---

## 🗂️ Camadas do Data Lake

- **Raw:** dados brutos (CSV/Parquet)
- **Bronze:** schema e tipagem padronizados
- **Silver:** dados limpos e enriquecidos
- **Gold:** agregações e KPIs prontos para análise

---

## 🚀 Passo a Passo de Execução

### 1. Subir a infraestrutura
```bash
cd infra
docker compose up -d --build
MinIO: http://localhost:9001 (user: minio, pass: minio123)

Airflow: http://localhost:8080 (user: admin, pass: admin)

Metabase: http://localhost:3000

Spark: porta 7077

2. Ingestão de dados (Raw)
bash
docker exec -it airflow bash -lc "python /opt/project/src/ingestion/ingest_to_minio.py"
Resultado: arquivos vendas.csv e vendas.parquet em s3://raw/vendas/.

3. Processamento (Bronze → Silver → Gold)
bash
docker exec -it spark bash -lc "spark-submit /opt/project/src/processing/spark_job.py"
Resultado:

s3://bronze/vendas

s3://silver/vendas

s3://gold/vendas_daily_city

s3://gold/vendas_by_product

4. Orquestração com Airflow
Acesse http://localhost:8080

Ative o DAG pipeline_vendas

Execute manualmente ou agende para rodar diariamente

Verifique logs e status das tarefas

5. Visualização com Metabase
Acesse http://localhost:3000

Configure conexão (Postgres interno ou exporte CSV do Gold)

Crie dashboards com KPIs:

Receita por cidade/data

Receita por produto

Unidades vendidas por região

6. API opcional (FastAPI)
bash
export MINIO_ENDPOINT=localhost:9000 MINIO_ACCESS_KEY=minio MINIO_SECRET_KEY=minio123
uvicorn src.api.main:app --reload --port 8000
Endpoints disponíveis:

GET /v1/revenue/city → Top 20 cidades por receita

GET /v1/revenue/product → Top 20 produtos por receita

📊 Dataset de Exemplo
Arquivo: datasets/vendas.csv

Campos:

order_id → ID do pedido

order_date → Data do pedido

customer_id → Cliente

store_id → Loja

product_id → Produto

quantity → Quantidade

unit_price → Preço unitário

currency → Moeda

city → Cidade

state → Estado

🔍 Critérios de Avaliação
Entendimento da solução entregue

Clareza sobre papel individual

Noções de arquitetura de dados

Domínio das ferramentas utilizadas

Documentação completa e organizada

⚠️ Limitações e Melhorias Futuras
Metabase não lê Parquet direto do MinIO → solução: materializar em Postgres

Validações básicas → pode evoluir para Great Expectations

Sem catálogo formal → pode ser adicionado Glue/Unity Catalog

Escalabilidade → adicionar mais workers Spark/Airflow

📝 Como reiniciar do zero
bash
docker compose down -v
docker compose up -d --build