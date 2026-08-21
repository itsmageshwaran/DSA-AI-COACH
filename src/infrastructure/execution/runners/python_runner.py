"""Python code execution runner with AST analysis, process isolation, and test evaluation."""

from __future__ import annotations

import asyncio
import json
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

from src.infrastructure.execution.ast_analyzer import analyze_python_ast
from src.infrastructure.execution.runners.base import BaseRunner
from src.infrastructure.execution.schemas import (
    ExecutionResult,
    ExecutionStatus,
    TestCaseInput,
    TestCaseResult,
)


class PythonRunner(BaseRunner):
    """Python language execution runner."""

    @property
    def language(self) -> str:
        """Python language identifier."""
        return "python"

    async def run(
        self,
        code: str,
        test_cases: list[TestCaseInput],
        entrypoint: str | None = None,
        timeout_seconds: float = 2.0,
        memory_limit_mb: int = 512,
    ) -> ExecutionResult:
        """Execute Python code against test cases with static checks and subprocess isolation."""
        ast_result = analyze_python_ast(code)
        if not ast_result.is_valid:
            return self._handle_invalid_ast(ast_result, len(test_cases))

        selected_entrypoint = entrypoint
        if not selected_entrypoint and ast_result.function_names:
            selected_entrypoint = ast_result.function_names[0]

        if not selected_entrypoint:
            return ExecutionResult(
                status=ExecutionStatus.COMPILATION_ERROR,
                passed_count=0,
                total_count=len(test_cases),
                pass_rate=0.0,
                avg_runtime_ms=0.0,
                peak_memory_kb=0.0,
                test_results=[],
                ast_analysis=ast_result,
                compilation_output="No callable function definition found in submission.",
            )

        test_results: list[TestCaseResult] = []
        for idx, tc in enumerate(test_cases):
            tc_res = await self._run_single_test_case(
                code=code,
                entrypoint=selected_entrypoint,
                test_case=tc,
                test_index=idx,
                timeout_seconds=timeout_seconds,
            )
            test_results.append(tc_res)

        return self._aggregate_execution_results(test_results, len(test_cases), ast_result)

    def _handle_invalid_ast(self, ast_result: Any, total_count: int) -> ExecutionResult:
        """Handle invalid AST due to syntax error or forbidden import security violation."""
        if ast_result.syntax_error:
            return ExecutionResult(
                status=ExecutionStatus.COMPILATION_ERROR,
                passed_count=0,
                total_count=total_count,
                pass_rate=0.0,
                avg_runtime_ms=0.0,
                peak_memory_kb=0.0,
                test_results=[],
                ast_analysis=ast_result,
                compilation_output=ast_result.syntax_error,
            )
        forbidden_str = ", ".join(ast_result.forbidden_imports)
        return ExecutionResult(
            status=ExecutionStatus.SECURITY_VIOLATION,
            passed_count=0,
            total_count=total_count,
            pass_rate=0.0,
            avg_runtime_ms=0.0,
            peak_memory_kb=0.0,
            test_results=[],
            ast_analysis=ast_result,
            compilation_output=f"Security Violation: Forbidden imports or functions detected ({forbidden_str})",
        )

    def _aggregate_execution_results(
        self,
        test_results: list[TestCaseResult],
        total_count: int,
        ast_result: Any,
    ) -> ExecutionResult:
        """Aggregate testcase results into overall execution result."""
        runtimes: list[float] = [r.runtime_ms for r in test_results]
        memories: list[float] = [r.memory_kb for r in test_results]
        overall_status = ExecutionStatus.ACCEPTED

        for tc_res in test_results:
            if not tc_res.passed:
                if tc_res.status == ExecutionStatus.TIME_LIMIT_EXCEEDED and overall_status == ExecutionStatus.ACCEPTED:
                    overall_status = ExecutionStatus.TIME_LIMIT_EXCEEDED
                elif tc_res.status == ExecutionStatus.RUNTIME_ERROR and overall_status == ExecutionStatus.ACCEPTED:
                    overall_status = ExecutionStatus.RUNTIME_ERROR
                elif overall_status == ExecutionStatus.ACCEPTED:
                    overall_status = ExecutionStatus.WRONG_ANSWER

        passed_count = sum(1 for r in test_results if r.passed)
        pass_rate = (passed_count / total_count) if total_count > 0 else 1.0
        avg_runtime = (sum(runtimes) / len(runtimes)) if runtimes else 0.0
        peak_memory = max(memories) if memories else 0.0

        return ExecutionResult(
            status=overall_status,
            passed_count=passed_count,
            total_count=total_count,
            pass_rate=pass_rate,
            avg_runtime_ms=round(avg_runtime, 2),
            peak_memory_kb=round(peak_memory, 2),
            test_results=test_results,
            ast_analysis=ast_result,
        )

    async def _run_single_test_case(
        self,
        code: str,
        entrypoint: str,
        test_case: TestCaseInput,
        test_index: int,
        timeout_seconds: float,
    ) -> TestCaseResult:
        """Run a single testcase in an isolated python subprocess harness."""
        harness_script = self._build_harness_script(
            user_code=code,
            entrypoint=entrypoint,
            input_data=test_case.input_data,
        )

        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as temp_file:
            temp_file.write(harness_script)
            temp_path = temp_file.name

        start_time = time.perf_counter()
        try:
            process = await asyncio.create_subprocess_exec(
                sys.executable,
                temp_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout_seconds,
                )
                elapsed_ms = (time.perf_counter() - start_time) * 1000.0

                stdout_str = stdout_bytes.decode("utf-8", errors="replace").strip()
                stderr_str = stderr_bytes.decode("utf-8", errors="replace").strip()

                if process.returncode != 0:
                    return TestCaseResult(
                        test_case_index=test_index,
                        passed=False,
                        input_data=test_case.input_data,
                        expected_output=test_case.expected_output,
                        actual_output=None,
                        stdout=stdout_str,
                        stderr=stderr_str,
                        runtime_ms=round(elapsed_ms, 2),
                        memory_kb=0.0,
                        status=ExecutionStatus.RUNTIME_ERROR,
                        error_message=stderr_str or "Runtime Exception",
                        is_hidden=test_case.is_hidden,
                    )

                try:
                    payload = json.loads(stdout_str)
                    actual = payload.get("result")
                    user_stdout = payload.get("stdout", "")
                    user_stderr = payload.get("stderr", "")
                    memory_kb = float(payload.get("memory_kb", 0.0))

                    passed = actual == test_case.expected_output

                    return TestCaseResult(
                        test_case_index=test_index,
                        passed=passed,
                        input_data=test_case.input_data,
                        expected_output=test_case.expected_output,
                        actual_output=actual,
                        stdout=user_stdout,
                        stderr=user_stderr,
                        runtime_ms=round(elapsed_ms, 2),
                        memory_kb=round(memory_kb, 2),
                        status=ExecutionStatus.ACCEPTED if passed else ExecutionStatus.WRONG_ANSWER,
                        is_hidden=test_case.is_hidden,
                    )
                except json.JSONDecodeError:
                    return TestCaseResult(
                        test_case_index=test_index,
                        passed=False,
                        input_data=test_case.input_data,
                        expected_output=test_case.expected_output,
                        actual_output=stdout_str,
                        stdout=stdout_str,
                        stderr=stderr_str,
                        runtime_ms=round(elapsed_ms, 2),
                        memory_kb=0.0,
                        status=ExecutionStatus.RUNTIME_ERROR,
                        error_message="Invalid execution output payload",
                        is_hidden=test_case.is_hidden,
                    )

            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return TestCaseResult(
                    test_case_index=test_index,
                    passed=False,
                    input_data=test_case.input_data,
                    expected_output=test_case.expected_output,
                    actual_output=None,
                    stdout="",
                    stderr="Time Limit Exceeded",
                    runtime_ms=timeout_seconds * 1000.0,
                    memory_kb=0.0,
                    status=ExecutionStatus.TIME_LIMIT_EXCEEDED,
                    error_message=f"Execution timed out after {timeout_seconds}s",
                    is_hidden=test_case.is_hidden,
                )
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def _build_harness_script(
        self,
        user_code: str,
        entrypoint: str,
        input_data: Any,
    ) -> str:
        """Construct isolated Python runner harness wrapping user code."""
        input_json = json.dumps(input_data)
        return (
            f"import sys\n"
            f"import io\n"
            f"import json\n"
            f"import tracemalloc\n\n"
            f"{user_code}\n\n"
            f"def __run_harness__():\n"
            f"    input_val = json.loads({repr(input_json)})\n"
            f"    old_stdout = sys.stdout\n"
            f"    old_stderr = sys.stderr\n"
            f"    captured_stdout = io.StringIO()\n"
            f"    captured_stderr = io.StringIO()\n"
            f"    sys.stdout = captured_stdout\n"
            f"    sys.stderr = captured_stderr\n"
            f"    tracemalloc.start()\n"
            f"    try:\n"
            f"        fn = globals()['{entrypoint}']\n"
            f"        if isinstance(input_val, dict):\n"
            f"            res = fn(**input_val)\n"
            f"        elif isinstance(input_val, list):\n"
            f"            res = fn(*input_val)\n"
            f"        else:\n"
            f"            res = fn(input_val)\n"
            f"        current, peak = tracemalloc.get_traced_memory()\n"
            f"        tracemalloc.stop()\n"
            f"        sys.stdout = old_stdout\n"
            f"        sys.stderr = old_stderr\n"
            f"        output_payload = {{\n"
            f"            'result': res,\n"
            f"            'stdout': captured_stdout.getvalue(),\n"
            f"            'stderr': captured_stderr.getvalue(),\n"
            f"            'memory_kb': round(peak / 1024.0, 2)\n"
            f"        }}\n"
            f"        print(json.dumps(output_payload))\n"
            f"    except Exception as exc:\n"
            f"        tracemalloc.stop()\n"
            f"        sys.stdout = old_stdout\n"
            f"        sys.stderr = old_stderr\n"
            f"        sys.stderr.write(str(exc))\n"
            f"        sys.exit(1)\n\n"
            f"if __name__ == '__main__':\n"
            f"    __run_harness__()\n"
        )
