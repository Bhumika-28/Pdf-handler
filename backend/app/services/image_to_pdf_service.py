import fitz
from io import BytesIO
from PIL import Image


PAGE_SIZES = {
    "A4": (595.28, 841.89),
    "LETTER": (612, 792)
}


def create_pdf_from_images(
    image_files,
    page_size="A4",
    orientation="PORTRAIT"
):
    pdf = fitz.open()

    for image_file in image_files:

        image_bytes = image_file

        # Read image dimensions
        image = Image.open(BytesIO(image_bytes))

        image_width, image_height = image.size

        # -----------------------------------------
        # FIT TO IMAGE
        # -----------------------------------------

        if page_size == "FIT":

            # Convert pixels approximately to PDF points
            page_width = image_width * 72 / 96
            page_height = image_height * 72 / 96

            page = pdf.new_page(
                width=page_width,
                height=page_height
            )

            rect = fitz.Rect(
                0,
                0,
                page_width,
                page_height
            )

        # -----------------------------------------
        # A4 / LETTER
        # -----------------------------------------

        else:

            page_width, page_height = PAGE_SIZES.get(
                page_size,
                PAGE_SIZES["A4"]
            )

            # Orientation
            if orientation == "LANDSCAPE":
                page_width, page_height = (
                    page_height,
                    page_width
                )

            elif orientation == "AUTO":

                if image_width > image_height:
                    page_width, page_height = (
                        max(page_width, page_height),
                        min(page_width, page_height)
                    )
                else:
                    page_width, page_height = (
                        min(page_width, page_height),
                        max(page_width, page_height)
                    )

            else:
                # PORTRAIT
                if page_width > page_height:
                    page_width, page_height = (
                        page_height,
                        page_width
                    )

            page = pdf.new_page(
                width=page_width,
                height=page_height
            )

            # -----------------------------------------
            # Maintain image aspect ratio
            # -----------------------------------------

            image_ratio = image_width / image_height
            page_ratio = page_width / page_height

            if image_ratio > page_ratio:

                # Image is wider
                new_width = page_width
                new_height = page_width / image_ratio

            else:

                # Image is taller
                new_height = page_height
                new_width = page_height * image_ratio

            x = (page_width - new_width) / 2
            y = (page_height - new_height) / 2

            rect = fitz.Rect(
                x,
                y,
                x + new_width,
                y + new_height
            )

        # -----------------------------------------
        # Insert image
        # -----------------------------------------

        page.insert_image(
            rect,
            stream=image_bytes,
            keep_proportion=True
        )

    # Save PDF in memory
    output = BytesIO()

    pdf.save(
        output,
        garbage=4,
        deflate=True
    )

    pdf.close()

    output.seek(0)

    return output