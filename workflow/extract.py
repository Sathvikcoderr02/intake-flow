from workflow.llm import generate_json_model
from workflow.schemas import ClassifyResult, ExtractResult


def extract_information(request_text: str, classification: ClassifyResult) -> ExtractResult:
    system = (
        "You extract structured business fields from unstructured request text. "
        "Populate `structured` with keys only when present or strongly implied "
        "(e.g. customer_name, company, amount, currency, dates, invoice_id, "
        "customer_id, payment_reference, contact_email, subject, urgency_phrases). "
        "Use string values; omit unknown keys. notes: ambiguities only."
    )
    user = (
        f"Request type (hint): {classification.request_type}\n"
        f"Summary (hint): {classification.summary}\n\n"
        f"Extract from:\n\n{request_text.strip()}"
    )
    return generate_json_model(system, user, ExtractResult, temperature=0.1)
