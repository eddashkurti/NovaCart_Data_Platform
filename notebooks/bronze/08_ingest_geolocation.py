"""
Bronze ingestion for the Olist geolocation dataset.

Reads the raw geolocation CSV from Azure Data Lake Storage,
validates the expected schema, adds ingestion metadata,
writes the data as Delta, and validates the result.
"""

from datetime import datetime, timezone

from pyspark.sql import functions as F


RAW_GEOLOCATION_PATH = (
    "abfss://raw@stnovacartdev.dfs.core.windows.net/"
    "olist/olist_geolocation_dataset.csv"
)

BRONZE_GEOLOCATION_PATH = (
    "abfss://bronze@stnovacartdev.dfs.core.windows.net/"
    "olist/geolocation"
)

EXPECTED_COLUMNS = {
    "geolocation_zip_code_prefix",
    "geolocation_lat",
    "geolocation_lng",
    "geolocation_city",
    "geolocation_state",
}

batch_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


geolocation_raw_df = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .option("mode", "FAILFAST")
    .csv(RAW_GEOLOCATION_PATH)
    .select(
        "*",
        F.col("_metadata.file_path").alias("_source_file"),
    )
)


missing_columns = EXPECTED_COLUMNS - set(geolocation_raw_df.columns)

if missing_columns:
    raise ValueError(
        "Geolocation source is missing required columns: "
        f"{sorted(missing_columns)}"
    )


geolocation_bronze_df = (
    geolocation_raw_df
    .withColumn("_ingestion_timestamp", F.current_timestamp())
    .withColumn("_batch_id", F.lit(batch_id))
)


source_count = geolocation_bronze_df.count()

if source_count == 0:
    raise RuntimeError("The geolocation source file contains no records.")


(
    geolocation_bronze_df.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", True)
    .save(BRONZE_GEOLOCATION_PATH)
)


geolocation_written_df = (
    spark.read
    .format("delta")
    .load(BRONZE_GEOLOCATION_PATH)
)

written_count = geolocation_written_df.count()


if source_count != written_count:
    raise RuntimeError(
        "Row-count validation failed. "
        f"Source rows: {source_count}, "
        f"Bronze rows: {written_count}"
    )


print("Geolocation Bronze ingestion completed successfully.")
print(f"Batch ID: {batch_id}")
print(f"Rows written: {written_count}")
print(f"Destination: {BRONZE_GEOLOCATION_PATH}")

display(geolocation_written_df.limit(10))