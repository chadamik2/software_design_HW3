import os

class Settings:
    FILES_DIR: str = os.getenv("FILES_DIR", "/app/data/files")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///file_storage.db")

settings = Settings()