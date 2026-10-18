"""
OpenAI API compatibility shim
Session 53 (2026-10-19) - Phase 3a

Handles the API differences between gpt-4o-mini (retiring Jan 14, 2027)
and gpt-5.x series:

1. gpt-4o-mini uses max_tokens=
2. gpt-5.x uses max_completion_tokens=
3. gpt-5.5+ rejects non-default temperature (only temp=1 allowed)

This shim builds model-aware payloads. Callers always pass max_tokens=
and the shim translates to the correct field for the model.

Usage (in any module that hits OpenAI via httpx):
    from openai_compat import build_payload
    payload = build_payload(model, messages, max_tokens=500,
                             temperature=0.7, json_mode=True)

Usage (with the higher-level httpx helper):
    from openai_compat import call_openai_raw
    data = await call_openai_raw(model, messages, max_tokens=500)

See COMMITMENT.md "Phase 2 Evaluation — RESULT (2026-10-19)" for the
model successor decision and migration plan.
"""

import os
import httpx

OPENAI_BASE = os.getenv("OPENAI_BASE", "https://api.openai.com/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


def _is_gpt5(model: str) -> bool:
    """Is this a GPT-5.x model? (uses max_completion_tokens)"""
    return bool(model) and model.startswith("gpt-5")


def _is_gpt55_plus(model: str) -> bool:
    """Is this GPT-5.5 or newer? (rejects non-default temperature)"""
    return bool(model) and model.startswith("gpt-5.5")


def build_payload(model: str, messages: list, max_tokens: int = None,
                   temperature: float = 0.7, json_mode: bool = False,
                   **extra) -> dict:
    """
    Build a model-aware OpenAI chat completion payload.

    Args:
        model: OpenAI model id (e.g. "gpt-4o-mini", "gpt-5.4-nano")
        messages: chat messages list
        max_tokens: token budget (translated to correct param)
        temperature: model temperature (skipped for gpt-5.5+)
        json_mode: whether to force JSON response_format
        **extra: additional params passed through (e.g. tools, stop)

    Returns:
        dict ready to POST to /chat/completions
    """
    payload = {
        "model": model,
        "messages": messages,
    }

    # Token param: GPT-5.x requires max_completion_tokens
    if max_tokens is not None:
        if _is_gpt5(model):
            payload["max_completion_tokens"] = max_tokens
        else:
            payload["max_tokens"] = max_tokens

    # Temperature: GPT-5.5+ only accepts default (1.0)
    if _is_gpt55_plus(model):
        # Deliberately omitted — let the model use its default
        pass
    else:
        payload["temperature"] = temperature

    # JSON mode
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    # Extra kwargs pass-through (tools, stop, seed, etc.)
    for k, v in extra.items():
        payload[k] = v

    return payload


async def call_openai_raw(model: str, messages: list, **kwargs) -> dict:
    """
    Direct httpx call to OpenAI with compat payload building.

    Returns the raw API response JSON (or {"error": "..."} on failure).
    """
    if not OPENAI_API_KEY:
        return {"error": "OPENAI_API_KEY not set"}

    payload = build_payload(model, messages, **kwargs)
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{OPENAI_BASE}/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            return response.json()
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}

def translate_kwargs(model: str, max_tokens: int = None,
                      temperature: float = 0.7, json_mode: bool = False,
                      **extra) -> dict:
    """
    Translate caller kwargs into model-appropriate OpenAI SDK kwargs.

    Designed for use with the `openai` Python SDK (>= 1.0):
        from openai_compat import translate_kwargs
        response = client.chat.completions.create(
            model=model, messages=messages,
            **translate_kwargs(model, max_tokens=500, temperature=0.7, json_mode=True)
        )

    Handles:
    - gpt-5.x    -> max_completion_tokens
    - gpt-4o-*   -> max_tokens (backward compat)
    - gpt-5.5+   -> skips temperature (rejects non-default)
    - json_mode  -> response_format json_object
    """
    kwargs = {}

    # Token param: GPT-5.x requires max_completion_tokens
    if max_tokens is not None:
        if _is_gpt5(model):
            kwargs["max_completion_tokens"] = max_tokens
        else:
            kwargs["max_tokens"] = max_tokens

    # Temperature: GPT-5.5+ only accepts default (1.0)
    if not _is_gpt55_plus(model):
        kwargs["temperature"] = temperature

    # JSON mode
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    # Extra kwargs pass-through (tools, stop, seed, etc.)
    for k, v in extra.items():
        kwargs[k] = v

    return kwargs
