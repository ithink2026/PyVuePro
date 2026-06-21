"""部门管理 API"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.core.security import get_current_admin, require_permission
from app.schemas.rbac import DepartmentCreate, DepartmentUpdate
from app.services.rbac_service import (
    get_department_tree, create_department, update_department, delete_department,
)

router = APIRouter(prefix="/departments", tags=["部门管理"])


@router.get("/tree")
async def list_departments(
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_permission("system:dept:list")),
):
    return await get_department_tree(db)


@router.post("", status_code=201)
async def add_department(
    data: DepartmentCreate,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_permission("system:dept:add")),
):
    return await create_department(db, data.model_dump())


@router.put("/{dept_id}")
async def edit_department(
    dept_id: int,
    data: DepartmentUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_permission("system:dept:edit")),
):
    dept = await update_department(db, dept_id, data.model_dump(exclude_none=True))
    if not dept:
        raise NotFoundError("部门不存在或已被删除")
    return dept


@router.delete("/{dept_id}")
async def remove_department(
    dept_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_permission("system:dept:del")),
):
    if not await delete_department(db, dept_id):
        raise NotFoundError("部门不存在或已被删除")
    return {"message": "删除成功"}