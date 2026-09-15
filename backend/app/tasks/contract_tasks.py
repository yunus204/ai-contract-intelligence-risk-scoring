from backend.app.celery_app import celery_app

from backend.app.services.document_processor import (
    process_document,
)

from backend.app.services.entity_extractor import (
    extract_entities,
)

from backend.app.services.clause_classifier import (
    clause_classifier,
)

from backend.app.services.risk_scoring import (
    score_contract_risk,
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
    """
    Complete asynchronous contract-processing pipeline.

    Stages:
    1. Document extraction
    2. Entity extraction
    3. Clause classification
    4. Risk scoring
    5. Pinecone vector indexing
    """

    # --------------------------------------------------
    # Stage 1: Document extraction
    # --------------------------------------------------

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

    document_text = document[
        "text"
    ]

    # --------------------------------------------------
    # Stage 2: Entity extraction
    # --------------------------------------------------

    self.update_state(
        state="PROCESSING",
        meta={
            "stage": "entity_extraction",
            "progress": 45,
        },
    )

    entities = extract_entities(
        document_text
    )

    # --------------------------------------------------
    # Stage 3: Clause classification
    # --------------------------------------------------

    self.update_state(
        state="PROCESSING",
        meta={
            "stage": "clause_classification",
            "progress": 65,
        },
    )

    clause_analysis = (
        clause_classifier.analyze(
            document_text
        )
    )

    # --------------------------------------------------
    # Stage 4: Risk scoring
    # --------------------------------------------------

    self.update_state(
        state="PROCESSING",
        meta={
            "stage": "risk_scoring",
            "progress": 75,
        },
    )

    risk_analysis = (
        score_contract_risk(
            clause_analysis[
                "detected_clauses"
            ]
        )
    )

    # --------------------------------------------------
    # Stage 5: Pinecone vector indexing
    # --------------------------------------------------

    self.update_state(
        state="PROCESSING",
        meta={
            "stage": "vector_indexing",
            "progress": 85,
        },
    )

    vector_result = (
        vector_search.index_document(
            file_path=file_path,
            contract_id=contract_id,
            original_filename=original_filename,
        )
    )

    # --------------------------------------------------
    # Final result
    # --------------------------------------------------

    self.update_state(
        state="PROCESSING",
        meta={
            "stage": "finalizing",
            "progress": 95,
        },
    )

    return {
        "contract_id":
            contract_id,

        "filename":
            original_filename,

        "file_type":
            document[
                "file_type"
            ],

        "extraction_method":
            document[
                "extraction_method"
            ],

        "character_count":
            document[
                "character_count"
            ],

        "word_count":
            document[
                "word_count"
            ],

        "entities": {
            "organizations":
                entities[
                    "organizations"
                ],

            "dates":
                entities[
                    "dates"
                ],

            "money":
                entities[
                    "money"
                ],

            "jurisdictions":
                entities[
                    "jurisdictions"
                ],

            "persons":
                entities[
                    "persons"
                ],
        },

        "clause_analysis":
            clause_analysis,

        "risk_analysis":
            risk_analysis,

        "vector_index": {
            "indexed":
                True,

            "namespace":
                vector_result[
                    "namespace"
                ],

            "chunks":
                vector_result[
                    "chunks"
                ],
        },

        "status":
            "completed",
    }