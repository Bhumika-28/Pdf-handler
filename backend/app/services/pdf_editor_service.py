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


# ============================================================
# PDF EDITOR FUNCTIONS
# ============================================================


def delete_pages(
    file_path: str,
    page_numbers: list[int]
):
    """
    Delete selected pages from PDF.

    page_numbers are 1-based.

    Example:
        delete_pages(file_path, [2, 4])
    """

    doc = fitz.open(file_path)

    try:

        total_pages = doc.page_count

        if not page_numbers:
            raise ValueError("No pages selected")

        # Remove duplicates
        page_numbers = list(set(page_numbers))

        # Validate pages
        for page_number in page_numbers:

            if page_number < 1 or page_number > total_pages:
                raise ValueError(
                    f"Page {page_number} does not exist"
                )

        # Don't allow deleting all pages
        if len(page_numbers) >= total_pages:
            raise ValueError(
                "Cannot delete all pages from the PDF"
            )

        # PyMuPDF deletes using 0-based indexes.
        # Delete from highest to lowest so indexes
        # don't shift.
        indexes = sorted(
            [page - 1 for page in page_numbers],
            reverse=True
        )

        for index in indexes:
            doc.delete_page(index)

        output_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        )

        output_path = output_file.name
        output_file.close()

        doc.save(output_path)

        return output_path

    finally:
        doc.close()


def rotate_page(
    file_path: str,
    page_number: int,
    rotation: int
):
    """
    Rotate a single PDF page.

    page_number is 1-based.

    rotation:
        90   -> clockwise
        -90  -> counter-clockwise
    """

    doc = fitz.open(file_path)

    try:

        if page_number < 1 or page_number > doc.page_count:
            raise ValueError(
                "Page number out of range"
            )

        if rotation not in [90, -90, 180]:
            raise ValueError(
                "Rotation must be 90, -90 or 180"
            )

        page = doc.load_page(
            page_number - 1
        )

        current_rotation = page.rotation

        new_rotation = (
            current_rotation + rotation
        ) % 360

        page.set_rotation(
            new_rotation
        )

        output_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        )

        output_path = output_file.name
        output_file.close()

        doc.save(output_path)

        return output_path

    finally:
        doc.close()


def insert_pdf(
    file_path: str,
    insert_file_path: str,
    position: int
):
    """
    Insert another PDF into the current PDF.

    position is 1-based.

    Example:
        position = 3

    means the inserted PDF will appear
    before page 3.
    """

    doc = fitz.open(file_path)
    insert_doc = fitz.open(insert_file_path)

    try:

        if position < 1 or position > doc.page_count + 1:
            raise ValueError(
                "Insert position out of range"
            )

        # Convert 1-based position to 0-based
        insert_at = position - 1

        doc.insert_pdf(
            insert_doc,
            start_at=insert_at
        )

        output_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        )

        output_path = output_file.name
        output_file.close()

        doc.save(output_path)

        return output_path

    finally:
        insert_doc.close()
        doc.close()