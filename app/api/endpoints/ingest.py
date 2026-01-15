import os
import uuid
import logging
from fastapi import APIRouter, UploadFile, File
from app.services.pdf_loader import PDFLoader

router = APIRouter()
logger = logging.getLogger(__name__)

UPLOAD_DIR = "data/raw"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Uploads a PDF, extracts text, and saves it locally.
    Returns the extracted text and a reference ID.
    """
    logger.info(f"Receiving upload: {file.filename}")
    
    # Extract
    text = await PDFLoader.extract_text(file)
    
    # Save temporarily (Phase 2 requirement)
    file_id = str(uuid.uuid4())
    save_path = os.path.join(UPLOAD_DIR, f"{file_id}.txt")
    
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(text)
        
    return {
        "status": "success",
        "file_id": file_id,
        "filename": file.filename,
        "text_length": len(text),
        "text": text  # Returning full text as requested
    }
