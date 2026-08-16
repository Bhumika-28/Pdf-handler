import os
import tempfile

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse

from app.services.pdf_compress_service import compress_pdf


router = APIRouter(
    prefix="/compress",
    tags=["Compress PDF"]
)


@router.post("/")
async def compress_pdf_endpoint(
    file: UploadFile = File(...),
    quality: str = Form("medium")
):

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    if quality not in ["low", "medium", "high"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid compression quality."
        )

    input_path = None
    output_path = None

    try:

        # Temporary input file
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as input_file:

            input_path = input_file.name

            content = await file.read()

            input_file.write(content)


        # Temporary output file
        output_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        )

        output_path = output_file.name

        output_file.close()


        # Compress PDF
        compress_pdf(
            input_path,
            output_path,
            quality
        )


        original_size = os.path.getsize(input_path)
        compressed_size = os.path.getsize(output_path)


        return FileResponse(
            output_path,
            media_type="application/pdf",
            filename="compressed.pdf",
            headers={
                "X-Original-Size": str(original_size),
                "X-Compressed-Size": str(compressed_size)
            }
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"PDF compression failed: {str(e)}"
        )

    finally:

        if input_path and os.path.exists(input_path):
            os.remove(input_path)
            