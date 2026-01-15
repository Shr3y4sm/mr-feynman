import logging
import io
from pypdf import PdfReader
from fastapi import HTTPException, UploadFile

logger = logging.getLogger(__name__)

class PDFLoader:
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

    @staticmethod
    async def extract_text(file: UploadFile) -> str:
        """
        Extracts text from an uploaded PDF file.
        """
        # 1. Validate File Size/Type
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Invalid file type. Only PDFs are allowed.")
        
        # Check size (requires seeking to end, getting position, then resetting)
        file.file.seek(0, 2)
        size = file.file.tell()
        file.file.seek(0)
        
        if size > PDFLoader.MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail=f"File too large. Max size is {PDFLoader.MAX_FILE_SIZE/1024/1024}MB.")

        try:
            # 2. Extract Text using pypdf
            # Read file into bytes to pass to PdfReader
            content = await file.read()
            pdf = PdfReader(io.BytesIO(content))
            
            text = []
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text.append(extracted)
            
            full_text = "\n".join(text)
            
            if not full_text.strip():
                raise HTTPException(status_code=400, detail="No extractable text found in PDF. Scanned PDFs are not supported in this phase.")
                
            return full_text

        except Exception as e:
            logger.error(f"Error reading PDF: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")
