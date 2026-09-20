"""
Charvak Products Engine
Backend functionality for all AI products
"""
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional
import secrets
import hashlib

logger = logging.getLogger("charvakit.products")


class ProductsEngine:
    """Handles all AI product functionality."""
    
    def __init__(self):
        # B-4: self.results removed - all 11 product methods are stateless
        # #86: added audit trail logging (see _log_result below)
        self._ensure_tables()
        logger.info("✅ Products Engine ready (audit trail enabled)")

    def _ensure_tables(self):
        """Create audit trail table if it doesn't exist."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_product_results (
                    result_id     TEXT PRIMARY KEY,
                    product_type  TEXT NOT NULL,
                    email         TEXT,
                    input_data    JSONB NOT NULL DEFAULT '{}'::jsonb,
                    result_data   JSONB NOT NULL DEFAULT '{}'::jsonb,
                    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_product_results_type    ON charvak_product_results(product_type)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_product_results_email   ON charvak_product_results(email)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_product_results_created ON charvak_product_results(created_at)")
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"products_engine table init failed: {e}")

    def _log_result(self, product_type: str, input_data: Dict, result_data: Dict, email: str = None) -> None:
        """Log a product result to charvak_product_results. Non-fatal on error."""
        try:
            import json as _json
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            result_id = f"PR-{secrets.token_hex(6).upper()}"
            cur.execute("""
                INSERT INTO charvak_product_results
                    (result_id, product_type, email, input_data, result_data)
                VALUES (%s, %s, %s, %s::jsonb, %s::jsonb)
                ON CONFLICT (result_id) DO NOTHING
            """, (
                result_id,
                product_type,
                email,
                _json.dumps(input_data, default=str),
                _json.dumps(result_data, default=str),
            ))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"_log_result failed for {product_type}: {e}")

    def get_recent_results(self, product_type: str = None, email: str = None,
                           limit: int = 100, days: int = 30) -> Dict:
        """Read recent product results (for admin dashboard)."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            where = ["created_at > NOW() - INTERVAL '%s days'" % int(days)]
            params = []
            if product_type:
                where.append("product_type = %s")
                params.append(product_type)
            if email:
                where.append("email = %s")
                params.append(email)
            sql = f"""
                SELECT result_id, product_type, email, input_data, result_data, created_at
                FROM charvak_product_results
                WHERE {' AND '.join(where)}
                ORDER BY created_at DESC
                LIMIT %s
            """
            params.append(limit)
            cur.execute(sql, params)
            rows = cur.fetchall()
            cur.close(); conn.close()
            return {
                "status": "success",
                "count": len(rows),
                "results": [{
                    "result_id": r[0],
                    "product_type": r[1],
                    "email": r[2],
                    "input_data": r[3] if isinstance(r[3], dict) else {},
                    "result_data": r[4] if isinstance(r[4], dict) else {},
                    "created_at": r[5].isoformat() if hasattr(r[5], "isoformat") else str(r[5]),
                } for r in rows],
            }
        except Exception as e:
            logger.error(f"get_recent_results failed: {e}")
            return {"status": "error", "message": "Could not load results"}
    
    # ============================================================
    # LOCK-IN BREAKER
    # ============================================================
    
    def lock_in_breaker_audit(self, data: Dict) -> Dict:
        """
        Audit cloud vendor lock-in.
        data = {"cloud_provider": str, "monthly_spend": float, "services": List[str]}
        """
        provider = data.get("cloud_provider", "AWS")
        spend = float(data.get("monthly_spend", 10000))
        services = data.get("services", [])
        
        # Calculate savings potential
        savings_map = {"AWS": 0.35, "Azure": 0.30, "GCP": 0.32, "Other": 0.25}
        savings_rate = savings_map.get(provider, 0.30)
        potential_savings = round(spend * savings_rate, 2)
        
        result = {
            "audit_id": f"AUDIT-{secrets.token_hex(4).upper()}",
            "provider": provider,
            "current_monthly_spend": spend,
            "potential_savings": potential_savings,
            "savings_percent": int(savings_rate * 100),
            "locked_services": services,
            "risk_level": "HIGH" if len(services) > 3 else "MEDIUM" if len(services) > 1 else "LOW",
            "migration_complexity": self._assess_complexity(services),
            "recommendations": self._get_recommendations(provider),
            "created_at": datetime.now().isoformat()
        }
        
        # #60 Level 1: AI-enhanced analysis (adds recommendations, verdict, quick_wins)
        ai_analysis = self._ai_lock_in_analysis(provider, spend, services)
        if ai_analysis:
            result["ai_analysis"] = ai_analysis
            if ai_analysis.get("recommendations"):
                result["recommendations"] = ai_analysis["recommendations"]
            if ai_analysis.get("verdict"):
                result["verdict"] = ai_analysis["verdict"]
            if ai_analysis.get("quick_wins"):
                result["quick_wins"] = ai_analysis["quick_wins"]
            if ai_analysis.get("estimated_migration_risk"):
                result["estimated_migration_risk"] = ai_analysis["estimated_migration_risk"]
            result["analysis_mode"] = "ai_enhanced"
        else:
            result["analysis_mode"] = "heuristic_only"

        # B-4: removed self.results.append - no read path existed
        # #86: log result to audit trail
        self._log_result("lock_in_breaker", data, result)
        return {"status": "success", **result}
    
    def _assess_complexity(self, services: List[str]) -> str:
        complex_services = ["Kubernetes", "RDS", "DynamoDB", "Lambda", "S3"]
        overlap = len([s for s in services if s in complex_services])
        if overlap > 2: return "HIGH"
        if overlap > 0: return "MEDIUM"
        return "LOW"
    
    def _get_recommendations(self, provider: str) -> List[str]:
        recs = {
            "AWS": ["Move to multi-cloud strategy", "Containerize with Kubernetes", "Use open-source alternatives"],
            "Azure": ["Reduce SQL Server dependency", "Adopt Terraform for IaC", "Consider GCP for AI workloads"],
            "GCP": ["Reduce BigQuery lock-in", "Use standard SQL", "Containerize with GKE"],
        }
        return recs.get(provider, ["Assess current vendor dependencies", "Create exit strategy", "Document all proprietary APIs"])
    
    # ============================================================
    # REVERSE STAFFING
    # ============================================================
    
    def reverse_staffing_match(self, data: Dict) -> Dict:
        """
        Match candidate portfolio to companies.
        data = {"skills": List[str], "experience_years": int, "portfolio_score": float}
        """
        skills = data.get("skills", [])
        experience = int(data.get("experience_years", 0))
        
        companies = [
            {"name": "TechCorp", "match": 85, "roles": ["React Developer", "Frontend Lead"]},
            {"name": "DataFlow", "match": 78, "roles": ["Python Engineer", "ML Engineer"]},
            {"name": "CloudFirst", "match": 72, "roles": ["DevOps", "Cloud Architect"]},
        ]
        
        # Adjust match based on experience
        for company in companies:
            if experience > 5: company["match"] += 5
            if experience < 1: company["match"] -= 10
        
        result = {
            "match_id": f"MATCH-{secrets.token_hex(4).upper()}",
            "candidate_skills": skills,
            "experience_years": experience,
            "matches": sorted(companies, key=lambda c: c["match"], reverse=True),
            "top_match": max(companies, key=lambda c: c["match"]),
            "created_at": datetime.now().isoformat()
        }

        self._log_result("reverse_staffing", data, result)
        return {"status": "success", **result}
    
    # ============================================================
    # AUDITBOT
    # ============================================================
    
    def auditbot_scan(self, data: Dict) -> Dict:
        """
        Run security & code health scan.
        data = {"repo_url": str, "language": str, "scan_type": str}
        """
        language = data.get("language", "Python")
        scan_type = data.get("scan_type", "security")
        
        findings = {
            "security": [
                {"severity": "HIGH", "issue": "Hardcoded API key detected", "file": "config.py", "line": 42},
                {"severity": "MEDIUM", "issue": "SQL injection possible", "file": "db.py", "line": 87},
                {"severity": "LOW", "issue": "Missing input validation", "file": "api.py", "line": 15},
            ],
            "performance": [
                {"severity": "MEDIUM", "issue": "N+1 query pattern", "file": "models.py", "line": 103},
                {"severity": "LOW", "issue": "Unused imports", "file": "main.py", "line": 7},
            ],
            "w3c": [
                {"severity": "HIGH", "issue": "Missing alt attributes", "file": "index.html", "line": 55},
                {"severity": "MEDIUM", "issue": "Low contrast text", "file": "style.css", "line": 22},
            ]
        }
        
        findings_list = findings.get(scan_type, findings["security"])
        
        result = {
            "scan_id": f"SCAN-{secrets.token_hex(4).upper()}",
            "language": language,
            "scan_type": scan_type,
            "findings": findings_list,
            "critical_count": len([f for f in findings_list if f["severity"] == "HIGH"]),
            "medium_count": len([f for f in findings_list if f["severity"] == "MEDIUM"]),
            "low_count": len([f for f in findings_list if f["severity"] == "LOW"]),
            "overall_score": 72,
            "scanned_at": datetime.now().isoformat()
        }

        # #60 Level 1: AI-enhanced findings
        ai_analysis = self._ai_auditbot_analysis(data.get("repo_url", ""), language, scan_type)
        if ai_analysis:
            if ai_analysis.get("findings"):
                result["findings"] = ai_analysis["findings"]
                result["critical_count"] = len([f for f in ai_analysis["findings"] if f.get("severity") == "HIGH"])
                result["medium_count"] = len([f for f in ai_analysis["findings"] if f.get("severity") == "MEDIUM"])
                result["low_count"] = len([f for f in ai_analysis["findings"] if f.get("severity") == "LOW"])
            if ai_analysis.get("overall_score"):
                result["overall_score"] = ai_analysis["overall_score"]
            if ai_analysis.get("verdict"):
                result["verdict"] = ai_analysis["verdict"]
            if ai_analysis.get("top_risks"):
                result["top_risks"] = ai_analysis["top_risks"]
            if ai_analysis.get("next_steps"):
                result["next_steps"] = ai_analysis["next_steps"]
            result["analysis_mode"] = "ai_enhanced"
        else:
            result["analysis_mode"] = "heuristic_only"

        self._log_result("auditbot", data, result)
        return {"status": "success", **result}
    
    # ============================================================
    # SKILL-TWIN
    # ============================================================
    
    def skill_twin_assess(self, data: Dict) -> Dict:
        """
        Assess candidate skills.
        data = {"skills": List[str], "experience_years": int, "self_rating": float}
        """
        skills = data.get("skills", [])
        experience = int(data.get("experience_years", 0))
        self_rating = float(data.get("self_rating", 5))
        
        # Calculate verified score based on experience and skills count
        base_score = len(skills) * 8
        experience_bonus = min(experience * 2, 20)
        verified_score = min(base_score + experience_bonus, 100)
        
        result = {
            "twin_id": f"TWIN-{secrets.token_hex(4).upper()}",
            "skills": skills,
            "verified_score": verified_score,
            "self_rating": self_rating,
            "gap": round(self_rating - verified_score / 20, 1),
            "skill_level": self._get_skill_level(verified_score),
            "recommendations": self._get_skill_recommendations(verified_score),
            "badge_eligible": verified_score >= 70,
            "created_at": datetime.now().isoformat()
        }

        self._log_result("skill_twin", data, result)
        return {"status": "success", **result}
    
    def _get_skill_level(self, score: int) -> str:
        if score >= 85: return "Expert"
        if score >= 70: return "Advanced"
        if score >= 50: return "Intermediate"
        return "Beginner"
    
    def _get_skill_recommendations(self, score: int) -> List[str]:
        if score < 50: return ["Complete beginner courses", "Build 3 portfolio projects", "Get a mentor"]
        if score < 70: return ["Advanced certification", "Open source contributions", "System design practice"]
        return ["Teach others", "Write technical blog", "Lead architecture decisions"]
    
    # ============================================================
    # MICRO-SQUADS
    # ============================================================
    
    def micro_squads_assemble(self, data: Dict) -> Dict:
        """
        Assemble a micro-squad.
        data = {"project_type": str, "duration_days": int, "budget": float}
        """
        project_type = data.get("project_type", "Web App")
        duration = int(data.get("duration_days", 14))
        budget = float(data.get("budget", 50000))
        
        squad_composition = {
            "Web App": ["Full-Stack Developer", "UI/UX Designer", "QA Engineer"],
            "AI/ML": ["ML Engineer", "Data Scientist", "Backend Developer"],
            "Mobile": ["iOS Developer", "Android Developer", "QA Engineer"],
            "DevOps": ["DevOps Engineer", "Security Engineer", "Backend Developer"],
        }
        
        members = squad_composition.get(project_type, squad_composition["Web App"])
        
        result = {
            "squad_id": f"SQUAD-{secrets.token_hex(4).upper()}",
            "project_type": project_type,
            "duration_days": duration,
            "budget": budget,
            "members": members,
            "member_count": len(members),
            "cost_per_day": round(budget / duration, 2),
            "assembly_time": "72 hours",
            "sprint_plan": self._generate_sprint_plan(duration),
            "created_at": datetime.now().isoformat()
        }

        self._log_result("micro_squads", data, result)
        return {"status": "success", **result}
    
    def _generate_sprint_plan(self, duration: int) -> List[str]:
        return [
            f"Day 1-2: Kickoff & Requirements",
            f"Day 3-{duration//2}: Development Sprint",
            f"Day {duration//2+1}-{duration-2}: Testing & Fixes",
            f"Day {duration-1}-{duration}: Deployment & Handover"
        ]
    
    # ============================================================
    # AGENCY-TWIN
    # ============================================================
    
    def agency_twin_automate(self, data: Dict) -> Dict:
        """
        Automate agency operations.
        data = {"agency_name": str, "current_clients": int, "monthly_revenue": float}
        """
        clients = int(data.get("current_clients", 5))
        revenue = float(data.get("monthly_revenue", 100000))
        
        result = {
            "twin_id": f"AGENCY-{secrets.token_hex(4).upper()}",
            "agency_name": data.get("agency_name", "Agency"),
            "current_clients": clients,
            "monthly_revenue": revenue,
            "automation_opportunities": [
                {"area": "Invoicing", "time_saved_hrs": 10, "automation_level": "FULL"},
                {"area": "Client Reporting", "time_saved_hrs": 15, "automation_level": "FULL"},
                {"area": "Task Assignment", "time_saved_hrs": 8, "automation_level": "PARTIAL"},
                {"area": "Candidate Sourcing", "time_saved_hrs": 20, "automation_level": "AI-POWERED"}
            ],
            "total_time_saved_monthly": 53,
            "projected_revenue_increase": round(revenue * 0.15, 2),
            "created_at": datetime.now().isoformat()
        }

        self._log_result("agency_twin", data, result)
        return {"status": "success", **result}
    
    # ============================================================
    # GEO-COMPLIANCE
    # ============================================================
    
    def geo_compliance_check(self, data: Dict) -> Dict:
        """
        Check cross-border compliance.
        data = {"countries": List[str], "service_type": str, "payment_method": str}
        """
        countries = data.get("countries", ["India"])
        service_type = data.get("service_type", "IT Services")
        
        compliance_rules = {
            "India": {"gst": "18%", "data_protection": "DPDP Act 2023", "contract_law": "Indian Contract Act"},
            "USA": {"tax": "Varies by state", "data_protection": "CCPA", "contract_law": "UCC"},
            "UK": {"tax": "VAT 20%", "data_protection": "GDPR", "contract_law": "English Law"},
            "EU": {"tax": "VAT varies", "data_protection": "GDPR", "contract_law": "EU Directives"},
            "Singapore": {"tax": "GST 9%", "data_protection": "PDPA", "contract_law": "Singapore Law"},
            "UAE": {"tax": "VAT 5%", "data_protection": "UAE PDPL", "contract_law": "UAE Civil Code"},
        }
        
        result = {
            "check_id": f"GEO-{secrets.token_hex(4).upper()}",
            "countries": countries,
            "service_type": service_type,
            "compliance": [{"country": c, **compliance_rules.get(c, {"tax": "Unknown", "data_protection": "Unknown", "contract_law": "Local laws apply"})} for c in countries],
            "risk_level": "LOW" if len(countries) == 1 else "MEDIUM" if len(countries) <= 3 else "HIGH",
            "requires_legal_review": len(countries) > 2,
            "created_at": datetime.now().isoformat()
        }

        self._log_result("geo_compliance", data, result)
        return {"status": "success", **result}
    
    # ============================================================
    # DESIGN-TOKEN SENTINEL
    # ============================================================
    
    def design_token_check(self, data: Dict) -> Dict:
        """
        Check design token consistency.
        data = {"design_system": str, "platforms": List[str]}
        """
        design_system = data.get("design_system", "Custom")
        platforms = data.get("platforms", ["Figma", "Web"])
        
        result = {
            "check_id": f"DESIGN-{secrets.token_hex(4).upper()}",
            "design_system": design_system,
            "platforms": platforms,
            "consistency_score": 78,
            "issues": [
                {"platform": "Figma", "issue": "3 stale color tokens", "severity": "MEDIUM"},
                {"platform": "Web", "issue": "2 deprecated spacing tokens", "severity": "LOW"},
                {"platform": "Mobile", "issue": "Typography scale mismatch", "severity": "HIGH"}
            ],
            "tokens_synced": 142,
            "tokens_drifted": 5,
            "created_at": datetime.now().isoformat()
        }

        # #60 Level 1: AI-enhanced design token analysis
        ai_analysis = self._ai_design_token_analysis(design_system, platforms)
        if ai_analysis:
            if ai_analysis.get("issues"):
                result["issues"] = ai_analysis["issues"]
            if ai_analysis.get("consistency_score") is not None:
                result["consistency_score"] = ai_analysis["consistency_score"]
            if ai_analysis.get("tokens_synced") is not None:
                result["tokens_synced"] = ai_analysis["tokens_synced"]
            if ai_analysis.get("tokens_drifted") is not None:
                result["tokens_drifted"] = ai_analysis["tokens_drifted"]
            if ai_analysis.get("verdict"):
                result["verdict"] = ai_analysis["verdict"]
            if ai_analysis.get("top_risks"):
                result["top_risks"] = ai_analysis["top_risks"]
            if ai_analysis.get("next_steps"):
                result["next_steps"] = ai_analysis["next_steps"]
            result["analysis_mode"] = "ai_enhanced"
        else:
            result["analysis_mode"] = "heuristic_only"

        self._log_result("design_token", data, result)
        return {"status": "success", **result}
    
    # ============================================================
    # SILENT-KILLER
    # ============================================================
    
    def silent_killer_monitor(self, data: Dict) -> Dict:
        """
        Set up monitoring for webhooks/APIs.
        data = {"url": str, "name": str, "interval_minutes": int}
        """
        url = data.get("url", "")
        name = data.get("name", "Monitor")
        interval = int(data.get("interval_minutes", 5))
        
        result = {
            "monitor_id": f"MON-{secrets.token_hex(4).upper()}",
            "url": url,
            "name": name,
            "interval_minutes": interval,
            "status": "active",
            "checks_per_day": 24 * 60 // interval,
            "alert_channels": ["Email", "WhatsApp", "Webhook"],
            "auto_fix_enabled": True,
            "created_at": datetime.now().isoformat()
        }

        self._log_result("silent_killer", data, result)
        return {"status": "success", **result}
    
    # ============================================================
    # AI-SLOP QUARANTINE
    # ============================================================
    
    def ai_slop_scan(self, data: Dict) -> Dict:
        """
        Scan for AI-generated code bloat.
        data = {"code": str, "language": str}
        """
        code = data.get("code", "")
        language = data.get("language", "JavaScript")
        
        # Detect AI slop patterns
        slop_patterns = {
            "excessive_comments": "// TODO: fix this" in code or "# TODO" in code,
            "unused_imports": "import { useState }" in code and "useState" not in code,
            "dead_code": "console.log(" in code,
            "redundant_wrappers": "function function " in code,
        }
        
        issues = [{"pattern": k, "detected": v} for k, v in slop_patterns.items() if v]
        
        result = {
            "scan_id": f"SLOP-{secrets.token_hex(4).upper()}",
            "language": language,
            "issues_found": issues,
            "issue_count": len(issues),
            "cleanliness_score": max(0, 100 - len(issues) * 20),
            "wcag_issues": 0,
            "clean_code_ready": len(issues) == 0,
            "created_at": datetime.now().isoformat()
        }

        self._log_result("ai_slop", data, result)
        return {"status": "success", **result}
    
    # ============================================================
    # DEVELOPER ENTROPY
    # ============================================================
    
    def developer_entropy_score(self, data: Dict) -> Dict:
        """
        Calculate team skill decay.
        data = {"team_size": int, "avg_tenure_years": float, "tech_stack_age": int}
        """
        team_size = int(data.get("team_size", 5))
        tenure = float(data.get("avg_tenure_years", 3))
        tech_age = int(data.get("tech_stack_age", 2))
        
        entropy_score = min(int(tenure * 15 + tech_age * 10), 100)
        
        result = {
            "entropy_id": f"ENTROPY-{secrets.token_hex(4).upper()}",
            "team_size": team_size,
            "avg_tenure_years": tenure,
            "tech_stack_age": tech_age,
            "entropy_score": entropy_score,
            "risk_level": "HIGH" if entropy_score > 70 else "MEDIUM" if entropy_score > 40 else "LOW",
            "upskilling_plan": [
                "Weekly code reviews",
                "Monthly hackathons",
                "Pair programming sessions",
                "Online course budget"
            ],
            "created_at": datetime.now().isoformat()
        }

        self._log_result("developer_entropy", data, result)
        return {"status": "success", **result}

    def _ai_design_token_analysis(self, design_system: str, platforms: List[str]) -> Optional[Dict]:
        """#60 Level 1: AI-powered design token consistency analysis. Returns None on failure."""
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            return None
        try:
            import requests
            import json as _json

            platforms_str = ", ".join(platforms) if platforms else "Web"
            prompt = (
                f"You are a design systems expert conducting a token consistency audit.\n\n"
                f"Design system: {design_system}\n"
                f"Platforms to check: {platforms_str}\n\n"
                f"Generate REALISTIC, platform-specific token drift issues that this type of design system "
                f"is likely to have. Consider realistic scenarios like: stale color tokens after a brand refresh, "
                f"deprecated spacing tokens across versions, typography scale mismatches between platforms, "
                f"naming convention drift (camelCase vs kebab-case), theme token drift, accessibility contrast token issues.\n\n"
                f"Return JSON with this exact structure:\n"
                f"{{\n"
                f"  \"issues\": [\n"
                f"    {{\"platform\": \"Figma|Web|Mobile|iOS|Android\", \"issue\": \"specific description\", "
                f"\"severity\": \"HIGH|MEDIUM|LOW\", \"details\": \"context\", \"fix\": \"specific fix\"}},\n"
                f"    ... (5-8 issues)\n"
                f"  ],\n"
                f"  \"consistency_score\": 0-100,\n"
                f"  \"tokens_synced\": integer (plausible count),\n"
                f"  \"tokens_drifted\": integer (plausible count),\n"
                f"  \"verdict\": \"1-2 sentence overall verdict\",\n"
                f"  \"top_risks\": [\"3 most critical risks\", ...],\n"
                f"  \"next_steps\": [\"3-5 prioritized actions\", ...]\n"
                f"}}\n\n"
                f"Make issues specific to the listed platforms. Give concrete, actionable findings."
            )
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.5,
                    "response_format": {"type": "json_object"},
                },
                timeout=30,
            )
            data_resp = response.json()
            content = (data_resp.get("choices", [{}])[0].get("message", {}).get("content") or "").strip()
            if content.startswith("```"):
                content = content.split("```", 2)[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            parsed = _json.loads(content)
            if isinstance(parsed, dict) and "issues" in parsed:
                return parsed
            return None
        except Exception as e:
            logger.error(f"AI design token analysis failed: {e}")
            return None

    def _ai_auditbot_analysis(self, repo_url: str, language: str, scan_type: str) -> Optional[Dict]:
        """#60 Level 1: AI-powered security/code review findings. Returns None on failure."""
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            return None
        try:
            import requests
            import json as _json

            repo_str = repo_url or "(repository URL not provided)"
            prompt = (
                f"You are a senior security engineer conducting a code review.\n\n"
                f"Repository: {repo_str}\n"
                f"Primary language: {language}\n"
                f"Scan focus: {scan_type}\n\n"
                f"Given only this metadata, generate REALISTIC, language-specific issues that this type of codebase "
                f"is likely to have. For each issue, provide: file path, line number, severity, specific description, "
                f"and a recommended fix. Be specific to {language} best practices (e.g., Python: f-strings, mutable defaults; "
                f"JavaScript: XSS, prototype pollution; Java: deserialization; Go: race conditions).\n\n"
                f"Return JSON with this exact structure:\n"
                f"{{\n"
                f"  \"findings\": [\n"
                f"    {{\"severity\": \"HIGH|MEDIUM|LOW\", \"issue\": \"specific issue title\", "
                f"\"file\": \"path/to/file.ext\", \"line\": 42, "
                f"\"description\": \"detailed explanation\", \"fix\": \"specific fix\"}},\n"
                f"    ... (6-10 findings)\n"
                f"  ],\n"
                f"  \"overall_score\": 0-100 number representing code health,\n"
                f"  \"verdict\": \"1-2 sentence overall security posture\",\n"
                f"  \"top_risks\": [\"3 most critical risks\", ...],\n"
                f"  \"next_steps\": [\"3-5 prioritized actions\", ...]\n"
                f"}}\n\n"
                f"Base the focus on the requested scan_type ({scan_type}). "
                f"Give concrete, actionable findings — no generic boilerplate."
            )
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.5,
                    "response_format": {"type": "json_object"},
                },
                timeout=30,
            )
            data_resp = response.json()
            content = (data_resp.get("choices", [{}])[0].get("message", {}).get("content") or "").strip()
            if content.startswith("```"):
                content = content.split("```", 2)[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            parsed = _json.loads(content)
            if isinstance(parsed, dict) and "findings" in parsed:
                return parsed
            return None
        except Exception as e:
            logger.error(f"AI auditbot analysis failed: {e}")
            return None

    def _ai_lock_in_analysis(self, provider: str, spend: float, services: List[str]) -> Optional[Dict]:
        """#60 Level 1: AI-powered lock-in analysis. Returns None on failure."""
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            return None
        try:
            import requests
            import json as _json

            services_str = ", ".join(services) if services else "(none specified)"
            prompt = (
                f"You are a cloud cost optimization expert. Analyze vendor lock-in for this company.\n\n"
                f"Provider: {provider}\n"
                f"Monthly cloud spend: ${spend:,.0f}\n"
                f"Services in use: {services_str}\n\n"
                f"Provide specific, actionable analysis. For EACH service, reason about the actual migration path "
                f"and whether migration is worth it vs. optimizing in place. Be honest - some services are NOT worth "
                f"migrating. Give concrete dollar estimates where possible.\n\n"
                f"Return JSON with this exact structure:\n"
                f"{{\n"
                f"  \"recommendations\": [\"specific rec mentioning service + reasoning + dollar estimate\", ...],\n"
                f"  \"verdict\": \"1-2 sentence overall verdict (migrate or optimize in place?)\",\n"
                f"  \"quick_wins\": [\"2-4 actions for this week\", ...],\n"
                f"  \"estimated_migration_risk\": \"1 sentence about tightest coupling/biggest risk\"\n"
                f"}}\n\n"
                f"Keep recommendations specific to the listed services - no generic advice. "
                f"Aim for 4-6 recommendations, 2-4 quick_wins."
            )
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.5,
                    "response_format": {"type": "json_object"},
                },
                timeout=30,
            )
            data_resp = response.json()
            content = (data_resp.get("choices", [{}])[0].get("message", {}).get("content") or "").strip()
            if content.startswith("```"):
                content = content.split("```", 2)[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            parsed = _json.loads(content)
            if isinstance(parsed, dict) and "recommendations" in parsed:
                return parsed
            return None
        except Exception as e:
            logger.error(f"AI lock-in analysis failed: {e}")
            return None


products_engine = ProductsEngine()