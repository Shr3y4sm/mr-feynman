import json
import logging
from app.services.llm_engine import llm_engine

logger = logging.getLogger(__name__)

COMPARISON_SYSTEM_PROMPT = """You are Richard Feynman.
Your goal is to compare a student's previous explanation of a concept with their current one to track progress.

Analyze the two explanations based on:
1. Clarity: Did they simplify the jargon?
2. Accuracy: Did they fix the logical gaps identified previously?
3. Completeness: Did they incorporate new information?

Return ONLY valid JSON matching this structure exactly:
{
    "summary_of_progress": "A brief, encouraging comment on how they have improved (or regressed).",
    "improvements": ["Specific thing 1 they fixed", "Specific concept they clarified"],
    "remaining_gaps": ["Logic hole still present", "New confusion introduced"],
    "next_step_suggestion": "The single most important thing to focus on next."
}
"""

COMPARISON_USER_PROMPT = """
Concept: {concept}

Previous Explanation:
"{previous_text}"

Previous Gaps Identified:
{previous_gaps}

Current Explanation:
"{current_text}"

Compare them. Did the student fix the gaps?
"""

def compare_explanations(
    previous: dict,
    current: dict
) -> dict:
    """
    Compare two explanation attempts and return structured feedback.
    
    Args:
        previous (dict): Dict containing 'explanation_text' and 'analysis_result' of the older attempt.
        current (dict): Dict containing 'explanation_text' of the new attempt.
        
    Returns:
        dict: The structured JSON comparison from the LLM.
    """
    try:
        prev_text = previous.get("explanation_text", "")
        # Extract gaps from the previous analysis result to see if they were fixed
        prev_analysis = previous.get("analysis_result", {})
        # Handle case where analysis might be a string (stored JSON) or dict
        if isinstance(prev_analysis, str):
            try:
                prev_analysis = json.loads(prev_analysis)
            except:
                prev_analysis = {}
                
        prev_gaps = prev_analysis.get("gaps", [])
        
        curr_text = current.get("explanation_text", "")
        concept = current.get("concept", "Unknown Concept")

        # Construct Prompt
        user_prompt = COMPARISON_USER_PROMPT.format(
            concept=concept,
            previous_text=prev_text,
            previous_gaps=json.dumps(prev_gaps),
            current_text=curr_text
        )

        # Generate Response
        response_str = llm_engine.generate(
            system_prompt=COMPARISON_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            max_tokens=800
        )

        # Parse JSON
        # Strip code blocks if the LLM adds them
        clean_response = response_str.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_response)

    except Exception as e:
        logger.error(f"Error comparing explanations: {e}")
        # Return a safe fallback so the UI schema doesn't break
        return {
            "summary_of_progress": "Unable to generate comparison.",
            "improvements": [],
            "remaining_gaps": [],
            "next_step_suggestion": "Continue refining your explanation."
        }
