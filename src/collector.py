"""Dependency data collector for Python pip packages."""

import json
import os
import re
import urllib.error
import urllib.request
from src.constants import (
    DEFAULT_PYPI_URL,
    HTTP_STATUS_OK,
    REQUEST_TIMEOUT_SEC,
    ZERO,
)

REQ_NAME_PATTERN = re.compile(r"^([a-zA-Z0-9_\-\.]+)")
EXTRA_PATTERN = re.compile(r"""extra\s*==\s*['"][^'"]+['"]""")


class CollectorError(RuntimeError):
    """Exception raised when dependency data cannot be collected."""


def normalize_package_name(name: str) -> str:
    """Normalize package name according to PEP 503."""
    return re.sub(r"[-_.]+", "-", name).lower()


def parse_requirement_line(req_line: str) -> tuple[str, bool]:
    """Parse PEP 508 requirement line into name and extra-flag."""
    clean_line = req_line.strip()
    if len(clean_line) == ZERO:
        return "", False

    is_extra = bool(EXTRA_PATTERN.search(clean_line))
    match = REQ_NAME_PATTERN.match(clean_line)
    if not match:
        return "", False

    raw_name = match.group(1)
    return normalize_package_name(raw_name), is_extra


def _build_pypi_url(package_name: str, version: str, base_url: str) -> str:
    """Construct PyPI JSON API endpoint URL."""
    clean_base = base_url.rstrip("/")
    if len(version.strip()) == ZERO or version.strip() == "*":
        return f"{clean_base}/{package_name}/json"
    return f"{clean_base}/{package_name}/{version}/json"


def _read_pypi_json(url: str) -> dict:
    """Execute HTTP GET request and parse PyPI JSON payload."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "DependencyVisualizer/1.0"},
    )
    try:
        with urllib.request.urlopen(
            req, timeout=REQUEST_TIMEOUT_SEC
        ) as response:
            if response.status != HTTP_STATUS_OK:
                raise CollectorError(
                    f"HTTP response error {response.status} from {url}"
                )
            content = response.read().decode("utf-8")
            return json.loads(content)
    except urllib.error.HTTPError as err:
        raise CollectorError(
            f"PyPI HTTP error {err.code} for {url}: {err.reason}"
        ) from err
    except urllib.error.URLError as err:
        raise CollectorError(
            f"Network error accessing {url}: {err.reason}"
        ) from err


def load_test_repository(repo_path: str) -> dict[str, list[str]]:
    """Parse test repository file in JSON or key-value format."""
    if not os.path.isfile(repo_path):
        raise CollectorError(f"Test repository file not found: {repo_path}")

    with open(repo_path, "r", encoding="utf-8") as handle:
        content = handle.read().strip()

    if content.startswith("{"):
        try:
            raw_data = json.loads(content)
            return {
                str(k).strip(): [str(dep).strip() for dep in v]
                for k, v in raw_data.items()
            }
        except json.JSONDecodeError as err:
            raise CollectorError(f"Malformed test repo JSON: {err}") from err

    result = {}
    for line in content.splitlines():
        trimmed = line.strip()
        if len(trimmed) == ZERO or trimmed.startswith("#"):
            continue
        if ":" in trimmed:
            key, deps_str = trimmed.split(":", 1)
            deps = [d.strip() for d in deps_str.split(",") if d.strip()]
            result[key.strip()] = deps
    return result


def fetch_from_pypi(
    package_name: str,
    version: str,
    repo_url: str = DEFAULT_PYPI_URL,
) -> list[str]:
    """Retrieve direct runtime dependencies from PyPI API."""
    url = _build_pypi_url(package_name, version, repo_url)
    payload = _read_pypi_json(url)

    info = payload.get("info", {})
    raw_requires = info.get("requires_dist")
    if not raw_requires:
        return []

    direct_deps = set()
    for req_item in raw_requires:
        pkg, is_extra = parse_requirement_line(req_item)
        if len(pkg) > ZERO and not is_extra:
            direct_deps.add(pkg)

    return sorted(direct_deps)


def get_direct_dependencies(
    package_name: str,
    version: str,
    repo_url: str,
    test_mode: bool,
) -> list[str]:
    """Obtain direct dependencies in either real or test mode."""
    if test_mode:
        repo = load_test_repository(repo_url)
        norm_name = package_name.strip()
        if norm_name not in repo:
            raise CollectorError(
                f"Package '{norm_name}' not found in test repository"
            )
        return sorted(set(repo[norm_name]))

    return fetch_from_pypi(package_name, version, repo_url)
