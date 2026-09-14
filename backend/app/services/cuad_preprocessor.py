import json
from pathlib import Path
from collections import Counter


PROJECT_ROOT = Path(__file__).resolve().parents[3]

INPUT_FILE = PROJECT_ROOT / "data" / "cuad" / "CUADv1.json"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"

EXAMPLES_FILE = OUTPUT_DIR / "cuad_examples.jsonl"
LABELS_FILE = OUTPUT_DIR / "clause_labels.json"
STATS_FILE = OUTPUT_DIR / "cuad_stats.json"


def load_cuad():
    """Load the original CUAD JSON dataset."""
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"CUAD dataset not found at: {INPUT_FILE}"
        )

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def preprocess_cuad(dataset):
    """
    Convert CUAD's SQuAD-style structure into flat,
    training-friendly examples.
    """

    examples = []
    unique_questions = set()

    contract_count = 0
    paragraph_count = 0
    qa_count = 0
    answer_count = 0

    for contract in dataset.get("data", []):
        contract_count += 1

        title = contract.get("title", "")

        for paragraph_index, paragraph in enumerate(
            contract.get("paragraphs", [])
        ):
            paragraph_count += 1

            context = paragraph.get("context", "")

            for qa in paragraph.get("qas", []):
                qa_count += 1

                question = qa.get("question", "").strip()
                unique_questions.add(question)

                answers = qa.get("answers", [])

                answer_texts = []
                answer_starts = []

                for answer in answers:
                    answer_texts.append(
                        answer.get("text", "")
                    )
                    answer_starts.append(
                        answer.get("answer_start", -1)
                    )
                    answer_count += 1

                example = {
                    "contract_title": title,
                    "paragraph_id": paragraph_index,
                    "qa_id": qa.get("id", ""),
                    "question": question,
                    "context": context,
                    "answers": answer_texts,
                    "answer_starts": answer_starts,
                    "has_answer": len(answers) > 0,
                }

                examples.append(example)

    return examples, sorted(unique_questions), {
        "contracts": contract_count,
        "paragraphs": paragraph_count,
        "qa_examples": qa_count,
        "answers": answer_count,
    }


def assign_clause_labels(examples, questions):
    """
    CUAD contains 41 legal categories represented through
    annotation questions.

    We assign each unique question a numeric label so the
    transformer pipeline can use them later.
    """

    question_to_label = {
        question: index
        for index, question in enumerate(questions)
    }

    for example in examples:
        example["label_id"] = question_to_label[
            example["question"]
        ]

    return question_to_label


def save_jsonl(examples):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with EXAMPLES_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        for example in examples:
            file.write(
                json.dumps(
                    example,
                    ensure_ascii=False
                )
                + "\n"
            )


def save_labels(label_mapping):
    with LABELS_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            label_mapping,
            file,
            indent=2,
            ensure_ascii=False,
        )


def save_stats(stats, examples, label_mapping):
    answer_distribution = Counter(
        "answered"
        if example["has_answer"]
        else "no_answer"
        for example in examples
    )

    stats["legal_categories"] = len(label_mapping)
    stats["answered_examples"] = answer_distribution[
        "answered"
    ]
    stats["no_answer_examples"] = answer_distribution[
        "no_answer"
    ]

    with STATS_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            stats,
            file,
            indent=2
        )

    return stats


def main():
    print("=" * 60)
    print("CUAD DATA PREPROCESSING")
    print("=" * 60)

    print(f"\nLoading dataset:")
    print(INPUT_FILE)

    dataset = load_cuad()

    print("\nPreprocessing CUAD...")

    examples, questions, stats = preprocess_cuad(
        dataset
    )

    label_mapping = assign_clause_labels(
        examples,
        questions
    )

    save_jsonl(examples)
    save_labels(label_mapping)

    stats = save_stats(
        stats,
        examples,
        label_mapping
    )

    print("\nPreprocessing completed successfully.")
    print("-" * 60)

    print(f"Contracts            : {stats['contracts']}")
    print(f"Paragraphs           : {stats['paragraphs']}")
    print(f"QA examples          : {stats['qa_examples']}")
    print(f"Answer annotations   : {stats['answers']}")
    print(f"Legal categories     : {stats['legal_categories']}")
    print(f"Answered examples    : {stats['answered_examples']}")
    print(f"No-answer examples   : {stats['no_answer_examples']}")

    print("-" * 60)

    print("\nGenerated:")
    print(EXAMPLES_FILE)
    print(LABELS_FILE)
    print(STATS_FILE)


if __name__ == "__main__":
    main()