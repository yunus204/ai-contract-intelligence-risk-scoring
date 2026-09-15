import os
from pathlib import Path

from dotenv import load_dotenv
from pdf2image import convert_from_path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

SOURCE_PDF = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "sample_contract.pdf"
)

OUTPUT_PDF = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "scanned_contract.pdf"
)

load_dotenv(PROJECT_ROOT / ".env")

POPPLER_PATH = os.getenv("POPPLER_PATH")


def main():
    print("=" * 60)
    print("CREATE IMAGE-ONLY SCANNED PDF")
    print("=" * 60)

    if not SOURCE_PDF.exists():
        raise FileNotFoundError(
            f"Source PDF not found: {SOURCE_PDF}"
        )

    if not POPPLER_PATH:
        raise RuntimeError(
            "POPPLER_PATH is missing from .env"
        )

    poppler_path = Path(POPPLER_PATH)

    if not poppler_path.exists():
        raise FileNotFoundError(
            f"Poppler directory does not exist: {poppler_path}"
        )

    print(f"\nSource PDF : {SOURCE_PDF}")
    print(f"Poppler    : {POPPLER_PATH}")

    print("\nConverting PDF pages into images...")

    images = convert_from_path(
        str(SOURCE_PDF),
        dpi=200,
        poppler_path=POPPLER_PATH,
    )

    if not images:
        raise RuntimeError(
            "No pages were generated from the source PDF."
        )

    print(f"Pages generated: {len(images)}")

    rgb_images = [
        image.convert("RGB")
        for image in images
    ]

    first_page = rgb_images[0]

    remaining_pages = rgb_images[1:]

    first_page.save(
        str(OUTPUT_PDF),
        format="PDF",
        resolution=200,
        save_all=True,
        append_images=remaining_pages,
    )

    print("\n" + "=" * 60)
    print("SCANNED PDF CREATED SUCCESSFULLY")
    print("=" * 60)

    print(f"Pages  : {len(images)}")
    print(f"Output : {OUTPUT_PDF}")


if __name__ == "__main__":
    main()