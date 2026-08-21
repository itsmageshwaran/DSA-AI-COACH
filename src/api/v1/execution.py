"""FastAPI router for code execution and exercise submissions."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.auth.models import User
from src.infrastructure.database.dependencies import get_db_session
from src.modules.auth.dependencies import get_current_active_user
from src.modules.execution.schemas import (
    ExecutionRunRequest,
    ExecutionRunResponse,
    ExecutionSubmitRequest,
    ExecutionSubmitResponse,
)
from src.modules.execution.service import execution_service

router = APIRouter()


@router.post(
    "/run",
    name="execution-run",
    status_code=status.HTTP_200_OK,
    response_model=ExecutionRunResponse,
    tags=["Code Execution"],
)
async def run_code(
    request: ExecutionRunRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ExecutionRunResponse:
    """Run code against custom or sample test cases without recording submission."""
    return await execution_service.run_code(user_id=current_user.id, request=request, session=db)


@router.post(
    "/submit",
    name="execution-submit",
    status_code=status.HTTP_200_OK,
    response_model=ExecutionSubmitResponse,
    tags=["Code Execution"],
)
async def submit_code(
    request: ExecutionSubmitRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ExecutionSubmitResponse:
    """Submit solution for an exercise, run test cases, record submission and update progress."""
    return await execution_service.submit_code(
        user_id=current_user.id,
        request=request,
        session=db,
    )
