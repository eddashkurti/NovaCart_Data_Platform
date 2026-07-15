# Data Quality

This folder contains notebooks that monitor and report data quality across the NovaCart Silver and Gold layers.

## Notebooks

### 01_silver_quarantine_summary

Reads all Silver quarantine Delta tables and creates consolidated summaries for rejected records.

Outputs include:

- rejected row counts by dataset
- affected batch counts
- first and last quarantine timestamps
- dataset-level quality status
- rejection counts by rejection reason

Gold outputs:

- `olist/data_quality/silver_quarantine_summary`
- `olist/data_quality/rejection_reason_summary`

### 02_data_quality_metrics

Calculates reusable quality metrics across Silver and Gold tables.

Checks include:

- table row counts
- null business keys
- duplicate grain records
- table-level quality status

The notebook validates 9 Silver tables and 8 Gold tables.

Gold output:

- `olist/data_quality/data_quality_metrics`

### 03_data_quality_report

Combines quarantine summaries and table-level quality metrics into reporting-ready datasets for monitoring and dashboards.

Outputs include:

- pass rate by data layer
- passed and review table counts
- total row counts
- total null business key counts
- total duplicate grain counts
- total quarantined rows
- datasets with and without rejected records

Gold outputs:

- `olist/data_quality/quality_overview`
- `olist/data_quality/quarantine_overview`

## Current Results

The current quality report shows:

- 9 Silver tables validated
- 8 Gold tables validated
- 17 total quality metric records
- 100% table-level pass rate across Silver and Gold
- 198 quarantined Silver records
- 3 datasets with rejected records
- 6 datasets without rejected records

The quarantined records consist of:

- 189 order records with invalid delivery timestamp sequences
- 6 product records with invalid product weight
- 3 payment records with invalid payment type