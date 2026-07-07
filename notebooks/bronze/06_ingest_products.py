"""
Bronze ingestion for the Olist products dataset.

Reads the raw products CSV from Azure Data Lake Storage,
validates the expected schema, adds ingestion metadata,
writes the data as Delta, and validates the result.
"""

from datetime import datetime, timezone
from pyspark.sql import functions as F


RAW_PRODUCTS_PATH = (
    "abfss://raw@stnovacartdev.dfs.core.windows.net/"
    "olist/olist_products_dataset.csv"
)

BRONZE_PRODUCTS_PATH = (
    "abfss://bronze@stnovacartdev.dfs.core.windows.net/"
    "olist/products"
)

EXPECTED_COLUMNS = {
    "product_id",
    "product_category_name",
    "product_name_lenght",
    "product_description_lenght",
    "product_photos_qty",
    "product_weight_g",
    "product_length_cm",
    "product_height_cm",
    "product_width_cm",
}

batch_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


products_raw_df = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .option("mode", "FAILFAST")
    .csv(RAW_PRODUCTS_PATH)
    .select(
        "*",
        F.col("_metadata.file_path").alias("_source_file"),
    )
)


missing_columns = EXPECTED_COLUMNS - set(products_raw_df.columns)

if missing_columns:
    raise ValueError(
        "Products source is missing required columns: "
        f"{sorted(missing_columns)}"
    )


products_bronze_df = (
    products_raw_df
    .withColumn("_ingestion_timestamp", F.current_timestamp())
    .withColumn("_batch_id", F.lit(batch_id))
)


source_count = products_bronze_df.count()

if source_count == 0:
    raise RuntimeError("The products source file contains no records.")


(
    products_bronze_df.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", True)
    .save(BRONZE_PRODUCTS_PATH)
)


products_written_df = (
    spark.read
    .format("delta")
    .load(BRONZE_PRODUCTS_PATH)
)

written_count = products_written_df.count()


if source_count != written_count:
    raise RuntimeError(
        "Row-count validation failed. "
        f"Source rows: {source_count}, "
        f"Bronze rows: {written_count}"
    )


print("Products Bronze ingestion completed successfully.")
print(f"Batch ID: {batch_id}")
print(f"Rows written: {written_count}")
print(f"Destination: {BRONZE_PRODUCTS_PATH}")

display(products_written_df.limit(10))