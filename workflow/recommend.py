from typing import Any

from workflow.schemas import ClassifyResult, ExtractResult


def recommend_next_action(
    classification: ClassifyResult,
    extracted: ExtractResult,
    validation: dict[str, Any],
    risk_priority: dict[str, object],
) -> str:
    if not validation.get("complete"):
        return (
            "Reply to the requester asking only for the missing fields listed under "
            "validation; do not start processing until intake is complete."
        )

    req = classification.request_type.lower()
    risk = str(risk_priority.get("risk_level", "low"))

    if "refund" in req:
        base = (
            "Open a refund case in payments ops, attach bank/payment references, "
            "and initiate reconciliation with finance."
        )
    elif "invoice" in req:
        base = "Route to AR/billing with invoice identifiers for lookup and response."
    elif "contract" in req:
        base = "Assign to legal for review with the contract version and counterparty."
    elif "support" in req:
        base = "Create a support ticket with severity from priority and assign to L1."
    else:
        base = "Triage in the general intake queue and assign an owner by domain."

    if risk == "high":
        return base + " Flag for supervisor review due to elevated risk signals."
    return base
