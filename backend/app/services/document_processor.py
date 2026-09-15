import os
from pathlib import Path
import pymupdf
import pytesseract
from docx import Document
from dotenv import load_dotenv
from pdf2image import convert_from_path


PROJECT_ROOT = Path(__file__).resolve().parents[3]

load_dotenv(PROJECT_ROOT / ".env")


TESSERACT_CMD = os.getenv("TESSERACT_CMD")
POPPLER_PATH = os.getenv("POPPLER_PATH")


if TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
}


def clean_text(text: str) -> str:
    lines = []

    for line in text.splitlines():
        cleaned = " ".join(line.split())

        if cleaned:
            lines.append(cleaned)

    return "\n".join(lines)


def extract_pdf_text(pdf_path: Path) -> str:
    """
    Extract embedded text using PyMuPDF.
    """

    document = pymupdf.open(pdf_path)

    pages = []

    for page in document:
        text = page.get_text("text")

        if text:
            pages.append(text)

    document.close()

    return clean_text("\n".join(pages))


def extract_pdf_with_ocr(pdf_path: Path) -> str:
    """
    Convert PDF pages to images and run Tesseract OCR.
    """

    if not POPPLER_PATH:
        raise RuntimeError(
            "POPPLER_PATH is not configured in .env"
        )

    images = convert_from_path(
        str(pdf_path),
        dpi=300,
        poppler_path=POPPLER_PATH,
    )

    pages = []

    for index, image in enumerate(images, start=1):

        print(
            f"OCR processing page "
            f"{index}/{len(images)}"
        )

        text = pytesseract.image_to_string(
            image,
            lang="eng",
        )

        pages.append(text)

    return clean_text("\n".join(pages))


def extract_docx_text(docx_path: Path) -> str:
    """
    Extract text from a Microsoft Word contract.
    """

    document = Document(docx_path)

    paragraphs = [
        paragraph.text
        for paragraph in document.paragraphs
        if paragraph.text.strip()
    ]

    return clean_text("\n".join(paragraphs))


def process_document(file_path: str) -> dict:

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Document not found: {path}"
        )

    extension = path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {extension}"
        )

    extraction_method = None

    if extension == ".pdf":

        text = extract_pdf_text(path)

        # A scanned PDF usually contains almost
        # no embedded text.
        if len(text.strip()) < 100:

            print(
                "Insufficient embedded text detected."
            )

            print(
                "Falling back to Tesseract OCR..."
            )

            text = extract_pdf_with_ocr(path)

            extraction_method = "tesseract_ocr"

        else:
            extraction_method = "pymupdf"

    elif extension == ".docx":

        text = extract_docx_text(path)

        extraction_method = "python_docx"

    return {
        "filename": path.name,
        "file_type": extension,
        "extraction_method": extraction_method,
        "character_count": len(text),
        "word_count": len(text.split()),
        "text": text,
    }