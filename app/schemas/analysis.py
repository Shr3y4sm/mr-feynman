from pydantic import BaseModel, Field
from typing import List

class AnalysisRequest(BaseModel):
    concept: str = Field(..., description="The concept being explained")
    explanation: str = Field(..., description="The user's explanation")
    target_audience: str = Field("5-year-old", description="The target audience")

class AnalysisResponse(BaseModel):
    summary: str = Field(..., description="Brief assessment of the user's understanding")
    gaps: List[str] = Field(..., description="List of identified missing logical steps or jargon issues")
    suggestions: List[str] = Field(..., description="Concrete ways to simplify or clarify")
    follow_up_questions: List[str] = Field(..., description="Questions to test depth of knowledge")

