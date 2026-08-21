"""Code intelligence and sandbox execution agent tools."""

from __future__ import annotations

from typing import Any

from src.infrastructure.agents.tools.base import BaseTool, ToolResult
from src.infrastructure.execution.ast_analyzer import analyze_python_ast
from src.infrastructure.execution.engine import execution_engine
from src.infrastructure.execution.schemas import ExecutionStatus, TestCaseInput


class ExecuteCodeTool(BaseTool):
    """Tool executing user code inside isolated process sandbox."""

    @property
    def name(self) -> str:
        """Tool name identifier."""
        return "execute_code"

    @property
    def description(self) -> str:
        """Tool description."""
        return "Executes source code in isolated sandbox process and returns stdout, stderr, and execution status."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        """Tool JSON schema parameters."""
        return {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Source code text to execute"},
                "language": {"type": "string", "description": "Programming language (default 'python')"},
            },
            "required": ["code"],
        }

    async def execute(self, **kwargs: Any) -> ToolResult:
        """Execute sandbox code runner."""
        code = str(kwargs.get("code", ""))
        language = str(kwargs.get("language", "python"))

        try:
            res = await execution_engine.run_code(code=code, language=language, test_cases=[])
            stdout = res.test_results[0].stdout if res.test_results else ""
            stderr = res.test_results[0].stderr if res.test_results else ""
            err_msg = res.test_results[0].error_message if res.test_results else res.compilation_output

            return ToolResult(
                tool_name=self.name,
                success=res.status == ExecutionStatus.ACCEPTED,
                data={
                    "status": res.status.value,
                    "stdout": stdout,
                    "stderr": stderr,
                    "execution_time_ms": res.avg_runtime_ms,
                    "peak_memory_kb": res.peak_memory_kb,
                },
                error=err_msg if res.status != ExecutionStatus.ACCEPTED else None,
            )
        except Exception as e:
            return ToolResult(tool_name=self.name, success=False, error=str(e))


class InspectASTTool(BaseTool):
    """Tool performing static AST analysis and security checks."""

    @property
    def name(self) -> str:
        """Tool name identifier."""
        return "inspect_ast"

    @property
    def description(self) -> str:
        """Tool description."""
        return "Statically parses Python AST to audit dangerous imports, function recursion, and loop nesting depth."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        """Tool JSON schema parameters."""
        return {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Python source code text to inspect"},
            },
            "required": ["code"],
        }

    async def execute(self, **kwargs: Any) -> ToolResult:
        """Execute static AST analysis."""
        code = str(kwargs.get("code", ""))
        ast_res = analyze_python_ast(code)
        is_safe = len(ast_res.forbidden_imports) == 0
        return ToolResult(
            tool_name=self.name,
            success=ast_res.is_valid and is_safe,
            data={
                "is_valid_syntax": ast_res.is_valid,
                "is_safe": is_safe,
                "syntax_error": ast_res.syntax_error,
                "forbidden_imports": ast_res.forbidden_imports,
                "max_loop_nesting_depth": ast_res.nesting_depth,
                "function_names": ast_res.function_names,
                "is_recursive": ast_res.has_recursion,
            },
            error="AST Security Violation" if not is_safe else None,
        )


class EvaluateTestCasesTool(BaseTool):
    """Tool evaluating code submission against a set of input/output test cases."""

    @property
    def name(self) -> str:
        """Tool name identifier."""
        return "evaluate_test_cases"

    @property
    def description(self) -> str:
        """Tool description."""
        return "Runs code submission against multiple test cases and reports pass/fail ratio."

    @property
    def parameters_schema(self) -> dict[str, Any]:
        """Tool JSON schema parameters."""
        return {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Python source code"},
                "test_cases": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "input_data": {"type": "string"},
                            "expected_output": {"type": "string"},
                        },
                    },
                },
            },
            "required": ["code", "test_cases"],
        }

    async def execute(self, **kwargs: Any) -> ToolResult:
        """Execute test cases runner."""
        code = str(kwargs.get("code", ""))
        raw_cases = kwargs.get("test_cases", [])

        test_case_objs = [
            TestCaseInput(
                input_data=c.get("input_data", ""),
                expected_output=c.get("expected_output", ""),
            )
            for c in raw_cases
        ]

        try:
            res = await execution_engine.run_code(code=code, language="python", test_cases=test_case_objs)
            return ToolResult(
                tool_name=self.name,
                success=res.status == ExecutionStatus.ACCEPTED,
                data={
                    "status": res.status.value,
                    "total_test_cases": res.total_count,
                    "passed_test_cases": res.passed_count,
                    "pass_ratio": res.pass_rate,
                },
            )
        except Exception as e:
            return ToolResult(tool_name=self.name, success=False, error=str(e))
