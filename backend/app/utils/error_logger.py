"""错误日志记录"""

import logging
import traceback
from datetime import datetime

from app.core.config import settings

# 配置日志
logger = logging.getLogger("app.error")
logger.setLevel(logging.INFO)

# 文件 Handler
try:
    fh = logging.FileHandler("error.log", encoding="utf-8")
    fh.setLevel(logging.WARNING)
    fh.setFormatter(logging.Formatter(
        "[%(asctime)s] %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))
    logger.addHandler(fh)
except Exception:
    pass


def log_error(
    error_code: str,
    detail: str,
    path: str = "",
    method: str = "",
    user_id: str | None = None,
    exc_info: Exception | None = None,
):
    """记录错误日志"""
    extra = {
        "error_code": error_code,
        "path": path,
        "method": method,
        "user_id": user_id or "-",
        "timestamp": datetime.now().isoformat(),
    }

    if exc_info:
        extra["traceback"] = "".join(
            traceback.format_exception(type(exc_info), exc_info, exc_info.__traceback__)
        )[-2000:]  # 截断避免日志过大

    log_msg = f"[{extra['error_code']}] {extra['method']} {extra['path']} user={extra['user_id']} | {detail}"
    if exc_info:
        logger.error(log_msg)
    else:
        logger.warning(log_msg)