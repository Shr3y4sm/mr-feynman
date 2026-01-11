import json
import logging
import re
from app.services.llm_engine import llm_engine
from app.prompts.templates import FEYNMAN_SYSTEM_PROMPT, get_prompt_template, PromptMode
from app.schemas.analysis import AnalysisRequest, AnalysisResponse

logger = logging.getLogger(__name__)

class FeynmanAnalyzer:
    def __init__(self):
        self.llm = llm_engine

    def clean_json_string(self, json_str: str) -> str:
        """Helper to clean LLM output if it includes markdown code blocks."""
        json_str = json_str.strip()
        if json_str.startswith("```json"):
            json_str = json_str[7:]
        if json_str.startswith("```"):
            json_str = json_str[3:]
        if json_str.endswith("```"):
            json_str = json_str[:-3]
        return json_str.strip()

    def analyze_explanation(self, request: AnalysisRequest) -> AnalysisResponse:
        user_prompt = get_prompt_template(
            PromptMode.FEYNMAN_ANALYSIS,
            concept=request.concept,
            target_audience=request.target_audience,
            explanation=request.explanation
        )

        logger.info(f"Analyzing concept: {request.concept}")
        
        raw_response = self.llm.generate(
            system_prompt=FEYNMAN_SYSTEM_PROMPT,
            user_prompt=user_prompt
        )

        try:
            cleaned_response = self.clean_json_string(raw_response)
            data = json.loads(cleaned_response)
            return AnalysisResponse(**data)
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse JSON response: {raw_response}")
            # Fallback for demo/error cases
            return AnalysisResponse(
                summary="We couldn't process the AI response correctly. Please try again.",
                gaps=["System Error: Invalid JSON response from model"],
                suggestions=["Ensure the model file is loaded correctly"],
                follow_up_questions=[]
            )

analyzer_service = FeynmanAnalyzer()
