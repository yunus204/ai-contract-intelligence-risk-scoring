import json

import numpy as np
import torch
from sklearn.metrics import (
    f1_score,
    precision_score,
    recall_score,
)
from torch.utils.data import DataLoader
from transformers import (
    AutoModelForSequenceClassification,
)

from backend.app.services.train_clause_classifier import (
    BATCH_SIZE,
    CUADClauseDataset,
    MODEL_OUTPUT_DIR,
    PROJECT_ROOT,
    load_records,
    prepare_smoke_test,
    split_by_contract,
)


OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "classification"
    / "threshold_tuning.json"
)


def collect_predictions(
    model,
    dataloader,
    device,
):
    model.eval()

    all_probabilities = []
    all_labels = []

    with torch.no_grad():

        for batch in dataloader:

            input_ids = (
                batch["input_ids"]
                .to(device)
            )

            attention_mask = (
                batch["attention_mask"]
                .to(device)
            )

            labels = (
                batch["labels"]
                .cpu()
                .numpy()
            )

            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
            )

            probabilities = torch.sigmoid(
                outputs.logits
            )

            all_probabilities.append(
                probabilities.cpu().numpy()
            )

            all_labels.append(labels)

    return (
        np.vstack(all_probabilities),
        np.vstack(all_labels),
    )


def evaluate_threshold(
    probabilities,
    labels,
    threshold,
):
    predictions = (
        probabilities >= threshold
    ).astype(int)

    precision = precision_score(
        labels,
        predictions,
        average="micro",
        zero_division=0,
    )

    recall = recall_score(
        labels,
        predictions,
        average="micro",
        zero_division=0,
    )

    f1 = f1_score(
        labels,
        predictions,
        average="micro",
        zero_division=0,
    )

    predicted_positives = int(
        predictions.sum()
    )

    actual_positives = int(
        labels.sum()
    )

    return {
        "threshold": threshold,
        "precision_micro": precision,
        "recall_micro": recall,
        "f1_micro": f1,
        "predicted_positives":
            predicted_positives,
        "actual_positives":
            actual_positives,
    }


def main():

    print("=" * 70)
    print("CUAD CLAUSE THRESHOLD TUNING")
    print("=" * 70)

    device = torch.device(
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    print(
        f"\nDevice : {device}"
    )

    records = load_records()

    (
        train_records,
        validation_records,
    ) = split_by_contract(records)

    (
        _,
        validation_records,
    ) = prepare_smoke_test(
        train_records,
        validation_records,
    )

    print(
        f"Validation examples : "
        f"{len(validation_records)}"
    )

    dataset = CUADClauseDataset(
        validation_records
    )

    dataloader = DataLoader(
        dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
    )

    print(
        f"Loading model : "
        f"{MODEL_OUTPUT_DIR}"
    )

    model = (
        AutoModelForSequenceClassification
        .from_pretrained(
            MODEL_OUTPUT_DIR
        )
    )

    model.to(device)

    print(
        "\nCollecting model probabilities..."
    )

    probabilities, labels = (
        collect_predictions(
            model,
            dataloader,
            device,
        )
    )

    thresholds = [
        0.10,
        0.15,
        0.20,
        0.25,
        0.30,
        0.35,
        0.40,
        0.45,
        0.50,
        0.55,
        0.60,
        0.65,
        0.70,
        0.75,
        0.80,
        0.85,
        0.90,
    ]

    results = []

    print("\n")
    print(
        "Threshold | Precision | Recall | F1"
    )
    print("-" * 50)

    for threshold in thresholds:

        result = evaluate_threshold(
            probabilities,
            labels,
            threshold,
        )

        results.append(result)

        print(
            f"{threshold:9.2f} | "
            f"{result['precision_micro']:9.4f} | "
            f"{result['recall_micro']:6.4f} | "
            f"{result['f1_micro']:6.4f}"
        )

    best_result = max(
        results,
        key=lambda item:
            item["f1_micro"],
    )

    print("\n" + "=" * 70)
    print("BEST THRESHOLD")
    print("=" * 70)

    print(
        f"Threshold : "
        f"{best_result['threshold']}"
    )

    print(
        f"Precision : "
        f"{best_result['precision_micro']:.4f}"
    )

    print(
        f"Recall    : "
        f"{best_result['recall_micro']:.4f}"
    )

    print(
        f"F1        : "
        f"{best_result['f1_micro']:.4f}"
    )

    print(
        f"Actual positive labels    : "
        f"{best_result['actual_positives']}"
    )

    print(
        f"Predicted positive labels : "
        f"{best_result['predicted_positives']}"
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output = {
        "best": best_result,
        "all_thresholds": results,
    }

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            output,
            file,
            indent=2,
        )

    print(
        f"\nResults saved to: "
        f"{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()