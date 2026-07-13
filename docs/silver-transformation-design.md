# Silver Transformation Design

## Purpose

The Silver layer contains cleaned, standardized, and validated datasets derived from the Bronze Delta layer.

Bronze preserves raw source structure with ingestion metadata. Silver improves data quality while keeping each dataset close to its original business meaning.

## Design Principles

The Silver layer follows these principles:

- one transformation notebook per source dataset
- dataset-specific validation rules
- invalid records routed to quarantine
- valid records written to the Silver container
- Bronze lineage columns preserved
- Silver processing metadata added
- row-count reconciliation performed after every transformation

## Storage Layout

Silver outputs are written to:

`abfss://silver@stnovacartdev.dfs.core.windows.net/olist/<dataset_name>`

Quarantined records are written to:

`abfss://quarantine@stnovacartdev.dfs.core.windows.net/olist/<dataset_name>`

## Notebook Structure

Silver notebooks are stored under:

`notebooks/02_silver/`

Current Silver notebooks:

- `01_transform_customers.ipynb`
- `02_transform_orders.ipynb`
- `03_transform_order_items.ipynb`
- `04_transform_order_payments.ipynb`
- `05_transform_order_reviews.ipynb`
- `06_transform_products.ipynb`
- `07_transform_sellers.ipynb`
- `08_transform_geolocation.ipynb`
- `09_transform_category_translation.ipynb`

Each notebook follows the same general flow:

1. define storage paths
2. read Bronze Delta data
3. validate required columns
4. profile data quality
5. clean and standardize fields
6. apply dataset-specific validation rules
7. assign rejection reasons
8. split valid and invalid records
9. add Silver and quarantine metadata
10. write Delta outputs
11. read outputs back
12. validate row counts

## Metadata Columns

Silver datasets preserve Bronze metadata:

- `_source_file`
- `_ingestion_timestamp`
- `_batch_id`

Silver datasets add:

- `_silver_processed_at`

Quarantine datasets add:

- `_rejection_reason`
- `_quarantined_at`
- `_source_dataset`

## Dataset Rules

### Customers

Rules applied:

- validate customer IDs
- validate customer unique IDs
- validate ZIP prefix range
- normalize city names
- normalize state codes
- validate state format

Result:

- Silver rows: 99,441
- Quarantined rows: 0

### Orders

Rules applied:

- validate order IDs
- validate customer IDs
- validate allowed order statuses
- validate purchase timestamp
- validate timestamp chronology
- derive delivery metrics

Derived columns:

- `delivery_days`
- `estimated_delivery_days`
- `delivery_delay_days`
- `is_delayed`

Result:

- Silver rows: 99,252
- Quarantined rows: 189

### Order Items

Rules applied:

- validate order IDs
- validate order item IDs
- validate product IDs
- validate seller IDs
- validate shipping limit date
- reject null or negative price
- reject null or negative freight value
- check duplicate `(order_id, order_item_id)` keys

Result:

- Silver rows: 112,650
- Quarantined rows: 0

### Order Payments

Rules applied:

- validate order IDs
- validate payment sequence
- validate payment type
- validate payment installments
- reject null or negative payment values
- route `not_defined` payment types to quarantine

Result:

- Silver rows: 103,883
- Quarantined rows: 3

### Order Reviews

Rules applied:

- validate review IDs
- validate order IDs
- validate review score range
- validate review timestamps
- clean comment title and message
- preserve missing comments as valid

Result:

- Silver rows: 99,224
- Quarantined rows: 0

### Products

Rules applied:

- validate product IDs
- standardize category names
- rename misspelled Bronze columns:
  - `product_name_lenght` to `product_name_length`
  - `product_description_lenght` to `product_description_length`
- validate product weight and dimensions
- derive product volume

Derived column:

- `product_volume_cm3`

Result:

- Silver rows: 32,945
- Quarantined rows: 6

### Sellers

Rules applied:

- validate seller IDs
- validate ZIP prefix range
- normalize city names
- normalize state codes
- validate state format

Result:

- Silver rows: 3,095
- Quarantined rows: 0

### Geolocation

Rules applied:

- validate ZIP prefix range
- validate latitude range
- validate longitude range
- normalize city names
- normalize state codes
- validate state format

Geolocation records are not deduplicated in Silver. Repeated ZIP or coordinate records are preserved because Silver should not change the source grain. Aggregation can be handled later in Gold if a geolocation dimension is needed.

Result:

- Silver rows: 1,000,163
- Quarantined rows: 0

### Category Translation

Rules applied:

- validate Portuguese category names
- validate English category names
- trim and lowercase category values

Result:

- Silver rows: 71
- Quarantined rows: 0

## Reconciliation Rule

For each Silver pipeline:

`Silver row count + quarantine row count = Bronze input row count`

This confirms that every Bronze record is either accepted into Silver or routed to quarantine.

## Notes

Silver transformations are intentionally not centralized into one generic function yet. Each dataset has different business rules, so keeping the validation logic inside each notebook makes the layer easier to understand and debug.

Reusable Silver utilities may be introduced later for repeated tasks such as row-count reconciliation, required-column checks, and Delta write validation.