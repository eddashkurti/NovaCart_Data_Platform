"""
Validate Databricks access to the NovaCart raw data in ADLS Gen2.
"""

RAW_OLIST_PATH = (
    "abfss://raw@stnovacartdev.dfs.core.windows.net/olist/"
)


def list_source_files(path: str) -> list[str]:
    """Return filenames available in the supplied ADLS directory."""
    files = dbutils.fs.ls(path)

    if not files:
        raise RuntimeError(f"No files were found at: {path}")

    return [file.name for file in files if not file.isDir()]


source_files = list_source_files(RAW_OLIST_PATH)

print(f"Connection successful. Found {len(source_files)} files:\n")

for filename in sorted(source_files):
    print(f"- {filename}")