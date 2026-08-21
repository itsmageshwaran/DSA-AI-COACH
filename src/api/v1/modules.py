"""Modules API endpoints (/api/v1/modules)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from src.domain.auth.models import User
from src.domain.learning.models import Module
from src.infrastructure.database.dependencies import get_unit_of_work
from src.infrastructure.database.unit_of_work import UnitOfWork
from src.infrastructure.repositories.learning_repository import ModuleRepository
from src.modules.auth.dependencies import get_current_active_user, require_role
from src.modules.learning.schemas import ModuleCreate, ModuleResponse

router = APIRouter()


@router.get("", response_model=list[ModuleResponse], summary="List all modules")
async def list_modules(
    course_id: str | None = None,
    uow: UnitOfWork = Depends(get_unit_of_work),
    current_user: User = Depends(get_current_active_user),
) -> list[ModuleResponse]:
    """Retrieve all modules or filter by course_id."""
    repo = ModuleRepository(uow.session)
    if course_id:
        modules = await repo.get_by_course(course_id)
    else:
        modules = await repo.get_all()
    return [ModuleResponse.model_validate(m) for m in modules]


@router.post(
    "",
    response_model=ModuleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new module",
)
async def create_module(
    payload: ModuleCreate,
    uow: UnitOfWork = Depends(get_unit_of_work),
    current_user: User = Depends(require_role("admin")),
) -> ModuleResponse:
    """Create a new module (Admin only)."""
    repo = ModuleRepository(uow.session)
    module = Module(
        title=payload.title,
        description=payload.description,
        order=payload.order,
        course_id=payload.course_id,
    )
    created = await repo.create(module)
    await uow.commit()
    return ModuleResponse.model_validate(created)


@router.get("/{module_id}", response_model=ModuleResponse, summary="Get module by ID")
async def get_module(
    module_id: str,
    uow: UnitOfWork = Depends(get_unit_of_work),
    current_user: User = Depends(get_current_active_user),
) -> ModuleResponse:
    """Retrieve module by unique ID."""
    repo = ModuleRepository(uow.session)
    module = await repo.get_by_id(module_id)
    if not module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")
    return ModuleResponse.model_validate(module)
