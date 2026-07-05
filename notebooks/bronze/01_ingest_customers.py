"""
Bronze ingestion for the Olist customers dataset.

Reads the raw customers CSV from Azure Data Lake Storage,
validates the expected schema, adds ingestion metadata,
writes the data as Delta, and validates the result.
"""

from datetime import datetime, timezone

from pyspark.sql import functions as F


RAW_CUSTOMERS_PATH = (
    "abfss://raw@stnovacartdev.dfs.core.windows.net/"
    "olist/olist_customers_dataset.csv"
)

BRONZE_CUSTOMERS_PATH = (
    "abfss://bronze@stnovacartdev.dfs.core.windows.net/"
    "olist/customers"
)

EXPECTED_COLUMNS = {
    "customer_id",
    "customer_unique_id",
    "customer_zip_code_prefix",
    "customer_city",
    "customer_state",
}

batch_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


# Read the raw CSV and capture the source file path
customers_raw_df = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .option("mode", "FAILFAST")
    .csv(RAW_CUSTOMERS_PATH)
    .select(
        "*",
        F.col("_metadata.file_path").alias("_source_file"),
    )
)


# Validate that the required source columns exist
source_columns = set(customers_raw_df.columns)
missing_columns = EXPECTED_COLUMNS - source_columns

if missing_columns:
    raise ValueError(
        "Customers source is missing required columns: "
        f"{sorted(missing_columns)}"
    )


# Add Bronze ingestion metadata
customers_bronze_df = (
    customers_raw_df
    .withColumn("_ingestion_timestamp", F.current_timestamp())
    .withColumn("_batch_id", F.lit(batch_id))
)


# Count the source records before writing
source_count = customers_bronze_df.count()

if source_count == 0:
    raise RuntimeError("The customers source file contains no records.")


# Write the Bronze dataset as Delta
(
    customers_bronze_df.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", True)
    .save(BRONZE_CUSTOMERS_PATH)
)


# Read the written Delta dataset
customers_written_df = (
    spark.read
    .format("delta")
    .load(BRONZE_CUSTOMERS_PATH)
)

written_count = customers_written_df.count()


# Validate that the source and destination row counts match
if source_count != written_count:
    raise RuntimeError(
        "Row-count validation failed. "
        f"Source rows: {source_count}, "
        f"Bronze rows: {written_count}"
    )


print("Customers Bronze ingestion completed successfully.")
print(f"Batch ID: {batch_id}")
print(f"Rows written: {written_count}")
print(f"Destination: {BRONZE_CUSTOMERS_PATH}")

display(customers_written_df.limit(10))