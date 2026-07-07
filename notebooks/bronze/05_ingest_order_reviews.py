"""
Bronze ingestion for the Olist order reviews dataset.

Reads the raw reviews CSV from Azure Data Lake Storage,
validates the expected schema, adds ingestion metadata,
writes the data as Delta, and validates the result.
"""

from datetime import datetime, timezone

from pyspark.sql import functions as F


RAW_ORDER_REVIEWS_PATH = (
    "abfss://raw@stnovacartdev.dfs.core.windows.net/"
    "olist/olist_order_reviews_dataset.csv"
)

BRONZE_ORDER_REVIEWS_PATH = (
    "abfss://bronze@stnovacartdev.dfs.core.windows.net/"
    "olist/order_reviews"
)

EXPECTED_COLUMNS = {
    "review_id",
    "order_id",
    "review_score",
    "review_comment_title",
    "review_comment_message",
    "review_creation_date",
    "review_answer_timestamp",
}

batch_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


order_reviews_raw_df = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .option("mode", "FAILFAST")
    .csv(RAW_ORDER_REVIEWS_PATH)
    .select(
        "*",
        F.col("_metadata.file_path").alias("_source_file"),
    )
)


missing_columns = EXPECTED_COLUMNS - set(order_reviews_raw_df.columns)

if missing_columns:
    raise ValueError(
        "Order reviews source is missing required columns: "
        f"{sorted(missing_columns)}"
    )


order_reviews_bronze_df = (
    order_reviews_raw_df
    .withColumn("_ingestion_timestamp", F.current_timestamp())
    .withColumn("_batch_id", F.lit(batch_id))
)


source_count = order_reviews_bronze_df.count()

if source_count == 0:
    raise RuntimeError("The order reviews source file contains no records.")


(
    order_reviews_bronze_df.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", True)
    .save(BRONZE_ORDER_REVIEWS_PATH)
)


order_reviews_written_df = (
    spark.read
    .format("delta")
    .load(BRONZE_ORDER_REVIEWS_PATH)
)

written_count = order_reviews_written_df.count()


if source_count != written_count:
    raise RuntimeError(
        "Row-count validation failed. "
        f"Source rows: {source_count}, "
        f"Bronze rows: {written_count}"
    )


print("Order reviews Bronze ingestion completed successfully.")
print(f"Batch ID: {batch_id}")
print(f"Rows written: {written_count}")
print(f"Destination: {BRONZE_ORDER_REVIEWS_PATH}")

display(order_reviews_written_df.limit(10))