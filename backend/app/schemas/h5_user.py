"""H5 用户相关 Pydantic 模型"""

from typing import Optional
from pydantic import BaseModel, Field


class H5UserCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=6, max_length=128)
    name: Optional[str] = Field(None, max_length=64)
    id_card: Optional[str] = Field(None, max_length=18)
    phone: Optional[str] = Field(None, max_length=20)
    bank_card: Optional[str] = Field(None, max_length=32)
    bank_card_name: Optional[str] = Field(None, max_length=64)
    bank_card_balance: Optional[float] = Field(None, ge=0)


class H5UserResponse(BaseModel):
    id: int
    username: str
    name: Optional[str]
    id_card: Optional[str]
    phone: Optional[str]
    bank_card: Optional[str]
    bank_card_name: Optional[str]
    bank_card_balance: Optional[float]

    model_config = {"from_attributes": True}