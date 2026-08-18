from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import StreamingResponse

from app.services.image_to_pdf_service import create_pdf_from_images


router = APIRouter()


@router.post("/images-to-pdf")
async def images_to_pdf(
    files: list[UploadFile] = File(...),
    page_size: str = Form("A4"),
    orientation: str = Form("PORTRAIT")
):

    image_data = []

    for file in files:

        if not file.content_type.startswith("image/"):
            continue

        data = await file.read()

        image_data.append(data)

    if not image_data:

        return {
            "error": "No valid image files provided"
        }

    pdf_file = create_pdf_from_images(
        image_data,
        page_size,
        orientation
    )

    return StreamingResponse(
        pdf_file,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                "attachment; filename=images_to_pdf.pdf"
        }
    )