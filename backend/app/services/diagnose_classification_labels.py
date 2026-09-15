import json
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]

EXAMPLES_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "cuad_examples.jsonl"
)

LABELS_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "clause_labels.json"
)

CLASSIFICATION_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "classification"
    / "cuad_classification.jsonl"
)


def load_label_mapping():
    with LABELS_FILE.open("r", encoding="utf-8") as file:
        question_to_id = json.load(file)

    return question_to_id


def count_original_annotations():
    answer_counts = Counter()

    with EXAMPLES_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            record = json.loads(line)

            label_id = record["label_id"]

            if record["answers"]:
                answer_counts[label_id] += len(
                    record["answers"]
                )

    return answer_counts


def count_classification_labels():
    window_counts = Counter()

    with CLASSIFICATION_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:

        for line in file:
            record = json.loads(line)

            for label_id in record["labels"]:
                window_counts[label_id] += 1

    return window_counts


def main():
    question_to_id = load_label_mapping()

    id_to_question = {
        int(label_id): question
        for question, label_id
        in question_to_id.items()
    }

    original_counts = count_original_annotations()
    window_counts = count_classification_labels()

    all_label_ids = set(id_to_question.keys())

    labels_with_answers = set(original_counts.keys())
    labels_in_windows = set(window_counts.keys())

    no_answer_labels = (
        all_label_ids - labels_with_answers
    )

    lost_during_windowing = (
        labels_with_answers - labels_in_windows
    )

    print("=" * 70)
    print("CUAD CLASSIFICATION LABEL DIAGNOSTICS")
    print("=" * 70)

    print(f"Total label schema       : {len(all_label_ids)}")
    print(f"Labels with annotations  : {len(labels_with_answers)}")
    print(f"Labels found in windows  : {len(labels_in_windows)}")

    print("\n" + "=" * 70)
    print("LABELS WITH NO ANSWER ANNOTATIONS")
    print("=" * 70)

    if not no_answer_labels:
        print("None")
    else:
        for label_id in sorted(no_answer_labels):
            print(
                f"\nLabel {label_id}"
                f"\nQuestion: {id_to_question[label_id]}"
                f"\nOriginal annotations: 0"
            )

    print("\n" + "=" * 70)
    print("LABELS LOST DURING WINDOW GENERATION")
    print("=" * 70)

    if not lost_during_windowing:
        print("None")
    else:
        for label_id in sorted(lost_during_windowing):
            print(
                f"\nLabel {label_id}"
                f"\nQuestion: {id_to_question[label_id]}"
                f"\nOriginal annotations: "
                f"{original_counts[label_id]}"
                f"\nClassification windows: "
                f"{window_counts[label_id]}"
            )

    print("\n" + "=" * 70)
    print("ALL LABEL COUNTS")
    print("=" * 70)

    for label_id in sorted(all_label_ids):
        print(
            f"{label_id:2d} | "
            f"answers={original_counts[label_id]:4d} | "
            f"windows={window_counts[label_id]:4d} | "
            f"{id_to_question[label_id][:70]}"
        )


if __name__ == "__main__":
    main()