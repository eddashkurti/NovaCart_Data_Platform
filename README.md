# NovaCart Data Platform

NovaCart is an end-to-end e-commerce data engineering project built on Microsoft Azure and Databricks.

The project uses the Olist Brazilian E-Commerce dataset to implement a cloud-based Medallion Architecture with Raw ingestion, Bronze Delta processing, Silver cleansing and validation, quarantine handling, Gold analytical modeling, data-quality reporting, Databricks Job orchestration, and bundle-based deployment.

The goal is to simulate a small production-style data platform using modern cloud data engineering tools and practices.

---

## Architecture

```text
Olist CSV files
      ↓
Raw ADLS container
      ↓
Bronze Delta ingestion
      ↓
Silver cleansing and validation
      ├── valid records → Silver
      └── invalid records → Quarantine
      ↓
Gold dimensions and facts
      ↓
Business aggregates
      ↓
Gold quality checks
      ↓
Data quality reporting
```

---

## Technology Stack

- Azure Data Lake Storage Gen2
- Azure Databricks
- Databricks Serverless Compute
- Databricks Jobs
- Databricks Declarative Automation Bundles
- Unity Catalog
- Azure Databricks Access Connector
- Managed Identity
- Delta Lake
- PySpark
- Python
- GitHub

---

## Dataset

The project uses nine files from the Olist Brazilian E-Commerce public dataset:

- customers
- orders
- order items
- order payments
- order reviews
- products
- sellers
- geolocation
- product category translation

---

## Implementation Highlights

### Bronze Layer

The Bronze layer ingests all nine raw CSV files into Delta format.

Key features:

- explicit PySpark schemas
- shared ingestion logic
- required-column validation
- ingestion metadata
- empty-input checks
- Delta write and row-count validation

Shared ingestion module:

```text
src/bronze_ingestion.py
```

### Silver Layer

The Silver layer applies dataset-specific cleansing and validation.

Key features:

- text standardization
- timestamp validation
- domain validation
- duplicate business-key checks
- invalid-record quarantine
- row-count reconciliation
- Delta readback validation

### Quarantine Layer

Invalid Silver records are preserved in a separate ADLS container with rejection metadata.

Current quarantine result:

```text
198 rejected rows
3 datasets with rejected records
6 datasets without rejected records
```

### Gold Layer

The Gold layer contains analytics-ready dimensions and facts.

Dimensions:

- `dim_customers`
- `dim_dates`
- `dim_products`
- `dim_sellers`

Facts:

- `fact_orders`
- `fact_order_items`
- `fact_payments`
- `fact_reviews`

The Gold layer also includes business aggregates and dedicated quality checks.

### Data Quality Framework

The project produces reporting-ready quality datasets for:

- Silver quarantine summaries
- rejection reason summaries
- Silver and Gold quality metrics
- overall quality status
- quarantine monitoring

All current quality checks pass.

---

## Final Dataset Counts

### Bronze

| Dataset | Rows |
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

### Silver

| Dataset | Valid Rows | Quarantined Rows |
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

### Gold

| Dataset | Rows |
|---|---:|
| `dim_customers` | 99,441 |
| `dim_dates` | 1,314 |
| `dim_products` | 32,951 |
| `dim_sellers` | 3,095 |
| `fact_orders` | 99,252 |
| `fact_order_items` | 112,650 |
| `fact_payments` | 103,883 |
| `fact_reviews` | 99,224 |

---

## Databricks Job Orchestration

The end-to-end Databricks Job contains 31 notebook tasks:

```text
9 Bronze tasks
      ↓
9 Silver tasks
      ↓
8 Gold dimension and fact tasks
      ↓
Gold business aggregates
      ↓
Gold quality checks
      ↓
3 data quality reporting tasks
```

The workflow supports:

- parallel task execution
- dataset-level dependencies
- failure isolation
- repair runs
- centralized run monitoring

The complete pipeline was executed successfully on July 21, 2026.

```text
Final run status: Succeeded
```

## Deployment

The project uses a Databricks Declarative Automation Bundle to manage the end-to-end workflow as Infrastructure as Code.

Bundle configuration:

- `databricks.yml`
- `resources/novacart_end_to_end_pipeline.job.yml`

The existing 31-task Databricks Job was imported and bound to the bundle, allowing the workflow configuration to be version-controlled alongside the project source code.

The bundle supports:

- configuration validation
- reproducible deployment
- version-controlled workflow configuration

Deployment was validated using:

```bash
databricks bundle validate
databricks bundle deploy
```

---

## Repository Structure

```text
NovaCart_Data_Platform/
│
├── architecture/
│   ├── medallion-architecture.md
│   └── storage-layout.md
│
├── config/
│   └── README.md
│
├── docs/
│   ├── adls-unity-catalog-setup.md
│   ├── bronze-ingestion-design.md
│   ├── gold-layer-design.md
│   ├── project-status.md
│   └── silver-transformation-design.md
│
├── notebooks/
│   ├── bronze/
│   ├── silver/
│   ├── gold/
│   └── quality/
│
├── resources/
│   └── novacart_end_to_end_pipeline.job.yml
│
├── src/
│   ├── __init__.py
│   ├── README.md
│   └── bronze_ingestion.py
│
├── tests/
│   ├── README.md
│   └── test_plan.md
│
├── LICENSE.md
├── README.md
└── databricks.yml
```

---

## Storage

The project uses separate ADLS Gen2 containers:

| Container | Purpose |
|---|---|
| `raw` | Original source files |
| `bronze` | Source-preserving Delta datasets |
| `silver` | Cleaned and validated datasets |
| `quarantine` | Rejected Silver records |
| `gold` | Analytical models and quality outputs |
| `logs` | Reserved for future operational logging |

Storage access is governed through Unity Catalog and managed identity.

No secrets are stored in the repository.

---

## Current Status

```text
Raw: Completed
Bronze: Completed
Silver: Completed
Quarantine: Completed
Gold: Completed
Data quality: Completed
Databricks Job orchestration: Completed
Bundle deployment: Completed
Dashboards: Not started
Automated tests: Planned
```

---

## Future Improvements

- Databricks SQL dashboards
- scheduled job execution
- parameterized workflow runs
- pipeline audit logging
- executable PySpark tests
- CI-based validation
- incremental processing

---
### Future Refactoring

Bronze ingestion has been consolidated into a shared ingestion module.

Silver and Gold notebooks intentionally remain self-contained for readability. If the platform grows beyond the current nine datasets, common validation and write/readback logic can be extracted into shared utility modules (for example `silver_utils.py`, `gold_utils.py`, and `quality_utils.py`) to further reduce duplication.

## Documentation

Detailed implementation documentation is available in:

- `architecture/medallion-architecture.md`
- `architecture/storage-layout.md`
- `docs/bronze-ingestion-design.md`
- `docs/silver-transformation-design.md`
- `docs/gold-layer-design.md`
- `docs/project-status.md`

---

## License

This project is licensed under the MIT License.

See `LICENSE.md`.
