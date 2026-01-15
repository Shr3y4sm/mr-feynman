import json
import logging
from app.services.llm_engine import llm_engine

logger = logging.getLogger(__name__)

class ExplanationComparator:
    def __init__(self):
        self.llm = llm_engine

    def clean_json_string(self, json_str: str) -> str:
        json_str = json_str.strip()
        if json_str.startswith("```json"):
            json_str = json_str[7:]
        if json_str.startswith("```"):
            json_str = json_str[3:]
        if json_str.endswith("```"):
            json_str = json_str[:-3]
        return json_str.strip()

    def compare_attempts(self, old_analysis: dict, new_analysis: dict) -> dict:
        """
        Compares two analysis results to generate progress feedback.
        """
        prompt = f"""
You are a mentor tracking a student's progress. Compare their previous attempt vs current attempt.

Previous Attempt Analysis:
Summary: {old_analysis.get('summary', 'N/A')}
Gaps: {old_analysis.get('gaps', [])}

Current Attempt Analysis:
Summary: {new_analysis.get('summary', 'N/A')}
Gaps: {new_analysis.get('gaps', [])}

Output valid JSON only:
{{
    "improvement_status": "better" | "same" | "worse",
    "key_changes": ["change 1", "change 2"],
    "encouragement": "Short encouraging sentence."
}}
"""
        try:
            raw_response = self.llm.generate(
                system_prompt="You are a helpful mentor.",
                user_prompt=prompt
            )
            cleaned = self.clean_json_string(raw_response)
            return json.loads(cleaned)
        except Exception as e:
            logger.error(f"Comparison failed: {e}")
            return None
