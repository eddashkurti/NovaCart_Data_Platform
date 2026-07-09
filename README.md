# NovaCart Data Platform

NovaCart is an end-to-end e-commerce data engineering project built on Azure and Databricks. The project uses the Olist Brazilian E-Commerce dataset to implement a cloud-based Medallion Architecture with raw ingestion, Bronze Delta tables, Silver validation and cleansing, quarantine handling, and future Gold analytics models.

The goal of this project is to simulate how a real data engineering team would build a small production-style data platform using Azure Data Lake Storage Gen2, Azure Databricks, Unity Catalog, Delta Lake, PySpark, and Databricks Workflows.

---

## Project Objectives

The main objectives of this project are to:

- Build an end-to-end data platform on Azure.
- Store raw source files in Azure Data Lake Storage Gen2.
- Use Azure Databricks and PySpark for ingestion and transformation.
- Implement a Medallion Architecture: Raw → Bronze → Silver → Gold.
- Store processed data in Delta format.
- Use Unity Catalog and managed identity for governed storage access.
- Validate source schemas before ingestion.
- Add ingestion metadata for traceability.
- Separate invalid Silver records into quarantine.
- Prepare clean analytical datasets for dashboards.
- Orchestrate pipelines with Databricks Workflows.
- Document architecture, design decisions, and troubleshooting.

---

## Technology Stack

- Azure Data Lake Storage Gen2
- Azure Databricks
- Unity Catalog
- Azure Databricks Access Connector
- Managed Identity
- Delta Lake
- PySpark
- Databricks Serverless Compute
- Databricks Workflows
- Databricks SQL / Dashboards

---

## Dataset

This project uses the Olist Brazilian E-Commerce public dataset.

Raw source files:

```text
olist_customers_dataset.csv
olist_geolocation_dataset.csv
olist_order_items_dataset.csv
olist_order_payments_dataset.csv
olist_order_reviews_dataset.csv
olist_orders_dataset.csv
olist_products_dataset.csv
olist_sellers_dataset.csv
product_category_name_translation.csv