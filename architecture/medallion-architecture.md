# Medallion Architecture

## Overview

NovaCart uses the Medallion Architecture pattern to organize the Olist e-commerce data platform into progressive data-quality layers.

The layers are:

- Raw
- Bronze
- Silver
- Gold

Each layer has a specific responsibility and is stored separately in Azure Data Lake Storage Gen2.

## Data Flow

```text
Olist CSV files
      ↓
Raw ADLS container
      ↓
Bronze Delta layer
      ↓
Silver cleaned and validated layer
      ↓
Gold analytical models
      ↓
Databricks SQL dashboards
```

## Raw Layer

The Raw layer stores the original Olist CSV files exactly as uploaded.

Raw path:

`abfss://raw@stnovacartdev.dfs.core.windows.net/olist/`

Raw responsibilities:

- Store original source files
- Preserve input files before processing
- Act as the landing zone for ingestion

Raw files are not modified by the pipeline.

## Bronze Layer

The Bronze layer converts the raw CSV files into Delta datasets.

Bronze path:

`abfss://bronze@stnovacartdev.dfs.core.windows.net/olist/<dataset_name>`

Bronze responsibilities:

- Read raw CSV files
- Validate required source columns
- Add ingestion metadata
- Write Delta output
- Validate row counts after write

Bronze does not perform heavy business cleaning.

Bronze metadata columns:

- `_source_file`
- `_ingestion_timestamp`
- `_batch_id`

## Silver Layer

The Silver layer cleans, standardizes, and validates the Bronze datasets.

Silver path:

`abfss://silver@stnovacartdev.dfs.core.windows.net/olist/<dataset_name>`

Silver responsibilities:

- Clean and standardize text fields
- Validate business rules
- Route invalid records to quarantine
- Preserve Bronze lineage columns
- Add Silver processing metadata
- Derive useful operational fields
- Validate row-count reconciliation

Silver metadata column:

- `_silver_processed_at`

Quarantined records are written to:

`abfss://quarantine@stnovacartdev.dfs.core.windows.net/olist/<dataset_name>`

Quarantine metadata columns:

- `_rejection_reason`
- `_quarantined_at`
- `_source_dataset`

## Gold Layer

The Gold layer has not been implemented yet.

Planned Gold responsibilities:

- Create fact tables
- Create dimension tables
- Define business KPIs
- Prepare dashboard-ready datasets
- Support Databricks SQL reporting

Potential Gold models:

- `dim_customers`
- `dim_sellers`
- `dim_products`
- `dim_dates`
- `fact_orders`
- `fact_order_items`
- `fact_payments`
- `fact_reviews`

## Layer Responsibilities

| Layer | Purpose | Format |
|---|---|---|
| Raw | Original uploaded CSV files | CSV |
| Bronze | Source-preserving ingestion layer | Delta |
| Silver | Cleaned and validated datasets | Delta |
| Quarantine | Invalid Silver records | Delta |
| Gold | Business-ready analytical models | Delta |

## Design Decisions

### One Notebook per Dataset

Bronze and Silver both use one notebook per Olist dataset.

This provides:

- Easier debugging
- Independent reruns
- Clear failure isolation
- Simpler Databricks Job task design
- Readable Git history

### Bronze Stays Simple

Bronze intentionally avoids business-rule logic.

It preserves the source structure and adds technical metadata only.

### Silver Handles Data Quality

Silver applies dataset-specific validation rules.

Invalid records are not deleted. They are routed to quarantine so they can be inspected later.

### Gold Will Handle Business Modeling

Gold will be responsible for analytical modeling, joins, aggregations, and KPIs.

For example, geolocation records are preserved at source grain in Silver. If an aggregated geolocation dimension is needed, it should be created in Gold.