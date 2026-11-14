"""Code style and quality compliance verification tests."""

import ast
import os
import re
import tokenize
import unittest
from src.constants import (
    MAX_CYCLOMATIC_COMPLEXITY,
    MAX_FUNCTION_ARGS,
    MAX_FUNCTION_LINES,
    MAX_LINE_LENGTH,
    ZERO,
)

BASE_COMPLEXITY = 1
SNAKE_CASE_REGEX = r"^_{0,2}[a-z][a-z0-9_]*$"


def _calc_complexity(node: ast.AST) -> int:
    """Calculate cyclomatic complexity of an AST node."""
    complexity = BASE_COMPLEXITY
    for child in ast.walk(node):
        if isinstance(
            child,
            (
                ast.If,
                ast.While,
                ast.For,
                ast.AsyncFor,
                ast.ExceptHandler,
                ast.With,
                ast.AsyncWith,
            ),
        ):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            complexity += len(child.values) - 1
    return complexity


def _check_import_aliases(
    tree: ast.AST, path: str, pattern: re.Pattern
) -> list[str]:
    """Check that module import aliases follow snake_case."""
    errors = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.asname and not pattern.match(alias.asname):
                    msg = (
                        f"Alias '{alias.asname}' in {path}:{node.lineno} "
                        "is not snake_case"
                    )
                    errors.append(msg)
    return errors


class TestCodeStyle(unittest.TestCase):
    """Test verification of code style rules."""

    def get_py_files(self) -> list[str]:
        """Collect all python files in src and tests directories."""
        py_files = []
        for root_dir in ("src", "tests"):
            for dirpath, _, filenames in os.walk(root_dir):
                for filename in filenames:
                    if filename.endswith(".py"):
                        py_files.append(os.path.join(dirpath, filename))
        return py_files

    def test_line_length(self):
        """Ensure no line in any Python file exceeds 80 characters (P2)."""
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
        doc_violations = []

        for filepath in self.get_py_files():
            with open(filepath, "r", encoding="utf-8") as handle:
                tree = ast.parse(handle.read(), filename=filepath)

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    func_len = (node.end_lineno - node.lineno) + 1
                    if func_len > MAX_FUNCTION_LINES:
                        length_violations.append(
                            f"{filepath}:{node.lineno} {node.name}:{func_len}"
                        )
                    total_args = (
                        len(node.args.args)
                        + len(node.args.posonlyargs)
                        + len(node.args.kwonlyargs)
                    )
                    if total_args > MAX_FUNCTION_ARGS:
                        arg_violations.append(
                            f"{filepath}:{node.lineno} {node.name}:{total_args}"
                        )
                    doc = ast.get_docstring(node)
                    if not doc:
                        doc_violations.append(
                            f"{filepath}:{node.lineno} {node.name}"
                        )

        self.assertEqual(len(length_violations), ZERO, str(length_violations))
        self.assertEqual(len(arg_violations), ZERO, str(arg_violations))
        self.assertEqual(len(doc_violations), ZERO, str(doc_violations))

    def test_cyclomatic_complexity(self):
        """Rule C1: Cyclomatic complexity must not exceed 10."""
        violations = []
        for filepath in self.get_py_files():
            with open(filepath, "r", encoding="utf-8") as handle:
                tree = ast.parse(handle.read(), filename=filepath)

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    complexity = _calc_complexity(node)
                    if complexity > MAX_CYCLOMATIC_COMPLEXITY:
                        violations.append(
                            f"{filepath}:{node.lineno} {node.name}:{complexity}"
                        )
        self.assertEqual(len(violations), ZERO, str(violations))

    def test_no_magic_numbers_in_comparisons(self):
        """Rule M1: Code must not use raw numeric literals in comparisons."""
        violations = []
        for filepath in self.get_py_files():
            with open(filepath, "r", encoding="utf-8") as handle:
                tree = ast.parse(handle.read(), filename=filepath)

            for node in ast.walk(tree):
                if isinstance(node, ast.Compare):
                    operands = [node.left] + node.comparators
                    for item in operands:
                        if isinstance(item, ast.Constant) and isinstance(
                            item.value, (int, float)
                        ):
                            violations.append(
                                f"{filepath}:{node.lineno} val={item.value}"
                            )
        self.assertEqual(len(violations), ZERO, str(violations))

    def test_no_inline_comments(self):
        """Rule K1: Code must not use comments instead of docstrings."""
        violations = []
        for filepath in self.get_py_files():
            with open(filepath, "rb") as handle:
                tokens = tokenize.tokenize(handle.readline)
                for tok in tokens:
                    if tok.type == tokenize.COMMENT:
                        violations.append(f"{filepath}:{tok.start[0]}")
        self.assertEqual(len(violations), ZERO, str(violations))

    def test_pep8_naming(self):
        """Rule I1: Module import aliases must follow snake_case."""
        pattern = re.compile(SNAKE_CASE_REGEX)
        for filepath in self.get_py_files():
            with open(filepath, "r", encoding="utf-8") as handle:
                tree = ast.parse(handle.read(), filename=filepath)
            errors = _check_import_aliases(tree, filepath, pattern)
            self.assertEqual(len(errors), ZERO, str(errors))


if __name__ == "__main__":
    unittest.main()
