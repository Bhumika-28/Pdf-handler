from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, Response
import tempfile
import os

from app.services.pdf_editor_service import (
    get_pdf_info,
    render_pdf_page,
    extract_page_range
)


router = APIRouter(
    prefix="/extract",
    tags=["Extract"]
)


@router.post("/info")
async def pdf_info(
    file: UploadFile = File(...)
):
    """
    Get total page count of uploaded PDF.
    """

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    )

    temp_path = temp_file.name

    try:

        content = await file.read()

        temp_file.write(content)
        temp_file.close()

        info = get_pdf_info(temp_path)

        return info

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        if os.path.exists(temp_path):
            os.remove(temp_path)


@router.post("/preview")
async def preview_pdf_page(
    file: UploadFile = File(...),
    page: int = 1
):
    """
    Return selected PDF page as PNG.

    page is 1-based.
    """

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    )

    temp_path = temp_file.name

    try:

        content = await file.read()

        temp_file.write(content)
        temp_file.close()

        # Convert 1-based frontend page to 0-based PyMuPDF page
        page_bytes = render_pdf_page(
            temp_path,
            page - 1
        )

        return Response(
            content=page_bytes,
            media_type="image/png"
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        if os.path.exists(temp_path):
            os.remove(temp_path)


@router.post("/pages")
async def extract_pages(
    file: UploadFile = File(...),
    start_page: int = 1,
    end_page: int = 1
):
    """
    Extract selected page range from PDF.
    """

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    )

    temp_path = temp_file.name

    output_path = None

    try:

        content = await file.read()

        temp_file.write(content)
        temp_file.close()

        output_path = extract_page_range(
            temp_path,
            start_page,
            end_page
        )

        return FileResponse(
            output_path,
            media_type="application/pdf",
            filename="extracted.pdf"
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        if os.path.exists(temp_path):
            os.remove(temp_path)