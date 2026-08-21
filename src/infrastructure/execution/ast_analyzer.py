"""AST Static Code Analyzer and Security Guard."""

from __future__ import annotations

import ast

from src.infrastructure.execution.schemas import ASTAnalysisResult

FORBIDDEN_MODULES: set[str] = {
    "os",
    "sys",
    "subprocess",
    "socket",
    "shutil",
    "importlib",
    "builtins",
    "ctypes",
    "multiprocessing",
    "threading",
    "asyncio",
    "signal",
    "tempfile",
    "pathlib",
}

FORBIDDEN_FUNCTIONS: set[str] = {
    "eval",
    "exec",
    "open",
    "__import__",
    "compile",
    "globals",
    "locals",
    "input",
}


class ASTVisitor(ast.NodeVisitor):
    """AST visitor traversing nodes to collect metrics and detect forbidden constructs."""

    def __init__(self) -> None:
        self.forbidden_imports: list[str] = []
        self.max_nesting_depth: int = 0
        self.current_nesting_depth: int = 0
        self.function_names: list[str] = []
        self.called_functions: list[str] = []

    def visit_Import(self, node: ast.Import) -> None:
        """Inspect import statements."""
        for alias in node.names:
            module_base = alias.name.split(".")[0]
            if module_base in FORBIDDEN_MODULES:
                self.forbidden_imports.append(module_base)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Inspect import from statements."""
        if node.module:
            module_base = node.module.split(".")[0]
            if module_base in FORBIDDEN_MODULES:
                self.forbidden_imports.append(module_base)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Inspect function call nodes."""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            self.called_functions.append(func_name)
            if func_name in FORBIDDEN_FUNCTIONS:
                self.forbidden_imports.append(f"builtin:{func_name}")
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Inspect function definitions."""
        self.function_names.append(node.name)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Inspect async function definitions."""
        self.function_names.append(node.name)
        self.generic_visit(node)

    def _visit_loop(self, node: ast.For | ast.AsyncFor | ast.While) -> None:
        self.current_nesting_depth += 1
        if self.current_nesting_depth > self.max_nesting_depth:
            self.max_nesting_depth = self.current_nesting_depth
        self.generic_visit(node)
        self.current_nesting_depth -= 1

    def visit_For(self, node: ast.For) -> None:
        """Inspect for loop nodes."""
        self._visit_loop(node)

    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        """Inspect async for loop nodes."""
        self._visit_loop(node)

    def visit_While(self, node: ast.While) -> None:
        """Inspect while loop nodes."""
        self._visit_loop(node)


def analyze_python_ast(code: str) -> ASTAnalysisResult:
    """Perform static AST code analysis and security inspection on Python code."""
    try:
        parsed_ast = ast.parse(code)
    except SyntaxError as err:
        return ASTAnalysisResult(
            is_valid=False,
            syntax_error=f"SyntaxError on line {err.lineno}: {err.msg}",
        )

    visitor = ASTVisitor()
    visitor.visit(parsed_ast)

    # Detect recursion if any function name is called inside the AST
    has_recursion = any(fn in visitor.called_functions for fn in visitor.function_names)

    is_valid = len(visitor.forbidden_imports) == 0

    return ASTAnalysisResult(
        is_valid=is_valid,
        syntax_error=None,
        forbidden_imports=list(set(visitor.forbidden_imports)),
        nesting_depth=visitor.max_nesting_depth,
        has_recursion=has_recursion,
        function_names=visitor.function_names,
    )
