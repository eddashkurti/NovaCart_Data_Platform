"""
Bronze ingestion for the Olist orders dataset.

Reads the raw orders CSV from Azure Data Lake Storage,
validates the expected schema, adds ingestion metadata,
writes the data as Delta, and validates the result.
"""

from datetime import datetime, timezone

from pyspark.sql import functions as F


RAW_ORDERS_PATH = (
    "abfss://raw@stnovacartdev.dfs.core.windows.net/"
    "olist/olist_orders_dataset.csv"
)

BRONZE_ORDERS_PATH = (
    "abfss://bronze@stnovacartdev.dfs.core.windows.net/"
    "olist/orders"
)

EXPECTED_COLUMNS = {
    "order_id",
    "customer_id",
    "order_status",
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
}

batch_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


orders_raw_df = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .option("mode", "FAILFAST")
    .csv(RAW_ORDERS_PATH)
    .select(
        "*",
        F.col("_metadata.file_path").alias("_source_file"),
    )
)


missing_columns = EXPECTED_COLUMNS - set(orders_raw_df.columns)

if missing_columns:
    raise ValueError(
        "Orders source is missing required columns: "
        f"{sorted(missing_columns)}"
    )


orders_bronze_df = (
    orders_raw_df
    .withColumn("_ingestion_timestamp", F.current_timestamp())
    .withColumn("_batch_id", F.lit(batch_id))
)


source_count = orders_bronze_df.count()

if source_count == 0:
    raise RuntimeError("The orders source file contains no records.")


(
    orders_bronze_df.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", True)
    .save(BRONZE_ORDERS_PATH)
)


orders_written_df = (
    spark.read
    .format("delta")
    .load(BRONZE_ORDERS_PATH)
)

written_count = orders_written_df.count()


if source_count != written_count:
    raise RuntimeError(
        "Row-count validation failed. "
        f"Source rows: {source_count}, "
        f"Bronze rows: {written_count}"
    )


print("Orders Bronze ingestion completed successfully.")
print(f"Batch ID: {batch_id}")
print(f"Rows written: {written_count}")
print(f"Destination: {BRONZE_ORDERS_PATH}")

display(orders_written_df.limit(10))