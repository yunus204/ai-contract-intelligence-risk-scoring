import json
import os
import re
from pathlib import Path
from typing import Dict, List

import torch
from dotenv import load_dotenv
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]

load_dotenv(PROJECT_ROOT / ".env")


MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "clause_classifier"
)

LABEL_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "clause_labels.json"
)


MAX_LENGTH = 512

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200

THRESHOLD = float(
    os.getenv(
        "CLAUSE_THRESHOLD",
        "0.45",
    )
)


class ClauseClassifier:

    def __init__(self):

        if not MODEL_PATH.exists():
            raise RuntimeError(
                "Clause classifier model was not found at "
                f"{MODEL_PATH}. Train the model first."
            )

        if not LABEL_FILE.exists():
            raise RuntimeError(
                "Clause label mapping was not found."
            )

        self.device = torch.device(
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        print(
            f"Loading clause classifier on "
            f"{self.device}..."
        )

        self.tokenizer = (
            AutoTokenizer.from_pretrained(
                MODEL_PATH
            )
        )

        self.model = (
            AutoModelForSequenceClassification
            .from_pretrained(
                MODEL_PATH
            )
        )

        self.model.to(
            self.device
        )

        self.model.eval()

        self.id_to_clause = (
            self._load_labels()
        )

    def _load_labels(
        self,
    ) -> Dict[int, str]:

        with LABEL_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:

            question_to_id = (
                json.load(file)
            )

        id_to_clause = {}

        for question, label_id in (
            question_to_id.items()
        ):

            match = re.search(
                r'related to "([^"]+)"',
                question,
                re.IGNORECASE,
            )

            if match:
                clause_name = (
                    match.group(1)
                )
            else:
                clause_name = question

            id_to_clause[
                int(label_id)
            ] = clause_name

        return id_to_clause

    def _split_text(
        self,
        text: str,
    ) -> List[str]:

        chunks = []

        start = 0
        text_length = len(text)

        step = (
            CHUNK_SIZE
            - CHUNK_OVERLAP
        )

        while start < text_length:

            end = min(
                start + CHUNK_SIZE,
                text_length,
            )

            chunk = text[
                start:end
            ].strip()

            if chunk:
                chunks.append(chunk)

            if end == text_length:
                break

            start += step

        return chunks

    def analyze(
        self,
        text: str,
    ) -> Dict:

        if not text.strip():

            return {
                "threshold": THRESHOLD,
                "chunks_analyzed": 0,
                "detected_clauses": [],
            }

        chunks = self._split_text(
            text
        )

        best_by_label = {}

        with torch.no_grad():

            for chunk_index, chunk in enumerate(
                chunks
            ):

                encoding = self.tokenizer(
                    chunk,
                    return_tensors="pt",
                    truncation=True,
                    max_length=MAX_LENGTH,
                    padding=True,
                )

                input_ids = (
                    encoding[
                        "input_ids"
                    ].to(self.device)
                )

                attention_mask = (
                    encoding[
                        "attention_mask"
                    ].to(self.device)
                )

                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                )

                probabilities = (
                    torch.sigmoid(
                        outputs.logits
                    )[0]
                    .cpu()
                    .numpy()
                )

                for label_id, confidence in (
                    enumerate(probabilities)
                ):

                    confidence = float(
                        confidence
                    )

                    if confidence < THRESHOLD:
                        continue

                    clause_name = (
                        self.id_to_clause.get(
                            label_id,
                            f"Label {label_id}",
                        )
                    )

                    previous = (
                        best_by_label.get(
                            label_id
                        )
                    )

                    if (
                        previous is None
                        or confidence
                        > previous[
                            "confidence"
                        ]
                    ):

                        best_by_label[
                            label_id
                        ] = {
                            "label_id":
                                label_id,

                            "clause":
                                clause_name,

                            "confidence":
                                round(
                                    confidence,
                                    4,
                                ),

                            "chunk_index":
                                chunk_index,

                            "evidence":
                                chunk[:700],
                        }

        detected = sorted(
            best_by_label.values(),
            key=lambda item:
                item["confidence"],
            reverse=True,
        )

        return {
            "threshold": THRESHOLD,
            "chunks_analyzed":
                len(chunks),
            "detected_clauses":
                detected,
        }


clause_classifier = (
    ClauseClassifier()
)