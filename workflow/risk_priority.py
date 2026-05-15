from __future__ import annotations

import re
from typing import Any

from workflow.schemas import ClassifyResult, ExtractResult


def _parse_amount(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if not isinstance(value, str):
        return None
    cleaned = re.sub(r"[^\d.]", "", value.replace(",", ""))
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def assess_risk_priority(
    classification: ClassifyResult,
    extracted: ExtractResult,
    validation: dict[str, Any],
) -> dict[str, Any]:
    text_blob = " ".join(
        str(x).lower()
        for x in (extracted.structured or {}).values()
        if isinstance(x, (str, int, float))
    )
    urgent = any(
        w in text_blob
        for w in ("urgent", "asap", "immediately", "escalate", "legal", "regulator")
    )
    amount = _parse_amount((extracted.structured or {}).get("amount"))

    risk = "low"
    if urgent or (amount and amount >= 100_000):
        risk = "high"
    elif not validation.get("complete", False) or (amount and amount >= 25_000):
        risk = "medium"

    priority = "P3"
    if risk == "high" or urgent:
        priority = "P1"
    elif risk == "medium":
        priority = "P2"

    return {
        "risk_level": risk,
        "priority": priority,
        "signals": {
            "urgency_language": urgent,
            "amount": amount,
            "incomplete_intake": not validation.get("complete", False),
        },
    }
