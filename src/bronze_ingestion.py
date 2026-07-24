from datetime import datetime, timezone
from typing import Iterable

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType


def ingest_csv_to_delta(
    *,
    dataset_name: str,
    source_path: str,
    destination_path: str,
    expected_columns: Iterable[str],
    source_schema: StructType,
    spark_session: SparkSession,
    csv_options: dict[str, object] | None = None,
) -> DataFrame:
    """
    Ingest a CSV dataset into the Bronze Delta layer.

    The function:
    - reads the source CSV using an explicit schema;
    - applies optional dataset-specific CSV settings;
    - captures source-file lineage;
    - validates required columns;
    - adds Bronze ingestion metadata;
    - checks for empty input;
    - writes Delta output;
    - validates the written row count;
    - returns the written Bronze DataFrame.
    """

    expected_columns_set = set(expected_columns)
    schema_columns_set = set(source_schema.fieldNames())
    csv_options = csv_options or {}

    missing_schema_columns = (
        expected_columns_set - schema_columns_set
    )

    if missing_schema_columns:
        raise ValueError(
            f"{dataset_name} schema is missing required columns: "
            f"{sorted(missing_schema_columns)}"
        )

    batch_id = datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ"
    )

    reader = (
    spark_session.read
    .option("header", True)
    .option("mode", "FAILFAST")
    .option("enforceSchema", False)
    .schema(source_schema)
)

    for option_name, option_value in csv_options.items():
        reader = reader.option(option_name, option_value)

    raw_df = (
        reader
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
        spark_session.read
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

    display_name = dataset_name.replace("_", " ").title()

    print(
        f"{display_name} Bronze ingestion completed successfully."
    )
    print(f"Batch ID: {batch_id}")
    print(f"Rows written: {written_count}")
    print(f"Destination: {destination_path}")

    return written_df