"""Unit tests for dependency collector module."""

import json
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from src.collector import (
    CollectorError,
    fetch_from_pypi,
    get_direct_dependencies,
    load_test_repository,
    normalize_package_name,
    parse_requirement_line,
)
from src.constants import ZERO


class TestCollector(unittest.TestCase):
    """Test suite for dependency collector functions."""

    def test_normalize_package_name(self):
        """Verify PEP 503 normalization rules."""
        self.assertEqual(normalize_package_name("Foo_Bar.Baz"), "foo-bar-baz")
        self.assertEqual(normalize_package_name("Requests"), "requests")

    def test_parse_requirement_standard(self):
        """Verify parsing standard requirement line."""
        pkg, is_extra = parse_requirement_line("urllib3<3,>=1.21.1")
        self.assertEqual(pkg, "urllib3")
        self.assertFalse(is_extra)

    def test_parse_requirement_with_extra(self):
        """Verify requirement with extra flag is detected."""
        line = 'PySocks!=1.5.7,>=1.5.6; extra == "socks"'
        pkg, is_extra = parse_requirement_line(line)
        self.assertEqual(pkg, "pysocks")
        self.assertTrue(is_extra)

    def test_parse_requirement_empty(self):
        """Verify empty lines return empty name."""
        pkg, is_extra = parse_requirement_line("   ")
        self.assertEqual(len(pkg), ZERO)
        self.assertFalse(is_extra)

    def test_load_test_repository_json(self):
        """Verify loading test repository from JSON format."""
        data = {"A": ["B", "C"], "B": ["D"]}
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as tmp:
            json.dump(data, tmp)
            tmp_path = tmp.name

        try:
            repo = load_test_repository(tmp_path)
            self.assertEqual(repo["A"], ["B", "C"])
            self.assertEqual(repo["B"], ["D"])
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_load_test_repository_text(self):
        """Verify loading test repository from text format."""
        content = "A: B, C\nB: D\n# comment\n"
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            repo = load_test_repository(tmp_path)
            self.assertEqual(repo["A"], ["B", "C"])
            self.assertEqual(repo["B"], ["D"])
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_get_direct_dependencies_test_mode(self):
        """Verify extracting direct dependencies in test mode."""
        repo_path = os.path.join("test_repos", "simple_repo.json")
        deps = get_direct_dependencies(
            package_name="A",
            version="1.0.0",
            repo_url=repo_path,
            test_mode=True,
        )
        self.assertEqual(deps, ["B", "C"])

    def test_get_direct_dependencies_missing_package(self):
        """Verify error when package is not in test repo."""
        repo_path = os.path.join("test_repos", "simple_repo.json")
        with self.assertRaises(CollectorError):
            get_direct_dependencies(
                package_name="UNKNOWN",
                version="1.0.0",
                repo_url=repo_path,
                test_mode=True,
            )

    @patch("urllib.request.urlopen")
    def test_fetch_from_pypi_mocked(self, mock_urlopen):
        """Verify parsing PyPI JSON response with mocked HTTP."""
        fake_payload = {
            "info": {
                "name": "requests",
                "version": "2.31.0",
                "requires_dist": [
                    "charset-normalizer<4,>=2",
                    "idna<4,>=2.5",
                    "urllib3<3,>=1.21.1",
                    'PySocks!=1.5.7,>=1.5.6; extra == "socks"',
                ],
            }
        }
        mock_response = MagicMock()
        mock_response.status = 200
        raw_json = json.dumps(fake_payload).encode("utf-8")
        mock_response.read.return_value = raw_json
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        deps = fetch_from_pypi("requests", "2.31.0")
        self.assertEqual(deps, ["charset-normalizer", "idna", "urllib3"])


if __name__ == "__main__":
    unittest.main()
