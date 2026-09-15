from typing import Dict, List


RISK_WEIGHTS = {
    "uncapped liability": 25,
    "non-compete": 18,
    "exclusivity": 15,
    "liquidated damages": 15,
    "minimum commitment": 15,
    "most favored nation": 14,
    "renewal term": 12,
    "volume restriction": 12,
    "price restrictions": 12,
    "change of control": 10,
    "anti-assignment": 10,
    "no-solicit of employees": 10,
    "no-solicit of customers": 10,
    "audit rights": 8,
    "post-termination services": 8,
    "cap on liability": 6,
    "warranty duration": 5,
}


def _normalize(
    value: str,
) -> str:

    return (
        value
        .strip()
        .lower()
        .replace("_", " ")
    )


def score_contract_risk(
    detected_clauses: List[Dict],
) -> Dict:

    total_score = 0.0

    risk_factors = []

    for detection in detected_clauses:

        clause = detection[
            "clause"
        ]

        confidence = float(
            detection[
                "confidence"
            ]
        )

        normalized = _normalize(
            clause
        )

        weight = (
            RISK_WEIGHTS.get(
                normalized,
                3,
            )
        )

        contribution = (
            weight
            * confidence
        )

        total_score += contribution

        risk_factors.append(
            {
                "clause":
                    clause,

                "confidence":
                    confidence,

                "risk_weight":
                    weight,

                "risk_contribution":
                    round(
                        contribution,
                        2,
                    ),
            }
        )

    score = min(
        round(total_score, 2),
        100.0,
    )

    if score >= 70:

        level = "critical"

    elif score >= 45:

        level = "high"

    elif score >= 20:

        level = "medium"

    else:

        level = "low"

    risk_factors.sort(
        key=lambda item:
            item[
                "risk_contribution"
            ],
        reverse=True,
    )

    return {
        "risk_score": score,
        "risk_level": level,
        "risk_factors":
            risk_factors[:10],
        "method": (
            "CUAD clause confidence "
            "+ heuristic legal risk weights"
        ),
    }