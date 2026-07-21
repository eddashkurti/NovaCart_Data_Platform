# Configuration

This folder is reserved for non-secret project configuration for the NovaCart Data Platform.

## Current State

No standalone configuration file is currently used.

Environment-specific paths and dataset settings are defined directly in the Databricks notebooks and shared Python modules.

## Intended Use

This folder may later contain non-secret configuration such as:

- project name
- environment name
- storage account name
- ADLS container names
- base storage paths
- dataset names
- source file mappings
- Bronze, Silver, Quarantine, and Gold paths
- workflow parameters

## Security Rules

Do not store secrets in this folder.

Never commit:

- passwords
- storage account keys
- SAS tokens
- client secrets
- connection strings
- personal access tokens

Authentication is handled through Azure Databricks, Unity Catalog, and managed identity.

## Future Improvement

A structured configuration file may be added later if the pipeline is refactored to centralize environment settings.

Possible options include:

- `dev_config.json`
- YAML configuration
- Databricks widgets
- Databricks Asset Bundle variables
- environment-specific job parameters

Any future configuration file must contain only non-secret values.