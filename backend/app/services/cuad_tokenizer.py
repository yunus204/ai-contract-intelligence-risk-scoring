import json
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
    / "tokenized"
)

OUTPUT_FILE = OUTPUT_DIR / "cuad_tokenized.jsonl"
STATS_FILE = OUTPUT_DIR / "tokenization_stats.json"

MODEL_NAME = "roberta-base"

MAX_LENGTH = 512
DOC_STRIDE = 128


def load_examples():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Processed CUAD file not found: {INPUT_FILE}"
        )

    examples = []

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            examples.append(json.loads(line))

    return examples


def load_tokenizer():
    print(f"Loading tokenizer: {MODEL_NAME}")

    return AutoTokenizer.from_pretrained(
        MODEL_NAME,
        use_fast=True,
    )


def get_answer_span(example):
    """
    CUAD can contain multiple answer annotations.

    For the baseline training pipeline we use the first
    annotated span. Examples without answers are treated
    as no-answer examples.
    """

    if not example["answers"]:
        return None, None

    answer_text = example["answers"][0]
    answer_start = example["answer_starts"][0]

    answer_end = answer_start + len(answer_text)

    return answer_start, answer_end


def tokenize_example(example, tokenizer):
    question = example["question"].strip()
    context = example["context"]

    encoded = tokenizer(
        question,
        context,
        max_length=MAX_LENGTH,
        truncation="only_second",
        stride=DOC_STRIDE,
        return_overflowing_tokens=True,
        return_offsets_mapping=True,
        padding="max_length",
        return_attention_mask=True,
    )

    answer_start, answer_end = get_answer_span(example)

    records = []

    for feature_index in range(len(encoded["input_ids"])):

        input_ids = encoded["input_ids"][feature_index]
        attention_mask = encoded["attention_mask"][feature_index]
        offsets = encoded["offset_mapping"][feature_index]

        sequence_ids = encoded.sequence_ids(feature_index)

        # RoBERTa CLS token
        cls_index = input_ids.index(
            tokenizer.cls_token_id
        )

        start_position = cls_index
        end_position = cls_index
        contains_answer = False

        if answer_start is not None:

            context_token_indexes = [
                i
                for i, sequence_id in enumerate(sequence_ids)
                if sequence_id == 1
            ]

            if context_token_indexes:

                context_start = context_token_indexes[0]
                context_end = context_token_indexes[-1]

                window_start_char = offsets[
                    context_start
                ][0]

                window_end_char = offsets[
                    context_end
                ][1]

                # Check whether the full answer is
                # contained inside this window.
                if (
                    answer_start >= window_start_char
                    and answer_end <= window_end_char
                ):
                    contains_answer = True

                    token_start = context_start

                    while (
                        token_start <= context_end
                        and offsets[token_start][0]
                        <= answer_start
                    ):
                        token_start += 1

                    start_position = token_start - 1

                    token_end = context_end

                    while (
                        token_end >= context_start
                        and offsets[token_end][1]
                        >= answer_end
                    ):
                        token_end -= 1

                    end_position = token_end + 1

        record = {
            "qa_id": example["qa_id"],
            "contract_title": example["contract_title"],
            "question": question,
            "label_id": example["label_id"],
            "has_answer": example["has_answer"],
            "contains_answer": contains_answer,
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "start_position": start_position,
            "end_position": end_position,
        }

        records.append(record)

    return records


def tokenize_examples(examples, tokenizer):
    tokenized_records = []

    examples_with_multiple_windows = 0
    answer_windows = 0

    for index, example in enumerate(examples, start=1):

        records = tokenize_example(
            example,
            tokenizer,
        )

        if len(records) > 1:
            examples_with_multiple_windows += 1

        for record in records:
            if record["contains_answer"]:
                answer_windows += 1

            tokenized_records.append(record)

        if index % 500 == 0:
            print(
                f"Processed {index}/{len(examples)} "
                f"CUAD examples"
            )

    return (
        tokenized_records,
        examples_with_multiple_windows,
        answer_windows,
    )


def save_tokenized_data(records):
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
                json.dumps(record)
                + "\n"
            )


def save_statistics(
    original_examples,
    tokenized_records,
    multiple_windows,
    answer_windows,
):
    stats = {
        "model_name": MODEL_NAME,
        "max_length": MAX_LENGTH,
        "document_stride": DOC_STRIDE,
        "original_examples": original_examples,
        "tokenized_windows": tokenized_records,
        "examples_requiring_multiple_windows":
            multiple_windows,
        "windows_containing_answers":
            answer_windows,
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
    print("CUAD SLIDING-WINDOW TOKENIZATION")
    print("=" * 60)

    examples = load_examples()

    print(
        f"\nLoaded {len(examples)} CUAD examples."
    )

    tokenizer = load_tokenizer()

    print(
        f"\nMaximum length : {MAX_LENGTH}"
    )
    print(
        f"Document stride: {DOC_STRIDE}"
    )

    print("\nStarting tokenization...")

    (
        records,
        multiple_windows,
        answer_windows,
    ) = tokenize_examples(
        examples,
        tokenizer,
    )

    save_tokenized_data(records)

    stats = save_statistics(
        len(examples),
        len(records),
        multiple_windows,
        answer_windows,
    )

    print("\nTokenization completed.")
    print("-" * 60)

    print(
        f"Model                     : "
        f"{stats['model_name']}"
    )
    print(
        f"Original examples         : "
        f"{stats['original_examples']}"
    )
    print(
        f"Generated windows         : "
        f"{stats['tokenized_windows']}"
    )
    print(
        f"Multi-window examples     : "
        f"{stats['examples_requiring_multiple_windows']}"
    )
    print(
        f"Windows containing answer : "
        f"{stats['windows_containing_answers']}"
    )

    print("-" * 60)

    print("\nGenerated:")
    print(OUTPUT_FILE)
    print(STATS_FILE)


if __name__ == "__main__":
    main()