"""
recruiter_screen_engine.py

F3 — Enterprise AI recruiter screen agent.

Two-phase chat screening:
  Phase 1 (3 questions): years exp, current CTC, expected CTC
  Phase 2 (9 questions): remaining fields for qualified candidates

Features:
- Structured field extraction via OpenAI JSON mode
- Budget-based auto-qualification
- Auto-scheduling with calendar links
- Full audit trail (5 tables)
- Consent capture
- Rate limiting per candidate
- Escalation to human on edge cases
"""

import os
import json
import uuid
import secrets
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("charvakit.screen_agent")


# Defensive OpenAI model getter — falls back to global_config if env vars missing
def _get_openai_model(cheap=True):
    import os
    try:
        from global_config import OPENAI_MODEL, OPENAI_MODEL_CHEAP
    except ImportError:
        OPENAI_MODEL = "gpt-4o-mini"
        OPENAI_MODEL_CHEAP = OPENAI_MODEL
    if cheap:
        return os.getenv("OPENAI_MODEL_CHEAP") or OPENAI_MODEL_CHEAP or OPENAI_MODEL or "gpt-4o-mini"
    return os.getenv("OPENAI_MODEL") or OPENAI_MODEL or "gpt-4o-mini"


PHASE1_FIELDS = ["total_experience_years", "current_ctc_inr", "expected_ctc_inr"]
PHASE2_FIELDS = [
    "current_role", "current_company", "notice_period_days",
    "work_authorization", "availability_date", "preferred_work_mode",
    "current_location", "reason_for_change", "relocation_willingness"
]
ALL_FIELDS = PHASE1_FIELDS + PHASE2_FIELDS

DEFAULT_CONSENT = (
    "Charvak will use AI to screen your application for this role. "
    "Your responses are logged for audit purposes and shared with the recruiter. "
    "You can pause, exit, or request a human at any time. "
    "Data is retained for 90 days unless you request erasure. "
    "By continuing, you consent to this processing."
)

DEFAULT_EXPIRY_DAYS = 7


class RecruiterScreenEngine:
    def __init__(self):
        self._ensure_tables()

    def _ensure_tables(self):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute(open("migrations/20261027_screen_agent.sql", "r", encoding="utf-8").read())
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.debug(f"_ensure_tables: {e}")

    def _gen_id(self, prefix: str) -> str:
        return f"{prefix}-{secrets.token_hex(6).upper()}"

    def _log_event(self, candidate_screen_id: Optional[str], session_id: Optional[str],
                   event_type: str, event_data: dict, ip: str = None, ua: str = None):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute(
                """INSERT INTO charvak_screen_events
                   (event_id, candidate_screen_id, session_id, event_type, event_data, ip_address, user_agent)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (self._gen_id("SCREV"), candidate_screen_id, session_id, event_type,
                 json.dumps(event_data), ip, ua)
            )
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.warning(f"_log_event failed: {e}")

    def create_screen_session(self, recruiter_email: str, jd_text: str,
                              budget_max_inr: Optional[int] = None,
                              role_id: Optional[str] = None,
                              language: str = "en",
                              consent_text: Optional[str] = None,
                              expiry_days: int = DEFAULT_EXPIRY_DAYS) -> dict:
        """Create a screen session from a JD. Parses JD via jd_parser_engine."""
        try:
            from jd_parser_engine import parse_jd
            _result = parse_jd(jd_text)
            # unwrap jd_parser result: it returns {"status": "success", "parsed": {...}}
            if isinstance(_result, dict) and "parsed" in _result and isinstance(_result["parsed"], dict):
                parsed = _result["parsed"]
            elif isinstance(_result, dict):
                parsed = _result
            else:
                parsed = {}
        except Exception as e:
            logger.error(f"parse_jd failed: {e}")
            parsed = {}

        # Extract budget from parsed JD if not overridden
        if budget_max_inr is None:
            parsed_budget = None
            if isinstance(parsed, dict):
                sal = parsed.get("salary_range") or parsed.get("compensation")
                if isinstance(sal, dict):
                    parsed_budget = sal.get("max_inr")
                elif isinstance(sal, str):
                    import re
                    nums = re.findall(r"(\d+(?:\.\d+)?)\s*(?:L|lakh|lpa|LPA)", sal)
                    if nums:
                        parsed_budget = int(float(nums[-1]) * 100000)
            budget_max_inr = parsed_budget

        session_id = self._gen_id("SCREEN")
        role_title = parsed.get("title", "Unknown Role") if isinstance(parsed, dict) else "Unknown Role"
        company_name = parsed.get("company", "") if isinstance(parsed, dict) else ""
        consent = consent_text or DEFAULT_CONSENT
        expires_at = datetime.now() + timedelta(days=expiry_days)

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute(
                """INSERT INTO charvak_screen_sessions
                   (session_id, recruiter_email, role_id, jd_text, parsed_jd, role_title,
                    company_name, budget_max_inr, consent_text, language, expires_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (session_id, recruiter_email.lower(), role_id, jd_text,
                 json.dumps(parsed), role_title, company_name, budget_max_inr,
                 consent, language, expires_at)
            )
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"create_screen_session insert failed: {e}")
            return {"status": "error", "message": str(e)}

        self._log_event(None, session_id, "session_created", {
            "role_title": role_title,
            "budget_max_inr": budget_max_inr,
            "language": language,
        })

        return {
            "status": "success",
            "session_id": session_id,
            "role_title": role_title,
            "company_name": company_name,
            "budget_max_inr": budget_max_inr,
            "parsed_jd": parsed,
            "consent_text": consent,
            "expires_at": expires_at.isoformat(),
        }

    def get_session(self, session_id: str, include_candidates: bool = True) -> dict:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute(
                """SELECT session_id, recruiter_email, role_id, jd_text, parsed_jd,
                          role_title, company_name, status, candidates_invited,
                          candidates_responded, candidates_qualified, budget_max_inr,
                          consent_text, language, expires_at, created_at, completed_at
                   FROM charvak_screen_sessions WHERE session_id = %s""",
                (session_id,)
            )
            row = cur.fetchone()
            if not row:
                cur.close(); conn.close()
                return {"status": "error", "message": "Session not found."}

            session = {
                "session_id": row[0], "recruiter_email": row[1], "role_id": row[2],
                "jd_text": row[3], "parsed_jd": row[4], "role_title": row[5],
                "company_name": row[6], "status": row[7],
                "candidates_invited": row[8], "candidates_responded": row[9],
                "candidates_qualified": row[10], "budget_max_inr": row[11],
                "consent_text": row[12], "language": row[13],
                "expires_at": row[14].isoformat() if row[14] else None,
                "created_at": row[15].isoformat() if row[15] else None,
                "completed_at": row[16].isoformat() if row[16] else None,
            }

            if include_candidates:
                cur.execute(
                    """SELECT candidate_screen_id, token, candidate_email, candidate_name,
                              status, invited_at, first_response_at, completed_at,
                              qualification_score, qualified, disqualify_reason
                       FROM charvak_screen_candidates
                       WHERE session_id = %s ORDER BY invited_at DESC""",
                    (session_id,)
                )
                candidates = []
                for c in cur.fetchall():
                    candidates.append({
                        "candidate_screen_id": c[0], "token": c[1],
                        "email_masked": self._mask_email(c[2]),
                        "name": c[3], "status": c[4],
                        "invited_at": c[5].isoformat() if c[5] else None,
                        "first_response_at": c[6].isoformat() if c[6] else None,
                        "completed_at": c[7].isoformat() if c[7] else None,
                        "qualification_score": c[8], "qualified": c[9],
                        "disqualify_reason": c[10],
                    })
                session["candidates"] = candidates

            cur.close(); conn.close()
            return {"status": "success", "session": session}
        except Exception as e:
            logger.error(f"get_session failed: {e}")
            return {"status": "error", "message": str(e)}

    def list_sessions(self, recruiter_email: str, status: Optional[str] = None) -> list:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            if status:
                cur.execute(
                    """SELECT session_id, role_title, company_name, status,
                              candidates_invited, candidates_responded, candidates_qualified,
                              created_at
                       FROM charvak_screen_sessions
                       WHERE LOWER(recruiter_email) = LOWER(%s) AND status = %s
                       ORDER BY created_at DESC""",
                    (recruiter_email, status)
                )
            else:
                cur.execute(
                    """SELECT session_id, role_title, company_name, status,
                              candidates_invited, candidates_responded, candidates_qualified,
                              created_at
                       FROM charvak_screen_sessions
                       WHERE LOWER(recruiter_email) = LOWER(%s)
                       ORDER BY created_at DESC""",
                    (recruiter_email,)
                )
            rows = cur.fetchall()
            cur.close(); conn.close()
            return [
                {"session_id": r[0], "role_title": r[1], "company_name": r[2],
                 "status": r[3], "candidates_invited": r[4],
                 "candidates_responded": r[5], "candidates_qualified": r[6],
                 "created_at": r[7].isoformat() if r[7] else None}
                for r in rows
            ]
        except Exception as e:
            logger.error(f"list_sessions failed: {e}")
            return []

    def pause_session(self, session_id: str, recruiter_email: str) -> dict:
        return self._update_session_status(session_id, recruiter_email, "paused")

    def close_session(self, session_id: str, recruiter_email: str) -> dict:
        return self._update_session_status(session_id, recruiter_email, "closed", completed=True)

    def _update_session_status(self, session_id, recruiter_email, new_status, completed=False) -> dict:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute(
                "SELECT recruiter_email FROM charvak_screen_sessions WHERE session_id = %s",
                (session_id,)
            )
            row = cur.fetchone()
            if not row or row[0].lower() != recruiter_email.lower():
                cur.close(); conn.close()
                return {"status": "error", "message": "Not authorized or not found."}

            if completed:
                cur.execute(
                    "UPDATE charvak_screen_sessions SET status = %s, completed_at = NOW() WHERE session_id = %s",
                    (new_status, session_id)
                )
            else:
                cur.execute(
                    "UPDATE charvak_screen_sessions SET status = %s WHERE session_id = %s",
                    (new_status, session_id)
                )
            conn.commit()
            cur.close(); conn.close()
            return {"status": "success", "new_status": new_status}
        except Exception as e:
            logger.error(f"_update_session_status failed: {e}")
            return {"status": "error", "message": str(e)}

    def _mask_email(self, email: str) -> str:
        if not email or "@" not in email:
            return "anonymous"
        local, domain = email.split("@", 1)
        if len(local) <= 2:
            return local[0] + "*" * max(1, len(local) - 1) + "@" + domain
        return local[0] + "*" * (len(local) - 2) + local[-1] + "@" + domain


    # =====================================================
    # CHAT FLOW (Phase 1 + Phase 2)
    # =====================================================

    def invite_candidate(self, session_id, candidate_email, candidate_name=None):
        """Invite one candidate."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT status FROM charvak_screen_sessions WHERE session_id = %s", (session_id,))
            row = cur.fetchone()
            if not row or row[0] != "active":
                cur.close(); conn.close()
                return {"status": "error", "message": "Session not found or not active."}
            cur.execute(
                "SELECT candidate_screen_id, token FROM charvak_screen_candidates "
                "WHERE session_id = %s AND LOWER(candidate_email) = LOWER(%s)",
                (session_id, candidate_email)
            )
            existing = cur.fetchone()
            if existing:
                cur.close(); conn.close()
                return {
                    "status": "success", "candidate_screen_id": existing[0],
                    "token": existing[1], "invite_url": "/screen/" + existing[1],
                    "note": "already_invited",
                }
            candidate_screen_id = self._gen_id("SCAND")
            token = secrets.token_urlsafe(24)
            cur.execute(
                "INSERT INTO charvak_screen_candidates "
                "(candidate_screen_id, session_id, token, candidate_email, candidate_name) "
                "VALUES (%s, %s, %s, %s, %s)",
                (candidate_screen_id, session_id, token, candidate_email.lower(), candidate_name)
            )
            cur.execute(
                "UPDATE charvak_screen_sessions SET candidates_invited = candidates_invited + 1 "
                "WHERE session_id = %s",
                (session_id,)
            )
            conn.commit()
            cur.close(); conn.close()
            self._log_event(candidate_screen_id, session_id, "candidate_invited", {"candidate_email": candidate_email})
            return {"status": "success", "candidate_screen_id": candidate_screen_id,
                    "token": token, "invite_url": "/screen/" + token}
        except Exception as e:
            logger.error("invite_candidate failed: " + str(e))
            return {"status": "error", "message": str(e)}

    def invite_batch(self, session_id, candidates):
        invited = []
        failed = []
        for c in candidates:
            email = (c.get("email") or "").strip().lower()
            name = c.get("name")
            if not email or "@" not in email:
                failed.append({"email": email, "reason": "invalid_email"})
                continue
            result = self.invite_candidate(session_id, email, name)
            if result.get("status") == "success":
                invited.append({"email": email, "token": result["token"]})
            else:
                failed.append({"email": email, "reason": result.get("message", "unknown")})
        return {"status": "success", "invited_count": len(invited),
                "failed_count": len(failed), "invited": invited, "failed": failed}

    def get_candidate_by_token(self, token):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute(
                "SELECT c.candidate_screen_id, c.session_id, c.candidate_email, "
                "c.candidate_name, c.status, c.captured_data, c.language, "
                "c.consent_given_at, c.completed_at, c.qualified, "
                "s.role_title, s.company_name, s.consent_text, s.parsed_jd, "
                "s.budget_max_inr, s.language, s.expires_at, s.status "
                "FROM charvak_screen_candidates c "
                "JOIN charvak_screen_sessions s ON c.session_id = s.session_id "
                "WHERE c.token = %s",
                (token,)
            )
            row = cur.fetchone()
            if not row:
                cur.close(); conn.close()
                return {"status": "error", "message": "Invalid or expired link."}
            result = {
                "status": "success",
                "candidate": {
                    "candidate_screen_id": row[0], "session_id": row[1],
                    "email_masked": self._mask_email(row[2]), "name": row[3],
                    "status": row[4], "captured_data": row[5] or {},
                    "language": row[6],
                    "consent_given_at": row[7].isoformat() if row[7] else None,
                    "completed_at": row[8].isoformat() if row[8] else None,
                    "qualified": row[9],
                },
                "session": {
                    "role_title": row[10], "company_name": row[11],
                    "consent_text": row[12], "parsed_jd": row[13],
                    "budget_max_inr": row[14], "language": row[15],
                    "expires_at": row[16].isoformat() if row[16] else None,
                    "status": row[17],
                },
            }
            cur.close(); conn.close()
            return result
        except Exception as e:
            logger.error("get_candidate_by_token failed: " + str(e))
            return {"status": "error", "message": str(e)}

    def start_chat(self, token, ip=None, ua=None):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute(
                "SELECT c.candidate_screen_id, c.session_id, c.status, c.consent_given_at, c.captured_data "
                "FROM charvak_screen_candidates c WHERE c.token = %s",
                (token,)
            )
            row = cur.fetchone()
            if not row:
                cur.close(); conn.close()
                return {"status": "error", "message": "Invalid link."}
            candidate_screen_id, session_id, status, consent_at, captured = row

            if not consent_at:
                cur.execute(
                    "UPDATE charvak_screen_candidates SET consent_given_at = NOW(), "
                    "consent_ip = %s, status = 'chatting', first_response_at = NOW() "
                    "WHERE candidate_screen_id = %s",
                    (ip, candidate_screen_id)
                )
                cur.execute(
                    "UPDATE charvak_screen_sessions SET candidates_responded = candidates_responded + 1 "
                    "WHERE session_id = %s",
                    (session_id,)
                )
                conn.commit()
                self._log_event(candidate_screen_id, session_id, "consent_given", {}, ip, ua)

            captured = captured or {}
            next_field = self._next_field(captured)
            cur.close(); conn.close()

            if not next_field:
                return {"status": "success", "done": True, "message": "All questions complete."}

            question = self._question_for_field(next_field, captured)
            return {
                "status": "success", "next_field": next_field, "question": question,
                "phase": "phase1" if next_field in PHASE1_FIELDS else "phase2",
                "captured_so_far": list(captured.keys()), "done": False,
            }
        except Exception as e:
            logger.error("start_chat failed: " + str(e))
            return {"status": "error", "message": str(e)}

    def submit_answer(self, token, answer, ip=None, ua=None):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute(
                "SELECT c.candidate_screen_id, c.session_id, c.captured_data, "
                "s.role_title, s.company_name, s.parsed_jd, s.budget_max_inr "
                "FROM charvak_screen_candidates c "
                "JOIN charvak_screen_sessions s ON c.session_id = s.session_id "
                "WHERE c.token = %s",
                (token,)
            )
            row = cur.fetchone()
            if not row:
                cur.close(); conn.close()
                return {"status": "error", "message": "Invalid link."}
            candidate_screen_id, session_id, captured, role, company, jd, budget = row
            captured = captured or {}

            msg_id = self._gen_id("SMSG")
            cur.execute(
                "INSERT INTO charvak_screen_messages (message_id, candidate_screen_id, role, content) "
                "VALUES (%s, %s, %s, %s)",
                (msg_id, candidate_screen_id, "candidate", answer)
            )
            conn.commit()

            next_field = self._next_field(captured)
            if not next_field:
                cur.close(); conn.close()
                return {"status": "success", "done": True}

            extracted_value = self._extract_field(answer, next_field, role, budget)

            if extracted_value is not None:
                captured[next_field] = extracted_value
                cur.execute(
                    "UPDATE charvak_screen_candidates SET captured_data = %s WHERE candidate_screen_id = %s",
                    (json.dumps(captured), candidate_screen_id)
                )
                conn.commit()
                self._log_event(candidate_screen_id, session_id, "field_captured",
                                {"field": next_field, "value": extracted_value}, ip, ua)

                if next_field in PHASE1_FIELDS and all(f in captured for f in PHASE1_FIELDS):
                    passed, reason = self._check_phase1_qualification(captured, budget)
                    if not passed:
                        cur.execute(
                            "UPDATE charvak_screen_candidates SET status = 'disqualified', "
                            "qualified = FALSE, disqualify_reason = %s, completed_at = NOW() "
                            "WHERE candidate_screen_id = %s",
                            (reason, candidate_screen_id)
                        )
                        conn.commit()
                        cur.close(); conn.close()
                        self._log_event(candidate_screen_id, session_id, "disqualified_phase1", {"reason": reason}, ip, ua)
                        return {"status": "success", "done": True, "disqualified": True,
                                "reason": reason, "message": "Thank you for your time. " + reason}

            next_field = self._next_field(captured)
            if not next_field:
                cur.close(); conn.close()
                evaluation = self.evaluate_candidate(candidate_screen_id)
                slots = self.propose_schedule_slots(candidate_screen_id)
                return {"status": "success", "done": True,
                        "qualified": evaluation.get("qualified", True),
                        "qualification_score": evaluation.get("qualification_score", 0),
                        "next_action": "schedule",
                        "proposed_slots": slots.get("proposed_slots", []),
                        "message": "Thank you! We would like to schedule a call. Please pick a slot."}

            question = self._question_for_field(next_field, captured)
            cur.close(); conn.close()
            return {"status": "success", "next_field": next_field, "question": question,
                    "phase": "phase1" if next_field in PHASE1_FIELDS else "phase2",
                    "done": False, "captured_so_far": list(captured.keys())}
        except Exception as e:
            logger.error("submit_answer failed: " + str(e))
            return {"status": "error", "message": str(e)}

    def _next_field(self, captured):
        for f in PHASE1_FIELDS:
            if f not in captured:
                return f
        for f in PHASE2_FIELDS:
            if f not in captured:
                return f
        return None

    def _question_for_field(self, field, captured):
        questions = {
            "total_experience_years": "How many years of total professional experience do you have?",
            "current_ctc_inr": "What is your current CTC (annual, in INR or LPA)?",
            "expected_ctc_inr": "What is your expected CTC for this role (annual, in INR or LPA)?",
            "current_role": "What is your current role title?",
            "current_company": "Which company do you currently work at?",
            "notice_period_days": "What is your notice period (in days or weeks)?",
            "work_authorization": "What is your work authorization status? (Indian citizen / PIO / requires visa)",
            "availability_date": "When can you start if selected? (a specific date or timeframe)",
            "preferred_work_mode": "Do you prefer remote, hybrid, or office-based work?",
            "current_location": "Which city are you currently based in?",
            "reason_for_change": "What is your primary reason for looking for a new role?",
            "relocation_willingness": "Are you willing to relocate for this role? (yes/no/conditional)",
        }
        return questions.get(field, "Could you tell me about " + field.replace("_", " ") + "?")

    def _extract_field(self, answer, field, role="", budget=None):
        """Use OpenAI to extract structured value from natural language answer."""
        try:
            from openai_compat import build_payload
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            prompt = (
                "You extract structured data from candidate chat answers. "
                "The field to extract is: " + field + ". "
                "Return ONLY a JSON object with key value containing the extracted value. "
                "For numeric fields (years, INR, days), return a number. "
                "For LPA, convert to INR (1 LPA = 100000). "
                "For textual fields, return a short normalized string. "
                "If the answer does not contain the field, return value as null. "
                "Never invent data."
            )

            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": answer}
            ]

            payload = build_payload(
                messages=messages,
                model=_get_openai_model(cheap=True),
                max_tokens=200,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            response = client.chat.completions.create(**payload)
            text = response.choices[0].message.content
            parsed = json.loads(text)
            # Accept any single-key JSON shape — AI returns {"field_name": X} sometimes
            # instead of {"value": X}. Handle both.
            if isinstance(parsed, dict):
                if "value" in parsed:
                    return parsed["value"]
                if field in parsed:
                    return parsed[field]
                # Any single-key dict: use the value
                values = list(parsed.values())
                if len(values) == 1:
                    return values[0]
            return None
        except Exception as e:
            logger.debug("_extract_field failed for " + field + ": " + str(e))
            return None

    def _check_phase1_qualification(self, captured, budget_max):
        """Phase 1 gate: disqualified if expected CTC > budget."""
        if not budget_max:
            return (True, "")
        expected = captured.get("expected_ctc_inr")
        if not expected:
            return (True, "")
        try:
            expected_val = float(expected)
        except (ValueError, TypeError):
            return (True, "")
        if expected_val > budget_max * 1.05:
            return (False, "Considering your experience and our current budget for this role, this particular opportunity may not be the best match. We will keep your profile on file for future roles that align more closely with your compensation range.")
        return (True, "")

    # =====================================================
    # EVALUATION + SCHEDULING
    # =====================================================

    def evaluate_candidate(self, candidate_screen_id):
        """Compute qualification score from captured fields."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute(
                "SELECT captured_data, session_id FROM charvak_screen_candidates WHERE candidate_screen_id = %s",
                (candidate_screen_id,)
            )
            row = cur.fetchone()
            if not row:
                cur.close(); conn.close()
                return {"status": "error", "message": "Not found."}
            captured = row[0] or {}
            session_id = row[1]

            score = 0
            qualified = True
            reasons = []

            # Years exp scoring
            exp = captured.get("total_experience_years")
            try:
                exp_val = float(exp) if exp else 0
            except (ValueError, TypeError):
                exp_val = 0
            if exp_val >= 5:
                score += 30
            elif exp_val >= 3:
                score += 20
            elif exp_val >= 1:
                score += 10
            else:
                reasons.append("Limited experience")

            # CTC fit scoring
            expected = captured.get("expected_ctc_inr")
            current = captured.get("current_ctc_inr")
            cur.execute(
                "SELECT budget_max_inr FROM charvak_screen_sessions WHERE session_id = %s",
                (session_id,)
            )
            budget_row = cur.fetchone()
            budget = budget_row[0] if budget_row else None

            if budget and expected:
                try:
                    expected_val = float(expected)
                    if expected_val <= budget:
                        score += 30
                    elif expected_val <= budget * 1.1:
                        score += 15
                        reasons.append("Slightly above budget")
                    else:
                        qualified = False
                        reasons.append("Expected CTC above budget")
                except (ValueError, TypeError):
                    pass

            # Notice period scoring
            notice = captured.get("notice_period_days")
            try:
                notice_val = float(notice) if notice else 90
            except (ValueError, TypeError):
                notice_val = 90
            if notice_val <= 30:
                score += 20
            elif notice_val <= 60:
                score += 15
            else:
                score += 5
                if notice_val > 90:
                    reasons.append("Long notice period")

            # Availability scoring
            if captured.get("availability_date"):
                score += 10

            # Work auth scoring
            wa = (captured.get("work_authorization") or "").lower()
            if "citizen" in wa or "no restriction" in wa:
                score += 10
            elif "visa" in wa or "require" in wa:
                score += 3
                reasons.append("Visa required")

            score = min(100, score)
            qualified = qualified and score >= 40

            cur.execute(
                "UPDATE charvak_screen_candidates SET qualification_score = %s, qualified = %s WHERE candidate_screen_id = %s",
                (score, qualified, candidate_screen_id)
            )
            conn.commit()
            cur.close(); conn.close()

            return {
                "status": "success",
                "qualified": qualified,
                "qualification_score": score,
                "reasons": reasons,
            }
        except Exception as e:
            logger.error("evaluate_candidate failed: " + str(e))
            return {"status": "error", "message": str(e)}

    def propose_schedule_slots(self, candidate_screen_id, num_slots=3):
        """Generate 3 proposed call slots (next 3 business days, 10 AM / 2 PM / 5 PM IST)."""
        try:
            from database import db
            from datetime import datetime, timedelta
            conn = db.get_connection()
            cur = conn.cursor()

            slots = []
            base = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            day_added = 0
            times = [10, 14, 17]  # 10am, 2pm, 5pm IST
            time_idx = 0

            while len(slots) < num_slots and day_added < 10:
                base = base + timedelta(days=1)
                day_added += 1
                # Skip weekends
                if base.weekday() >= 5:
                    continue
                hour = times[time_idx % len(times)]
                slot_start = base.replace(hour=hour)
                slot_end = slot_start + timedelta(hours=1)
                slots.append({
                    "start_iso": slot_start.isoformat(),
                    "end_iso": slot_end.isoformat(),
                    "timezone": "Asia/Kolkata",
                    "display": slot_start.strftime("%a, %b %d at %I:%M %p IST"),
                })
                time_idx += 1

            schedule_id = self._gen_id("SSCH")
            cur.execute(
                "INSERT INTO charvak_screen_schedules (schedule_id, candidate_screen_id, proposed_slots) "
                "VALUES (%s, %s, %s)",
                (schedule_id, candidate_screen_id, json.dumps(slots))
            )
            conn.commit()
            cur.close(); conn.close()

            return {"status": "success", "schedule_id": schedule_id, "proposed_slots": slots}
        except Exception as e:
            logger.error("propose_schedule_slots failed: " + str(e))
            return {"status": "error", "message": str(e)}

    def confirm_schedule(self, candidate_screen_id, selected_slot, recruiter_notes=None):
        """Confirm candidate-selected slot, generate calendar link."""
        try:
            from database import db
            from datetime import datetime
            import urllib.parse
            conn = db.get_connection()
            cur = conn.cursor()

            # Get role title and company for calendar event
            cur.execute(
                "SELECT s.role_title, s.company_name, c.candidate_email, c.candidate_name "
                "FROM charvak_screen_candidates c "
                "JOIN charvak_screen_sessions s ON c.session_id = s.session_id "
                "WHERE c.candidate_screen_id = %s",
                (candidate_screen_id,)
            )
            row = cur.fetchone()
            if not row:
                cur.close(); conn.close()
                return {"status": "error", "message": "Candidate not found."}

            role_title, company, cand_email, cand_name = row

            start_iso = selected_slot.get("start_iso")
            end_iso = selected_slot.get("end_iso")
            display = selected_slot.get("display", "")

            # Generate Google Calendar link
            title = "Screen call: " + (cand_name or cand_email) + " for " + (role_title or "role")
            details = "Charvak screen call. Role: " + (role_title or "") + ". Company: " + (company or "") + "."
            dates = start_iso.replace("-", "").replace(":", "").split(".")[0] + "/" + end_iso.replace("-", "").replace(":", "").split(".")[0]
            gcal_params = urllib.parse.urlencode({
                "action": "TEMPLATE",
                "text": title,
                "dates": dates,
                "details": details,
            })
            calendar_link = "https://calendar.google.com/calendar/render?" + gcal_params

            cur.execute(
                "UPDATE charvak_screen_schedules SET selected_slot = %s, scheduled_at = %s, "
                "calendar_link = %s, recruiter_notes = %s "
                "WHERE candidate_screen_id = %s AND selected_slot IS NULL",
                (json.dumps(selected_slot), start_iso, calendar_link, recruiter_notes, candidate_screen_id)
            )
            cur.execute(
                "UPDATE charvak_screen_candidates SET status = 'completed', completed_at = NOW(), qualified = TRUE "
                "WHERE candidate_screen_id = %s",
                (candidate_screen_id,)
            )
            conn.commit()
            cur.close(); conn.close()

            return {
                "status": "success",
                "scheduled_at": display or start_iso,
                "calendar_link": calendar_link,
            }
        except Exception as e:
            logger.error("confirm_schedule failed: " + str(e))
            return {"status": "error", "message": str(e)}

    def escalate_to_human(self, candidate_screen_id, reason):
        """Mark candidate for human follow-up."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute(
                "UPDATE charvak_screen_candidates SET status = 'escalated', "
                "disqualify_reason = %s, completed_at = NOW() WHERE candidate_screen_id = %s",
                ("HUMAN_REVIEW: " + reason, candidate_screen_id)
            )
            conn.commit()
            cur.close(); conn.close()
            self._log_event(candidate_screen_id, None, "escalated_to_human", {"reason": reason})
            return {"status": "success", "escalated": True}
        except Exception as e:
            logger.error("escalate_to_human failed: " + str(e))
            return {"status": "error", "message": str(e)}

    def list_candidates_for_session(self, session_id, status=None):
        """List candidates with their captured data."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            if status:
                cur.execute(
                    "SELECT candidate_screen_id, token, candidate_email, candidate_name, status, "
                    "captured_data, qualification_score, qualified, disqualify_reason, "
                    "invited_at, completed_at "
                    "FROM charvak_screen_candidates WHERE session_id = %s AND status = %s "
                    "ORDER BY invited_at DESC",
                    (session_id, status)
                )
            else:
                cur.execute(
                    "SELECT candidate_screen_id, token, candidate_email, candidate_name, status, "
                    "captured_data, qualification_score, qualified, disqualify_reason, "
                    "invited_at, completed_at "
                    "FROM charvak_screen_candidates WHERE session_id = %s "
                    "ORDER BY invited_at DESC",
                    (session_id,)
                )
            rows = cur.fetchall()
            cur.close(); conn.close()
            return [
                {
                    "candidate_screen_id": r[0], "token": r[1],
                    "email_masked": self._mask_email(r[2]), "name": r[3],
                    "status": r[4], "captured_data": r[5] or {},
                    "qualification_score": r[6], "qualified": r[7],
                    "disqualify_reason": r[8],
                    "invited_at": r[9].isoformat() if r[9] else None,
                    "completed_at": r[10].isoformat() if r[10] else None,
                }
                for r in rows
            ]
        except Exception as e:
            logger.error("list_candidates_for_session failed: " + str(e))
            return []


# Singleton
recruiter_screen_engine = RecruiterScreenEngine()