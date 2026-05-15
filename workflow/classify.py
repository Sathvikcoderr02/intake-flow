from workflow.llm import generate_json_model
from workflow.schemas import ClassifyResult


def classify_request(request_text: str) -> ClassifyResult:
    system = (
        "You classify inbound business requests for an operations intake queue. "
        "Choose a concise snake_case request_type (e.g. refund_request, invoice_query, "
        "contract_review, support_issue, account_change, other). "
        "confidence is how sure you are from 0 to 1. summary is one factual sentence."
    )
    user = f"Classify this request:\n\n{request_text.strip()}"
    return generate_json_model(system, user, ClassifyResult, temperature=0.1)
