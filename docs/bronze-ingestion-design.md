# Bronze Ingestion Design

## Purpose

The Bronze layer is the first Delta Lake layer in the NovaCart Data Platform.

Its purpose is to ingest the original Olist CSV datasets from the raw ADLS container and store them as Delta datasets with minimal transformation.

Bronze is designed to preserve the source structure while adding technical metadata and basic ingestion validation.

## Source Data

Raw Olist CSV files are stored under:

`abfss://raw@stnovacartdev.dfs.core.windows.net/olist/`

The source datasets are:

- customers
- orders
- order items
- order payments
- order reviews
- products
- sellers
- geolocation
- category translation

## Storage Layout

Bronze Delta outputs are written to:

`abfss://bronze@stnovacartdev.dfs.core.windows.net/olist/<dataset_name>`

Current Bronze output paths:

- `bronze/olist/customers`
- `bronze/olist/orders`
- `bronze/olist/order_items`
- `bronze/olist/order_payments`
- `bronze/olist/order_reviews`
- `bronze/olist/products`
- `bronze/olist/sellers`
- `bronze/olist/geolocation`
- `bronze/olist/category_translation`

## Notebook Structure

Bronze notebooks are stored under:

`notebooks/01_bronze/`

Each source dataset has its own notebook:

- `01_ingest_customers.ipynb`
- `02_ingest_orders.ipynb`
- `03_ingest_order_items.ipynb`
- `04_ingest_order_payments.ipynb`
- `05_ingest_order_reviews.ipynb`
- `06_ingest_products.ipynb`
- `07_ingest_sellers.ipynb`
- `08_ingest_geolocation.ipynb`
- `09_ingest_category_translation.ipynb`

Keeping one notebook per dataset makes the pipelines easier to run, debug, retry, and later schedule as separate Databricks Job tasks.

## Shared Ingestion Module

Reusable Bronze ingestion logic is stored in:

`src/bronze_ingestion.py`

The shared function is:

`ingest_csv_to_delta`

It handles:

1. reading the CSV source file
2. applying optional CSV options
3. capturing source-file lineage
4. validating expected columns
5. adding ingestion metadata
6. checking for empty input
7. writing Delta output
8. reading the written output back
9. validating row counts
10. printing completion details

This keeps the notebooks short and table-specific while avoiding duplicated ingestion boilerplate.

## Bronze Metadata Columns

Every Bronze dataset includes these metadata columns:

- `_source_file`
- `_ingestion_timestamp`
- `_batch_id`

These columns provide traceability for source-file lineage, ingestion time, and batch identification.

## CSV Reading Strategy

Bronze CSV files are read with:

- header enabled
- schema inference enabled
- FAILFAST mode

The order reviews dataset uses additional CSV options because review comments can contain multiline text:

- `multiLine`
- `quote`
- `escape`

## Validation Rules

Bronze performs only basic technical validation:

- required columns must exist
- source file must contain records
- Delta write must complete
- written row count must match source row count

Bronze does not perform heavy cleaning, business validation, or standardization. Those responsibilities belong to the Silver layer.

## Design Decision

Bronze intentionally keeps the source data close to the original CSV structure.

Examples:

- source column names are preserved
- product misspellings such as `product_name_lenght` remain unchanged
- business-rule validation is not applied
- invalid business values are not quarantined in Bronze

This makes Bronze a reliable raw Delta representation of the source data.

## Completed Bronze Row Counts

- Customers: 99,441
- Orders: 99,441
- Order items: 112,650
- Order payments: 103,886
- Order reviews: 99,224
- Products: 32,951
- Sellers: 3,095
- Geolocation: 1,000,163
- Category translation: 71

## Relationship to Silver

Silver reads from Bronze Delta paths and applies:

- cleaning
- type standardization
- business validation
- quarantine routing
- derived columns
- row-count reconciliation

Bronze should remain simple and stable.