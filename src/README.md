# Source Modules

This folder contains reusable Python modules for the NovaCart Data Platform.

## Current Modules

### `bronze_ingestion.py`

Reusable ingestion logic for the Bronze layer.

The main function is:

`ingest_csv_to_delta`

It handles:

- reading CSV source files
- applying optional CSV options
- validating expected columns
- adding Bronze metadata
- checking for empty input
- writing Delta output
- reading the written output back
- validating row counts
- printing completion details

## Current Design

Bronze uses a shared module because ingestion logic is mostly repeated across datasets.

Silver logic currently remains inside individual notebooks because each dataset has different validation and transformation rules.

Reusable Silver utilities may be added later if repeated patterns become stable, such as:

- required-column validation
- row-count reconciliation
- Delta write validation
- quarantine metadata handling

## Security

Do not store secrets in source modules.

Authentication is handled through Azure Databricks, Unity Catalog, and managed identity.