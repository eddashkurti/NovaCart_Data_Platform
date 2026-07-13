# Configuration

This folder stores non-secret project configuration for the NovaCart Data Platform.

## Files

- `dev_config.json`

## Purpose

The configuration file documents stable development settings such as:

- project name
- environment name
- storage account name
- ADLS container names
- base storage paths
- dataset file names
- Bronze, Silver, and quarantine dataset paths

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