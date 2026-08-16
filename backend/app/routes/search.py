import os
import tempfile

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.services.pdf_search_service import search_pdf


router = APIRouter(
    prefix="/search",
    tags=["Search PDF"]
)


@router.post("/")
async def search_pdf_endpoint(
    file: UploadFile = File(...),
    search_text: str = Form(...)
):

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    if not search_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Search text cannot be empty."
        )

    temp_path = None

    try:

        # Create temporary PDF file
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as temp_file:

            temp_path = temp_file.name

            content = await file.read()

            temp_file.write(content)

        # Search PDF
        result = search_pdf(
            temp_path,
            search_text.strip()
        )

        return result

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"PDF search failed: {str(e)}"
        )

    finally:

        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)