# Project Status

## NovaCart Data Platform

This document tracks the current implementation status of the NovaCart Data Platform.

## Completed

### Cloud and Storage Setup

- Azure resource group created
- Azure Data Lake Storage Gen2 account created
- ADLS containers created:
  - raw
  - bronze
  - silver
  - gold
  - quarantine
  - logs
- Azure Databricks workspace created
- Unity Catalog storage credential configured
- External locations configured for:
  - raw
  - bronze
  - silver
  - quarantine

### Raw Layer

- All nine Olist CSV files uploaded to:

`abfss://raw@stnovacartdev.dfs.core.windows.net/olist/`

### Bronze Layer

- All nine Bronze ingestion pipelines completed
- Bronze ingestion refactored using:

`src/bronze_ingestion.py`

- Bronze outputs written as Delta datasets
- Bronze row-count validation completed

Bronze datasets:

- customers
- orders
- order items
- order payments
- order reviews
- products
- sellers
- geolocation
- category translation

### Silver Layer

- All nine Silver transformation pipelines completed
- Dataset-specific validation rules applied
- Invalid records routed to quarantine
- Silver row-count reconciliation completed
- Silver outputs written as Delta datasets

Silver datasets:

- customers
- orders
- order items
- order payments
- order reviews
- products
- sellers
- geolocation
- category translation

## Silver Validation Summary

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

## In Progress

No active layer is currently in progress.

## Not Started

### Gold Layer

Planned work:

- create fact and dimension models
- define business KPIs
- prepare dashboard-ready tables

Possible Gold models:

- `dim_customers`
- `dim_sellers`
- `dim_products`
- `dim_dates`
- `fact_orders`
- `fact_order_items`
- `fact_payments`
- `fact_reviews`

### Data Quality Framework

Planned work:

- reusable validation helpers
- reusable quarantine helpers
- data quality summary outputs

### Workflows

Planned work:

- Databricks Jobs
- task dependencies
- scheduled execution
- parameterized runs
- audit logging

### Dashboards

Planned work:

- Databricks SQL queries
- KPI dashboards
- order performance metrics
- payment analysis
- review analysis
- product and seller performance

### Tests

Planned work:

- manual test plan
- possible PySpark unit tests
- validation of row counts and schemas

## Current Recommendation

The next implementation milestone should be the Gold layer design.