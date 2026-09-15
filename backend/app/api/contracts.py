import shutil
import uuid
from pathlib import Path
from backend.app.services.vector_search import (
    vector_search,
)
from fastapi import (
    APIRouter,
    File,
    HTTPException,
    UploadFile,
)

from backend.app.services.document_processor import (
    process_document,
)

from backend.app.services.entity_extractor import (
    extract_entities,
)


router = APIRouter(
    prefix="/api/contracts",
    tags=["Contracts"],
)


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[3]
)

UPLOAD_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "uploads"
)

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
}


@router.post("/upload")
async def upload_contract(
    file: UploadFile = File(...),
):

    filename = file.filename

    if not filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    extension = (
        Path(filename)
        .suffix
        .lower()
    )

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Only PDF and DOCX "
                "documents are supported."
            ),
        )

    contract_id = str(
        uuid.uuid4()
    )

    stored_filename = (
        f"{contract_id}{extension}"
    )

    destination = (
        UPLOAD_DIR
        / stored_filename
    )

    try:
        with destination.open(
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer,
            )

        result = process_document(
            str(destination)
        )

        entities = extract_entities(
            result["text"]
        )
        vector_result = (
            vector_search.index_document(
            file_path=str(destination),
            contract_id=contract_id,
            original_filename=filename,
    )
)

    except Exception as error:

        if destination.exists():
            destination.unlink()

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

    return {
        "contract_id": contract_id,

        "filename": filename,

        "file_type":
            result["file_type"],

        "extraction_method":
            result[
                "extraction_method"
            ],

        "character_count":
            result[
                "character_count"
            ],

        "word_count":
            result[
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
    }