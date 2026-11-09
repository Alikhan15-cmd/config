"""CLI entry point for dependency graph visualizer."""

import argparse
import sys
from src.config import ConfigError, load_config
from src.constants import (
    DEFAULT_CONFIG_PATH,
    EXIT_CODE_ERROR,
    EXIT_CODE_SUCCESS,
    ONE,
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


def main(argv=None) -> int:
    """Main CLI entry point."""
    parser = build_argument_parser()
    args = parser.parse_args(argv)

    try:
        if args.stage == ONE:
            return run_stage_one(args.config)
        print(f"Stage {args.stage} is not yet implemented.")
        return EXIT_CODE_SUCCESS
    except ConfigError as err:
        print(f"Config error: {err}", file=sys.stderr)
        return EXIT_CODE_ERROR
    except Exception as err:
        print(f"Unexpected error: {err}", file=sys.stderr)
        return EXIT_CODE_ERROR


if __name__ == "__main__":
    sys.exit(main())
