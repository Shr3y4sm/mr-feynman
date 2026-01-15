from pydantic import BaseModel, Field
from typing import List, Optional, Any

class AnalysisRequest(BaseModel):
    concept: str = Field(..., description="The concept being explained")
    explanation: str = Field(..., description="The user's explanation")
    target_audience: str = Field("5-year-old", description="The target audience")
    # Phase 2 additions
    source_text: Optional[str] = None
    previous_attempt_id: Optional[str] = None

class AnalysisResponse(BaseModel):
    analysis: dict
    comparison: Optional[dict] = None
    attempt_id: str

