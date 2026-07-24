# Silver Transformation Design

## Purpose

The Silver layer contains cleaned, standardized, and validated datasets derived from the Bronze Delta layer.

Bronze preserves the original source structure with ingestion metadata. Silver improves data quality while keeping each dataset close to its original business meaning.

## Design Principles

The Silver layer follows these principles:

- one transformation notebook per source dataset
- dataset-specific validation rules
- invalid records routed to quarantine
- valid records written to the Silver container
- Bronze lineage columns preserved
- Silver processing metadata added
- duplicate business-key validation applied where a reliable grain exists
- row-count reconciliation performed after every transformation

## Storage Layout

Silver outputs are written to:

```text
abfss://silver@stnovacartdev.dfs.core.windows.net/olist/<dataset_name>
```

Quarantined records are written to:

```text
abfss://quarantine@stnovacartdev.dfs.core.windows.net/olist/<dataset_name>
```

## Notebook Structure

Silver notebooks are stored under:

```text
notebooks/silver/
```

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
6. calculate duplicate business-key counts where applicable
7. apply dataset-specific validation rules
8. assign rejection reasons
9. split valid and invalid records
10. add Silver and quarantine metadata
11. write Delta outputs
12. read outputs back
13. validate row counts

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

Temporary duplicate-count columns are removed before valid and quarantined outputs are written.

## Dataset Rules

### Customers

Business grain:

```text
customer_id
```

Rules applied:

- validate customer IDs
- validate customer unique IDs
- validate ZIP prefix range
- normalize city names
- normalize state codes
- validate state format
- reject duplicate customer IDs

Duplicate rejection reason:

```text
DUPLICATE_CUSTOMER_ID
```

Result:

- Silver rows: 99,441
- Quarantined rows: 0

### Orders

Business grain:

```text
order_id
```

Rules applied:

- validate order IDs
- validate customer IDs
- validate allowed order statuses
- validate purchase timestamp
- validate timestamp chronology
- reject duplicate order IDs
- derive delivery metrics

Derived columns:

- `delivery_days`
- `estimated_delivery_days`
- `delivery_delay_days`
- `is_delayed`

Duplicate rejection reason:

```text
DUPLICATE_ORDER_ID
```

Result:

- Silver rows: 99,252
- Quarantined rows: 189

### Order Items

Business grain:

```text
order_id + order_item_id
```

Rules applied:

- validate order IDs
- validate order item IDs
- validate product IDs
- validate seller IDs
- validate shipping limit date
- reject null or negative price
- reject null or negative freight value
- reject duplicate order-item keys

Duplicate rejection reason:

```text
DUPLICATE_ORDER_ITEM_KEY
```

Result:

- Silver rows: 112,650
- Quarantined rows: 0

### Order Payments

Business grain:

```text
order_id + payment_sequential
```

Rules applied:

- validate order IDs
- validate payment sequence
- validate payment type
- validate payment installments
- reject null or negative payment values
- route `not_defined` payment types to quarantine
- reject duplicate payment keys

Duplicate rejection reason:

```text
DUPLICATE_PAYMENT_KEY
```

Result:

- Silver rows: 103,883
- Quarantined rows: 3

### Order Reviews

Business grain:

```text
review_id + order_id
```

Rules applied:

- validate review IDs
- validate order IDs
- validate review score range
- validate review timestamps
- clean comment title and message
- preserve missing comments as valid
- reject duplicate review-order keys

Duplicate rejection reason:

```text
DUPLICATE_REVIEW_ORDER_KEY
```

Result:

- Silver rows: 99,224
- Quarantined rows: 0

### Products

Business grain:

```text
product_id
```

Rules applied:

- validate product IDs
- standardize category names
- rename misspelled Bronze columns:
  - `product_name_lenght` to `product_name_length`
  - `product_description_lenght` to `product_description_length`
- validate product weight and dimensions
- derive product volume
- reject duplicate product IDs

Derived column:

```text
product_volume_cm3
```

Duplicate rejection reason:

```text
DUPLICATE_PRODUCT_ID
```

Result:

- Silver rows: 32,945
- Quarantined rows: 6

### Sellers

Business grain:

```text
seller_id
```

Rules applied:

- validate seller IDs
- validate ZIP prefix range
- normalize city names
- normalize state codes
- validate state format
- reject duplicate seller IDs

Duplicate rejection reason:

```text
DUPLICATE_SELLER_ID
```

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

Geolocation records are not deduplicated in Silver.

Repeated ZIP prefixes, coordinates, cities, and states can be legitimate in the source data. The dataset therefore does not have a reliable unique business grain for duplicate quarantine.

Aggregation or deduplication can be handled later if a dedicated geolocation dimension is introduced.

Result:

- Silver rows: 1,000,163
- Quarantined rows: 0

### Category Translation

Business grain:

```text
product_category_name
```

Rules applied:

- validate Portuguese category names
- validate English category names
- trim and lowercase category values
- reject duplicate Portuguese category names

Duplicate rejection reason:

```text
DUPLICATE_PRODUCT_CATEGORY_NAME
```

Result:

- Silver rows: 71
- Quarantined rows: 0

## Reconciliation Rule

For each Silver pipeline:

```text
Silver row count + quarantine row count = Bronze input row count
```

This confirms that every Bronze record is either accepted into Silver or routed to quarantine.

## Current Quarantine Summary

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

Total quarantined rows:

```text
198
```

Datasets with quarantined records:

- orders
- order payments
- products

## Design Decision

Silver transformations are intentionally not centralized into one generic transformation function.

Each dataset has different business rules, grains, validation logic, and derived columns. Keeping the main validation logic inside each notebook makes the pipelines easier to understand, debug, and review.

Reusable Silver utilities may be introduced later for repeated operations such as:

- required-column validation
- row-count reconciliation
- duplicate-key detection
- Delta write validation
- output readback checks

## Write Strategy

Silver currently uses full overwrite writes.

This is intentional because the Olist source is a static batch dataset and the current platform is designed for complete pipeline reruns.

Incremental processing, merge logic, and change-data handling may be added later if the project is extended to support continuously arriving data.

## Relationship to Gold

Gold reads only validated Silver outputs.

Quarantined records are excluded from Gold dimensions, facts, analytics datasets, and quality metrics.

The Gold layer then applies:

- dimension and fact modeling
- analytical grain enforcement
- business aggregations
- final null-key validation
- duplicate grain validation
- reporting-ready quality checks