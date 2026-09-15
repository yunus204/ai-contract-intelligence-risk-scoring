import hashlib
import os
from pathlib import Path
from typing import Dict, List

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone import Pinecone

from backend.app.services.document_processor import (
    process_document,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]

load_dotenv(PROJECT_ROOT / ".env")


PINECONE_API_KEY = os.getenv(
    "PINECONE_API_KEY"
)

PINECONE_INDEX_NAME = os.getenv(
    "PINECONE_INDEX_NAME",
    "contract-intelligence",
)


EMBEDDING_MODEL = (
    "sentence-transformers/all-MiniLM-L6-v2"
)

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200


class ContractVectorSearch:
    """
    Semantic search service for legal contracts.

    Pipeline:
        Document
        -> Text extraction
        -> LangChain chunks
        -> Hugging Face embeddings
        -> Pinecone
        -> Semantic retrieval
    """

    def __init__(self):

        if not PINECONE_API_KEY:
            raise RuntimeError(
                "PINECONE_API_KEY is missing from .env"
            )

        self.pc = Pinecone(
            api_key=PINECONE_API_KEY
        )

        self.index = self.pc.Index(
            PINECONE_INDEX_NAME
        )

        print(
            f"Loading embedding model: "
            f"{EMBEDDING_MODEL}"
        )

        self.embeddings = (
            HuggingFaceEmbeddings(
                model_name=EMBEDDING_MODEL,
                model_kwargs={
                    "device": "cpu"
                },
                encode_kwargs={
                    "normalize_embeddings": True
                },
            )
        )

        self.text_splitter = (
            RecursiveCharacterTextSplitter(
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP,
                separators=[
                    "\n\n",
                    "\n",
                    ". ",
                    " ",
                    "",
                ],
            )
        )

    @staticmethod
    def _create_contract_id(
        filename: str,
    ) -> str:

        return hashlib.sha256(
            filename.encode("utf-8")
        ).hexdigest()[:16]

    @staticmethod
    def _create_vector_id(
        contract_id: str,
        chunk_index: int,
    ) -> str:

        return (
            f"{contract_id}-"
            f"{chunk_index:05d}"
        )

    def _get_vector_store(
        self,
        namespace: str,
    ) -> PineconeVectorStore:

        return PineconeVectorStore(
            index=self.index,
            embedding=self.embeddings,
            namespace=namespace,
        )

    def index_document(
        self,
        file_path: str,
        contract_id: str | None = None,
        original_filename: str | None = None,
)       -> Dict:

        print("=" * 60)
        print("CONTRACT VECTOR INDEXING")
        print("=" * 60)

        result = process_document(
            file_path
        )

        text = result["text"]

        if not text.strip():
            raise ValueError(
                "No text could be extracted "
                "from the document."
            )

        filename = (
        original_filename
        or result["filename"]
)

        if contract_id is None:
            contract_id = (
        self._create_contract_id(
            filename
        )
    )

        namespace = contract_id

        print(
            f"\nDocument   : {filename}"
        )

        print(
            f"Contract ID: {contract_id}"
        )

        print(
            f"Extraction : "
            f"{result['extraction_method']}"
        )

        print(
            f"Characters : "
            f"{result['character_count']}"
        )

        print("\nCreating LangChain chunks...")

        chunks = (
            self.text_splitter
            .split_text(text)
        )

        print(
            f"Chunks created: {len(chunks)}"
        )

        documents: List[Document] = []

        ids: List[str] = []

        for chunk_index, chunk in enumerate(
            chunks
        ):

            document = Document(
                page_content=chunk,
                metadata={
                    "contract_id":
                        contract_id,

                    "filename":
                        filename,

                    "chunk_index":
                        chunk_index,

                    "file_type":
                        result["file_type"],

                    "extraction_method":
                        result[
                            "extraction_method"
                        ],
                },
            )

            documents.append(
                document
            )

            ids.append(
                self._create_vector_id(
                    contract_id,
                    chunk_index,
                )
            )

        vector_store = (
            self._get_vector_store(
                namespace
            )
        )

        print(
            "\nGenerating embeddings "
            "and uploading to Pinecone..."
        )

        vector_store.add_documents(
            documents=documents,
            ids=ids,
        )

        print(
            "Pinecone upload complete."
        )

        return {
            "contract_id": contract_id,
            "namespace": namespace,
            "filename": filename,
            "chunks": len(chunks),
            "characters":
                result["character_count"],
            "words":
                result["word_count"],
            "extraction_method":
                result["extraction_method"],
        }

    def search(
        self,
        query: str,
        contract_id: str,
        top_k: int = 5,
    ) -> List[Dict]:

        if not query.strip():
            raise ValueError(
                "Search query cannot be empty."
            )

        vector_store = (
            self._get_vector_store(
                contract_id
            )
        )

        results = (
            vector_store
            .similarity_search_with_score(
                query=query,
                k=top_k,
            )
        )

        formatted_results = []

        for rank, (
            document,
            score,
        ) in enumerate(
            results,
            start=1,
        ):

            formatted_results.append(
                {
                    "rank": rank,
                    "score": float(score),
                    "text":
                        document.page_content,
                    "metadata":
                        document.metadata,
                }
            )

        return formatted_results


vector_search = ContractVectorSearch()