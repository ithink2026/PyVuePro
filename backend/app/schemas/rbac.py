"""RBAC 相关 Pydantic 模型"""

from datetime import datetime
from pydantic import BaseModel, Field


# ========== 部门 ==========
class DepartmentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    parent_id: int | None = None
    sort: int = 0
    status: int = 1

class DepartmentUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=64)
    parent_id: int | None = None
    sort: int | None = None
    status: int | None = None


# ========== 角色 ==========
class RoleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    code: str = Field(..., min_length=1, max_length=64)
    description: str | None = None
    menu_ids: str | None = None
    status: int = 1

class RoleUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=64)
    description: str | None = None
    menu_ids: str | None = None
    status: int | None = None

class RoleResponse(BaseModel):
    id: int
    name: str
    code: str
    description: str | None = None
    menu_ids: str | None = None
    status: int = 1
    is_system: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None
    model_config = {"from_attributes": True}


# ========== 菜单 ==========
class MenuCreate(BaseModel):
    parent_id: int | None = None
    name: str = Field(..., min_length=1, max_length=64)
    type: str = Field(..., pattern="^(catalog|menu|button)$")
    path: str | None = None
    component: str | None = None
    permission: str | None = None
    icon: str | None = None
    sort: int = 0
    visible: int = 1
    status: int = 1

class MenuUpdate(BaseModel):
    parent_id: int | None = None
    name: str | None = Field(None, min_length=1, max_length=64)
    type: str | None = None
    path: str | None = None
    component: str | None = None
    permission: str | None = None
    icon: str | None = None
    sort: int | None = None
    visible: int | None = None
    status: int | None = None

class MenuResponse(BaseModel):
    id: int
    parent_id: int | None = None
    name: str
    type: str
    path: str | None = None
    component: str | None = None
    permission: str | None = None
    icon: str | None = None
    sort: int = 0
    visible: int = 1
    status: int = 1
    created_at: datetime | None = None
    updated_at: datetime | None = None
    children: list["MenuResponse"] | None = None
    model_config = {"from_attributes": True}


# ========== WebSocket 开关 ==========
class WebSocketToggleRequest(BaseModel):
    enabled: bool

class WebSocketToggleResponse(BaseModel):
    enabled: bool
