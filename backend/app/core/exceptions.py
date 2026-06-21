"""统一错误异常体系"""

from typing import Any


class AppError(Exception):
    """应用基础异常"""
    status_code: int = 500
    detail: str = "服务器内部错误"
    log_level: str = "error"
    error_code: str = "INTERNAL_ERROR"

    def __init__(self, detail: str | None = None, **kwargs: Any):
        self.detail = detail or self.detail
        self.extra = kwargs
        super().__init__(self.detail)


class BadRequestError(AppError):
    """请求参数错误 - 400"""
    status_code = 400
    detail = "请求参数不正确"
    log_level = "warning"
    error_code = "BAD_REQUEST"


class AuthError(AppError):
    """认证失败 - 401"""
    status_code = 401
    detail = "登录信息已过期，请重新登录"
    log_level = "warning"
    error_code = "UNAUTHORIZED"


class ForbiddenError(AppError):
    """权限不足 - 403"""
    status_code = 403
    detail = "您没有权限执行此操作"
    log_level = "warning"
    error_code = "FORBIDDEN"


class NotFoundError(AppError):
    """资源不存在 - 404"""
    status_code = 404
    detail = "请求的资源不存在"
    log_level = "warning"
    error_code = "NOT_FOUND"


class ConflictError(AppError):
    """资源冲突 - 409"""
    status_code = 409
    detail = "数据冲突，请检查后重试"
    log_level = "warning"
    error_code = "CONFLICT"


class ValidationError(AppError):
    """数据验证失败 - 422"""
    status_code = 422
    detail = "数据格式不正确"
    log_level = "warning"
    error_code = "VALIDATION_ERROR"


class ServerError(AppError):
    """服务器内部错误 - 500"""
    status_code = 500
    detail = "服务器繁忙，请稍后重试"
    log_level = "error"
    error_code = "SERVER_ERROR"


# 用户友好错误消息映射
USER_FRIENDLY_MESSAGES = {
    # 通用 HTTP 状态码
    "HTTP_400": "请求参数不正确，请检查填写内容",
    "HTTP_401": "登录信息已过期，请重新登录",
    "HTTP_403": "您没有权限执行此操作",
    "HTTP_404": "请求的资源不存在或已被删除",
    "HTTP_409": "数据已存在或存在冲突，请检查后重试",
    "HTTP_422": "提交的数据格式不正确，请按提示修正",
    "HTTP_500": "服务器繁忙，请稍后重试",
    # 业务错误码
    "BAD_REQUEST": "请求参数不正确，请检查填写内容",
    "UNAUTHORIZED": "登录信息已过期，请重新登录",
    "FORBIDDEN": "您没有权限执行此操作，请联系管理员",
    "NOT_FOUND": "请求的资源不存在或已被删除",
    "CONFLICT": "数据已存在或存在冲突，请检查后重试",
    "VALIDATION_ERROR": "数据格式不正确，请按提示修正",
    "SERVER_ERROR": "服务器繁忙，请稍后重试",
    "DB_ERROR": "数据操作失败，请稍后重试",
    "REDIS_ERROR": "缓存服务异常，请稍后重试",
    "RATE_LIMIT": "操作过于频繁，请稍后再试",
    "NETWORK_ERROR": "网络连接失败，请检查网络后重试",
    "TIMEOUT_ERROR": "请求超时，请稍后重试",
    # 密码相关
    "PASSWORD_MISMATCH": "当前密码不正确，请重新输入",
    "PASSWORD_WEAK": "密码强度不足，至少需要6位",
    "PASSWORD_SAME": "新密码不能与旧密码相同",
    # 用户相关
    "USERNAME_EXISTS": "该用户名已被使用，请更换后重试",
    "USER_NOT_FOUND": "该用户不存在或已被删除",
    "SUPER_ADMIN_DELETE": "超级管理员账号不可删除",
    "ADMIN_ONLY": "仅管理端用户可执行此操作",
    "H5_ONLY": "仅 H5 端用户可执行此操作",
    "LOGIN_FAILED": "用户名或密码错误，请检查后重试",
    "LOGIN_WRONG_PORTAL": "该账号无法在此登录，请检查登录入口",
    "ACCOUNT_DISABLED": "该账户已被禁用，请联系管理员",
    # 角色相关
    "ROLE_CODE_EXISTS": "该角色编码已被使用，请更换后重试",
    "ROLE_SYSTEM_LOCKED": "系统角色不允许此操作",
    "ROLE_NOT_FOUND": "角色不存在或已被删除",
    # 菜单相关
    "MENU_HAS_CHILDREN": "请先删除子菜单后再操作",
    "MENU_NOT_FOUND": "菜单不存在或已被删除",
    # 部门相关
    "DEPT_HAS_CHILDREN": "请先删除子部门后再操作",
    "DEPT_HAS_USERS": "部门下仍有用户，请先转移用户后再删除",
    "DEPT_NOT_FOUND": "部门不存在或已被删除",
    # 功能开关
    "WS_DISABLED": "WebSocket 功能已关闭，如需使用请联系管理员",
    "WS_TOGGLE_FORBIDDEN": "仅超级管理员可操作此开关",
    "ONLINE_TOGGLE_FORBIDDEN": "仅超级管理员可操作此开关",
}