"""
Bronze ingestion for the Olist sellers dataset.

Reads the raw sellers CSV from Azure Data Lake Storage,
validates the expected schema, adds ingestion metadata,
writes the data as Delta, and validates the result.
"""

from datetime import datetime, timezone

from pyspark.sql import functions as F


RAW_SELLERS_PATH = (
    "abfss://raw@stnovacartdev.dfs.core.windows.net/"
    "olist/olist_sellers_dataset.csv"
)

BRONZE_SELLERS_PATH = (
    "abfss://bronze@stnovacartdev.dfs.core.windows.net/"
    "olist/sellers"
)

EXPECTED_COLUMNS = {
    "seller_id",
    "seller_zip_code_prefix",
    "seller_city",
    "seller_state",
}

batch_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


sellers_raw_df = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .option("mode", "FAILFAST")
    .csv(RAW_SELLERS_PATH)
    .select(
        "*",
        F.col("_metadata.file_path").alias("_source_file"),
    )
)


missing_columns = EXPECTED_COLUMNS - set(sellers_raw_df.columns)

if missing_columns:
    raise ValueError(
        "Sellers source is missing required columns: "
        f"{sorted(missing_columns)}"
    )


sellers_bronze_df = (
    sellers_raw_df
    .withColumn("_ingestion_timestamp", F.current_timestamp())
    .withColumn("_batch_id", F.lit(batch_id))
)


source_count = sellers_bronze_df.count()

if source_count == 0:
    raise RuntimeError("The sellers source file contains no records.")


(
    sellers_bronze_df.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", True)
    .save(BRONZE_SELLERS_PATH)
)


sellers_written_df = (
    spark.read
    .format("delta")
    .load(BRONZE_SELLERS_PATH)
)

written_count = sellers_written_df.count()


if source_count != written_count:
    raise RuntimeError(
        "Row-count validation failed. "
        f"Source rows: {source_count}, "
        f"Bronze rows: {written_count}"
    )


print("Sellers Bronze ingestion completed successfully.")
print(f"Batch ID: {batch_id}")
print(f"Rows written: {written_count}")
print(f"Destination: {BRONZE_SELLERS_PATH}")

display(sellers_written_df.limit(10))