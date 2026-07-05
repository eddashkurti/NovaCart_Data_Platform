# ADLS and Unity Catalog Setup

## Project resources

- Resource group: `rg-novacart-dev`
- Storage account: `stnovacartdev`
- Databricks workspace: `dbw-novacart-dev`
- Azure Databricks Access Connector: `unity-catalog-access-connector`
- Storage credential: `dbw_novacart_dev`
- External location: `novacart_raw_location`

## Storage design

The storage account uses Azure Data Lake Storage Gen2 with hierarchical namespace enabled.

Containers:

- `raw`
- `bronze`
- `silver`
- `gold`
- `quarantine`
- `logs`

The Olist source files were uploaded to:

```text
raw/olist/