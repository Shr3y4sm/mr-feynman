import logging
from app.core.config import settings

# Configure logger
logger = logging.getLogger(__name__)

try:
    from llama_cpp import Llama
    HAS_LLAMA = True
except ImportError:
    HAS_LLAMA = False
    logger.warning("llama-cpp-python not found. LLM features will be disabled.")

class LLMEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMEngine, cls).__new__(cls)
            cls._instance.model = None
        return cls._instance

    def load_model(self):
        if not HAS_LLAMA:
            raise ImportError("llama-cpp-python is not installed. Please check your setup.")

        if not self.model:
            try:
                logger.info(f"Loading model from {settings.MODEL_PATH}...")
                self.model = Llama(
                    model_path=settings.MODEL_PATH,
                    n_ctx=settings.N_CTX,
                    n_threads=settings.N_THREADS,
                    verbose=False
                )
                logger.info("Model loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                # For development without model files, we might want to mock this or raise
                raise e

    def generate(self, system_prompt: str, user_prompt: str, max_tokens: int = 1000) -> str:
        if not self.model:
            self.load_model()
        
        # Phi-3 / Llama-3 standard prompt format
        # Note: This is a generic formatting. For Phi-3 specifically, the format is usually:
        # <|user|>\n{prompt}<|end|>\n<|assistant|>
        
        formatted_prompt = f"<|system|>\n{system_prompt}<|end|>\n<|user|>\n{user_prompt}<|end|>\n<|assistant|>"
        
        output = self.model(
            formatted_prompt,
            max_tokens=max_tokens,
            stop=["<|end|>", "<|user|>"],
            echo=False,
            temperature=0.7
        )
        
        return output['choices'][0]['text']

llm_engine = LLMEngine()
