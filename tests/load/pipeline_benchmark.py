import time
from pathlib import Path

import requests


BASE_URL = "http://127.0.0.1:8000"

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)

SAMPLE_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "sample_contract.pdf"
)

RUNS = 3


def upload_contract():
    start = time.perf_counter()

    with SAMPLE_FILE.open("rb") as file:
        response = requests.post(
            f"{BASE_URL}/api/contracts/upload",
            files={
                "file": (
                    SAMPLE_FILE.name,
                    file,
                    "application/pdf",
                )
            },
            timeout=30,
        )

    response.raise_for_status()

    elapsed = (
        time.perf_counter()
        - start
    )

    return (
        response.json(),
        elapsed,
    )


def wait_for_task(task_id):
    start = time.perf_counter()

    while True:
        response = requests.get(
            (
                f"{BASE_URL}/api/contracts/"
                f"tasks/{task_id}"
            ),
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        status = data.get(
            "status"
        )

        if status == "SUCCESS":
            return (
                data,
                time.perf_counter()
                - start,
            )

        if status == "FAILURE":
            raise RuntimeError(
                data.get(
                    "error",
                    "Task failed.",
                )
            )

        time.sleep(1)


def main():
    if not SAMPLE_FILE.exists():
        raise FileNotFoundError(
            f"Sample contract not found: "
            f"{SAMPLE_FILE}"
        )

    total_times = []

    for run in range(
        1,
        RUNS + 1,
    ):
        print(
            f"\nRun {run}/{RUNS}"
        )

        upload_data, upload_time = (
            upload_contract()
        )

        task_id = upload_data[
            "task_id"
        ]

        print(
            f"Queued in: "
            f"{upload_time:.3f}s"
        )

        print(
            f"Task ID: {task_id}"
        )

        result, processing_time = (
            wait_for_task(task_id)
        )

        total_time = (
            upload_time
            + processing_time
        )

        total_times.append(
            total_time
        )

        print(
            f"Processing: "
            f"{processing_time:.2f}s"
        )

        print(
            f"Total: "
            f"{total_time:.2f}s"
        )

        print(
            "Result:",
            result["status"],
        )

    average = (
        sum(total_times)
        / len(total_times)
    )

    print(
        "\n-------------------------"
    )

    print(
        f"Average end-to-end time: "
        f"{average:.2f}s"
    )

    print(
        f"Fastest: "
        f"{min(total_times):.2f}s"
    )

    print(
        f"Slowest: "
        f"{max(total_times):.2f}s"
    )


if __name__ == "__main__":
    main()