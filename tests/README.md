# Tests

## Overview

This folder documents the current validation approach for the NovaCart Data Platform.

At this stage, the project uses notebook-level validation instead of automated PySpark unit tests.

The current validation approach includes:

- required-column checks
- empty-input checks
- Delta write validation
- row-count reconciliation
- quarantine row-count checks
- manual schema inspection
- sample output inspection

Automated tests can be added later when the project introduces reusable transformation modules or CI/CD.

## Current Validation Scope

### Bronze

Bronze notebooks validate that:

- required source columns exist
- source files are not empty
- Delta output is written successfully
- written row count matches source row count
- source-file lineage is captured

### Silver

Silver notebooks validate that:

- required Bronze columns exist
- dataset-specific quality rules are applied
- invalid records are routed to quarantine
- Silver outputs are written successfully
- quarantine outputs are written successfully
- written row counts match expected row counts
- Silver rows plus quarantined rows equal Bronze input rows

## Why Automated Tests Are Not Added Yet

Most transformation logic currently lives inside Databricks notebooks.

Automated PySpark tests will be more useful after repeated validation and write logic is extracted into reusable modules, such as:

- `src/silver_utils.py`
- `src/quality_utils.py`
- `src/logging_utils.py`

Until then, notebook-level validation is the active testing method.

## Future Test Ideas

Future automated tests may include:

- required-column validation tests
- schema validation tests
- row-count reconciliation tests
- quarantine rule tests
- duplicate-key checks
- derived-column checks
- sample transformation tests using small local DataFrames