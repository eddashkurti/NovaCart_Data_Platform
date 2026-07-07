"""
Bronze ingestion for the Olist order items dataset.

Reads the raw order items CSV from Azure Data Lake Storage,
validates the expected schema, adds ingestion metadata,
writes the data as Delta, and validates the result.
"""

from datetime import datetime, timezone

from pyspark.sql import functions as F


RAW_ORDER_ITEMS_PATH = (
    "abfss://raw@stnovacartdev.dfs.core.windows.net/"
    "olist/olist_order_items_dataset.csv"
)

BRONZE_ORDER_ITEMS_PATH = (
    "abfss://bronze@stnovacartdev.dfs.core.windows.net/"
    "olist/order_items"
)

EXPECTED_COLUMNS = {
    "order_id",
    "order_item_id",
    "product_id",
    "seller_id",
    "shipping_limit_date",
    "price",
    "freight_value",
}

batch_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


order_items_raw_df = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .option("mode", "FAILFAST")
    .csv(RAW_ORDER_ITEMS_PATH)
    .select(
        "*",
        F.col("_metadata.file_path").alias("_source_file"),
    )
)


missing_columns = EXPECTED_COLUMNS - set(order_items_raw_df.columns)

if missing_columns:
    raise ValueError(
        "Order items source is missing required columns: "
        f"{sorted(missing_columns)}"
    )


order_items_bronze_df = (
    order_items_raw_df
    .withColumn("_ingestion_timestamp", F.current_timestamp())
    .withColumn("_batch_id", F.lit(batch_id))
)


source_count = order_items_bronze_df.count()

if source_count == 0:
    raise RuntimeError("The order items source file contains no records.")


(
    order_items_bronze_df.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", True)
    .save(BRONZE_ORDER_ITEMS_PATH)
)


order_items_written_df = (
    spark.read
    .format("delta")
    .load(BRONZE_ORDER_ITEMS_PATH)
)

written_count = order_items_written_df.count()


if source_count != written_count:
    raise RuntimeError(
        "Row-count validation failed. "
        f"Source rows: {source_count}, "
        f"Bronze rows: {written_count}"
    )


print("Order items Bronze ingestion completed successfully.")
print(f"Batch ID: {batch_id}")
print(f"Rows written: {written_count}")
print(f"Destination: {BRONZE_ORDER_ITEMS_PATH}")

display(order_items_written_df.limit(10))