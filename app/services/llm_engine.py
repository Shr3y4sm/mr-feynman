import logging
from openai import OpenAI
from app.core.config import settings

# Configure logger
logger = logging.getLogger(__name__)

class LLMEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMEngine, cls).__new__(cls)
            cls._instance.client = None
        return cls._instance

    def get_client(self):
        if not self.client:
            try:
                self.client = OpenAI(
                    base_url=settings.LLM_API_BASE,
                    api_key=settings.LLM_API_KEY
                )
                logger.info(f"Connected to LLM Server at {settings.LLM_API_BASE}")
            except Exception as e:
                logger.error(f"Failed to create OpenAI client: {e}")
                raise e
        return self.client

    def generate(self, system_prompt: str, user_prompt: str, max_tokens: int = 1000) -> str:
        client = self.get_client()
        
        try:
            response = client.chat.completions.create(
                model="local-model", # The server ignores this usually, or uses the loaded model
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.2,
                response_format={"type": "json_object"},
                stop=["<|end|>", "User:", "Context:"]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM Generation Error: {e}")
            # If connection refused, guide the user
            if "Connection refused" in str(e) or "connect" in str(e).lower():
                return '{"summary": "Error: Local LLM Server is not running.", "gaps": ["Please run the start_model_server.ps1 script"], "suggestions": ["Check README"], "follow_up_questions": []}'
            raise e

llm_engine = LLMEngine()
