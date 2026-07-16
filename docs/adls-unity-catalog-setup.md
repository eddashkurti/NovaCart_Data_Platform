# ADLS and Unity Catalog Setup

## Project Resources

- Resource group: `rg-novacart-dev`
- Storage account: `stnovacartdev`
- Databricks workspace: `dbw-novacart-dev`
- Azure Databricks Access Connector: `unity-catalog-access-connector`
- Storage credential: `dbw_novacart_dev`

## Storage Design

The storage account uses Azure Data Lake Storage Gen2 with hierarchical namespace enabled.

Containers:

- `raw`
- `bronze`
- `silver`
- `quarantine`
- `gold`
- `logs`

## Container Layout

```text
raw/
└── olist/
    ├── olist_customers_dataset.csv
    ├── olist_geolocation_dataset.csv
    ├── olist_order_items_dataset.csv
    ├── olist_order_payments_dataset.csv
    ├── olist_order_reviews_dataset.csv
    ├── olist_orders_dataset.csv
    ├── olist_products_dataset.csv
    ├── olist_sellers_dataset.csv
    └── product_category_name_translation.csv

bronze/
└── olist/
    ├── customers/
    ├── geolocation/
    ├── order_items/
    ├── order_payments/
    ├── order_reviews/
    ├── orders/
    ├── products/
    ├── sellers/
    └── category_translation/

silver/
└── olist/
    ├── customers/
    ├── geolocation/
    ├── order_items/
    ├── order_payments/
    ├── order_reviews/
    ├── orders/
    ├── products/
    ├── sellers/
    └── category_translation/

quarantine/
└── olist/
    ├── customers/
    ├── geolocation/
    ├── order_items/
    ├── order_payments/
    ├── order_reviews/
    ├── orders/
    ├── products/
    ├── sellers/
    └── category_translation/

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
        ├── silver_quarantine_summary/
        ├── rejection_reason_summary/
        ├── data_quality_metrics/
        ├── quality_overview/
        └── quarantine_overview/
```

## Source Data Location

The Olist source files are stored at:

```text
abfss://raw@stnovacartdev.dfs.core.windows.net/olist/
```

## Delta Layer Locations

Bronze data:

```text
abfss://bronze@stnovacartdev.dfs.core.windows.net/olist/
```

Silver data:

```text
abfss://silver@stnovacartdev.dfs.core.windows.net/olist/
```

Quarantine data:

```text
abfss://quarantine@stnovacartdev.dfs.core.windows.net/olist/
```

Gold data:

```text
abfss://gold@stnovacartdev.dfs.core.windows.net/olist/
```

Gold quality outputs:

```text
abfss://gold@stnovacartdev.dfs.core.windows.net/olist/data_quality/
```

## Unity Catalog Access

Databricks accesses ADLS Gen2 through a managed identity using the Azure Databricks Access Connector.

The storage credential is:

```text
dbw_novacart_dev
```

External locations should be configured for the project containers so Databricks can access the corresponding ADLS paths.

Recommended external locations:

- `novacart_raw_location`
- `novacart_bronze_location`
- `novacart_silver_location`
- `novacart_quarantine_location`
- `novacart_gold_location`
- `novacart_logs_location`

## Example External Location Mapping

```text
novacart_raw_location
→ abfss://raw@stnovacartdev.dfs.core.windows.net/

novacart_bronze_location
→ abfss://bronze@stnovacartdev.dfs.core.windows.net/

novacart_silver_location
→ abfss://silver@stnovacartdev.dfs.core.windows.net/

novacart_quarantine_location
→ abfss://quarantine@stnovacartdev.dfs.core.windows.net/

novacart_gold_location
→ abfss://gold@stnovacartdev.dfs.core.windows.net/

novacart_logs_location
→ abfss://logs@stnovacartdev.dfs.core.windows.net/
```

## Access Model

The project uses:

- managed identity authentication
- Unity Catalog storage credentials
- external locations for governed ADLS access
- no storage keys embedded in notebooks
- no secrets committed to the repository

## Notes

The project stores processed data as Delta files using path-based reads and writes.

Unity Catalog is used for governed storage access, but the current implementation does not depend on registered managed tables for Bronze, Silver, or Gold datasets.