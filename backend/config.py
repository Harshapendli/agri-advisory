from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    MONGO_URI: str = "mongodb+srv://user:pass@cluster.mongodb.net/agri_advisory"
    NEO4J_URI: str = "neo4j+s://xxxxxxxx.databases.neo4j.io"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "your_password"
    QDRANT_URL: str = "https://xxxxxxxx.us-east4-0.gcp.cloud.qdrant.io"
    QDRANT_API_KEY: str = "your_qdrant_key"
    REDIS_URL: str = "redis://localhost:6379"
    OPENAI_API_KEY: str = "your_openai_key"
    GEMINI_API_KEY: str = ""
    OPENWEATHER_API_KEY: str = "your_weather_key"
    JWT_SECRET: str = "change_this_secret_in_production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080
    MODEL_PATH: str = "ml/models/crop_model.pkl"
    LABEL_ENCODER_PATH: str = "ml/models/label_encoder.pkl"
    DISEASE_MODEL_PATH: str = "ml/models/disease_model.pth"
    LLM_PROVIDER: str = "openai"
    APP_NAME: str = "AgriAdvisory"
    DEBUG: bool = True

    class Config:
        env_file = ".env"
        extra = "ignore"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
