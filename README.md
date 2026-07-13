# NovaCart Data Platform

NovaCart is an end-to-end e-commerce data engineering project built on Azure and Databricks.

The project uses the Olist Brazilian E-Commerce dataset to implement a cloud-based Medallion Architecture with raw ingestion, Bronze Delta ingestion, Silver validation and cleansing, quarantine handling, and future Gold analytics models.

The goal is to simulate how a small production-style data platform would be designed by a data engineering team using Azure Data Lake Storage Gen2, Azure Databricks, Unity Catalog, Delta Lake, PySpark, and Databricks Workflows.

---

## Project Objectives

The main objectives of this project are to:

- Build an end-to-end data platform on Azure
- Store raw source files in Azure Data Lake Storage Gen2
- Use Azure Databricks and PySpark for ingestion and transformation
- Implement a Medallion Architecture: Raw → Bronze → Silver → Gold
- Store processed layers in Delta format
- Use Unity Catalog and managed identity for governed storage access
- Validate source schemas before ingestion
- Add ingestion metadata for traceability
- Clean and standardize datasets in the Silver layer
- Route invalid Silver records to quarantine
- Prepare future Gold analytical datasets for dashboards
- Document architecture, validation rules, and design decisions

---

## Technology Stack

- Azure Data Lake Storage Gen2
- Azure Databricks
- Databricks Serverless Compute
- Unity Catalog
- Azure Databricks Access Connector
- Managed Identity
- Delta Lake
- PySpark
- Databricks Workflows
- Databricks SQL / Dashboards
- GitHub

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
```

The dataset contains information about customers, orders, order items, payments, reviews, products, sellers, geolocation, and product category translations.

---

## Architecture

NovaCart follows the Medallion Architecture pattern.

```text
Raw CSV files
      ↓
Bronze Delta layer
      ↓
Silver cleaned and validated layer
      ↓
Gold analytical models
      ↓
Databricks SQL dashboards
```

### Raw Layer

The Raw layer stores the original Olist CSV files exactly as uploaded.

Raw path:

```text
abfss://raw@stnovacartdev.dfs.core.windows.net/olist/
```

### Bronze Layer

The Bronze layer reads raw CSV files, validates required source columns, adds ingestion metadata, and writes Delta datasets.

Bronze path pattern:

```text
abfss://bronze@stnovacartdev.dfs.core.windows.net/olist/<dataset_name>
```

Bronze metadata columns:

- `_source_file`
- `_ingestion_timestamp`
- `_batch_id`

### Silver Layer

The Silver layer cleans, standardizes, validates, and enriches Bronze data.

Silver path pattern:

```text
abfss://silver@stnovacartdev.dfs.core.windows.net/olist/<dataset_name>
```

Silver metadata column:

- `_silver_processed_at`

Invalid Silver records are routed to quarantine.

Quarantine path pattern:

```text
abfss://quarantine@stnovacartdev.dfs.core.windows.net/olist/<dataset_name>
```

Quarantine metadata columns:

- `_rejection_reason`
- `_quarantined_at`
- `_source_dataset`

### Gold Layer

The Gold layer has not been implemented yet.

Planned Gold models include:

- `dim_customers`
- `dim_sellers`
- `dim_products`
- `dim_dates`
- `fact_orders`
- `fact_order_items`
- `fact_payments`
- `fact_reviews`

---

## Storage Layout

The project uses the following ADLS Gen2 containers:

| Container | Purpose |
|---|---|
| `raw` | Original uploaded Olist CSV files |
| `bronze` | Source-preserving Delta ingestion outputs |
| `silver` | Cleaned and validated Delta datasets |
| `gold` | Future business-ready analytical models |
| `quarantine` | Invalid records rejected during Silver validation |
| `logs` | Future pipeline audit and operational logs |

Storage account:

```text
stnovacartdev
```

Resource group:

```text
rg-novacart-dev
```

---

## Unity Catalog External Locations

Configured external locations:

| External Location | Container |
|---|---|
| `novacart_raw_location` | `raw` |
| `novacart_bronze_location` | `bronze` |
| `novacart_silver_location` | `silver` |
| `novacart_quarantine_location` | `quarantine` |

Future external locations:

| External Location | Container |
|---|---|
| `novacart_gold_location` | `gold` |
| `novacart_logs_location` | `logs` |

---

## Repository Structure

```text
NovaCart_Data_Platform/
│
├── architecture/
│   ├── medallion-architecture.md
│   └── storage-layout.md
│
├── config/
│   ├── README.md
│   └── dev_config.json
│
├── docs/
│   ├── adls-unity-catalog-setup.md
│   ├── bronze-ingestion-design.md
│   ├── project-status.md
│   └── silver-transformation-design.md
│
├── notebooks/
│   ├── 00_setup/
│   ├── 01_bronze/
│   ├── 02_silver/
│   ├── 03_gold/
│   ├── 04_quality/
│   ├── 05_workflows/
│   └── 06_dashboards/
│
├── src/
│   ├── __init__.py
│   ├── README.md
│   └── bronze_ingestion.py
│
├── tests/
│   ├── README.md
│   └── test_plan.md
│
└── README.md
```

---

## Bronze Layer

The Bronze layer is implemented for all nine Olist datasets.

Bronze ingestion uses a shared Python module:

```text
src/bronze_ingestion.py
```

Main function:

```text
ingest_csv_to_delta
```

The shared Bronze module handles:

- reading raw CSV files
- applying optional CSV options
- validating expected source columns
- adding ingestion metadata
- checking for empty input
- writing Delta output
- reading written Delta output back
- validating row counts

### Bronze Row Counts

| Dataset | Bronze Rows |
|---|---:|
| Customers | 99,441 |
| Orders | 99,441 |
| Order items | 112,650 |
| Order payments | 103,886 |
| Order reviews | 99,224 |
| Products | 32,951 |
| Sellers | 3,095 |
| Geolocation | 1,000,163 |
| Category translation | 71 |

---

## Silver Layer

The Silver layer is implemented for all nine Olist datasets.

Silver transformations are dataset-specific because each dataset has different validation rules and cleaning requirements.

Silver handles:

- required-column validation
- trimming and standardizing text fields
- timestamp validation
- domain validation
- invalid-record quarantine routing
- derived operational fields
- row-count reconciliation
- Delta write validation

### Silver Validation Summary

| Dataset | Silver Rows | Quarantined Rows |
|---|---:|---:|
| Customers | 99,441 | 0 |
| Orders | 99,252 | 189 |
| Order items | 112,650 | 0 |
| Order payments | 103,883 | 3 |
| Order reviews | 99,224 | 0 |
| Products | 32,945 | 6 |
| Sellers | 3,095 | 0 |
| Geolocation | 1,000,163 | 0 |
| Category translation | 71 | 0 |

---

## Quarantine Handling

Invalid records from Silver validation are not dropped.

They are written to the quarantine container with metadata explaining why the record was rejected.

Examples of quarantined records include:

- orders with invalid delivery timestamp chronology
- order payments with invalid payment type
- products with invalid weight values

This keeps the pipeline auditable and prevents silent data loss.

---

## Current Project Status

Completed:

- Azure resource group setup
- ADLS Gen2 storage account setup
- Raw, Bronze, Silver, Gold, quarantine, and logs containers
- Azure Databricks workspace setup
- Unity Catalog external locations for Raw, Bronze, Silver, and quarantine
- Raw file upload
- Bronze ingestion for all nine datasets
- Shared Bronze ingestion module
- Silver transformations for all nine datasets
- Quarantine handling
- Row-count reconciliation
- Architecture documentation
- Storage layout documentation
- Test plan documentation
- Development configuration metadata

Not started yet:

- Gold analytical models
- Databricks Workflows orchestration
- Databricks SQL dashboards
- Automated PySpark tests
- Pipeline audit logging

---

## Validation Approach

Current validation is performed inside Databricks notebooks.

Validation includes:

- source schema checks
- required-column checks
- empty-input checks
- row-count validation
- Delta write/readback validation
- Silver and quarantine reconciliation
- manual schema inspection
- sample output inspection

Automated tests are planned for a later stage after more reusable transformation utilities are introduced.

---

## Configuration

The `config/` folder stores non-secret development metadata.

It includes:

- project name
- environment name
- storage account name
- container names
- base storage paths
- dataset names
- raw file names
- Bronze, Silver, and quarantine path names

Secrets must not be stored in this repository.

Authentication is handled through Azure Databricks, Unity Catalog, and managed identity.

---

## Next Milestone

The next planned milestone is the Gold layer.

Gold will focus on:

- fact and dimension modeling
- analytical joins
- business KPI definitions
- dashboard-ready Delta datasets

Planned models:

- customer dimension
- seller dimension
- product dimension
- date dimension
- order fact table
- payment fact table
- review fact table

---

## Project Status

Current status:

```text
Raw: Completed
Bronze: Completed
Silver: Completed
Quarantine: Completed
Gold: Not started
Workflows: Not started
Dashboards: Not started
```