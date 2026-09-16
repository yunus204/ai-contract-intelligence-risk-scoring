import logging

from backend.app.celery_app import (
    celery_app,
)

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


logger = logging.getLogger(
    "contract_intelligence.worker"
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
    Asynchronous contract-processing pipeline.

    Stages:
    1. Document extraction
    2. Entity extraction
    3. Clause classification
    4. Risk scoring
    5. Vector indexing
    """

    task_id = self.request.id

    logger.info(
        "Contract processing started",
        extra={
            "task_id": task_id,
            "contract_id": contract_id,
            "stage": "started",
        },
    )

    try:
        # ---------------------------------------------
        # Stage 1: Document extraction
        # ---------------------------------------------

        self.update_state(
            state="PROCESSING",
            meta={
                "stage":
                    "document_extraction",

                "progress":
                    20,
            },
        )

        logger.info(
            "Document extraction started",
            extra={
                "task_id":
                    task_id,

                "contract_id":
                    contract_id,

                "stage":
                    "document_extraction",
            },
        )

        document = process_document(
            file_path
        )

        document_text = document[
            "text"
        ]

        logger.info(
            "Document extraction completed",
            extra={
                "task_id":
                    task_id,

                "contract_id":
                    contract_id,

                "stage":
                    "document_extraction",
            },
        )


        # ---------------------------------------------
        # Stage 2: Entity extraction
        # ---------------------------------------------

        self.update_state(
            state="PROCESSING",
            meta={
                "stage":
                    "entity_extraction",

                "progress":
                    45,
            },
        )

        logger.info(
            "Entity extraction started",
            extra={
                "task_id":
                    task_id,

                "contract_id":
                    contract_id,

                "stage":
                    "entity_extraction",
            },
        )

        entities = extract_entities(
            document_text
        )

        logger.info(
            "Entity extraction completed",
            extra={
                "task_id":
                    task_id,

                "contract_id":
                    contract_id,

                "stage":
                    "entity_extraction",
            },
        )


        # ---------------------------------------------
        # Stage 3: Clause classification
        # ---------------------------------------------

        self.update_state(
            state="PROCESSING",
            meta={
                "stage":
                    "clause_classification",

                "progress":
                    65,
            },
        )

        logger.info(
            "Clause classification started",
            extra={
                "task_id":
                    task_id,

                "contract_id":
                    contract_id,

                "stage":
                    "clause_classification",
            },
        )

        clause_analysis = (
            clause_classifier.analyze(
                document_text
            )
        )

        logger.info(
            "Clause classification completed",
            extra={
                "task_id":
                    task_id,

                "contract_id":
                    contract_id,

                "stage":
                    "clause_classification",
            },
        )


        # ---------------------------------------------
        # Stage 4: Risk scoring
        # ---------------------------------------------

        self.update_state(
            state="PROCESSING",
            meta={
                "stage":
                    "risk_scoring",

                "progress":
                    75,
            },
        )

        logger.info(
            "Risk scoring started",
            extra={
                "task_id":
                    task_id,

                "contract_id":
                    contract_id,

                "stage":
                    "risk_scoring",
            },
        )

        risk_analysis = (
            score_contract_risk(
                clause_analysis[
                    "detected_clauses"
                ]
            )
        )

        logger.info(
            "Risk scoring completed",
            extra={
                "task_id":
                    task_id,

                "contract_id":
                    contract_id,

                "stage":
                    "risk_scoring",
            },
        )


        # ---------------------------------------------
        # Stage 5: Vector indexing
        # ---------------------------------------------

        self.update_state(
            state="PROCESSING",
            meta={
                "stage":
                    "vector_indexing",

                "progress":
                    85,
            },
        )

        logger.info(
            "Vector indexing started",
            extra={
                "task_id":
                    task_id,

                "contract_id":
                    contract_id,

                "stage":
                    "vector_indexing",
            },
        )

        vector_result = (
            vector_search.index_document(
                file_path=file_path,
                contract_id=contract_id,
                original_filename=original_filename,
            )
        )

        logger.info(
            "Vector indexing completed",
            extra={
                "task_id":
                    task_id,

                "contract_id":
                    contract_id,

                "stage":
                    "vector_indexing",
            },
        )


        # ---------------------------------------------
        # Finalizing
        # ---------------------------------------------

        self.update_state(
            state="PROCESSING",
            meta={
                "stage":
                    "finalizing",

                "progress":
                    95,
            },
        )

        result = {
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

        logger.info(
            "Contract processing completed",
            extra={
                "task_id":
                    task_id,

                "contract_id":
                    contract_id,

                "stage":
                    "completed",
            },
        )

        return result

    except Exception:
        logger.exception(
            "Contract processing failed",
            extra={
                "task_id":
                    task_id,

                "contract_id":
                    contract_id,

                "stage":
                    "failed",
            },
        )

        raise