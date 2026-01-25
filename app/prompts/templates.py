from enum import Enum

class PromptMode(Enum):
    FEYNMAN_ANALYSIS = "feynman_analysis"

FEYNMAN_SYSTEM_PROMPT = """You are Richard Feynman. Help a student learn by analyzing their explanation.

Return ONLY raw JSON. No markdown. No intro/outro.

Instructions:
1. Compare the user's explanation to the concept's core truth.
2. Identify gaps in logic or understanding.
3. Provide constructive feedback.
4. Generate ONE 'interviewer_followup' question that tests depth or trade-offs (not just recall).

Required JSON Structure:
{
    "summary": "assessment",
    "gaps": ["list", "of", "missing", "logic"],
    "suggestions": ["list", "of", "tips"],
    "follow_up_questions": ["question1", "question2"],
    "speaking_clarity": {
        "issues": ["rambling", "run-on sentences", "filler words"],
        "suggestions": ["pause more", "break it down"]
    },
    "speaking_metrics": {
        "active_speaking_seconds": 12,
        "total_time_seconds": 15,
        "pause_ratio": 0.2,
        "insight": "Good pace but many pauses",
        "suggestions": ["Try to maintain a steady flow"]
    },
    "filler_analysis": {
        "total_filler_count": 5,
        "filler_density": 0.05,
        "common_fillers": ["um", "like"],
        "insight": "High usage of 'like' indicates hesitation.",
        "suggestions": ["Pause instead of saying 'like'."]
    },
    "interviewer_followup": {
        "question": "If X is true, how would that affect Y?",
        "intent": "Testing depth of understanding on related concept."
    }
}
"""

FEYNMAN_USER_PROMPT_TEMPLATE = """
Context: The user is explaining '{concept}' to a '{target_audience}'.

User's Explanation:
"{explanation}"

{speaking_context}

Analyze this explanation strictly using the Feynman principles.
"""

def get_prompt_template(mode: PromptMode, **kwargs) -> str:
    if mode == PromptMode.FEYNMAN_ANALYSIS:
        # Default empty string for optional params if not provided
        if "speaking_context" not in kwargs:
            kwargs["speaking_context"] = ""
            
        return FEYNMAN_USER_PROMPT_TEMPLATE.format(**kwargs)
    return ""
