import sys
from pathlib import Path


PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]

sys.path.insert(
    0,
    str(PROJECT_ROOT),
)


from backend.app.services.entity_extractor import (
    extract_entities,
)


TEST_CONTRACT = """
SERVICE AGREEMENT

This Service Agreement is entered into between
Acme Corporation and Global Technologies Ltd.
on January 15, 2026.

Acme Corporation shall provide software
development and consulting services to
Global Technologies Ltd.

The total consideration payable under this
Agreement is $250,000.

Payment shall be made within thirty days of
receipt of invoice.

This Agreement shall be governed by and
construed in accordance with the laws of
the State of California.

The Agreement will terminate on
December 31, 2028.
"""


def main():

    result = extract_entities(
        TEST_CONTRACT
    )

    print("=" * 60)
    print("LEGAL NER TEST")
    print("=" * 60)

    print("\nOrganizations:")
    for item in result["organizations"]:
        print(f"- {item}")

    print("\nDates:")
    for item in result["dates"]:
        print(f"- {item}")

    print("\nMoney:")
    for item in result["money"]:
        print(f"- {item}")

    print("\nJurisdictions:")
    for item in result["jurisdictions"]:
        print(f"- {item}")


if __name__ == "__main__":
    main()