from fastapi import APIRouter, HTTPException
from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.services.feynman_analyzer import analyzer_service

router = APIRouter()

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_explanation(request: AnalysisRequest):
    try:
        response = analyzer_service.analyze_explanation(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
