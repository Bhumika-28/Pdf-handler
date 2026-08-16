import fitz
import os
import tempfile


def get_pdf_info(file_path: str):
    """
    Open PDF and return basic information.
    """

    doc = fitz.open(file_path)

    try:
        return {
            "total_pages": doc.page_count
        }
    finally:
        doc.close()


def render_pdf_page(file_path: str, page_number: int):
    """
    Render one PDF page as PNG bytes.

    page_number is 0-based.
    """

    doc = fitz.open(file_path)

    try:
        if page_number < 0 or page_number >= doc.page_count:
            raise ValueError("Page number out of range")

        page = doc.load_page(page_number)

        # Similar to sir's editor.py
        matrix = fitz.Matrix(1.5, 1.5)

        pix = page.get_pixmap(
            matrix=matrix,
            alpha=False
        )

        return pix.tobytes("png")

    finally:
        doc.close()


def extract_page_range(
    file_path: str,
    start_page: int,
    end_page: int
):
    """
    Extract pages from start_page to end_page.

    Input pages are 1-based.
    """

    doc = fitz.open(file_path)

    try:

        total_pages = doc.page_count

        if start_page < 1 or end_page > total_pages:
            raise ValueError("Page number out of range")

        if start_page > end_page:
            raise ValueError(
                "Start page cannot be greater than end page"
            )

        new_doc = fitz.open()

        try:

            # PyMuPDF uses 0-based page numbers
            new_doc.insert_pdf(
                doc,
                from_page=start_page - 1,
                to_page=end_page - 1
            )

            output_file = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".pdf"
            )

            output_path = output_file.name
            output_file.close()

            new_doc.save(output_path)

            return output_path

        finally:
            new_doc.close()

    finally:
        doc.close()