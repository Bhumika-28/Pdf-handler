import fitz
import os
import zipfile


def convert_pdf_to_images(
    input_path: str,
    output_dir: str,
    image_format: str = "png",
    dpi: int = 150
):
    """
    Convert every page of a PDF into an image.

    Returns:
        List of generated image paths.
    """

    os.makedirs(output_dir, exist_ok=True)

    doc = fitz.open(input_path)

    image_paths = []

    try:

        # Convert DPI to PyMuPDF scale
        zoom = dpi / 72

        matrix = fitz.Matrix(zoom, zoom)

        for page_number in range(doc.page_count):

            page = doc.load_page(page_number)

            pix = page.get_pixmap(
                matrix=matrix,
                alpha=False
            )

            if image_format.lower() == "jpg":

                output_path = os.path.join(
                    output_dir,
                    f"page_{page_number + 1}.jpg"
                )

                pix.save(
                    output_path,
                    output="jpeg"
                )

            else:

                output_path = os.path.join(
                    output_dir,
                    f"page_{page_number + 1}.png"
                )

                pix.save(output_path)

            image_paths.append(output_path)

    finally:

        doc.close()

    return image_paths


def create_zip(
    image_paths,
    zip_path
):
    """
    Create ZIP containing all generated images.
    """

    with zipfile.ZipFile(
        zip_path,
        "w",
        zipfile.ZIP_DEFLATED
    ) as zip_file:

        for image_path in image_paths:

            zip_file.write(
                image_path,
                arcname=os.path.basename(image_path)
            )

    return zip_path