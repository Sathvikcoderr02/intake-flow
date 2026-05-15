import json
import os
from typing import Any, TypeVar

import google.generativeai as genai
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


def _get_model_name() -> str:
    return os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()


def configure_gemini() -> None:
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Copy .env.example to .env and add your key."
        )
    genai.configure(api_key=key)


def generate_json_model(
    system_prompt: str,
    user_prompt: str,
    model_cls: type[T],
    temperature: float = 0.2,
) -> T:
    configure_gemini()
    schema_json = json.dumps(model_cls.model_json_schema(), indent=2)
    full_system = (
        f"{system_prompt}\n\n"
        "Respond with JSON only (no markdown fences) that validates against:\n"
        f"{schema_json}"
    )
    model = genai.GenerativeModel(
        model_name=_get_model_name(),
        system_instruction=full_system,
        generation_config=genai.GenerationConfig(
            temperature=temperature,
            response_mime_type="application/json",
        ),
    )
    response = model.generate_content(user_prompt)
    text = (response.text or "").strip()
    try:
        data: dict[str, Any] = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Model returned non-JSON: {text[:500]}") from exc
    try:
        return model_cls.model_validate(data)
    except ValidationError as exc:
        raise ValueError(f"Model JSON failed validation: {data}") from exc
