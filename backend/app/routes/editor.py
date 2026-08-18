from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    HTTPException
)

from fastapi.responses import FileResponse, Response
import tempfile
import os

from app.services.pdf_editor_service import (
    get_pdf_info,
    render_pdf_page,
    delete_pages,
    rotate_page,
    insert_pdf
)


router = APIRouter(
    prefix="/editor",
    tags=["PDF Editor"]
)


# ============================================================
# OPEN PDF
# ============================================================

@router.post("/open")
async def open_pdf(
    file: UploadFile = File(...)
):

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    try:

        file_bytes = await file.read()

        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        )

        temp_file.write(file_bytes)
        temp_file.close()

        file_path = temp_file.name

        info = get_pdf_info(file_path)

        return {
            "file_path": file_path,
            "filename": file.filename,
            "total_pages": info["total_pages"]
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# RENDER PAGE
# ============================================================

@router.get("/page")
def get_page(
    file_path: str,
    page_number: int
):

    try:

        image_bytes = render_pdf_page(
            file_path,
            page_number
        )

        return Response(
            content=image_bytes,
            media_type="image/png"
        )

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# ============================================================
# DELETE
# ============================================================

@router.post("/delete")
async def delete_pdf_pages(
    file_path: str = Form(...),
    page_numbers: str = Form(...)
):

    try:

        pages = [
            int(page.strip())
            for page in page_numbers.split(",")
            if page.strip()
        ]

        output_path = delete_pages(
            file_path,
            pages
        )

        return {
            "file_path": output_path,
            "total_pages": get_pdf_info(output_path)["total_pages"]
        }

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


# ============================================================
# ROTATE
# ============================================================

@router.post("/rotate")
async def rotate_pdf_page(
    file_path: str = Form(...),
    page_number: int = Form(...),
    direction: str = Form(...)
):

    try:

        if direction == "clockwise":

            rotation = 90

        elif direction == "counterclockwise":

            rotation = -90

        else:

            raise ValueError(
                "Invalid rotation direction"
            )

        output_path = rotate_page(
            file_path,
            page_number,
            rotation
        )

        return {
            "file_path": output_path,
            "total_pages": get_pdf_info(output_path)["total_pages"]
        }

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


# ============================================================
# INSERT PDF
# ============================================================

@router.post("/insert")
async def insert_pdf_pages(
    file_path: str = Form(...),
    position: int = Form(...),
    file: UploadFile = File(...)
):

    if not file.filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    try:

        file_bytes = await file.read()

        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        )

        temp_file.write(file_bytes)
        temp_file.close()

        insert_file_path = temp_file.name

        output_path = insert_pdf(
            file_path,
            insert_file_path,
            position
        )

        return {
            "file_path": output_path,
            "total_pages": get_pdf_info(output_path)["total_pages"]
        }

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


# ============================================================
# DOWNLOAD / SAVE
# ============================================================

@router.get("/save")
def save_pdf(file_path: str):

    if not os.path.exists(file_path):

        raise HTTPException(
            status_code=404,
            detail="PDF file not found"
        )

    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename="edited.pdf"
    )