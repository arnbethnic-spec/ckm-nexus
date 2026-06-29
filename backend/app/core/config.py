from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "CKM Nexus"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    class Config:
        env_file = ".env"

settings = Settings()
