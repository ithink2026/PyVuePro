"""角色数据模型"""

from sqlalchemy import BigInteger, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Role(Base, TimestampMixin):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(256), nullable=True)
    menu_ids: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[int] = mapped_column(default=1)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)  # 系统角色不可删除/编辑

    users: Mapped[list["User"]] = relationship("User", back_populates="role_rel")