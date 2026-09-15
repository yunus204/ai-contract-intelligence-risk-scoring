import random
import shutil
from pathlib import Path

import spacy
from spacy.training import Example


PROJECT_ROOT = Path(__file__).resolve().parents[3]

OUTPUT_DIR = (
    PROJECT_ROOT
    / "models"
    / "legal_ner"
)


# Legal-style training sentences.
# We fine-tune the existing spaCy English NER model
# rather than training a new model from zero.
TRAINING_DATA = [
    (
        "This Agreement is entered into between Acme Corporation and Global Technologies Ltd. on January 15, 2026.",
        [
            ("Acme Corporation", "ORG"),
            ("Global Technologies Ltd.", "ORG"),
            ("January 15, 2026", "DATE"),
        ],
    ),
    (
        "Microsoft Corporation shall pay OpenAI Inc. $10,000,000 under this agreement.",
        [
            ("Microsoft Corporation", "ORG"),
            ("OpenAI Inc.", "ORG"),
            ("$10,000,000", "MONEY"),
        ],
    ),
    (
        "The Effective Date of this Agreement is March 1, 2026.",
        [
            ("March 1, 2026", "DATE"),
        ],
    ),
    (
        "ABC Private Limited agrees to pay XYZ Solutions ₹5,00,000.",
        [
            ("ABC Private Limited", "ORG"),
            ("XYZ Solutions", "ORG"),
            ("₹5,00,000", "MONEY"),
        ],
    ),
    (
        "Amazon Web Services Inc. will provide services beginning July 10, 2026.",
        [
            ("Amazon Web Services Inc.", "ORG"),
            ("July 10, 2026", "DATE"),
        ],
    ),
    (
        "The total consideration payable to Oracle Corporation is $250,000.",
        [
            ("Oracle Corporation", "ORG"),
            ("$250,000", "MONEY"),
        ],
    ),
    (
        "Infosys Limited entered into this contract with Tata Consultancy Services on 5 May 2026.",
        [
            ("Infosys Limited", "ORG"),
            ("Tata Consultancy Services", "ORG"),
            ("5 May 2026", "DATE"),
        ],
    ),
    (
        "The Buyer shall pay the Seller USD 75,000 within thirty days.",
        [
            ("USD 75,000", "MONEY"),
        ],
    ),
    (
        "Google LLC and Alphabet Inc. executed this agreement on September 20, 2025.",
        [
            ("Google LLC", "ORG"),
            ("Alphabet Inc.", "ORG"),
            ("September 20, 2025", "DATE"),
        ],
    ),
    (
        "The annual licensing fee payable to Adobe Inc. shall be $15,500.",
        [
            ("Adobe Inc.", "ORG"),
            ("$15,500", "MONEY"),
        ],
    ),
    (
        "This Agreement shall remain effective until December 31, 2028.",
        [
            ("December 31, 2028", "DATE"),
        ],
    ),
    (
        "IBM Corporation shall reimburse Red Hat Inc. an amount of EUR 100,000.",
        [
            ("IBM Corporation", "ORG"),
            ("Red Hat Inc.", "ORG"),
            ("EUR 100,000", "MONEY"),
        ],
    ),
    (
        "Wipro Limited and HCL Technologies Limited entered into this agreement on April 12, 2026.",
        [
            ("Wipro Limited", "ORG"),
            ("HCL Technologies Limited", "ORG"),
            ("April 12, 2026", "DATE"),
        ],
    ),
    (
        "The purchase price payable by the Company is INR 2,500,000.",
        [
            ("INR 2,500,000", "MONEY"),
        ],
    ),
    (
        "Meta Platforms Inc. entered into the Service Agreement on February 2, 2026.",
        [
            ("Meta Platforms Inc.", "ORG"),
            ("February 2, 2026", "DATE"),
        ],
    ),
    (
        "Tesla Inc. shall make a payment of $500,000 on June 30, 2027.",
        [
            ("Tesla Inc.", "ORG"),
            ("$500,000", "MONEY"),
            ("June 30, 2027", "DATE"),
        ],
    ),
    (
        "NVIDIA Corporation and Intel Corporation entered into this Agreement on August 18, 2026.",
        [
            ("NVIDIA Corporation", "ORG"),
            ("Intel Corporation", "ORG"),
            ("August 18, 2026", "DATE"),
        ],
    ),
    (
        "The fee payable to Salesforce Inc. is USD 120,000.",
        [
            ("Salesforce Inc.", "ORG"),
            ("USD 120,000", "MONEY"),
        ],
    ),
    (
        "Accenture Limited shall receive EUR 85,000 on October 1, 2026.",
        [
            ("Accenture Limited", "ORG"),
            ("EUR 85,000", "MONEY"),
            ("October 1, 2026", "DATE"),
        ],
    ),
    (
        "Cisco Systems Inc. executed the agreement on November 25, 2025.",
        [
            ("Cisco Systems Inc.", "ORG"),
            ("November 25, 2025", "DATE"),
        ],
    ),
    (
        "The consideration under this contract shall be ₹12,50,000.",
        [
            ("₹12,50,000", "MONEY"),
        ],
    ),
    (
        "Dell Technologies Inc. shall pay VMware Inc. $350,000.",
        [
            ("Dell Technologies Inc.", "ORG"),
            ("VMware Inc.", "ORG"),
            ("$350,000", "MONEY"),
        ],
    ),
    (
        "The Agreement commences on January 1, 2026 and expires on January 1, 2029.",
        [
            ("January 1, 2026", "DATE"),
            ("January 1, 2029", "DATE"),
        ],
    ),
    (
        "SAP SE agrees to pay ServiceNow Inc. USD 95,000.",
        [
            ("SAP SE", "ORG"),
            ("ServiceNow Inc.", "ORG"),
            ("USD 95,000", "MONEY"),
        ],
    ),

    # Negative examples help prevent legal terminology
    # from being incorrectly classified as entities.
    (
        "The parties agree to comply with the confidentiality obligations stated herein.",
        [],
    ),
    (
        "This Agreement contains provisions relating to termination and indemnification.",
        [],
    ),
    (
        "The receiving party shall maintain all confidential information in confidence.",
        [],
    ),
    (
        "Neither party may assign this Agreement without prior written consent.",
        [],
    ),
    (
        "The limitation of liability provision shall survive termination.",
        [],
    ),
]


def build_examples(nlp):
    examples = []

    for text, annotations in TRAINING_DATA:
        entities = []

        for entity_text, label in annotations:
            start = text.find(entity_text)

            if start == -1:
                raise ValueError(
                    f"Entity '{entity_text}' "
                    f"not found in:\n{text}"
                )

            end = start + len(entity_text)

            entities.append(
                (
                    start,
                    end,
                    label,
                )
            )

        doc = nlp.make_doc(text)

        example = Example.from_dict(
            doc,
            {
                "entities": entities
            },
        )

        examples.append(example)

    return examples


def main():
    print("=" * 60)
    print("LEGAL CONTRACT NER FINE-TUNING")
    print("=" * 60)

    print(
        "\nLoading pretrained spaCy model: "
        "en_core_web_sm"
    )

    nlp = spacy.load(
        "en_core_web_sm"
    )

    ner = nlp.get_pipe("ner")

    for label in [
        "ORG",
        "DATE",
        "MONEY",
    ]:
        ner.add_label(label)

    examples = build_examples(nlp)

    print(
        f"Training examples : "
        f"{len(examples)}"
    )

    print(
        "Target labels     : "
        "ORG, DATE, MONEY"
    )

    # Remove the old broken model.
    if OUTPUT_DIR.exists():
        shutil.rmtree(
            OUTPUT_DIR
        )

    # Only update the NER component.
    other_pipes = [
        pipe
        for pipe in nlp.pipe_names
        if pipe != "ner"
    ]

    with nlp.disable_pipes(
        *other_pipes
    ):
        optimizer = nlp.resume_training()

        print("\nFine-tuning NER...")

        for epoch in range(15):
            random.shuffle(examples)

            losses = {}

            nlp.update(
                examples,
                sgd=optimizer,
                drop=0.15,
                losses=losses,
            )

            print(
                f"Epoch "
                f"{epoch + 1:02d}/15 "
                f"- NER loss: "
                f"{losses.get('ner', 0):.4f}"
            )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    nlp.to_disk(
        OUTPUT_DIR
    )

    print("\n" + "=" * 60)
    print("FINE-TUNING COMPLETE")
    print("=" * 60)

    print(
        f"Model saved to: "
        f"{OUTPUT_DIR}"
    )


if __name__ == "__main__":
    main()