"""
NovaCart Data Platform
Environment setup and configuration validation.

This file contains non-sensitive project configuration.
Do not store passwords, access keys, or secrets here.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ProjectConfig:
    project_name: str = "NovaCart Data Platform"
    environment: str = "dev"

    storage_account: str = "stnovacartdev"
    raw_container: str = "raw"
    bronze_container: str = "bronze"
    silver_container: str = "silver"
    gold_container: str = "gold"
    quarantine_container: str = "quarantine"
    logs_container: str = "logs"


config = ProjectConfig()


def display_configuration() -> None:
    """Print the current non-sensitive project configuration."""

    print(f"Project: {config.project_name}")
    print(f"Environment: {config.environment}")
    print(f"Storage account: {config.storage_account}")
    print(
        "Containers:",
        [
            config.raw_container,
            config.bronze_container,
            config.silver_container,
            config.gold_container,
            config.quarantine_container,
            config.logs_container,
        ],
    )


display_configuration()