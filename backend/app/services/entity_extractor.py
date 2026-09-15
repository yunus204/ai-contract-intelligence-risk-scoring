from pathlib import Path
from typing import Dict, List

import spacy


PROJECT_ROOT = Path(__file__).resolve().parents[3]

LEGAL_MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "legal_ner"
)

GENERAL_MODEL_NAME = "en_core_web_sm"


class ContractEntityExtractor:

    def __init__(self):

        if not LEGAL_MODEL_PATH.exists():
            raise RuntimeError(
                "Legal NER model not found. "
                "Run train_legal_ner.py first."
            )

        self.legal_nlp = spacy.load(
            LEGAL_MODEL_PATH
        )

        self.general_nlp = spacy.load(
            GENERAL_MODEL_NAME
        )

    @staticmethod
    def _unique(
        values: List[str]
    ) -> List[str]:

        seen = set()
        result = []

        for value in values:

            cleaned = value.strip()

            if not cleaned:
                continue

            normalized = (
                cleaned.lower()
            )

            if normalized not in seen:

                seen.add(normalized)

                result.append(cleaned)

        return result

    def extract(self, text: str) -> Dict:

        if not text.strip():

            return {
                "organizations": [],
                "dates": [],
                "money": [],
                "persons": [],
                "jurisdictions": [],
                "all_entities": [],
            }

        if len(text) > self.legal_nlp.max_length:
            self.legal_nlp.max_length = (
                len(text) + 1000
            )

        if len(text) > self.general_nlp.max_length:
            self.general_nlp.max_length = (
                len(text) + 1000
            )

        legal_doc = self.legal_nlp(text)

        general_doc = self.general_nlp(
            text
        )

        organizations = []
        dates = []
        money = []
        persons = []
        jurisdictions = []

        all_entities = []

        # Our trained contract-specific model.
        for entity in legal_doc.ents:

            value = entity.text.strip()

            all_entities.append(
                {
                    "text": value,
                    "label": entity.label_,
                    "source": "legal_ner",
                    "start": entity.start_char,
                    "end": entity.end_char,
                }
            )

            if entity.label_ == "ORG":
                organizations.append(value)

            elif entity.label_ == "DATE":
                dates.append(value)

            elif entity.label_ == "MONEY":
                money.append(value)

        # Generic spaCy is retained only for
        # people and geographic/legal locations.
        for entity in general_doc.ents:

            value = entity.text.strip()

            if entity.label_ == "PERSON":

                persons.append(value)

                all_entities.append(
                    {
                        "text": value,
                        "label": "PERSON",
                        "source":
                            "general_spacy",
                        "start":
                            entity.start_char,
                        "end":
                            entity.end_char,
                    }
                )

            elif entity.label_ in {
                "GPE",
                "LOC",
                "LAW",
            }:

                jurisdictions.append(
                    value
                )

                all_entities.append(
                    {
                        "text": value,
                        "label":
                            entity.label_,
                        "source":
                            "general_spacy",
                        "start":
                            entity.start_char,
                        "end":
                            entity.end_char,
                    }
                )

        return {
            "organizations":
                self._unique(
                    organizations
                ),

            "dates":
                self._unique(
                    dates
                ),

            "money":
                self._unique(
                    money
                ),

            "persons":
                self._unique(
                    persons
                ),

            "jurisdictions":
                self._unique(
                    jurisdictions
                ),

            "all_entities":
                all_entities,
        }


entity_extractor = (
    ContractEntityExtractor()
)


def extract_entities(
    text: str
) -> Dict:

    return entity_extractor.extract(
        text
    )