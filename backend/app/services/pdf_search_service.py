import fitz


def search_pdf(file_path: str, search_text: str):
    """
    Search for text inside a PDF.

    Returns:
        {
            "query": search_text,
            "total_matches": int,
            "results": [
                {
                    "page": int,
                    "matches": int
                }
            ]
        }
    """

    doc = fitz.open(file_path)

    results = []
    total_matches = 0

    try:
        for page_number in range(doc.page_count):

            page = doc.load_page(page_number)

            matches = page.search_for(search_text)

            if matches:
                match_count = len(matches)

                results.append({
                    "page": page_number + 1,
                    "matches": match_count
                })

                total_matches += match_count

    finally:
        doc.close()

    return {
        "query": search_text,
        "total_matches": total_matches,
        "results": results
    }