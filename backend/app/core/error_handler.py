"""FastAPI 全局异常处理器"""

from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import AppError, ServerError, USER_FRIENDLY_MESSAGES
from app.utils.error_logger import log_error


async def app_exception_handler(request: Request, exc: AppError):
    """处理自定义应用异常"""
    log_error(
        error_code=exc.error_code,
        detail=exc.detail,
        path=request.url.path,
        method=request.method,
        user_id=getattr(request.state, "user_id", None),
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": exc.error_code,
        },
    )


async def http_exception_handler(request: Request, exc):
    """处理 HTTPException，转换为友好消息"""
    from fastapi.exceptions import HTTPException
    if isinstance(exc, HTTPException):
        status_code = exc.status_code

        # 优先使用已有的 detail 消息，避免覆盖真实错误信息
        detail = str(exc.detail) if exc.detail else ""
        if not detail or detail == str(status_code):
            detail = USER_FRIENDLY_MESSAGES.get(
                f"HTTP_{status_code}",
                f"请求处理失败（错误码：{status_code}）"
            )

        log_error(
            error_code=f"HTTP_{status_code}",
            detail=detail,
            path=request.url.path,
            method=request.method,
            user_id=getattr(request.state, "user_id", None),
        )
        return JSONResponse(
            status_code=status_code,
            content={"detail": detail, "error_code": f"HTTP_{status_code}"},
        )
    raise exc


async def validation_exception_handler(request: Request, exc):
    """处理 FastAPI 请求参数校验失败（422）"""
    from fastapi.exceptions import RequestValidationError
    if isinstance(exc, RequestValidationError):
        # 提取第一个校验错误，返回友好提示
        errors = exc.errors()
        detail = "请求参数不正确，请检查填写内容"
        if errors:
            first = errors[0]
            field = first.get("loc", ["未知字段"])[-1]
            msg = first.get("msg", "")
            if "required" in first.get("type", ""):
                detail = f"请填写必填项：{field}"
            elif "type" in first.get("type", ""):
                detail = f"字段 {field} 格式不正确"
            else:
                detail = f"字段 {field}：{msg}"

        log_error(
            error_code="VALIDATION_ERROR",
            detail=detail,
            path=request.url.path,
            method=request.method,
            user_id=getattr(request.state, "user_id", None),
        )
        return JSONResponse(
            status_code=422,
            content={"detail": detail, "error_code": "VALIDATION_ERROR"},
        )
    raise exc


async def general_exception_handler(request: Request, exc: Exception):
    """处理未捕获的异常"""
    log_error(
        error_code="SERVER_ERROR",
        detail=str(exc),
        path=request.url.path,
        method=request.method,
        user_id=getattr(request.state, "user_id", None),
        exc_info=exc,
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "服务器繁忙，请稍后重试",
            "error_code": "SERVER_ERROR",
        },
    )


def register_exception_handlers(app):
    """注册所有异常处理器"""
    from fastapi.exceptions import HTTPException, RequestValidationError
    app.add_exception_handler(AppError, app_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)