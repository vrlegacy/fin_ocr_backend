from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from app.auth import get_current_user
from app.models import User
from app.schemas import OcrResponse
from app.services.gemini import analyze_receipt_with_gemini

router = APIRouter(prefix="/api/ocr", tags=["OCR Scanner"])

@router.post("/scan", response_model=OcrResponse)
async def scan_receipt(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    # Validate mime types
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file format: {file.content_type}. Only JPG, PNG, and PDF files are allowed."
        )

    try:
        content = await file.read()
        extracted_data = analyze_receipt_with_gemini(content, file.content_type)
        return extracted_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Receipt analysis failed: {str(e)}"
        )
