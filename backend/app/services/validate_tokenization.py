import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]

ORIGINAL_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "cuad_examples.jsonl"
)

TOKENIZED_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "tokenized"
    / "cuad_tokenized.jsonl"
)


def load_original():
    answered_ids = set()
    examples = {}

    with ORIGINAL_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            record = json.loads(line)

            qa_id = record["qa_id"]

            examples[qa_id] = record

            if record["has_answer"]:
                answered_ids.add(qa_id)

    return answered_ids, examples


def load_covered_ids():
    covered_ids = set()

    with TOKENIZED_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            record = json.loads(line)

            if record["contains_answer"]:
                covered_ids.add(record["qa_id"])

    return covered_ids


def main():
    answered_ids, examples = load_original()
    covered_ids = load_covered_ids()

    uncovered_ids = answered_ids - covered_ids

    print("=" * 60)
    print("CUAD TOKENIZATION VALIDATION")
    print("=" * 60)

    print(f"Answered QA examples : {len(answered_ids)}")
    print(f"Covered QA examples  : {len(covered_ids)}")
    print(f"Uncovered examples   : {len(uncovered_ids)}")

    print("\nSample uncovered examples:")
    print("-" * 60)

    for qa_id in list(uncovered_ids)[:5]:
        example = examples[qa_id]

        print(f"\nQA ID:")
        print(qa_id)

        print("\nQuestion:")
        print(example["question"])

        print("\nAnswer start:")
        print(example["answer_starts"][:3])

        print("\nAnswer:")
        for answer in example["answers"][:1]:
            print(answer[:500])

        print("-" * 60)


if __name__ == "__main__":
    main()