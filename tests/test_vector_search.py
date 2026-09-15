import sys
from pathlib import Path


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

sys.path.insert(
    0,
    str(PROJECT_ROOT),
)


from backend.app.services.vector_search import (
    vector_search,
)


def main():

    if len(sys.argv) < 2:
        print(
            "Usage: python "
            "tests/test_vector_search.py "
            "<document>"
        )
        return

    file_path = sys.argv[1]

    print("\nINDEXING DOCUMENT\n")

    result = (
        vector_search
        .index_document(
            file_path
        )
    )

    print("\n" + "=" * 60)
    print("INDEXING RESULT")
    print("=" * 60)

    print(
        f"Contract ID : "
        f"{result['contract_id']}"
    )

    print(
        f"Filename    : "
        f"{result['filename']}"
    )

    print(
        f"Chunks      : "
        f"{result['chunks']}"
    )

    print(
        f"Extraction  : "
        f"{result['extraction_method']}"
    )

    query = (
        "What does the document say "
        "about contract risk and "
        "legal clauses?"
    )

    print("\n" + "=" * 60)
    print("SEMANTIC SEARCH")
    print("=" * 60)

    print(
        f"\nQuery:\n{query}"
    )

    results = (
        vector_search.search(
            query=query,
            contract_id=
                result["contract_id"],
            top_k=3,
        )
    )

    for item in results:

        print(
            "\n" + "-" * 60
        )

        print(
            f"Rank  : "
            f"{item['rank']}"
        )

        print(
            f"Score : "
            f"{item['score']:.4f}"
        )

        print(
            f"Chunk : "
            f"{item['metadata'].get('chunk_index')}"
        )

        print("\nText:")

        print(
            item["text"][:1000]
        )

    print("\n" + "=" * 60)
    print("VECTOR SEARCH TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()