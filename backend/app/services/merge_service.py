from io import BytesIO

from pypdf import PdfReader, PdfWriter


def merge_pdfs(files):

    writer = PdfWriter()

    for file in files:

        file_content = file.file.read()

        reader = PdfReader(
            BytesIO(file_content)
        )

        for page in reader.pages:
            writer.add_page(page)

    output = BytesIO()

    writer.write(output)

    output.seek(0)

    return output