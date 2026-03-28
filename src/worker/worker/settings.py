from pydantic_settings import BaseSettings, SettingsConfigDict


class WorkerSettings(BaseSettings):
    CELERY_BROKER_URL: str = "amqp://guest:guest@rabbitmq:5672//"

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""

    TEMP_BASE_DIR: str = "/tmp/brainrot_worker"  # nosec: B108
    MEDIA_BASE_DIR: str = "./media"

    SAMBANOVA_API_KEY: str
    AI_MODEL: str = "DeepSeek-V3-0324"
    AI_TEMPERATURE: float = 0.8
    AI_MAX_TOKENS: int = 2048

    ELEVENLABS_API_KEY: str

    PEXELS_API_KEY: str

    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_SECURE: bool = False
    MINIO_VIDEOS_BUCKET: str = "videos"

    KEK_KEY: str

    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None

    DB_PASSWORD: str
    DB_USER: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    @property
    def DB_URL(self) -> str:
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = WorkerSettings()
