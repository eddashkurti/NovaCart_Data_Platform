# Storage Layout

## Overview

NovaCart uses Azure Data Lake Storage Gen2 to separate data by processing layer.

The storage account is:

```text
stnovacartdev
```

The project uses separate containers for:

- `raw`
- `bronze`
- `silver`
- `quarantine`
- `gold`
- `logs`

This separation keeps source files, processed data, rejected records, analytical models, and future operational logs isolated from each other.

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
| `quarantine` | Records rejected during Silver validation |
| `gold` | Analytics-ready dimensions, facts, and quality reports |
| `logs` | Future pipeline audit and operational logs |

## Raw Container

Raw base path:

```text
abfss://raw@stnovacartdev.dfs.core.windows.net/olist/
```

The Raw container stores the original Olist CSV files:

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
- Raw data remains in CSV format.

## Bronze Container

Bronze base path:

```text
abfss://bronze@stnovacartdev.dfs.core.windows.net/olist/
```

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
- source-file lineage
- ingestion timestamps
- batch identifiers

Bronze metadata columns:

- `_source_file`
- `_ingestion_timestamp`
- `_batch_id`

## Silver Container

Silver base path:

```text
abfss://silver@stnovacartdev.dfs.core.windows.net/olist/
```

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

Silver contains:

- cleaned records
- standardized values
- validated business fields
- preserved Bronze lineage
- Silver processing metadata

Silver metadata column:

- `_silver_processed_at`

## Quarantine Container

Quarantine base path:

```text
abfss://quarantine@stnovacartdev.dfs.core.windows.net/olist/
```

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

The Quarantine container stores records that fail Silver validation.

Each quarantined record includes:

- original record fields
- `_rejection_reason`
- `_quarantined_at`
- `_source_dataset`
- Bronze lineage metadata

Current quarantine results:

| Dataset | Rejected Rows |
|---|---:|
| Customers | 0 |
| Orders | 189 |
| Order items | 0 |
| Order payments | 3 |
| Order reviews | 0 |
| Products | 6 |
| Sellers | 0 |
| Geolocation | 0 |
| Category translation | 0 |

Total quarantined rows:

```text
198
```

## Gold Container

Gold base path:

```text
abfss://gold@stnovacartdev.dfs.core.windows.net/olist/
```

The Gold container stores analytics-ready dimension and fact tables.

### Dimension Paths

| Dataset | Path |
|---|---|
| Customer dimension | `gold/olist/dim_customers` |
| Date dimension | `gold/olist/dim_dates` |
| Product dimension | `gold/olist/dim_products` |
| Seller dimension | `gold/olist/dim_sellers` |

### Fact Paths

| Dataset | Path |
|---|---|
| Orders fact | `gold/olist/fact_orders` |
| Order items fact | `gold/olist/fact_order_items` |
| Payments fact | `gold/olist/fact_payments` |
| Reviews fact | `gold/olist/fact_reviews` |

Current Gold row counts:

| Dataset | Rows |
|---|---:|
| `dim_customers` | 99,441 |
| `dim_dates` | 1,314 |
| `dim_products` | 32,951 |
| `dim_sellers` | 3,095 |
| `fact_orders` | 99,252 |
| `fact_order_items` | 112,650 |
| `fact_payments` | 103,883 |
| `fact_reviews` | 99,224 |

## Gold Data Quality Storage

Data-quality reporting outputs are stored under:

```text
abfss://gold@stnovacartdev.dfs.core.windows.net/olist/data_quality/
```

Quality dataset paths:

| Dataset | Path |
|---|---|
| Silver quarantine summary | `gold/olist/data_quality/silver_quarantine_summary` |
| Rejection reason summary | `gold/olist/data_quality/rejection_reason_summary` |
| Data quality metrics | `gold/olist/data_quality/data_quality_metrics` |
| Quality overview | `gold/olist/data_quality/quality_overview` |
| Quarantine overview | `gold/olist/data_quality/quarantine_overview` |

These datasets are used for:

- quality monitoring
- rejection analysis
- Silver and Gold validation reporting
- future operational dashboards

## Logs Container

Logs base path:

```text
abfss://logs@stnovacartdev.dfs.core.windows.net/
```

The logs layer has not been implemented yet.

Planned use:

- pipeline execution logs
- workflow run summaries
- audit records
- failure details
- operational status outputs

## External Locations

Unity Catalog external locations are configured at the container level.

Project external locations include:

| External location | Container |
|---|---|
| `novacart_raw_location` | `raw` |
| `novacart_bronze_location` | `bronze` |
| `novacart_silver_location` | `silver` |
| `novacart_quarantine_location` | `quarantine` |
| `novacart_gold_location` | `gold` |

A logs external location may be added when the logs layer is implemented:

| External location | Container |
|---|---|
| `novacart_logs_location` | `logs` |

## Design Decisions

### One Container per Layer

Each major data layer has its own ADLS container.

This improves:

- separation of concerns
- access control
- operational clarity
- debugging
- lifecycle management

### One External Location per Container

External locations are created at the container level rather than per dataset.

This avoids unnecessary Unity Catalog objects and keeps storage access management simpler.

### Delta for Processed Layers

Bronze, Silver, Quarantine, and Gold outputs are stored as Delta datasets.

This provides:

- ACID transactions
- schema enforcement
- transaction history
- reliable overwrite behavior
- efficient downstream reads

### Raw Files Remain CSV

The Raw container stores the original source files as CSV.

Conversion to Delta begins in the Bronze layer.

### Path-Based Data Access

The project uses path-based Delta reads and writes.

Example:

```text
abfss://silver@stnovacartdev.dfs.core.windows.net/olist/orders
```

Unity Catalog governs access to the ADLS containers, but the current pipeline does not depend on registered managed tables.

### Full Overwrite Strategy

Bronze, Silver, and Gold currently use full overwrite writes.

This is intentional because the Olist dataset is static and the platform is designed around complete batch reruns.

Incremental ingestion, Delta `MERGE`, and historical change processing are outside the current project scope.