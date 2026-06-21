"""应用配置，通过 pydantic-settings 读取 .env 环境变量"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    # 数据库
    DATABASE_URL: str = "mysql+pymysql://root:root@localhost:3306/subsidy"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # JWT
    JWT_SECRET_KEY: str = "change-me-to-a-random-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # H5 端是否存在
    H5_ENABLED: bool = True

    # H5 登录方式: ip / phone
    H5_LOGIN_MODE: str = "phone"

    # WebSocket 长连接开关
    ENABLE_WEBSOCKET: bool = True

    # 首页是否显示在线H5用户数
    SHOW_ONLINE_COUNT: bool = True

    # 心跳超时（秒）
    HEARTBEAT_TIMEOUT: int = 60
    HEARTBEAT_CLEANUP_INTERVAL: int = 30


settings = Settings()