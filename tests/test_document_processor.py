import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(
    0,
    str(PROJECT_ROOT)
)


from backend.app.services.document_processor import process_document


def main():
    if len(sys.argv) < 2:
        print(
            "Usage:\n"
            "python tests/test_document_processor.py "
            "<path_to_document>"
        )
        return

    document_path = sys.argv[1]

    try:
        result = process_document(document_path)

    except FileNotFoundError as error:
        print(f"\nERROR: {error}")
        return

    except ValueError as error:
        print(f"\nERROR: {error}")
        return

    except Exception as error:
        print(f"\nUnexpected error: {error}")
        return

    print("=" * 60)
    print("DOCUMENT PROCESSING RESULT")
    print("=" * 60)

    print(
        f"Filename          : "
        f"{result['filename']}"
    )

    print(
        f"Type              : "
        f"{result['file_type']}"
    )

    print(
        f"Extraction method : "
        f"{result['extraction_method']}"
    )

    print(
        f"Characters        : "
        f"{result['character_count']}"
    )

    print(
        f"Words             : "
        f"{result['word_count']}"
    )

    print("\nTEXT PREVIEW")
    print("-" * 60)

    text = result["text"]

    if text:
        print(text[:2000])
    else:
        print("No text was extracted from the document.")

    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()