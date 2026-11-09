"""CLI entry point for dependency graph visualizer."""

import argparse
import sys
from src.collector import CollectorError, get_direct_dependencies
from src.config import ConfigError, load_config
from src.constants import (
    DEFAULT_CONFIG_PATH,
    EXIT_CODE_ERROR,
    EXIT_CODE_SUCCESS,
    ONE,
    TWO,
    ZERO,
)


def build_argument_parser() -> argparse.ArgumentParser:
    """Construct command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Dependency Graph Visualizer for Python packages (pip)"
    )
    parser.add_argument(
        "--config",
        "-c",
        default=DEFAULT_CONFIG_PATH,
        help="Path to JSON configuration file (default: config.json)",
    )
    parser.add_argument(
        "--stage",
        "-s",
        type=int,
        default=ONE,
        choices=[1, 2, 3, 4, 5],
        help="Target stage to execute (1..5, default: 1)",
    )
    return parser


def run_stage_one(config_path: str) -> int:
    """Execute Stage 1: load config and display parameters."""
    config = load_config(config_path)
    print("=== Этап 1. Параметры конфигурации ===")
    print(config.format_key_value())
    return EXIT_CODE_SUCCESS


def run_stage_two(config_path: str) -> int:
    """Execute Stage 2: display direct dependencies."""
    config = load_config(config_path)
    deps = get_direct_dependencies(
        package_name=config.package_name,
        version=config.package_version,
        repo_url=config.repository_url,
        test_mode=config.test_mode,
    )
    header = (
        f"=== Этап 2. Прямые зависимости пакета "
        f"{config.package_name} ({config.package_version}) ==="
    )
    print(header)
    if len(deps) == ZERO:
        print("Прямые зависимости отсутствуют.")
    else:
        for dep in deps:
            print(f"- {dep}")
    return EXIT_CODE_SUCCESS


def main(argv=None) -> int:
    """Main CLI entry point."""
    parser = build_argument_parser()
    args = parser.parse_args(argv)

    try:
        if args.stage == ONE:
            return run_stage_one(args.config)
        if args.stage == TWO:
            return run_stage_two(args.config)
        print(f"Stage {args.stage} is not yet implemented.")
        return EXIT_CODE_SUCCESS
    except (ConfigError, CollectorError) as err:
        print(f"Error: {err}", file=sys.stderr)
        return EXIT_CODE_ERROR
    except Exception as err:
        print(f"Unexpected error: {err}", file=sys.stderr)
        return EXIT_CODE_ERROR


if __name__ == "__main__":
    sys.exit(main())
