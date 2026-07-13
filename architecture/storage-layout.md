# Storage Layout

## Overview

NovaCart uses Azure Data Lake Storage Gen2 to separate data by processing layer.

The storage account is:

`stnovacartdev`

The project uses separate containers for each major data layer:

- `raw`
- `bronze`
- `silver`
- `gold`
- `quarantine`
- `logs`

This separation keeps source data, processed data, invalid records, and future logs isolated from each other.

## Storage Account

| Property | Value |
|---|---|
| Storage account | `stnovacartdev` |
| Resource group | `rg-novacart-dev` |
| Region | North Europe |
| Hierarchical namespace | Enabled |
| Storage type | ADLS Gen2 |

## Container Responsibilities

| Container | Purpose |
|---|---|
| `raw` | Original uploaded Olist CSV files |
| `bronze` | Source-preserving Delta ingestion outputs |
| `silver` | Cleaned and validated Delta datasets |
| `gold` | Future business-ready analytical models |
| `quarantine` | Invalid records rejected during Silver validation |
| `logs` | Future pipeline audit logs and operational logs |

## Raw Container

Raw data path:

`abfss://raw@stnovacartdev.dfs.core.windows.net/olist/`

The raw container stores the original Olist CSV files:

- `olist_customers_dataset.csv`
- `olist_orders_dataset.csv`
- `olist_order_items_dataset.csv`
- `olist_order_payments_dataset.csv`
- `olist_order_reviews_dataset.csv`
- `olist_products_dataset.csv`
- `olist_sellers_dataset.csv`
- `olist_geolocation_dataset.csv`
- `product_category_name_translation.csv`

Rules:

- Raw files are uploaded manually.
- Raw files are not modified by the pipeline.
- Raw files act as the source of truth for Bronze ingestion.

## Bronze Container

Bronze base path:

`abfss://bronze@stnovacartdev.dfs.core.windows.net/olist/`

Bronze dataset paths:

| Dataset | Path |
|---|---|
| Customers | `bronze/olist/customers` |
| Orders | `bronze/olist/orders` |
| Order items | `bronze/olist/order_items` |
| Order payments | `bronze/olist/order_payments` |
| Order reviews | `bronze/olist/order_reviews` |
| Products | `bronze/olist/products` |
| Sellers | `bronze/olist/sellers` |
| Geolocation | `bronze/olist/geolocation` |
| Category translation | `bronze/olist/category_translation` |

Bronze outputs are stored as Delta datasets.

Each Bronze dataset contains:

- Delta transaction logs
- Parquet data files
- Bronze ingestion metadata columns

## Silver Container

Silver base path:

`abfss://silver@stnovacartdev.dfs.core.windows.net/olist/`

Silver dataset paths:

| Dataset | Path |
|---|---|
| Customers | `silver/olist/customers` |
| Orders | `silver/olist/orders` |
| Order items | `silver/olist/order_items` |
| Order payments | `silver/olist/order_payments` |
| Order reviews | `silver/olist/order_reviews` |
| Products | `silver/olist/products` |
| Sellers | `silver/olist/sellers` |
| Geolocation | `silver/olist/geolocation` |
| Category translation | `silver/olist/category_translation` |

Silver outputs are stored as Delta datasets.

Silver contains cleaned, standardized, and validated records.

## Quarantine Container

Quarantine base path:

`abfss://quarantine@stnovacartdev.dfs.core.windows.net/olist/`

Quarantine dataset paths:

| Dataset | Path |
|---|---|
| Customers | `quarantine/olist/customers` |
| Orders | `quarantine/olist/orders` |
| Order items | `quarantine/olist/order_items` |
| Order payments | `quarantine/olist/order_payments` |
| Order reviews | `quarantine/olist/order_reviews` |
| Products | `quarantine/olist/products` |
| Sellers | `quarantine/olist/sellers` |
| Geolocation | `quarantine/olist/geolocation` |
| Category translation | `quarantine/olist/category_translation` |

The quarantine container stores records that fail Silver validation.

Each quarantined record includes:

- original record fields
- `_rejection_reason`
- `_quarantined_at`
- `_source_dataset`
- Bronze lineage metadata

## Gold Container

Gold base path:

`abfss://gold@stnovacartdev.dfs.core.windows.net/`

The Gold layer has not been implemented yet.

Planned use:

- fact tables
- dimension tables
- KPI tables
- dashboard-ready analytical outputs

## Logs Container

Logs base path:

`abfss://logs@stnovacartdev.dfs.core.windows.net/`

The logs layer has not been implemented yet.

Planned use:

- pipeline execution logs
- audit summaries
- data quality run results
- workflow status outputs

## External Locations

Unity Catalog external locations are configured at the container level.

Current external locations:

| External location | Container |
|---|---|
| `novacart_raw_location` | `raw` |
| `novacart_bronze_location` | `bronze` |
| `novacart_silver_location` | `silver` |
| `novacart_quarantine_location` | `quarantine` |

Future external locations:

| External location | Container |
|---|---|
| `novacart_gold_location` | `gold` |
| `novacart_logs_location` | `logs` |

## Design Decisions

### One Container per Layer

Each data layer has its own ADLS container.

This improves:

- separation of concerns
- access control
- operational clarity
- debugging
- future lifecycle management

### One External Location per Container

External locations are created at the container level, not per dataset.

This avoids unnecessary Unity Catalog objects and keeps access management simpler.

### Delta for Processed Layers

Bronze, Silver, quarantine, and future Gold outputs are stored as Delta datasets.

This provides:

- ACID transactions
- schema enforcement
- reliable overwrite behavior
- transaction logs
- efficient downstream processing

### Raw Files Remain CSV

The raw container stores the original source files as CSV.

The conversion to Delta starts in Bronze.