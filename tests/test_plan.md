# Test Plan

## Purpose

This test plan describes the manual validation checks used for the NovaCart Data Platform.

The goal is to ensure that each pipeline writes correct, complete, and traceable Delta outputs.

## Bronze Test Plan

### 1. Raw File Access

Check that all raw Olist source files are visible under:

`abfss://raw@stnovacartdev.dfs.core.windows.net/olist/`

Expected files:

- `olist_customers_dataset.csv`
- `olist_orders_dataset.csv`
- `olist_order_items_dataset.csv`
- `olist_order_payments_dataset.csv`
- `olist_order_reviews_dataset.csv`
- `olist_products_dataset.csv`
- `olist_sellers_dataset.csv`
- `olist_geolocation_dataset.csv`
- `product_category_name_translation.csv`

### 2. Required Columns

Each Bronze notebook validates that the expected source columns exist.

Failure condition:

- one or more expected columns are missing

Expected result:

- notebook raises an error before writing Bronze output

### 3. Empty Source Check

Each Bronze notebook checks that the source dataset contains records.

Failure condition:

- source row count equals zero

Expected result:

- notebook raises an error before writing Bronze output

### 4. Delta Write Validation

Each Bronze notebook writes the dataset to Delta, reads it back, and compares row counts.

Expected result:

- source row count equals written Bronze row count

## Bronze Expected Row Counts

| Dataset | Expected Bronze Rows |
|---|---:|
| Customers | 99,441 |
| Orders | 99,441 |
| Order items | 112,650 |
| Order payments | 103,886 |
| Order reviews | 99,224 |
| Products | 32,951 |
| Sellers | 3,095 |
| Geolocation | 1,000,163 |
| Category translation | 71 |

## Silver Test Plan

### 1. Required Columns

Each Silver notebook validates that required Bronze columns exist.

Failure condition:

- one or more expected columns are missing

Expected result:

- notebook raises an error before transformations continue

### 2. Quality Profile

Each Silver notebook profiles missing, invalid, duplicate, or suspicious values before applying validation rules.

Expected result:

- profile output is reviewed before final validation rules are applied

### 3. Rejection Reason Assignment

Each invalid Silver record receives a `_rejection_reason`.

Expected result:

- valid rows have `_rejection_reason = null`
- invalid rows have a non-null rejection reason

### 4. Quarantine Routing

Each Silver notebook splits records into:

- valid Silver records
- invalid quarantine records

Expected result:

- invalid records are not dropped silently
- invalid records are written to the quarantine container

### 5. Row-Count Reconciliation

Each Silver notebook validates:

`Silver rows + quarantined rows = Bronze input rows`

Failure condition:

- row counts do not reconcile

Expected result:

- notebook raises an error

### 6. Delta Write Validation

Each Silver notebook writes Silver and quarantine outputs, reads them back, and compares row counts.

Expected result:

- written Silver row count equals expected Silver row count
- written quarantine row count equals expected quarantine row count

## Silver Expected Row Counts

| Dataset | Expected Silver Rows | Expected Quarantine Rows |
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

## Manual Review Checklist

Before merging a completed layer:

- [ ] All notebooks run from top to bottom
- [ ] All required-column checks pass
- [ ] All row-count validations pass
- [ ] All Delta write validations pass
- [ ] Quarantine paths are written where applicable
- [ ] Final schemas are inspected
- [ ] Sample output rows are displayed
- [ ] Commit messages clearly describe the change
- [ ] Pull request description includes validation results

## Future Automated Tests

Future automated tests should cover:

- reusable Bronze ingestion function
- row-count reconciliation helpers
- required-column validation helpers
- quarantine metadata helpers
- derived-column logic
- schema expectations