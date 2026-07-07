from datetime import datetime, timezone
from typing import Iterable

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F


def ingest_csv_to_delta(
    *,
    dataset_name: str,
    source_path: str,
    destination_path: str,
    expected_columns: Iterable[str],
    spark_session: SparkSession | None = None,
) -> DataFrame:
    """
    Ingest a CSV dataset into the Bronze Delta layer.

    The function:
    - reads the source CSV;
    - captures source-file lineage;
    - validates required columns;
    - adds Bronze ingestion metadata;
    - checks for empty input;
    - writes Delta output;
    - validates the written row count;
    - returns the written Bronze DataFrame.
    """

    active_spark = spark_session or spark

    expected_columns_set = set(expected_columns)

    batch_id = datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ"
    )

    raw_df = (
        active_spark.read
        .option("header", True)
        .option("inferSchema", True)
        .option("mode", "FAILFAST")
        .csv(source_path)
        .select(
            "*",
            F.col("_metadata.file_path").alias("_source_file"),
        )
    )

    missing_columns = (
        expected_columns_set - set(raw_df.columns)
    )

    if missing_columns:
        raise ValueError(
            f"{dataset_name} source is missing required columns: "
            f"{sorted(missing_columns)}"
        )

    bronze_df = (
        raw_df
        .withColumn(
            "_ingestion_timestamp",
            F.current_timestamp(),
        )
        .withColumn(
            "_batch_id",
            F.lit(batch_id),
        )
    )

    source_count = bronze_df.count()

    if source_count == 0:
        raise RuntimeError(
            f"The {dataset_name} source file contains no records."
        )

    (
        bronze_df.write
        .format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .save(destination_path)
    )

    written_df = (
        active_spark.read
        .format("delta")
        .load(destination_path)
    )

    written_count = written_df.count()

    if source_count != written_count:
        raise RuntimeError(
            f"{dataset_name} row-count validation failed. "
            f"Source rows: {source_count}, "
            f"Bronze rows: {written_count}"
        )

    print(
        f"{dataset_name.replace('_', ' ').title()} "
        "Bronze ingestion completed successfully."
    )
    print(f"Batch ID: {batch_id}")
    print(f"Rows written: {written_count}")
    print(f"Destination: {destination_path}")

    return written_df