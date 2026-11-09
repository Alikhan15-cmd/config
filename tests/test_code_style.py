"""Tests for project code style compliance."""

import ast
import os
import unittest
from src.constants import (
    MAX_LINE_LENGTH,
    MAX_FUNCTION_LINES,
    MAX_FUNCTION_ARGS,
    ZERO,
)


class TestCodeStyle(unittest.TestCase):
    """Test verification of code style rules."""

    def get_py_files(self):
        """Collect all python files in src and tests directories."""
        py_files = []
        for root_dir in ("src", "tests"):
            for dirpath, _, filenames in os.walk(root_dir):
                for filename in filenames:
                    if filename.endswith(".py"):
                        py_files.append(os.path.join(dirpath, filename))
        return py_files

    def test_line_length(self):
        """Ensure no line in any Python file exceeds 80 characters."""
        violations = []
        for filepath in self.get_py_files():
            with open(filepath, "r", encoding="utf-8") as handle:
                for idx, line in enumerate(handle, start=1):
                    raw = line.rstrip("\r\n")
                    if len(raw) > MAX_LINE_LENGTH:
                        msg = f"{filepath}:{idx} (len={len(raw)})"
                        violations.append(msg)
        self.assertEqual(len(violations), ZERO, str(violations))

    def test_function_length_and_arguments(self):
        """Ensure functions do not exceed maximum lines and arguments."""
        length_violations = []
        arg_violations = []

        for filepath in self.get_py_files():
            with open(filepath, "r", encoding="utf-8") as handle:
                tree = ast.parse(handle.read(), filename=filepath)

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    func_len = (node.end_lineno - node.lineno) + 1
                    if func_len > MAX_FUNCTION_LINES:
                        name = node.name
                        length_violations.append(
                            f"{filepath}:{node.lineno} {name}:{func_len}"
                        )
                    arg_count = len(node.args.args)
                    if arg_count > MAX_FUNCTION_ARGS:
                        name = node.name
                        arg_violations.append(
                            f"{filepath}:{node.lineno} {name}:{arg_count}"
                        )

        self.assertEqual(len(length_violations), ZERO, str(length_violations))
        self.assertEqual(len(arg_violations), ZERO, str(arg_violations))


if __name__ == "__main__":
    unittest.main()
