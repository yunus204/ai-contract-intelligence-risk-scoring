import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(
    0,
    str(PROJECT_ROOT),
)


from backend.app.services.document_processor import (
    process_document,
)

from backend.app.services.entity_extractor import (
    extract_entities,
)


def print_section(title, values):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

    if not values:
        print("None detected")
        return

    for value in values:
        print(f"- {value}")


def main():
    if len(sys.argv) < 2:
        print(
            "Usage: python "
            "tests/test_entity_extractor.py "
            "<document>"
        )
        return

    document_path = sys.argv[1]

    try:
        document = process_document(
            document_path
        )

    except Exception as error:
        print(f"ERROR: {error}")
        return

    print("=" * 60)
    print("CONTRACT ENTITY EXTRACTION")
    print("=" * 60)

    print(
        f"Document          : "
        f"{document['filename']}"
    )

    print(
        f"Extraction method : "
        f"{document['extraction_method']}"
    )

    print(
        f"Words             : "
        f"{document['word_count']}"
    )

    print("\nRunning spaCy NER...")

    entities = extract_entities(
        document["text"]
    )

    print_section(
        "ORGANIZATIONS",
        entities["organizations"],
    )

    print_section(
        "DATES",
        entities["dates"],
    )

    print_section(
        "MONETARY VALUES",
        entities["money"],
    )

    print_section(
        "PERSONS",
        entities["persons"],
    )

    print_section(
        "JURISDICTIONS / LOCATIONS",
        entities["jurisdictions"],
    )

    summary = {
        "organizations":
            len(entities["organizations"]),

        "dates":
            len(entities["dates"]),

        "money":
            len(entities["money"]),

        "persons":
            len(entities["persons"]),

        "jurisdictions":
            len(entities["jurisdictions"]),

        "total_entities":
            len(entities["all_entities"]),
    }

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    print(
        json.dumps(
            summary,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()