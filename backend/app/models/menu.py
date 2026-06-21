"""菜单/权限数据模型"""

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Menu(Base, TimestampMixin):
    __tablename__ = "menus"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    parent_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, default=None)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # catalog / menu / button
    path: Mapped[str | None] = mapped_column(String(200), nullable=True)  # 路由路径
    component: Mapped[str | None] = mapped_column(String(200), nullable=True)  # 组件路径
    permission: Mapped[str | None] = mapped_column(String(100), nullable=True)  # 权限标识
    icon: Mapped[str | None] = mapped_column(String(64), nullable=True)  # 图标
    sort: Mapped[int] = mapped_column(default=0)
    visible: Mapped[int] = mapped_column(default=1)  # 1=显示 0=隐藏
    status: Mapped[int] = mapped_column(default=1)
