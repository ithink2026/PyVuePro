"""用户数据模型"""

from sqlalchemy import BigInteger, ForeignKey, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    password: Mapped[str] = mapped_column(String(256), nullable=False)

    # RBAC 关联
    dept_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("departments.id"), nullable=True)
    role_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("roles.id"), nullable=True)
    is_super_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    department = relationship("Department", back_populates="users")
    role_rel = relationship("Role", back_populates="users")