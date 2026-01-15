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
        # Log the full error for debugging
        import logging
        logging.getLogger(__name__).error(f"Analysis API Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_history():
    from app.memory.attempts_store import load_attempts
    return load_attempts(limit=20)
