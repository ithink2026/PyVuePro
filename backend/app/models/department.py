"""部门数据模型"""

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Department(Base, TimestampMixin):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, default=None)
    sort: Mapped[int] = mapped_column(default=0)
    status: Mapped[int] = mapped_column(default=1)  # 1=启用 0=禁用

    users: Mapped[list["User"]] = relationship("User", back_populates="department")
