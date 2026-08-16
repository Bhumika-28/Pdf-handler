import os
import tempfile

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    HTTPException
)

from fastapi.responses import FileResponse

from app.services.pdf_convert_service import (
    convert_pdf_to_images,
    create_zip
)


router = APIRouter(
    prefix="/convert",
    tags=["PDF Convert"]
)


@router.post("/")
async def convert_pdf_endpoint(
    file: UploadFile = File(...),
    image_format: str = Form("png"),
    dpi: int = Form(150)
):

    # --------------------------------
    # Validate PDF
    # --------------------------------

    if not file.filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )


    # --------------------------------
    # Validate image format
    # --------------------------------

    image_format = image_format.lower()

    if image_format not in ["png", "jpg"]:

        raise HTTPException(
            status_code=400,
            detail="Image format must be png or jpg."
        )


    # --------------------------------
    # Validate DPI
    # --------------------------------

    if dpi not in [72, 150, 200, 300]:

        raise HTTPException(
            status_code=400,
            detail="DPI must be 72, 150, 200 or 300."
        )


    input_path = None
    temp_dir = None
    zip_path = None


    try:

        # --------------------------------
        # Create temporary input PDF
        # --------------------------------

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as input_file:

            input_path = input_file.name

            content = await file.read()

            input_file.write(content)


        # --------------------------------
        # Create temporary output directory
        # --------------------------------

        temp_dir = tempfile.mkdtemp()


        # --------------------------------
        # Convert PDF → Images
        # --------------------------------

        image_paths = convert_pdf_to_images(
            input_path=input_path,
            output_dir=temp_dir,
            image_format=image_format,
            dpi=dpi
        )


        if not image_paths:

            raise HTTPException(
                status_code=400,
                detail="PDF contains no pages."
            )


        # --------------------------------
        # Create ZIP
        # --------------------------------

        zip_path = os.path.join(
            temp_dir,
            "pdf_images.zip"
        )


        create_zip(
            image_paths,
            zip_path
        )


        # --------------------------------
        # Return ZIP
        # --------------------------------

        return FileResponse(
            zip_path,
            media_type="application/zip",
            filename="pdf_images.zip"
        )


    except HTTPException:

        raise


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"PDF conversion failed: {str(e)}"
        )


    finally:

        # Remove input file
        if input_path and os.path.exists(input_path):

            os.remove(input_path)