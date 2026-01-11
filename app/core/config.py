from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Mr. Feynman"
    VERSION: str = "1.0.0"
    MODEL_PATH: str = "models/Phi-3-mini-4k-instruct-q4.gguf"  # Default path, can be overridden by env var
    N_CTX: int = 4096  # Context window size
    N_THREADS: int = 4 # Number of threads for CPU inference

    class Config:
        env_file = ".env"

settings = Settings()
