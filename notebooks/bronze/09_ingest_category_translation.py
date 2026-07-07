"""
Bronze ingestion for the Olist product category translation dataset.

Reads the raw category translation CSV from Azure Data Lake Storage,
validates the expected schema, adds ingestion metadata,
writes the data as Delta, and validates the result.
"""

from datetime import datetime, timezone

from pyspark.sql import functions as F


RAW_CATEGORY_TRANSLATION_PATH = (
    "abfss://raw@stnovacartdev.dfs.core.windows.net/"
    "olist/product_category_name_translation.csv"
)

BRONZE_CATEGORY_TRANSLATION_PATH = (
    "abfss://bronze@stnovacartdev.dfs.core.windows.net/"
    "olist/category_translation"
)

EXPECTED_COLUMNS = {
    "product_category_name",
    "product_category_name_english",
}

batch_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


category_translation_raw_df = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .option("mode", "FAILFAST")
    .csv(RAW_CATEGORY_TRANSLATION_PATH)
    .select(
        "*",
        F.col("_metadata.file_path").alias("_source_file"),
    )
)


missing_columns = EXPECTED_COLUMNS - set(category_translation_raw_df.columns)

if missing_columns:
    raise ValueError(
        "Category translation source is missing required columns: "
        f"{sorted(missing_columns)}"
    )


category_translation_bronze_df = (
    category_translation_raw_df
    .withColumn("_ingestion_timestamp", F.current_timestamp())
    .withColumn("_batch_id", F.lit(batch_id))
)


source_count = category_translation_bronze_df.count()

if source_count == 0:
    raise RuntimeError(
        "The category translation source file contains no records."
    )


(
    category_translation_bronze_df.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", True)
    .save(BRONZE_CATEGORY_TRANSLATION_PATH)
)


category_translation_written_df = (
    spark.read
    .format("delta")
    .load(BRONZE_CATEGORY_TRANSLATION_PATH)
)

written_count = category_translation_written_df.count()


if source_count != written_count:
    raise RuntimeError(
        "Row-count validation failed. "
        f"Source rows: {source_count}, "
        f"Bronze rows: {written_count}"
    )


print("Category translation Bronze ingestion completed successfully.")
print(f"Batch ID: {batch_id}")
print(f"Rows written: {written_count}")
print(f"Destination: {BRONZE_CATEGORY_TRANSLATION_PATH}")

display(category_translation_written_df.limit(10))