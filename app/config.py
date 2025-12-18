from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    anthropic_api_key: str
    openai_api_key: str

    db_schema: str = "polaris"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()