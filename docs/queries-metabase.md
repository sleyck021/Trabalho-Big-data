# Queries SQL para Metabase - Dashboard de Vendas

## 📈 Query 1: Receita Total por Cidade (Ordenada)
```sql
SELECT 
    city,
    state,
    SUM(revenue) as total_revenue,
    SUM(units) as total_units
FROM vendas_daily_city
GROUP BY city, state
ORDER BY total_revenue DESC;
```

## 📅 Query 2: Receita ao Longo do Tempo
```sql
SELECT 
    order_date,
    SUM(revenue) as daily_revenue,
    SUM(units) as daily_units
FROM vendas_daily_city
GROUP BY order_date
ORDER BY order_date;
```

## 🏆 Query 3: Top 5 Produtos por Receita
```sql
SELECT 
    product_id,
    SUM(revenue) as total_revenue,
    SUM(units) as total_units
FROM vendas_by_product
GROUP BY product_id
ORDER BY total_revenue DESC
LIMIT 5;
```

## 🌍 Query 4: Receita por Estado
```sql
SELECT 
    state,
    SUM(revenue) as total_revenue,
    COUNT(DISTINCT city) as num_cities
FROM vendas_daily_city
GROUP BY state
ORDER BY total_revenue DESC;
```

## 📊 Query 5: Análise Detalhada de Vendas
```sql
SELECT 
    order_date,
    city,
    state,
    product_id,
    quantity,
    unit_price,
    total_value
FROM vendas_detalhadas
ORDER BY order_date DESC, total_value DESC;
```

## 💰 Query 6: Ticket Médio por Cidade
```sql
SELECT 
    city,
    state,
    ROUND(AVG(revenue)::numeric, 2) as avg_revenue,
    SUM(revenue) as total_revenue,
    COUNT(*) as num_transactions
FROM vendas_daily_city
GROUP BY city, state
ORDER BY avg_revenue DESC;
```

## 📈 Query 7: KPIs Principais (Dashboard Summary)
```sql
SELECT 
    SUM(revenue) as receita_total,
    SUM(units) as unidades_totais,
    COUNT(DISTINCT city) as cidades_atendidas,
    ROUND(AVG(revenue)::numeric, 2) as receita_media
FROM vendas_daily_city;
```

---

## 🎨 Como usar no Metabase:

1. Clique em "+ Novo" > "Pergunta SQL"
2. Selecione o banco "Vendas Pipeline"
3. Cole uma das queries acima
4. Clique em "Visualizar"
5. Escolha o tipo de gráfico (Barra, Linha, Pizza, etc.)
6. Salve a visualização

## 💡 Tipos de Gráficos Recomendados:

- **Query 1 (Cidade)**: Gráfico de Barras Horizontal
- **Query 2 (Tempo)**: Gráfico de Linha
- **Query 3 (Top Produtos)**: Gráfico de Barras
- **Query 4 (Estado)**: Gráfico de Pizza ou Barras
- **Query 5 (Detalhes)**: Tabela
- **Query 6 (Ticket Médio)**: Tabela ou Barras
- **Query 7 (KPIs)**: Números Grandes (Scalar)
