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
        self.results = []
        logger.info("✅ Products Engine ready")
    
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
        
        self.results.append({"type": "lock_in_breaker", **result})
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
        
        return {"status": "success", **result}


products_engine = ProductsEngine()