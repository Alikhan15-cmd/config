"""Configuration loader and validator for dependency visualizer."""

import json
import os
from src.constants import (
    KEY_FILTER_SUBSTRING,
    KEY_MAX_DEPTH,
    KEY_PACKAGE_NAME,
    KEY_PACKAGE_VERSION,
    KEY_REPOSITORY_URL,
    KEY_TEST_MODE,
    MIN_DEPTH,
    REQUIRED_CONFIG_KEYS,
    ZERO,
)


class ConfigError(ValueError):
    """Exception raised for errors in configuration."""


class AppConfig:
    """Represents application settings loaded from JSON config."""

    def __init__(
        self,
        package_name: str,
        repository_url: str,
        test_mode: bool,
        package_version: str,
        max_depth: int,
        filter_substring: str,
    ):
        """Initialize configuration values."""
        self.package_name = package_name
        self.repository_url = repository_url
        self.test_mode = test_mode
        self.package_version = package_version
        self.max_depth = max_depth
        self.filter_substring = filter_substring

    def to_dict(self) -> dict:
        """Convert configuration to dictionary."""
        return {
            KEY_PACKAGE_NAME: self.package_name,
            KEY_REPOSITORY_URL: self.repository_url,
            KEY_TEST_MODE: self.test_mode,
            KEY_PACKAGE_VERSION: self.package_version,
            KEY_MAX_DEPTH: self.max_depth,
            KEY_FILTER_SUBSTRING: self.filter_substring,
        }

    def format_key_value(self) -> str:
        """Format configuration parameters as key-value pairs."""
        lines = [
            f"{KEY_PACKAGE_NAME}: {self.package_name}",
            f"{KEY_REPOSITORY_URL}: {self.repository_url}",
            f"{KEY_TEST_MODE}: {self.test_mode}",
            f"{KEY_PACKAGE_VERSION}: {self.package_version}",
            f"{KEY_MAX_DEPTH}: {self.max_depth}",
            f"{KEY_FILTER_SUBSTRING}: {self.filter_substring}",
        ]
        return "\n".join(lines)


def _validate_types(data: dict) -> None:
    """Validate data types of individual config values."""
    if not isinstance(data[KEY_PACKAGE_NAME], str):
        raise ConfigError("package_name must be a string")
    if len(data[KEY_PACKAGE_NAME].strip()) == ZERO:
        raise ConfigError("package_name cannot be empty")

    if not isinstance(data[KEY_REPOSITORY_URL], str):
        raise ConfigError("repository_url must be a string")
    if len(data[KEY_REPOSITORY_URL].strip()) == ZERO:
        raise ConfigError("repository_url cannot be empty")

    if not isinstance(data[KEY_TEST_MODE], bool):
        raise ConfigError("test_mode must be a boolean (true/false)")

    if not isinstance(data[KEY_PACKAGE_VERSION], str):
        raise ConfigError("package_version must be a string")
    if len(data[KEY_PACKAGE_VERSION].strip()) == ZERO:
        raise ConfigError("package_version cannot be empty")

    depth = data[KEY_MAX_DEPTH]
    if isinstance(depth, bool) or not isinstance(depth, int):
        raise ConfigError("max_depth must be an integer")
    if depth < MIN_DEPTH:
        raise ConfigError(f"max_depth must be >= {MIN_DEPTH}")

    if not isinstance(data[KEY_FILTER_SUBSTRING], str):
        raise ConfigError("filter_substring must be a string")


def _validate_paths(data: dict) -> None:
    """Validate repository path when test mode is active."""
    if data[KEY_TEST_MODE]:
        path = data[KEY_REPOSITORY_URL]
        if not os.path.isfile(path):
            raise ConfigError(
                f"Test repository file does not exist: {path}"
            )


def validate_config_dict(data: dict) -> AppConfig:
    """Validate configuration dictionary and return AppConfig object."""
    if not isinstance(data, dict):
        raise ConfigError("Configuration root must be a JSON object")

    for req_key in REQUIRED_CONFIG_KEYS:
        if req_key not in data:
            raise ConfigError(f"Missing required configuration key: {req_key}")

    _validate_types(data)
    _validate_paths(data)

    return AppConfig(
        package_name=data[KEY_PACKAGE_NAME].strip(),
        repository_url=data[KEY_REPOSITORY_URL].strip(),
        test_mode=data[KEY_TEST_MODE],
        package_version=data[KEY_PACKAGE_VERSION].strip(),
        max_depth=data[KEY_MAX_DEPTH],
        filter_substring=data[KEY_FILTER_SUBSTRING],
    )


def load_config(filepath: str) -> AppConfig:
    """Read and parse configuration from specified JSON file."""
    if not os.path.isfile(filepath):
        raise ConfigError(f"Configuration file not found: {filepath}")

    try:
        with open(filepath, "r", encoding="utf-8") as handle:
            raw_data = json.load(handle)
    except json.JSONDecodeError as err:
        raise ConfigError(f"Invalid JSON syntax in {filepath}: {err}") from err

    return validate_config_dict(raw_data)
