"""
Judge0 Client (Session 28a, Career Assessment Phase 2b).

Thin wrapper around Judge0 CE for code execution. Used by the Career
Assessment coding format to run candidate submissions against test
cases.

Default endpoint: https://ce.judge0.com (free, no auth, no signup).
Optional: JUDGE0_API_KEY (for RapidAPI-hosted migration later).

Public API:
  run_code(source_code, stdin, expected_output, language_id, timeout_ms) -> dict
  run_test_cases(source_code, test_cases, language_id, timeout_ms) -> dict

Never raises. On failure returns {"status": "error", "message": ...}.
"""

import os
import time
import logging
import requests
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Language map (Judge0 numeric IDs). Python is the only one wired up in
# Session 28a; the rest are declared for 28b/28c expansion.
# ---------------------------------------------------------------------------
LANGUAGE_IDS = {
    "python":     71,   # Python 3.8.1
    "javascript": 63,   # Node.js 12.14.0
    "java":       62,   # Java (OpenJDK 13.0.1)
    "cpp":        54,   # C++ (GCC 9.2.0)
    "go":         60,   # Go 1.13.5
}

DEFAULT_LANGUAGE = "python"
DEFAULT_TIMEOUT_MS = 5000


class Judge0Client:
    def __init__(self):
        self.base_url = os.getenv("JUDGE0_BASE_URL", "https://ce.judge0.com").rstrip("/")
        self.api_key = os.getenv("JUDGE0_API_KEY", "").strip()

    def _headers(self) -> Dict[str, str]:
        h = {"Content-Type": "application/json"}
        # Only add the RapidAPI-style header if a key is set. This keeps
        # ce.judge0.com (no key) and RapidAPI (key) on the same code path.
        if self.api_key:
            h["X-RapidAPI-Key"] = self.api_key
        return h

    def _resolve_language_id(self, language) -> Optional[int]:
        if isinstance(language, int):
            return language
        if isinstance(language, str):
            return LANGUAGE_IDS.get(language.lower())
        return None

    # ----------------------------------------------------------------- public

    def run_code(
        self,
        source_code: str,
        stdin: str = "",
        expected_output: str = "",
        language_id: int = LANGUAGE_IDS["python"],
        timeout_ms: int = DEFAULT_TIMEOUT_MS,
    ) -> Dict:
        """
        Execute one code submission against one stdin. Returns a normalized dict:

        {
            "status":        "success" | "error",
            "accepted":      bool,             # only meaningful if expected_output given
            "stdout":        str,
            "stderr":        str,
            "compile_output": str,
            "exit_code":     int | None,
            "time_s":        float,
            "memory_kb":     int,
            "timed_out":     bool,
            "message":       str | None,       # only on error
            "raw_status":    str               # Judge0 status description
        }
        """
        url = f"{self.base_url}/submissions?base64_encoded=false&wait=true"
        payload = {
            "source_code": source_code,
            "language_id": language_id,
            "stdin": stdin or "",
            "cpu_time_limit": max(1, int(timeout_ms / 1000)),
            "wall_time_limit": max(1, int((timeout_ms + 1000) / 1000)),
        }
        if expected_output:
            payload["expected_output"] = expected_output

        try:
            r = requests.post(url, json=payload, headers=self._headers(), timeout=(timeout_ms / 1000) + 5)
        except requests.exceptions.Timeout:
            return {
                "status": "error",
                "message": "Judge0 request timed out",
                "timed_out": True,
                "stdout": "", "stderr": "", "compile_output": "",
                "exit_code": None, "time_s": 0.0, "memory_kb": 0,
                "accepted": False, "raw_status": "ClientTimeout",
            }
        except Exception as e:
            logger.warning(f"[judge0] request failed: {e}")
            return {
                "status": "error",
                "message": f"Judge0 request failed: {e}",
                "timed_out": False,
                "stdout": "", "stderr": "", "compile_output": "",
                "exit_code": None, "time_s": 0.0, "memory_kb": 0,
                "accepted": False, "raw_status": "ClientError",
            }

        if r.status_code != 200 and r.status_code != 201:
            return {
                "status": "error",
                "message": f"Judge0 HTTP {r.status_code}: {r.text[:200]}",
                "timed_out": False,
                "stdout": "", "stderr": "", "compile_output": "",
                "exit_code": None, "time_s": 0.0, "memory_kb": 0,
                "accepted": False, "raw_status": f"HTTP{r.status_code}",
            }

        try:
            data = r.json()
        except Exception as e:
            return {
                "status": "error",
                "message": f"Judge0 returned non-JSON: {e}",
                "timed_out": False,
                "stdout": "", "stderr": "", "compile_output": "",
                "exit_code": None, "time_s": 0.0, "memory_kb": 0,
                "accepted": False, "raw_status": "BadJSON",
            }

        return self._normalize(data)

    def run_test_cases(
        self,
        source_code: str,
        test_cases: List[Dict],
        language_id: int = LANGUAGE_IDS["python"],
        timeout_ms: int = DEFAULT_TIMEOUT_MS,
    ) -> Dict:
        """
        Run one code submission against N test cases (sequentially).
        Each test case is {"stdin": "...", "expected_output": "..."}.

        Returns:
        {
            "status":     "success" | "error",
            "total":      int,
            "passed":     int,
            "score":      int,          # 0-100, rounded
            "cases":      [ {case_index, passed, stdout, stderr, time_s, memory_kb} ... ],
            "message":    str | None    # only on hard error
        }
        """
        if not test_cases:
            return {
                "status": "error",
                "message": "No test cases provided",
                "total": 0, "passed": 0, "score": 0, "cases": [],
            }

        results = []
        for i, tc in enumerate(test_cases):
            stdin = tc.get("stdin", "")
            expected = tc.get("expected_output", "")
            r = self.run_code(
                source_code=source_code,
                stdin=stdin,
                expected_output=expected,
                language_id=language_id,
                timeout_ms=timeout_ms,
            )
            results.append({
                "case_index": i,
                "passed": bool(r.get("accepted")),
                "stdout": r.get("stdout", ""),
                "stderr": r.get("stderr", ""),
                "time_s": r.get("time_s", 0.0),
                "memory_kb": r.get("memory_kb", 0),
                "raw_status": r.get("raw_status", ""),
            })

        total = len(results)
        passed = sum(1 for x in results if x["passed"])
        score = int(round(passed / total * 100)) if total else 0

        return {
            "status": "success",
            "total": total,
            "passed": passed,
            "score": score,
            "cases": results,
            "message": None,
        }

    # --------------------------------------------------------------- internal

    def _normalize(self, data: Dict) -> Dict:
        """Convert Judge0's native response into the engine-facing shape."""
        status = data.get("status") or {}
        status_id = status.get("id")
        status_desc = status.get("description", "") or ""

        # Judge0 status IDs:
        #   1 = In Queue, 2 = Processing, 3 = Accepted
        #   4 = Wrong Answer, 5 = Time Limit Exceeded
        #   6 = Compilation Error, 7-12 = runtime errors, 13 = Internal Error
        accepted = (status_id == 3)
        timed_out = (status_id == 5)

        def _safe_str(v):
            return v if isinstance(v, str) else ("" if v is None else str(v))

        return {
            "status": "success",
            "accepted": accepted,
            "stdout": _safe_str(data.get("stdout")),
            "stderr": _safe_str(data.get("stderr")),
            "compile_output": _safe_str(data.get("compile_output")),
            "exit_code": None,   # Judge0 CE doesn't return exit code in the standard shape
            "time_s": float(data.get("time") or 0.0),
            "memory_kb": int(data.get("memory") or 0),
            "timed_out": timed_out,
            "raw_status": status_desc,
            "message": data.get("message"),
        }


# Module-level singleton, matching the pattern of payment_engine, ai_credit_engine, etc.
judge0_client = Judge0Client()