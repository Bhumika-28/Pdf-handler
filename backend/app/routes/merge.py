from typing import Annotated

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse

from app.services.merge_service import merge_pdfs


router = APIRouter(
    prefix="/merge",
    tags=["Merge PDF"]
)


@router.post("/")
async def merge(
    files: Annotated[list[UploadFile], File()]
):
    if len(files) < 2:
        raise HTTPException(
            status_code=400,
            detail="Please upload at least 2 PDF files."
        )

    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail=f"{file.filename} is not a PDF file."
            )

    try:
        merged_pdf = merge_pdfs(files)

        return StreamingResponse(
            merged_pdf,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=merged.pdf"
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to merge PDFs: {str(e)}"
        )