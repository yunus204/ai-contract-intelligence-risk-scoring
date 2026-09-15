import os

from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec


load_dotenv()


API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv(
    "PINECONE_INDEX_NAME",
    "contract-intelligence",
)

EMBEDDING_DIMENSION = 384


def main():

    if not API_KEY:
        raise RuntimeError(
            "PINECONE_API_KEY is missing from .env"
        )

    pc = Pinecone(
        api_key=API_KEY
    )

    print("=" * 60)
    print("PINECONE INDEX SETUP")
    print("=" * 60)

    print(
        f"\nIndex name : {INDEX_NAME}"
    )

    if pc.has_index(INDEX_NAME):

        print(
            "Index already exists."
        )

    else:

        print(
            "Creating Pinecone index..."
        )

        pc.create_index(
            name=INDEX_NAME,
            vector_type="dense",
            dimension=EMBEDDING_DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1",
            ),
            deletion_protection="disabled",
            tags={
                "project":
                    "contract-intelligence"
            },
        )

        print(
            "Index creation requested."
        )

    description = pc.describe_index(
        INDEX_NAME
    )

    print("\nIndex status:")
    print(
        f"Ready     : "
        f"{description.status['ready']}"
    )

    print(
        f"State     : "
        f"{description.status['state']}"
    )

    print(
        f"Dimension : "
        f"{description.dimension}"
    )

    print(
        f"Metric    : "
        f"{description.metric}"
    )


if __name__ == "__main__":
    main()