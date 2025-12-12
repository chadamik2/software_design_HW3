import os


class Settings:
    FILE_SERVICE_URL = os.getenv("FILE_SERVICE_URL", "http://file-storage:8001")
    ANALYSIS_SERVICE_URL = os.getenv("ANALYSIS_SERVICE_URL", "http://file-analysis:8002")


settings = Settings()
