from pydantic import BaseModel, Field
from typing import List, Optional, Any, Literal

class AnalysisRequest(BaseModel):
    concept: str = Field(..., description="The concept being explained")
    explanation: str = Field(..., description="The user's explanation")
    target_audience: str = Field("5-year-old", description="The target audience")
    # Phase 2 additions
    source_text: Optional[str] = None
    previous_attempt_id: Optional[str] = None
    # Phase 3 additions
    input_mode: str = Field("text", description="Input mode: 'text' or 'speech'")
    speaking_duration: Optional[dict] = Field(None, description="Metrics: total_seconds, active_seconds")
    # Phase 4 additions
    purpose: Literal["learning", "interview"] = Field("learning", description="Purpose: 'learning' or 'interview'")
    # Phase 4b: Interview Loop
    session_id: Optional[str] = None
    turn_index: int = 1

class AnalysisResponse(BaseModel):
    analysis: dict
    comparison: Optional[dict] = None
    attempt_id: str
    # Phase 4b additions
    interviewer_followup: Optional[dict] = None
    conversation_complete: bool = False
    session_id: Optional[str] = None
    turn_index: int = 1

