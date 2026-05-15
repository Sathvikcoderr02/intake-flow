from workflow.classify import classify_request
from workflow.extract import extract_information
from workflow.recommend import recommend_next_action
from workflow.risk_priority import assess_risk_priority
from workflow.schemas import IntakeResponse, WorkflowTraceStep
from workflow.validate_completeness import validate_completeness


def run_intake_workflow(request_text: str) -> IntakeResponse:
    trace: list[WorkflowTraceStep] = []

    if not request_text or not request_text.strip():
        raise ValueError("Request text is empty.")

    try:
        classification = classify_request(request_text)
        trace.append(
            WorkflowTraceStep(
                step="classify",
                status="ok",
                detail=f"type={classification.request_type}",
            )
        )
    except Exception as exc:  # noqa: BLE001 — surface to API layer
        trace.append(
            WorkflowTraceStep(
                step="classify",
                status="error",
                detail=str(exc),
            )
        )
        raise

    try:
        extracted = extract_information(request_text, classification)
        trace.append(
            WorkflowTraceStep(
                step="extract",
                status="ok",
                detail=f"keys={list((extracted.structured or {}).keys())}",
            )
        )
    except Exception as exc:  # noqa: BLE001
        trace.append(
            WorkflowTraceStep(step="extract", status="error", detail=str(exc))
        )
        raise

    validation = validate_completeness(classification, extracted)
    trace.append(
        WorkflowTraceStep(
            step="validate",
            status="ok",
            detail="rule_based_completeness_check",
        )
    )

    risk_priority = assess_risk_priority(classification, extracted, validation)
    trace.append(
        WorkflowTraceStep(
            step="risk_priority",
            status="ok",
            detail=f"{risk_priority.get('risk_level')}/{risk_priority.get('priority')}",
        )
    )

    action = recommend_next_action(
        classification, extracted, validation, risk_priority
    )
    trace.append(
        WorkflowTraceStep(
            step="recommend",
            status="ok",
            detail="rule_based_next_action",
        )
    )

    return IntakeResponse(
        request_type=classification.request_type,
        classification=classification,
        extracted=extracted,
        validation=validation,
        risk_priority=risk_priority,
        recommended_action=action,
        trace=trace,
    )
