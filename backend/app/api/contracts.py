import shutil
import uuid
from pathlib import Path

from celery.result import AsyncResult
from fastapi import (
    APIRouter,
    File,
    HTTPException,
    UploadFile,
    status,
)

from backend.app.celery_app import celery_app



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


@router.post(
    "/upload",
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_contract(
    file: UploadFile = File(...),
):
    """
    Save the uploaded contract and submit
    background processing to Celery.
    """

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

        task = celery_app.send_task(
            "process_contract",
            args=[
            str(destination),
            contract_id,
            filename,
    ],
)

    except Exception as error:

        if destination.exists():
            destination.unlink()

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

    finally:
        await file.close()

    return {
        "contract_id": contract_id,
        "filename": filename,
        "task_id": task.id,
        "status": "queued",
        "message": (
            "Contract uploaded successfully. "
            "Processing has started in the background."
        ),
    }


@router.get(
    "/tasks/{task_id}",
)
def get_task_status(
    task_id: str,
):
    """
    Check Celery processing status and
    retrieve the completed analysis.
    """

    task = AsyncResult(
        task_id,
        app=celery_app,
    )

    response = {
        "task_id": task_id,
        "status": task.state,
    }

    if task.state == "PENDING":

        response["message"] = (
            "Task is waiting to be processed."
        )

    elif task.state == "STARTED":

        response["message"] = (
            "Contract processing has started."
        )

    elif task.state == "PROCESSING":

        info = (
            task.info
            if isinstance(task.info, dict)
            else {}
        )

        response["stage"] = (
            info.get("stage")
        )

        response["progress"] = (
            info.get("progress", 0)
        )

    elif task.state == "SUCCESS":

        response["status"] = "SUCCESS"
        response["result"] = task.result

    elif task.state == "FAILURE":

        response["status"] = "FAILURE"
        response["error"] = str(
            task.info
        )

    else:

        response["message"] = (
            f"Task state: {task.state}"
        )

    return response