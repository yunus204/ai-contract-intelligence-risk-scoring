import json
from collections import defaultdict
from pathlib import Path

from transformers import AutoTokenizer


PROJECT_ROOT = Path(__file__).resolve().parents[3]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "cuad_examples.jsonl"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "classification"
)

OUTPUT_FILE = OUTPUT_DIR / "cuad_classification.jsonl"
STATS_FILE = OUTPUT_DIR / "classification_stats.json"

MODEL_NAME = "roberta-base"

MAX_LENGTH = 512

# Character-based chunking avoids losing CUAD character offsets.
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200
CHUNK_STEP = CHUNK_SIZE - CHUNK_OVERLAP


def load_examples():
    examples = []

    with INPUT_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        for line in file:
            examples.append(json.loads(line))

    return examples


def group_contracts(examples):
    contracts = {}

    for example in examples:
        title = example["contract_title"]

        if title not in contracts:
            contracts[title] = {
                "context": example["context"],
                "annotations": [],
            }

        for text, start in zip(
            example["answers"],
            example["answer_starts"],
        ):
            if start < 0:
                continue

            annotation = {
                "label_id": example["label_id"],
                "start": start,
                "end": start + len(text),
                "text": text,
            }

            contracts[title]["annotations"].append(
                annotation
            )

    # Remove duplicate annotations.
    for contract in contracts.values():

        unique = {}

        for annotation in contract["annotations"]:
            key = (
                annotation["label_id"],
                annotation["start"],
                annotation["end"],
                annotation["text"],
            )

            unique[key] = annotation

        contract["annotations"] = list(
            unique.values()
        )

    return contracts


def generate_character_windows(text):
    windows = []

    text_length = len(text)

    start = 0
    window_index = 0

    while start < text_length:

        end = min(
            start + CHUNK_SIZE,
            text_length,
        )

        windows.append(
            {
                "window_index": window_index,
                "start": start,
                "end": end,
                "text": text[start:end],
            }
        )

        if end == text_length:
            break

        start += CHUNK_STEP
        window_index += 1

    return windows


def find_window_labels(
    window_start,
    window_end,
    annotations,
):
    labels = set()
    matched_annotations = []

    for annotation in annotations:

        overlap_start = max(
            window_start,
            annotation["start"],
        )

        overlap_end = min(
            window_end,
            annotation["end"],
        )

        # Character ranges actually overlap.
        if overlap_start < overlap_end:

            labels.add(
                annotation["label_id"]
            )

            matched_annotations.append(
                {
                    "label_id":
                        annotation["label_id"],
                    "start":
                        annotation["start"],
                    "end":
                        annotation["end"],
                }
            )

    return (
        sorted(labels),
        matched_annotations,
    )


def build_dataset(
    contracts,
    tokenizer,
):
    records = []

    label_counts = defaultdict(int)

    positive_windows = 0
    negative_windows = 0

    total_contracts = len(contracts)

    for contract_number, (
        contract_title,
        contract_data,
    ) in enumerate(
        contracts.items(),
        start=1,
    ):

        context = contract_data["context"]
        annotations = contract_data["annotations"]

        windows = generate_character_windows(
            context
        )

        for window in windows:

            labels, matched = find_window_labels(
                window["start"],
                window["end"],
                annotations,
            )

            encoding = tokenizer(
                window["text"],
                max_length=MAX_LENGTH,
                truncation=True,
                padding="max_length",
                return_attention_mask=True,
            )

            if labels:
                positive_windows += 1

                for label_id in labels:
                    label_counts[label_id] += 1

            else:
                negative_windows += 1

            records.append(
                {
                    "contract_title":
                        contract_title,

                    "window_index":
                        window["window_index"],

                    "window_start":
                        window["start"],

                    "window_end":
                        window["end"],

                    "text":
                        window["text"],

                    "labels":
                        labels,

                    "is_positive":
                        bool(labels),

                    "matched_annotations":
                        matched,

                    "input_ids":
                        encoding["input_ids"],

                    "attention_mask":
                        encoding["attention_mask"],
                }
            )

        if contract_number % 25 == 0:
            print(
                f"Processed "
                f"{contract_number}/"
                f"{total_contracts} contracts"
            )

    return (
        records,
        positive_windows,
        negative_windows,
        label_counts,
    )


def save_dataset(records):
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:

        for record in records:

            file.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                )
                + "\n"
            )


def save_stats(
    contracts,
    records,
    positive_windows,
    negative_windows,
    label_counts,
):
    stats = {
        "model_name": MODEL_NAME,
        "max_length": MAX_LENGTH,

        "chunk_size_characters":
            CHUNK_SIZE,

        "chunk_overlap_characters":
            CHUNK_OVERLAP,

        "contracts":
            len(contracts),

        "total_windows":
            len(records),

        "positive_windows":
            positive_windows,

        "negative_windows":
            negative_windows,

        "labels_present":
            len(label_counts),

        "label_distribution":
            dict(
                sorted(label_counts.items())
            ),
    }

    with STATS_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            stats,
            file,
            indent=2,
        )

    return stats


def main():
    print("=" * 60)
    print("CUAD CLAUSE CLASSIFICATION DATASET")
    print("=" * 60)

    examples = load_examples()

    print(
        f"\nLoaded {len(examples)} QA examples."
    )

    contracts = group_contracts(
        examples
    )

    print(
        f"Reconstructed "
        f"{len(contracts)} contracts."
    )

    print(
        f"\nLoading tokenizer: "
        f"{MODEL_NAME}"
    )

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME,
        use_fast=True,
    )

    print(
        "\nCreating character-based "
        "contract windows..."
    )

    (
        records,
        positive_windows,
        negative_windows,
        label_counts,
    ) = build_dataset(
        contracts,
        tokenizer,
    )

    save_dataset(
        records
    )

    stats = save_stats(
        contracts,
        records,
        positive_windows,
        negative_windows,
        label_counts,
    )

    print(
        "\nDataset generation completed."
    )

    print("-" * 60)

    print(
        f"Contracts        : "
        f"{stats['contracts']}"
    )

    print(
        f"Total windows    : "
        f"{stats['total_windows']}"
    )

    print(
        f"Positive windows : "
        f"{stats['positive_windows']}"
    )

    print(
        f"Negative windows : "
        f"{stats['negative_windows']}"
    )

    print(
        f"Labels present   : "
        f"{stats['labels_present']}"
    )

    print("-" * 60)

    print("\nGenerated:")
    print(OUTPUT_FILE)
    print(STATS_FILE)


if __name__ == "__main__":
    main()