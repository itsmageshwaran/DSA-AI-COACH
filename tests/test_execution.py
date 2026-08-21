"""Unit and integration test suite for AST Analyzer, Python Runner, Execution Engine, and Execution APIs."""

from __future__ import annotations

import pytest
from fastapi import status
from httpx import AsyncClient

from src.domain.learning.models import Course, Exercise, Lesson, Module
from src.infrastructure.database.session import AsyncSessionFactory
from src.infrastructure.execution.ast_analyzer import analyze_python_ast
from src.infrastructure.execution.engine import execution_engine
from src.infrastructure.execution.runners.python_runner import PythonRunner
from src.infrastructure.execution.schemas import ExecutionStatus, TestCaseInput


def test_ast_analyzer_valid_code() -> None:
    """Verify AST analyzer parses valid Python code and calculates nesting depth and recursion."""
    code = """
def factorial(n):
    if n <= 1:
        return 1
    total = 0
    for i in range(1, n):
        for j in range(1, n):
            total += i * j
    return n * factorial(n - 1)
"""
    result = analyze_python_ast(code)
    assert result.is_valid is True
    assert result.syntax_error is None
    assert result.forbidden_imports == []
    assert result.nesting_depth == 2
    assert result.has_recursion is True
    assert "factorial" in result.function_names


def test_ast_analyzer_forbidden_import() -> None:
    """Verify AST analyzer catches forbidden imports and builtins."""
    code = """
import os
import sys

def malicious():
    eval("print('hack')")
    open('/etc/passwd')
"""
    result = analyze_python_ast(code)
    assert result.is_valid is False
    assert any("os" in imp for imp in result.forbidden_imports)
    assert any("sys" in imp for imp in result.forbidden_imports)
    assert any("eval" in imp for imp in result.forbidden_imports)


def test_ast_analyzer_syntax_error() -> None:
    """Verify AST analyzer detects invalid Python syntax."""
    code = "def broken_func("
    result = analyze_python_ast(code)
    assert result.is_valid is False
    assert result.syntax_error is not None
    assert "SyntaxError" in result.syntax_error


@pytest.mark.anyio
async def test_python_runner_success() -> None:
    """Verify PythonRunner executes valid code and accepts correct test cases."""
    runner = PythonRunner()
    code = """
def two_sum(a, b):
    print("Computing sum...")
    return a + b
"""
    test_cases = [
        TestCaseInput(input_data=[2, 3], expected_output=5),
        TestCaseInput(input_data=[-1, 1], expected_output=0),
    ]

    res = await runner.run(code=code, test_cases=test_cases)
    assert res.status == ExecutionStatus.ACCEPTED
    assert res.passed_count == 2
    assert res.total_count == 2
    assert res.pass_rate == 1.0
    assert res.test_results[0].stdout.strip() == "Computing sum..."


@pytest.mark.anyio
async def test_python_runner_wrong_answer() -> None:
    """Verify PythonRunner detects wrong answers."""
    runner = PythonRunner()
    code = """
def add(a, b):
    return a * b
"""
    test_cases = [
        TestCaseInput(input_data=[2, 3], expected_output=5),
    ]

    res = await runner.run(code=code, test_cases=test_cases)
    assert res.status == ExecutionStatus.WRONG_ANSWER
    assert res.passed_count == 0
    assert res.pass_rate == 0.0


@pytest.mark.anyio
async def test_python_runner_runtime_error() -> None:
    """Verify PythonRunner catches unhandled runtime exceptions."""
    runner = PythonRunner()
    code = """
def divide(a, b):
    return a / b
"""
    test_cases = [
        TestCaseInput(input_data=[10, 0], expected_output=0),
    ]

    res = await runner.run(code=code, test_cases=test_cases)
    assert res.status == ExecutionStatus.RUNTIME_ERROR
    assert "zero" in (res.test_results[0].error_message or "").lower()


@pytest.mark.anyio
async def test_python_runner_security_violation() -> None:
    """Verify PythonRunner rejects forbidden import code with SECURITY_VIOLATION."""
    runner = PythonRunner()
    code = """
import subprocess

def run_cmd():
    subprocess.run(["ls"])
"""
    test_cases = [TestCaseInput(input_data=[], expected_output=None)]
    res = await runner.run(code=code, test_cases=test_cases)
    assert res.status == ExecutionStatus.SECURITY_VIOLATION


@pytest.mark.anyio
async def test_python_runner_time_limit_exceeded() -> None:
    """Verify PythonRunner terminates infinite loops and returns TIME_LIMIT_EXCEEDED."""
    runner = PythonRunner()
    code = """
def infinite_loop(n):
    while True:
        pass
"""
    test_cases = [TestCaseInput(input_data=[5], expected_output=5)]
    res = await runner.run(code=code, test_cases=test_cases, timeout_seconds=0.5)
    assert res.status == ExecutionStatus.TIME_LIMIT_EXCEEDED


@pytest.mark.anyio
async def test_execution_engine_dispatcher() -> None:
    """Verify ExecutionEngine dispatches to registered language runners."""
    langs = execution_engine.get_supported_languages()
    assert "python" in langs
    assert "javascript" in langs
    assert "cpp" in langs

    # Dispatch python
    code = "def solution(x):\n    return x * 2\n"
    res = await execution_engine.run_code(
        code=code,
        language="python",
        test_cases=[TestCaseInput(input_data=[4], expected_output=8)],
    )
    assert res.status == ExecutionStatus.ACCEPTED

    # Invalid language raises ValueError
    with pytest.raises(ValueError, match="Unsupported language"):
        await execution_engine.run_code(
            code=code,
            language="brainfuck",
            test_cases=[],
        )


@pytest.mark.anyio
async def test_execution_api_run(auth_client: AsyncClient) -> None:
    """Verify POST /api/v1/execution/run evaluates code."""
    payload = {
        "code": "def solve(arr):\n    return sum(arr)\n",
        "language": "python",
        "test_cases": [
            {"input_data": [[1, 2, 3]], "expected_output": 6},
            {"input_data": [[]], "expected_output": 0},
        ],
    }
    response = await auth_client.post("/api/v1/execution/run", json=payload)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "execution" in data
    exec_data = data["execution"]
    assert exec_data["status"] == "ACCEPTED"
    assert exec_data["passed_count"] == 2
    assert exec_data["pass_rate"] == 1.0


@pytest.mark.anyio
async def test_execution_api_submit(
    client: AsyncClient,
) -> None:
    """Verify POST /api/v1/execution/submit evaluates submission and updates learner progress."""
    user_reg = {"email": "exec_user@example.com", "password": "Password123"}
    await client.post("/api/v1/auth/register", json=user_reg)
    login_res = await client.post("/api/v1/auth/login", json=user_reg)
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    async with AsyncSessionFactory() as db_session:
        course = Course(title="Algorithms 101", description="Intro to Algorithmic thinking")
        db_session.add(course)
        await db_session.commit()
        await db_session.refresh(course)

        module = Module(title="Arrays", course_id=course.id)
        db_session.add(module)
        await db_session.commit()
        await db_session.refresh(module)

        lesson = Lesson(title="Two Sum", content="Find pair summing to target", module_id=module.id)
        db_session.add(lesson)
        await db_session.commit()
        await db_session.refresh(lesson)

        exercise = Exercise(
            title="Sum Pair",
            instructions="Implement add(a, b)",
            starter_code="def add(a, b):\n    pass",
            lesson_id=lesson.id,
        )
        db_session.add(exercise)
        await db_session.commit()
        await db_session.refresh(exercise)
        exercise_id = exercise.id

    payload = {
        "exercise_id": exercise_id,
        "code": "def add(a, b):\n    return a + b\n",
        "language": "python",
    }

    response = await client.post("/api/v1/execution/submit", json=payload, headers=headers)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "submission_id" in data
    assert data["exercise_id"] == exercise_id
    assert data["status"] == "accepted"
    assert data["progress_updated"] is True
    assert data["execution"]["status"] == "ACCEPTED"
