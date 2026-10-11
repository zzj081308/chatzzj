from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    APP_NAME: str = "Chat Room"
    DEBUG: bool = False

    # 数据库 —— 本地 MySQL
    DATABASE_URL: str = "mysql+aiomysql://root:password@127.0.0.1:3306/chatzzj?charset=utf8mb4"

    # JWT
    SECRET_KEY: str = "change-me-to-a-random-secret-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Upload
    UPLOAD_DIR: str = str(Path(__file__).parent.parent / "uploads")
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_IMAGE_TYPES: list[str] = ["image/jpeg", "image/png", "image/webp", "image/gif"]
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100 MB
    ALLOWED_FILE_EXTENSIONS: list[str] = [
        ".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp",
        ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
        ".txt", ".csv", ".json", ".xml", ".md",
        ".zip", ".rar", ".7z", ".tar", ".gz",
        ".mp3", ".mp4", ".avi", ".mov", ".mkv",
        ".py", ".js", ".ts", ".html", ".css",
    ]

    # Admin
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"

    # AI Assistant
    AI_ASSISTANT_ENABLED: bool = True
    AI_ASSISTANT_USERNAME: str = "AI助手"
    AI_API_KEY: str = "sk-1f22bda43279420aabe042b211ab643b"
    AI_API_URL: str = "https://api.deepseek.com/v1/chat/completions"
    AI_MODEL: str = "deepseek-chat"
    AI_SYSTEM_PROMPT: str = "你是一个友好的聊天助手，用中文回答用户的问题。你的名字是AI助手，你的用户可以和你聊天、咨询问题。请用简洁明了的方式回答。"

    # CORS —— 逗号分隔，例如 "http://localhost:5173,https://chat.example.com"
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
