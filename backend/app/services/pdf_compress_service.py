import fitz


def compress_pdf(input_path: str, output_path: str, quality: str = "medium"):
    """
    Compress a PDF using PyMuPDF.

    quality:
        low    -> higher compression, lower image quality
        medium -> balanced
        high   -> better quality, less compression
    """

    doc = fitz.open(input_path)

    if quality == "low":
        image_quality = 50
    elif quality == "high":
        image_quality = 85
    else:
        image_quality = 70

    try:

        for page in doc:

            images = page.get_images(full=True)

            for image in images:

                xref = image[0]

                try:
                    pix = fitz.Pixmap(doc, xref)

                    # Skip CMYK / unsupported images
                    if pix.n - pix.alpha > 3:
                        pix = fitz.Pixmap(fitz.csRGB, pix)

                    # Resize very large images
                    max_dimension = 1800

                    if max(pix.width, pix.height) > max_dimension:

                        scale = max_dimension / max(
                            pix.width,
                            pix.height
                        )

                        new_width = int(pix.width * scale)
                        new_height = int(pix.height * scale)

                        pix = fitz.Pixmap(
                            pix,
                            new_width,
                            new_height
                        )

                    # Replace image
                    page.replace_image(
                        xref,
                        pixmap=pix
                    )

                except Exception:
                    # Continue if individual image cannot be processed
                    continue

        # Save with optimization
        doc.save(
            output_path,
            garbage=4,
            clean=True,
            deflate=True,
            deflate_images=True,
            deflate_fonts=True
        )

    finally:
        doc.close()