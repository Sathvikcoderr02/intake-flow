from typing import Any, Optional

from pydantic import BaseModel, Field


class ClassifyResult(BaseModel):
    request_type: str = Field(
        ...,
        description="Short snake_case label for the request category",
    )
    confidence: float = Field(..., ge=0.0, le=1.0)
    summary: str = Field(..., description="One sentence factual summary")


class ExtractResult(BaseModel):
    structured: dict[str, Any] = Field(default_factory=dict)
    notes: Optional[str] = Field(
        default=None,
        description="Optional ambiguities or extraction caveats",
    )


class WorkflowTraceStep(BaseModel):
    step: str
    status: str
    detail: str


class IntakeResponse(BaseModel):
    request_type: str
    classification: ClassifyResult
    extracted: ExtractResult
    validation: dict[str, Any]
    risk_priority: dict[str, Any]
    recommended_action: str
    trace: list[WorkflowTraceStep]


class ProcessRequestBody(BaseModel):
    request_text: str
