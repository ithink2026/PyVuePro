"""H5 端用户数据模型（独立表，含敏感个人信息字段）"""

from sqlalchemy import BigInteger, Boolean, String, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class H5User(Base, TimestampMixin):
    __tablename__ = "h5_users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    password: Mapped[str] = mapped_column(String(256), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1", comment="是否启用")

    # 敏感个人信息
    name: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="姓名")
    id_card: Mapped[str | None] = mapped_column(String(18), nullable=True, comment="身份证号")
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="手机号")
    bank_card: Mapped[str | None] = mapped_column(String(32), nullable=True, comment="银行卡号")
    bank_card_name: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="银行卡名称")
    bank_card_balance: Mapped[float | None] = mapped_column(DECIMAL(15, 2), nullable=True, comment="银行卡余额")