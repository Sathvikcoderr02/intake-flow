import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env", override=True)

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from workflow.pipeline import run_intake_workflow
from workflow.schemas import IntakeResponse, ProcessRequestBody

app = FastAPI(title="Intake Workflow", version="1.0.0")

_STATIC = Path(__file__).resolve().parent / "static"


@app.get("/")
def root() -> FileResponse:
    index = _STATIC / "index.html"
    if not index.exists():
        raise HTTPException(status_code=500, detail="UI bundle missing")
    return FileResponse(index)


@app.post("/api/process", response_model=IntakeResponse)
def process(body: ProcessRequestBody) -> IntakeResponse:
    try:
        return run_intake_workflow(body.request_text)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=502,
            detail=f"Workflow failed: {exc}",
        ) from exc


app.mount("/static", StaticFiles(directory=str(_STATIC)), name="static")


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
