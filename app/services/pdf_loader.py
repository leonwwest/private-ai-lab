from io import BytesIO

from pypdf import PdfReader


def extract_pdf_text(raw_pdf: bytes) -> str:
    reader = PdfReader(BytesIO(raw_pdf))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    text = text.strip()
    if not text:
        raise ValueError("PDF contains no extractable text")
    return text
