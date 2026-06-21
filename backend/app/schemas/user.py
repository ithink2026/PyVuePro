"""用户相关 Pydantic 模型"""

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=6, max_length=128)


class UserResponse(BaseModel):
    id: int
    username: str

    model_config = {"from_attributes": True}