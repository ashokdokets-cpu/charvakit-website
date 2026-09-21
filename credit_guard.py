# -*- coding: utf-8 -*-
"""
Charvak Credit Guard (Session G6)
Reusable helper for enforcing credit checks in FastAPI routes.

Two call patterns:
  1. require_credits_from_data(data, feature) -> dict
     Use when you've already parsed the request body as JSON.
     Returns success dict OR {"status": "error", "_http_status": 401/402, ...}.

  2. require_credits_dep(feature) -> FastAPI dependency
     Use as a router-level dependency when you don't have the body yet.
     Reads body, extracts email, enforces credits, raises HTTPException on failure.

Admin bypass is inherited from ai_credit_engine — admin emails are never charged.
"""
import logging
from fastapi import HTTPException, Request

logger = logging.getLogger("charvakit.credit_guard")

ADMIN_BYPASS_NOTE = "admin_bypass"


def require_credits_from_data(data: dict, feature: str) -> dict:
    """
    Enforce credits using an already-parsed request body.
    Returns:
        {"status": "success", "email": ..., "credits_deducted": ..., "credits_remaining": ...}
        OR
        {"status": "error", "_http_status": 401 or 402, "message": ..., ...}
    Caller is responsible for returning a JSONResponse with _http_status on error.
    """
    from ai_credit_engine import ai_credit_engine

    if not isinstance(data, dict):
        return {
            "status": "error",
            "_http_status": 400,
            "message": "Invalid request body.",
        }

    email = (data.get("email") or "").strip().lower()
    if not email:
        return {
            "status": "error",
            "_http_status": 401,
            "message": "Login required. Please log in and try again.",
            "login_url": "/login",
        }

    try:
        result = ai_credit_engine.check_and_deduct(email, feature)
    except Exception as e:
        logger.error(f"credit_guard check_and_deduct failed: {e}")
        return {
            "status": "error",
            "_http_status": 500,
            "message": "Credit check failed. Please try again.",
        }

    if result.get("status") != "success":
        return {
            "status": "error",
            "_http_status": 402,
            "message": result.get("message", "Insufficient credits."),
            "credits_needed": result.get("credits_needed"),
            "credits_remaining": result.get("credits_remaining"),
            "feature": feature,
            "buy_url": "/ai-credits-pricing",
        }

    # Success: include email so caller can reuse without reparsing
    result["email"] = email
    result["feature"] = feature
    return result


async def require_credits_dep(feature: str):
    """
    FastAPI dependency factory. Use as:
        @app.post("/api/x", dependencies=[Depends(require_credits_dep("feature_key"))])
    Raises HTTPException(401) if no email, HTTPException(402) if insufficient credits.
    Admin bypass: inherited from ai_credit_engine.
    """
    async def _dep(request: Request):
        from ai_credit_engine import ai_credit_engine

        try:
            data = await request.json()
        except Exception:
            data = {}

        email = (data.get("email") or "").strip().lower()
        if not email:
            raise HTTPException(
                status_code=401,
                detail={"status": "error", "message": "Login required.", "login_url": "/login"},
            )

        try:
            result = ai_credit_engine.check_and_deduct(email, feature)
        except Exception as e:
            logger.error(f"credit_guard dep failed: {e}")
            raise HTTPException(status_code=500, detail={"status": "error", "message": "Credit check failed."})

        if result.get("status") != "success":
            raise HTTPException(
                status_code=402,
                detail={
                    "status": "error",
                    "message": result.get("message", "Insufficient credits."),
                    "credits_needed": result.get("credits_needed"),
                    "credits_remaining": result.get("credits_remaining"),
                    "feature": feature,
                    "buy_url": "/ai-credits-pricing",
                },
            )

        return result

    return _dep