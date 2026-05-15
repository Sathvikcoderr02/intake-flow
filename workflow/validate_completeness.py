import re
from typing import Any

from workflow.schemas import ClassifyResult, ExtractResult

# Minimum fields we expect for common intake types (rule-based).
_REQUIRED_BY_TYPE: dict[str, list[str]] = {
    "refund_request": ["amount", "contact_email"],
    "invoice_query": ["contact_email"],
    "support_issue": ["contact_email"],
    "contract_review": ["contact_email"],
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


def validate_completeness(
    classification: ClassifyResult,
    extracted: ExtractResult,
) -> dict[str, Any]:
    structured = extracted.structured or {}
    req_type = classification.request_type.lower().strip()
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
