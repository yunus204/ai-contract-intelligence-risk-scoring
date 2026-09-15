import argparse
import json
import random
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import (
    f1_score,
    precision_score,
    recall_score,
)
from torch.utils.data import DataLoader, Dataset
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "classification"
    / "cuad_classification.jsonl"
)

LABEL_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "clause_labels.json"
)

MODEL_OUTPUT_DIR = (
    PROJECT_ROOT
    / "models"
    / "clause_classifier"
)

METRICS_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "classification"
    / "roberta_metrics.json"
)

MODEL_NAME = "roberta-base"

NUM_LABELS = 41

MAX_LENGTH = 512

BATCH_SIZE = 4

LEARNING_RATE = 2e-5

EPOCHS = 2
THRESHOLD = 0.45
RANDOM_SEED = 42


class CUADClauseDataset(Dataset):

    def __init__(self, records):
        self.records = records

    def __len__(self):
        return len(self.records)

    def __getitem__(self, index):

        record = self.records[index]

        label_vector = torch.zeros(
            NUM_LABELS,
            dtype=torch.float32,
        )

        for label_id in record["labels"]:
            label_vector[label_id] = 1.0

        return {
            "input_ids": torch.tensor(
                record["input_ids"],
                dtype=torch.long,
            ),

            "attention_mask": torch.tensor(
                record["attention_mask"],
                dtype=torch.long,
            ),

            "labels": label_vector,
        }


def load_records():

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Classification dataset not found: "
            f"{DATA_FILE}"
        )

    records = []

    with DATA_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:

        for line in file:
            records.append(
                json.loads(line)
            )

    return records


def split_by_contract(records):
    """
    Split by contract title instead of individual chunks.

    This prevents chunks from the same contract from
    appearing in both training and validation sets.
    """

    contract_names = sorted(
        {
            record["contract_title"]
            for record in records
        }
    )

    random.seed(RANDOM_SEED)
    random.shuffle(contract_names)

    split_index = int(
        len(contract_names) * 0.8
    )

    train_contracts = set(
        contract_names[:split_index]
    )

    validation_contracts = set(
        contract_names[split_index:]
    )

    train_records = [
        record
        for record in records
        if record["contract_title"]
        in train_contracts
    ]

    validation_records = [
        record
        for record in records
        if record["contract_title"]
        in validation_contracts
    ]

    return (
        train_records,
        validation_records,
    )


def prepare_smoke_test(
    train_records,
    validation_records,
):
    """
    Create a useful smoke-test sample containing
    both positive and negative clause windows.
    """

    random.seed(RANDOM_SEED)

    train_positive = [
        record
        for record in train_records
        if record["labels"]
    ]

    train_negative = [
        record
        for record in train_records
        if not record["labels"]
    ]

    val_positive = [
        record
        for record in validation_records
        if record["labels"]
    ]

    val_negative = [
        record
        for record in validation_records
        if not record["labels"]
    ]

    random.shuffle(train_positive)
    random.shuffle(train_negative)

    random.shuffle(val_positive)
    random.shuffle(val_negative)

    smoke_train = (
        train_positive[:192]
        + train_negative[:64]
    )

    smoke_validation = (
        val_positive[:96]
        + val_negative[:32]
    )

    random.shuffle(smoke_train)
    random.shuffle(smoke_validation)

    return (
        smoke_train,
        smoke_validation,
    )

def calculate_pos_weights(records):
    """
    Calculate positive-class weights for each of the
    41 CUAD categories.

    Rare legal clauses receive higher training weight.
    """

    positive_counts = np.zeros(
        NUM_LABELS,
        dtype=np.float32,
    )

    total_examples = len(records)

    for record in records:
        for label_id in record["labels"]:
            positive_counts[label_id] += 1

    negative_counts = (
        total_examples - positive_counts
    )

    positive_counts = np.maximum(
        positive_counts,
        1.0,
    )

    weights = (
        negative_counts
        / positive_counts
    )

    # Prevent extremely rare categories from
    # creating unstable gradients.
    weights = np.clip(
        weights,
        1.0,
        20.0,
    )

    return torch.tensor(
        weights,
        dtype=torch.float32,
    )
def evaluate(
    model,
    dataloader,
    device,
):

    model.eval()

    all_predictions = []
    all_labels = []

    total_loss = 0.0

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
                .to(device)
            )

            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels,
            )

            total_loss += (
                outputs.loss.item()
            )

            probabilities = torch.sigmoid(
                outputs.logits
            )

            predictions = (
                probabilities >= THRESHOLD
            ).int()

            all_predictions.append(
                predictions.cpu().numpy()
            )

            all_labels.append(
                labels.cpu().numpy()
            )

    predictions = np.vstack(
        all_predictions
    )

    labels = np.vstack(
        all_labels
    )

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

    average_loss = (
        total_loss
        / max(len(dataloader), 1)
    )

    return {
        "loss": average_loss,
        "precision_micro": precision,
        "recall_micro": recall,
        "f1_micro": f1,
    }


def train(
    train_records,
    validation_records,
    smoke_test=False,
):

    device = torch.device(
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    print(
        f"\nTraining device : {device}"
    )

    print(
        f"Model           : {MODEL_NAME}"
    )

    print(
        f"Number labels   : {NUM_LABELS}"
    )

    print(
        f"Train examples  : "
        f"{len(train_records)}"
    )

    print(
        f"Validation      : "
        f"{len(validation_records)}"
    )

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME
    )

    model = (
        AutoModelForSequenceClassification
        .from_pretrained(
            MODEL_NAME,
            num_labels=NUM_LABELS,
            problem_type=(
                "multi_label_classification"
            ),
        )
    )

    model.to(device)

    train_dataset = CUADClauseDataset(
        train_records
    )

    pos_weights = calculate_pos_weights(
        train_records
    )   .to(device)

    loss_function = torch.nn.BCEWithLogitsLoss(
        pos_weight=pos_weights
)

    print(
    "Weighted BCE loss : enabled"
)


    validation_dataset = (
        CUADClauseDataset(
            validation_records
        )
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
    )

    validation_loader = DataLoader(
        validation_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
    )

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=LEARNING_RATE,
    )

    epochs = 1 if smoke_test else EPOCHS

    print(
        f"Epochs          : {epochs}"
    )

    print("\nStarting fine-tuning...")

    for epoch in range(epochs):

        model.train()

        running_loss = 0.0

        for batch_index, batch in enumerate(
            train_loader,
            start=1,
        ):

            optimizer.zero_grad()

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
                .to(device)
            )

            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
)

            loss = loss_function(
                outputs.logits,
                labels,
)

            loss.backward()

            optimizer.step()

            running_loss += loss.item()

            if batch_index % 25 == 0:

                print(
                    f"Epoch "
                    f"{epoch + 1}/{epochs} "
                    f"| Batch "
                    f"{batch_index}/"
                    f"{len(train_loader)} "
                    f"| Loss "
                    f"{loss.item():.4f}"
                )

        train_loss = (
            running_loss
            / max(len(train_loader), 1)
        )

        metrics = evaluate(
            model,
            validation_loader,
            device,
        )

        print("\n" + "-" * 60)

        print(
            f"Epoch {epoch + 1} complete"
        )

        print(
            f"Train loss : "
            f"{train_loss:.4f}"
        )

        print(
            f"Val loss   : "
            f"{metrics['loss']:.4f}"
        )

        print(
            f"Precision  : "
            f"{metrics['precision_micro']:.4f}"
        )

        print(
            f"Recall     : "
            f"{metrics['recall_micro']:.4f}"
        )

        print(
            f"F1         : "
            f"{metrics['f1_micro']:.4f}"
        )

        print("-" * 60)

    MODEL_OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    model.save_pretrained(
        MODEL_OUTPUT_DIR
    )

    tokenizer.save_pretrained(
        MODEL_OUTPUT_DIR
    )

    final_metrics = {
        "model_name": MODEL_NAME,
        "num_labels": NUM_LABELS,
        "train_examples":
            len(train_records),
        "validation_examples":
            len(validation_records),
        "epochs": epochs,
        "threshold": THRESHOLD,
        "device": str(device),
        **metrics,
    }

    METRICS_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with METRICS_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            final_metrics,
            file,
            indent=2,
        )

    print("\n" + "=" * 60)

    print("TRAINING COMPLETE")

    print("=" * 60)

    print(
        f"Model saved   : "
        f"{MODEL_OUTPUT_DIR}"
    )

    print(
        f"Metrics saved : "
        f"{METRICS_FILE}"
    )


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help=(
            "Train on a very small subset to verify "
            "the pipeline."
        ),
    )

    args = parser.parse_args()

    print("=" * 60)
    print("CUAD ROBERTA CLAUSE CLASSIFIER")
    print("=" * 60)

    records = load_records()

    print(
        f"\nLoaded records : "
        f"{len(records)}"
    )

    (
        train_records,
        validation_records,
    ) = split_by_contract(records)

    if args.smoke_test:

        print(
            "\nSMOKE TEST MODE ENABLED"
        )

        (
            train_records,
            validation_records,
        ) = prepare_smoke_test(
            train_records,
            validation_records,
        )

    train(
        train_records,
        validation_records,
        smoke_test=args.smoke_test,
    )


if __name__ == "__main__":
    main()