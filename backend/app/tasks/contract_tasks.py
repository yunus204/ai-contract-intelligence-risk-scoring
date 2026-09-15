from backend.app.celery_app import celery_app
from backend.app.services.document_processor import (
    process_document,
)
from backend.app.services.entity_extractor import (
    extract_entities,
)
from backend.app.services.vector_search import (
    vector_search,
)


@celery_app.task(
    bind=True,
    name="process_contract",
)
def process_contract_task(
    self,
    file_path: str,
    contract_id: str,
    original_filename: str,
):

    self.update_state(
        state="PROCESSING",
        meta={
            "stage": "document_extraction",
            "progress": 20,
        },
    )

    document = process_document(
        file_path
    )

    self.update_state(
        state="PROCESSING",
        meta={
            "stage": "entity_extraction",
            "progress": 50,
        },
    )

    entities = extract_entities(
        document["text"]
    )

    self.update_state(
        state="PROCESSING",
        meta={
            "stage": "vector_indexing",
            "progress": 75,
        },
    )

    vector_result = (
        vector_search.index_document(
            file_path=file_path,
            contract_id=contract_id,
            original_filename=original_filename,
        )
    )

    return {
        "contract_id": contract_id,
        "filename": original_filename,

        "file_type":
            document["file_type"],

        "extraction_method":
            document["extraction_method"],

        "character_count":
            document["character_count"],

        "word_count":
            document["word_count"],

        "entities": {
            "organizations":
                entities["organizations"],

            "dates":
                entities["dates"],

            "money":
                entities["money"],

            "jurisdictions":
                entities["jurisdictions"],

            "persons":
                entities["persons"],
        },

        "vector_index": {
            "indexed": True,
            "namespace":
                vector_result["namespace"],
            "chunks":
                vector_result["chunks"],
        },

        "status": "completed",
    }