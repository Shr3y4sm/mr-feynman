from enum import Enum

class PromptMode(Enum):
    FEYNMAN_ANALYSIS = "feynman_analysis"

FEYNMAN_SYSTEM_PROMPT = """You are Richard Feynman. Help a student learn by analyzing their explanation.

Return ONLY raw JSON. No markdown. No intro/outro.

Required JSON Structure:
{
    "summary": "assessment",
    "gaps": ["list", "of", "missing", "logic"],
    "suggestions": ["list", "of", "tips"],
    "follow_up_questions": ["question1", "question2"]
}
"""

FEYNMAN_USER_PROMPT_TEMPLATE = """
Context: The user is explaining '{concept}' to a '{target_audience}'.

User's Explanation:
"{explanation}"

Analyze this explanation strictly using the Feynman principles.
"""

def get_prompt_template(mode: PromptMode, **kwargs) -> str:
    if mode == PromptMode.FEYNMAN_ANALYSIS:
        return FEYNMAN_USER_PROMPT_TEMPLATE.format(**kwargs)
    return ""
