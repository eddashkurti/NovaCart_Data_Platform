# Project Status

## NovaCart Data Platform

This document tracks the current implementation status of the NovaCart Data Platform.

## Completed

### Cloud and Storage Setup

- Azure resource group created
- Azure Data Lake Storage Gen2 account created
- ADLS Gen2 containers created:
  - raw
  - bronze
  - silver
  - quarantine
  - gold
  - logs
- Azure Databricks workspace created
- Unity Catalog storage credential configured
- External locations configured for the required storage containers
- Managed identity access configured for Databricks storage access

### Raw Layer

All nine Olist source CSV files were uploaded to:

```text
abfss://raw@stnovacartdev.dfs.core.windows.net/olist/
```

### Bronze Layer

- All nine Bronze ingestion pipelines completed
- Shared ingestion logic implemented in:

```text
src/bronze_ingestion.py
```

- Source files ingested from ADLS Gen2
- Explicit PySpark schemas implemented for all nine source datasets
- Bronze outputs written in Delta format
- Ingestion metadata added:
  - `_source_file`
  - `_ingestion_timestamp`
  - `_batch_id`
- Required-column validation implemented
- Source-schema validation implemented
- Bronze row-count validation completed

Bronze datasets:

- customers
- orders
- order_items
- order_payments
- order_reviews
- products
- sellers
- geolocation
- category_translation

### Silver Layer

- All nine Silver transformation pipelines completed
- Dataset-specific cleansing and validation rules applied
- Invalid records routed to the quarantine container
- Duplicate business-key validation enforced where a reliable grain exists
- Silver row-count reconciliation completed
- Silver outputs written in Delta format

Silver datasets:

- customers
- orders
- order_items
- order_payments
- order_reviews
- products
- sellers
- geolocation
- category_translation

### Silver Validation Summary

| Dataset | Silver Rows | Quarantined Rows |
|---|---:|---:|
| Customers | 99,441 | 0 |
| Orders | 99,252 | 189 |
| Order items | 112,650 | 0 |
| Order payments | 103,883 | 3 |
| Order reviews | 99,224 | 0 |
| Products | 32,951 | 6 |
| Sellers | 3,095 | 0 |
| Geolocation | 1,000,163 | 0 |
| Category translation | 71 | 0 |

Total quarantined rows: **198**

### Gold Layer

The Gold layer has been completed using dimension and fact tables designed for analytics and reporting.

Gold dimensions:

- `dim_customers`
- `dim_dates`
- `dim_products`
- `dim_sellers`

Gold facts:

- `fact_orders`
- `fact_order_items`
- `fact_payments`
- `fact_reviews`

Gold dataset counts:

| Dataset | Rows |
|---|---:|
| dim_customers | 99,441 |
| dim_dates | 1,314 |
| dim_products | 32,951 |
| dim_sellers | 3,095 |
| fact_orders | 99,252 |
| fact_order_items | 112,650 |
| fact_payments | 103,883 |
| fact_reviews | 99,224 |

Gold validation includes:

- null business-key checks
- duplicate grain checks
- row-count verification
- fact and dimension integrity checks
- date-key coverage validation

All current Gold validation checks pass.

### Data Quality Framework

The data quality reporting layer has been completed.

Implemented notebooks:

- `01_silver_quarantine_summary.ipynb`
- `02_data_quality_metrics.ipynb`
- `03_data_quality_report.ipynb`

Generated reporting datasets:

- `silver_quarantine_summary`
- `rejection_reason_summary`
- `data_quality_metrics`
- `quality_overview`
- `quarantine_overview`

Current quality results:

- 17 quality metric rows
- 9 Silver datasets checked
- 8 Gold datasets checked
- all quality checks passing
- 198 total quarantined rows
- 3 datasets with rejected records
- 6 datasets without rejected records

### Databricks Job Orchestration

The full NovaCart pipeline is orchestrated through a Databricks Job named:

```text
NovaCart End-to-End Pipeline
```

The job contains 31 notebook tasks across Bronze, Silver, Gold, and data quality reporting.

Execution structure:

```text
9 Bronze ingestion tasks
        ↓
9 Silver transformation tasks
        ↓
8 Gold dimension and fact tasks
        ↓
Gold business aggregates
        ↓
Gold quality checks
        ↓
Silver quarantine summary
        ↓
Data quality metrics
        ↓
Data quality report
```

Bronze tasks run independently in parallel.

Each Silver task depends on its corresponding Bronze task.

Gold dimensions and facts depend on the Silver datasets they consume.

The final quality tasks run only after Gold validation succeeds.

The complete end-to-end job was executed successfully on July 21, 2026.

Final run result:

```text
Succeeded
```

The successful run validated:

- all 9 Bronze datasets
- all 9 Silver datasets
- all 8 Gold dimension and fact tables
- Gold business aggregates
- Gold quality checks
- all 3 data quality reporting notebooks

## Current Limitations

### Batch Overwrite Strategy

The current implementation uses full overwrite writes across Bronze, Silver, and Gold.

This matches the current static-batch implementation of the Olist dataset.

Incremental ingestion, Delta `MERGE`, and historical change processing have not been implemented.

### Scheduling and Parameters

The Databricks Job currently supports manual end-to-end execution.

Scheduled triggers, job parameters, backfill logic, and audit logging have not yet been added.

## Not Started

### Dashboards

Planned work:

- Databricks SQL queries
- KPI dashboards
- sales and order performance
- payment analysis
- review analysis
- product and seller performance
- data quality monitoring

### Automated Tests

Planned work:

- executable PySpark tests
- schema validation tests
- data-quality rule tests
- pipeline reconciliation tests

## Current Recommendation

The next implementation milestone should be Databricks SQL dashboard development, followed by automated test coverage and optional job scheduling.