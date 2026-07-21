# Medallion Architecture

## Overview

NovaCart uses the Medallion Architecture pattern to organize the Olist e-commerce data platform into progressive data-quality layers.

The platform contains:

- Raw
- Bronze
- Silver
- Quarantine
- Gold
- Data quality reporting

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
      ├── valid records → Silver
      └── invalid records → Quarantine
      ↓
Gold dimensions and facts
      ↓
Gold business aggregates
      ↓
Gold quality validation
      ↓
Data quality reporting datasets
      ↓
Databricks SQL dashboards
```

The complete workflow is orchestrated through a Databricks Job named:

```text
NovaCart End-to-End Pipeline
```

## Raw Layer

The Raw layer stores the original Olist CSV files exactly as uploaded.

Raw path:

```text
abfss://raw@stnovacartdev.dfs.core.windows.net/olist/
```

Raw responsibilities:

- store original source files
- preserve input files before processing
- act as the landing zone for ingestion

Raw files are not modified by the pipeline.

## Bronze Layer

The Bronze layer converts raw CSV files into Delta datasets.

Bronze path:

```text
abfss://bronze@stnovacartdev.dfs.core.windows.net/olist/<dataset_name>
```

Bronze responsibilities:

- read raw CSV files
- apply explicit PySpark source schemas
- validate required source columns
- add ingestion metadata
- write Delta output
- validate row counts after writing

Bronze does not perform heavy business cleaning.

Bronze metadata columns:

- `_source_file`
- `_ingestion_timestamp`
- `_batch_id`

The Bronze layer uses explicit PySpark schemas for all nine source datasets.

This keeps column types stable across reruns and protects downstream Silver and Gold transformations from schema inference drift.

Bronze currently uses full overwrite writes because the Olist source is processed as a complete static batch.

## Silver Layer

The Silver layer cleans, standardizes, and validates the Bronze datasets.

Silver path:

```text
abfss://silver@stnovacartdev.dfs.core.windows.net/olist/<dataset_name>
```

Silver responsibilities:

- clean and standardize text fields
- validate business rules
- enforce duplicate business-key rules where a reliable grain exists
- route invalid records to quarantine
- preserve Bronze lineage columns
- add Silver processing metadata
- derive useful operational fields
- validate row-count reconciliation

Silver metadata column:

- `_silver_processed_at`

## Quarantine Layer

Invalid Silver records are written to:

```text
abfss://quarantine@stnovacartdev.dfs.core.windows.net/olist/<dataset_name>
```

Quarantine responsibilities:

- preserve rejected records
- store the reason each record was rejected
- support investigation and quality monitoring
- ensure rejected data is not silently discarded

Quarantine metadata columns:

- `_rejection_reason`
- `_quarantined_at`
- `_source_dataset`

Current quarantine totals:

- 198 rejected rows
- 3 datasets with rejected records
- 6 datasets without rejected records

## Gold Layer

The Gold layer contains analytics-ready dimension and fact tables.

Gold path:

```text
abfss://gold@stnovacartdev.dfs.core.windows.net/olist/
```

Gold responsibilities:

- create dimension tables
- create fact tables
- enforce analytical grains
- create business aggregates
- prepare reporting-ready datasets
- support business analysis
- support Databricks SQL dashboards

Current Gold dimensions:

- `dim_customers`
- `dim_dates`
- `dim_products`
- `dim_sellers`

Current Gold facts:

- `fact_orders`
- `fact_order_items`
- `fact_payments`
- `fact_reviews`

Current Gold row counts:

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
- dimension uniqueness checks
- fact grain validation
- date-key coverage validation across Gold facts

All current Gold quality checks pass.

## Data Quality Reporting

The project includes a dedicated reporting layer for Silver quarantine and Silver/Gold quality metrics.

Quality outputs are stored under:

```text
abfss://gold@stnovacartdev.dfs.core.windows.net/olist/data_quality/
```

Generated datasets:

- `silver_quarantine_summary`
- `rejection_reason_summary`
- `data_quality_metrics`
- `quality_overview`
- `quarantine_overview`

The quality framework currently checks:

- 9 Silver datasets
- 8 Gold datasets
- 17 total quality metric rows

All current quality metrics pass.

## Databricks Job Orchestration

The full platform is orchestrated through:

```text
NovaCart End-to-End Pipeline
```

The job contains 31 notebook tasks.

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

The quality reporting tasks run only after Gold validation succeeds.

The complete end-to-end workflow was executed successfully on July 21, 2026.

## Layer Responsibilities

| Layer | Purpose | Format |
|---|---|---|
| Raw | Original uploaded source files | CSV |
| Bronze | Source-preserving ingestion layer | Delta |
| Silver | Cleaned and validated datasets | Delta |
| Quarantine | Invalid Silver records with rejection reasons | Delta |
| Gold | Analytics-ready dimensions, facts, and aggregates | Delta |
| Data quality | Reporting-ready quality summaries and metrics | Delta |

## Design Decisions

### One Notebook per Dataset

Bronze and Silver use one notebook per Olist dataset.

This provides:

- easier debugging
- independent reruns
- clear failure isolation
- simpler Databricks Job task design
- readable Git history

Gold uses separate notebooks for dimensions, facts, business aggregates, and validation logic.

### Bronze Stays Simple

Bronze intentionally avoids business-rule validation.

It preserves the source structure, applies explicit schemas, and adds technical metadata.

### Silver Owns Data Quality

Silver applies dataset-specific validation rules.

Invalid records are not deleted. They are routed to quarantine so they can be inspected later.

Duplicate-key validation is enforced in Silver for datasets with reliable business grains.

Geolocation is not deduplicated because repeated ZIP prefixes and coordinates can be legitimate at the source grain.

### Gold Owns Business Modeling

Gold is responsible for analytical modeling, dimensions, facts, grains, aggregates, and reporting-ready outputs.

Gold consumes only valid Silver records. Quarantined records are excluded from Gold processing.

### Full Overwrite Strategy

Bronze, Silver, and Gold currently use full overwrite writes.

This matches the current static-batch implementation of the Olist dataset.

Incremental ingestion, Delta `MERGE`, and slowly changing dimensions have not been implemented.

### Workflow Orchestration

The platform uses a Databricks Job to manage task dependencies and full end-to-end execution.

The workflow supports:

- parallel Bronze execution
- dataset-level Silver dependencies
- Gold dependency management
- downstream quality validation
- repair runs after task failures
- centralized run monitoring

## Next Steps

Planned future work includes:

- scheduled job execution
- parameterized job runs
- pipeline audit logging
- Databricks SQL dashboards
- executable automated tests