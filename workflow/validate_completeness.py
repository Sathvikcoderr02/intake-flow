import re
from typing import Any

from workflow.schemas import ClassifyResult, ExtractResult

# Minimum fields we expect for common intake types (rule-based).
_REQUIRED_BY_TYPE: dict[str, list[str]] = {
    "refund_request": ["amount", "contact_email"],
    "invoice_query": ["contact_email"],
    "support_issue": ["contact_email"],
    "account_change": ["contact_email"],
}


def _has_value(structured: dict[str, Any], key: str) -> bool:
    val = structured.get(key)
    if val is None:
        return False
    if isinstance(val, str) and not val.strip():
        return False
    return True


def _looks_like_email(s: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", s.strip()))


def _validate_contract_review(structured: dict[str, Any]) -> dict[str, Any]:
    """
    Contract / legal intake: email is optional if we can identify a party
    (company or requester name). Invalid email still fails when that is the
    only identifier provided.
    """
    email = structured.get("contact_email")
    has_email = _has_value(structured, "contact_email")
    email_ok = isinstance(email, str) and _looks_like_email(email)
    has_party = _has_value(structured, "company") or _has_value(
        structured, "customer_name"
    )

    missing: list[str] = []
    if has_email and not email_ok and not has_party:
        missing.append("contact_email_valid_format")

    if email_ok or has_party:
        complete = len(missing) == 0
        rationale = (
            "Valid contact email on file."
            if email_ok
            else "Party or company identified; contact email optional for this profile."
        )
    else:
        complete = False
        if not missing:
            missing.append("contact_email_or_party_identity")
        rationale = (
            "Provide a valid contact email, or company / requester name so the "
            "request can be routed."
        )

    return {
        "complete": complete,
        "missing_fields": missing,
        "required_profile": "contract_review",
        "email_format_ok": email_ok if isinstance(email, str) else None,
        "rationale": rationale,
    }


def validate_completeness(
    classification: ClassifyResult,
    extracted: ExtractResult,
) -> dict[str, Any]:
    structured = extracted.structured or {}
    req_type = classification.request_type.lower().strip()

    if req_type == "contract_review":
        return _validate_contract_review(structured)

    required = _REQUIRED_BY_TYPE.get(req_type, ["contact_email"])

    missing: list[str] = []
    for field in required:
        if not _has_value(structured, field):
            missing.append(field)

    email = structured.get("contact_email")
    email_ok = isinstance(email, str) and _looks_like_email(email)
    if "contact_email" in required and email and not email_ok:
        missing.append("contact_email_valid_format")

    complete = len(missing) == 0
    return {
        "complete": complete,
        "missing_fields": missing,
        "required_profile": req_type,
        "email_format_ok": email_ok if isinstance(email, str) else None,
        "rationale": (
            "All required fields for this request profile are present."
            if complete
            else f"Missing or empty: {', '.join(missing)}"
        ),
    }
