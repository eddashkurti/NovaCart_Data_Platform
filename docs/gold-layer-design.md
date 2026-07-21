# Gold Layer Design

## Purpose

The Gold layer is the analytics-ready layer of the NovaCart Data Platform.

Its purpose is to transform validated Silver datasets into dimension and fact tables that support reporting, business analysis, and future dashboard development.

The Gold layer follows a simplified star-schema design.

## Source Data

Gold reads from the validated Silver Delta datasets stored under:

```text
abfss://silver@stnovacartdev.dfs.core.windows.net/olist/
```

Only valid Silver records are used.

Quarantined records are excluded from Gold processing.

## Storage Layout

Gold Delta outputs are written under:

```text
abfss://gold@stnovacartdev.dfs.core.windows.net/olist/
```

Current Gold datasets:

```text
gold/
└── olist/
    ├── dim_customers/
    ├── dim_dates/
    ├── dim_products/
    ├── dim_sellers/
    ├── fact_orders/
    ├── fact_order_items/
    ├── fact_payments/
    ├── fact_reviews/
    └── data_quality/
```

## Notebook Structure

Gold notebooks are stored under:

```text
notebooks/gold/
```

The Gold layer includes notebooks for:

- customer dimension
- date dimension
- product dimension
- seller dimension
- orders fact
- order items fact
- payments fact
- reviews fact
- aggregate or analytics-ready outputs
- Gold quality validation

## Dimension Tables

### dim_customers

The customer dimension contains one row per customer.

Primary business key:

```text
customer_id
```

Main attributes include:

- customer unique identifier
- ZIP code prefix
- city
- state

Expected row count:

```text
99,441
```

### dim_dates

The date dimension provides calendar attributes for order and delivery analysis.

Main attributes include:

- full date
- day
- month
- year
- quarter
- weekday
- weekend indicator

Expected row count:

```text
1,314
```

### dim_products

The product dimension contains one row per product.

Primary business key:

```text
product_id
```

Main attributes include:

- product category
- translated category name
- product name length
- description length
- photo quantity
- weight
- dimensions

Expected row count:

```text
32,951
```

### dim_sellers

The seller dimension contains one row per seller.

Primary business key:

```text
seller_id
```

Main attributes include:

- ZIP code prefix
- city
- state

Expected row count:

```text
3,095
```

## Fact Tables

### fact_orders

The orders fact contains one row per order.

Primary grain:

```text
order_id
```

Main measures and attributes include:

- customer identifier
- order status
- purchase timestamp
- approval timestamp
- carrier delivery timestamp
- customer delivery timestamp
- estimated delivery timestamp
- approval duration
- carrier handling duration
- delivery duration
- delay indicators

Expected row count:

```text
99,252
```

### fact_order_items

The order items fact contains one row per order-item combination.

Primary grain:

```text
order_id + order_item_id
```

Main measures and attributes include:

- product identifier
- seller identifier
- price
- freight value
- shipping limit timestamp

Expected row count:

```text
112,650
```

### fact_payments

The payments fact contains one row per payment sequence within an order.

Primary grain:

```text
order_id + payment_sequential
```

Main measures and attributes include:

- payment type
- installments
- payment value

Expected row count:

```text
103,883
```

### fact_reviews

The reviews fact contains one row per review-order combination.

Primary grain:

```text
review_id + order_id
```

Main attributes include:

- review score
- review title
- review message
- review creation timestamp
- review answer timestamp

Expected row count:

```text
99,224
```

## Gold Validation

The Gold layer includes dedicated validation checks before outputs are treated as analytics-ready.

Validation includes:

- null business-key checks
- duplicate grain checks
- row-count checks
- dimension uniqueness checks
- fact grain uniqueness checks
- expected output verification
- date-key coverage validation across Gold facts

The Gold quality notebook validates all eight Gold datasets.

## Current Gold Quality Results

The current Gold layer contains:

- 4 dimension tables
- 4 fact tables
- 8 validated Gold datasets
- 0 null business-key violations
- 0 duplicate grain violations
- all quality checks passing

## Data Quality Reporting

Gold also stores reporting-ready quality outputs under:

```text
abfss://gold@stnovacartdev.dfs.core.windows.net/olist/data_quality/
```

Generated datasets:

- `silver_quarantine_summary`
- `rejection_reason_summary`
- `data_quality_metrics`
- `quality_overview`
- `quarantine_overview`

These datasets support operational monitoring and future dashboards.

## Design Decisions

The Gold layer uses path-based Delta reads and writes.

The current implementation uses full overwrite writes because the Olist dataset is static and the platform is designed for complete batch reruns.

The Gold model focuses on clean analytical grains rather than preserving every Silver column.

## Current Limitations

The Gold layer currently does not include:

- incremental merge logic
- slowly changing dimensions
- BI dashboards
- automated test execution in CI

The Gold layer is orchestrated through the Databricks Job:

NovaCart End-to-End Pipeline

## Databricks Job Orchestration

Gold execution is managed through the `NovaCart End-to-End Pipeline` Databricks Job.

Execution order:


Gold dimensions and facts
        ↓
Gold business aggregates
        ↓
Gold quality checks
        ↓
Data quality reporting

## Relationship to Dashboards

The Gold layer is the source for future Databricks SQL and dashboard development.

Planned dashboard areas include:

- order performance
- delivery performance
- payment analysis
- review analysis
- product performance
- seller performance
- data quality monitoring