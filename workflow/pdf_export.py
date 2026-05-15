from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fpdf import FPDF

from workflow.schemas import IntakeResponse


def _register_fonts(pdf: FPDF) -> str:
    try:
        import fpdf as fpdf_pkg
        from pathlib import Path

        path = Path(fpdf_pkg.__file__).resolve().parent / "font" / "DejaVuSans.ttf"
        if path.is_file():
            pdf.add_font("DejaVu", "", str(path))
            return "DejaVu"
    except (OSError, RuntimeError, ValueError):
        pass
    return "Helvetica"


def _heading(pdf: FPDF, family: str, title: str) -> None:
    w = pdf.epw
    pdf.set_font(family, size=12)
    pdf.multi_cell(w, 7, title)
    pdf.set_font(family, size=10)
    pdf.ln(2)


def _kv_block(pdf: FPDF, family: str, rows: list[tuple[str, str]]) -> None:
    pdf.set_font(family, size=10)
    w = pdf.epw
    for label, value in rows:
        line = f"{label}: {value}"
        pdf.multi_cell(w, 6, line)
    pdf.ln(2)


def intake_response_to_pdf(result: IntakeResponse) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=14)
    pdf.set_margins(14, 14, 14)
    pdf.add_page()
    family = _register_fonts(pdf)
    pdf.set_font(family, size=10)
    w = pdf.epw

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    _heading(pdf, family, "Intake workflow result")
    pdf.multi_cell(w, 6, f"Generated: {ts}")
    pdf.ln(4)

    c = result.classification
    _heading(pdf, family, "Classification")
    _kv_block(
        pdf,
        family,
        [
            ("Request type", result.request_type),
            ("Confidence", f"{c.confidence:.2f}"),
            ("Summary", c.summary),
        ],
    )

    _heading(pdf, family, "Extracted information")
    structured = result.extracted.structured or {}
    if not structured:
        pdf.multi_cell(w, 6, "(No structured fields)")
        pdf.ln(2)
    else:
        for k in sorted(structured.keys(), key=str.lower):
            v = structured.get(k)
            _kv_block(pdf, family, [(str(k), str(v) if v is not None else "")])
    if result.extracted.notes:
        pdf.multi_cell(w, 6, f"Notes: {result.extracted.notes}")
        pdf.ln(2)

    _heading(pdf, family, "Validation")
    vmap: dict[str, Any] = dict(result.validation)
    missing = vmap.get("missing_fields") or []
    miss_s = ", ".join(str(x) for x in missing) if missing else "-"
    _kv_block(
        pdf,
        family,
        [
            ("Complete", "Yes" if vmap.get("complete") else "No"),
            ("Missing fields", miss_s),
            ("Rationale", str(vmap.get("rationale", ""))),
        ],
    )

    _heading(pdf, family, "Risk / priority")
    rp = result.risk_priority
    _kv_block(
        pdf,
        family,
        [
            ("Risk level", str(rp.get("risk_level", ""))),
            ("Priority", str(rp.get("priority", ""))),
        ],
    )

    _heading(pdf, family, "Recommended next action")
    pdf.multi_cell(w, 6, result.recommended_action)
    pdf.ln(4)

    _heading(pdf, family, "Workflow trace")
    for step in result.trace:
        pdf.multi_cell(w, 6, f"[{step.status}] {step.step}: {step.detail}")
    pdf.ln(2)

    out = pdf.output(dest="S")
    if isinstance(out, str):
        return out.encode("latin-1")
    return bytes(out)
