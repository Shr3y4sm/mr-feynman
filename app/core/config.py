from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Mr. Feynman"
    VERSION: str = "1.0.0"
    MODEL_PATH: str = "models/Phi-3-mini-4k-instruct-q4.gguf"
    # Local Server Config
    LLM_API_BASE: str = "http://localhost:8080/v1"
    LLM_API_KEY: str = "lm-studio"  # Dummy key for local server
    
    class Config:
        env_file = ".env"

settings = Settings()
