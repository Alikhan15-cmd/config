"""Unit tests for configuration loading and validation."""

import json
import os
import tempfile
import unittest

from src.config import AppConfig, ConfigError, load_config, validate_config_dict
from src.constants import (
    KEY_FILTER_SUBSTRING,
    KEY_MAX_DEPTH,
    KEY_PACKAGE_NAME,
    KEY_PACKAGE_VERSION,
    KEY_REPOSITORY_URL,
    KEY_TEST_MODE,
)


class TestConfig(unittest.TestCase):
    """Test cases for AppConfig validation and loading."""

    def setUp(self):
        """Prepare valid config fixture."""
        self.valid_data = {
            KEY_PACKAGE_NAME: "requests",
            KEY_REPOSITORY_URL: "https://pypi.org/pypi",
            KEY_TEST_MODE: False,
            KEY_PACKAGE_VERSION: "2.31.0",
            KEY_MAX_DEPTH: 3,
            KEY_FILTER_SUBSTRING: "test",
        }

    def test_valid_config(self):
        """Ensure valid dictionary parses into AppConfig."""
        config = validate_config_dict(self.valid_data)
        self.assertIsInstance(config, AppConfig)
        self.assertEqual(config.package_name, "requests")
        self.assertEqual(config.max_depth, 3)
        self.assertFalse(config.test_mode)

    def test_format_key_value(self):
        """Check key-value format representation."""
        config = validate_config_dict(self.valid_data)
        text = config.format_key_value()
        self.assertIn("package_name: requests", text)
        self.assertIn("max_depth: 3", text)

    def test_missing_key(self):
        """Ensure missing keys trigger ConfigError."""
        invalid_data = dict(self.valid_data)
        del invalid_data[KEY_PACKAGE_NAME]
        with self.assertRaises(ConfigError):
            validate_config_dict(invalid_data)

    def test_empty_package_name(self):
        """Ensure blank package name triggers ConfigError."""
        invalid_data = dict(self.valid_data)
        invalid_data[KEY_PACKAGE_NAME] = "   "
        with self.assertRaises(ConfigError):
            validate_config_dict(invalid_data)

    def test_negative_depth(self):
        """Ensure negative depth triggers ConfigError."""
        invalid_data = dict(self.valid_data)
        invalid_data[KEY_MAX_DEPTH] = -1
        with self.assertRaises(ConfigError):
            validate_config_dict(invalid_data)

    def test_invalid_depth_type(self):
        """Ensure non-integer depth triggers ConfigError."""
        invalid_data = dict(self.valid_data)
        invalid_data[KEY_MAX_DEPTH] = "3"
        with self.assertRaises(ConfigError):
            validate_config_dict(invalid_data)

    def test_invalid_test_mode_type(self):
        """Ensure non-bool test_mode triggers ConfigError."""
        invalid_data = dict(self.valid_data)
        invalid_data[KEY_TEST_MODE] = "true"
        with self.assertRaises(ConfigError):
            validate_config_dict(invalid_data)

    def test_load_config_from_file(self):
        """Ensure JSON file loads cleanly."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as tmp:
            json.dump(self.valid_data, tmp)
            tmp_path = tmp.name

        try:
            config = load_config(tmp_path)
            self.assertEqual(config.package_name, "requests")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_load_nonexistent_file(self):
        """Ensure missing file triggers ConfigError."""
        with self.assertRaises(ConfigError):
            load_config("nonexistent_config_file_123.json")

    def test_load_invalid_json(self):
        """Ensure syntax error in JSON triggers ConfigError."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write("{invalid_json:")
            tmp_path = tmp.name

        try:
            with self.assertRaises(ConfigError):
                load_config(tmp_path)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


if __name__ == "__main__":
    unittest.main()
