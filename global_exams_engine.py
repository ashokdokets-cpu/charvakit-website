"""
Charvak Global Exams - International Exam Preparation
Covers: Higher Education, English Proficiency, Finance, IT, PM, Medical Licensing
"""
import logging
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger("charvakit.global_exams")

class GlobalExamsEngine:
    def __init__(self):
        self.categories = self._initialize_global_exams()
        logger.info("Global Exams Engine ready - 55+ international exams")
    
    def _initialize_global_exams(self) -> Dict:
        return {
            "higher_education": {
                "name": "International Higher Education",
                "icon": "🎓",
                "exams": [
                    {"id": "sat", "name": "Digital SAT", "full_name": "Scholastic Assessment Test", "tier": "CBT", "sections": ["Reading", "Writing", "Math"], "questions": 98, "duration": "134 min", "fee_usd": 60},
                    {"id": "act", "name": "ACT", "full_name": "American College Testing", "tier": "CBT", "sections": ["English", "Math", "Reading", "Science"], "questions": 215, "duration": "175 min", "fee_usd": 68},
                    {"id": "ap_exams", "name": "AP Exams", "full_name": "Advanced Placement", "tier": "Digital", "sections": ["Subject Specific"], "questions": 55, "duration": "180 min", "fee_usd": 97},
                    {"id": "gre", "name": "GRE General", "full_name": "Graduate Record Examination", "tier": "CBT", "sections": ["Verbal", "Quant", "AWA"], "questions": 82, "duration": "114 min", "fee_usd": 220},
                    {"id": "gre_subject", "name": "GRE Subject", "full_name": "Physics/Psychology/Math", "tier": "CBT", "sections": ["Subject Specific"], "questions": 66, "duration": "170 min", "fee_usd": 150},
                    {"id": "gmat", "name": "GMAT Focus", "full_name": "Graduate Management Admission Test", "tier": "CBT", "sections": ["Quant", "Verbal", "Data Insights"], "questions": 64, "duration": "135 min", "fee_usd": 275},
                    {"id": "ea", "name": "Executive Assessment", "full_name": "For Executive MBA", "tier": "CBT", "sections": ["IR", "Verbal", "Quant"], "questions": 40, "duration": "90 min", "fee_usd": 350},
                    {"id": "lsat", "name": "LSAT", "full_name": "Law School Admission Test", "tier": "Digital", "sections": ["Logical Reasoning", "Reading Comp"], "questions": 99, "duration": "175 min", "fee_usd": 215},
                    {"id": "lnat", "name": "LNAT", "full_name": "National Admissions Test for Law", "tier": "CBT", "sections": ["Verbal Reasoning", "Essay"], "questions": 42, "duration": "135 min", "fee_usd": 75},
                    {"id": "mcat", "name": "MCAT", "full_name": "Medical College Admission Test", "tier": "CBT", "sections": ["Bio", "Chem", "Psych", "CARS"], "questions": 230, "duration": "375 min", "fee_usd": 330},
                    {"id": "ucat", "name": "UCAT", "full_name": "University Clinical Aptitude Test", "tier": "CBT", "sections": ["Verbal", "Decision Making", "Quant"], "questions": 228, "duration": "120 min", "fee_usd": 75},
                    {"id": "gamsat", "name": "GAMSAT", "full_name": "Graduate Medical School Admissions", "tier": "Digital", "sections": ["Reasoning", "Writing", "Science"], "questions": 102, "duration": "300 min", "fee_usd": 500}
                ]
            },
            "english_proficiency": {
                "name": "English Language Proficiency",
                "icon": "🗣️",
                "exams": [
                    {"id": "toefl", "name": "TOEFL iBT", "full_name": "Test of English as Foreign Language", "tier": "CBT", "sections": ["Reading", "Listening", "Speaking", "Writing"], "questions": 48, "duration": "180 min", "fee_usd": 195},
                    {"id": "ielts", "name": "IELTS", "full_name": "Academic & General Training", "tier": "Computer-Delivered", "sections": ["Listening", "Reading", "Writing", "Speaking"], "questions": 40, "duration": "165 min", "fee_usd": 250},
                    {"id": "pte", "name": "PTE Academic", "full_name": "Pearson Test of English", "tier": "CBT", "sections": ["Speaking", "Writing", "Reading", "Listening"], "questions": 52, "duration": "180 min", "fee_usd": 200},
                    {"id": "duolingo", "name": "Duolingo English Test", "full_name": "Fully automated AI-proctored", "tier": "Online", "sections": ["Literacy", "Comprehension", "Conversation"], "questions": 45, "duration": "60 min", "fee_usd": 59},
                    {"id": "celpip", "name": "CELPIP", "full_name": "Canadian English Language", "tier": "CBT", "sections": ["Listening", "Reading", "Writing", "Speaking"], "questions": 40, "duration": "180 min", "fee_usd": 280},
                    {"id": "oet", "name": "OET", "full_name": "Occupational English Test", "tier": "CBT", "sections": ["Listening", "Reading", "Writing", "Speaking"], "questions": 42, "duration": "170 min", "fee_usd": 455},
                    {"id": "cambridge", "name": "Cambridge English", "full_name": "C1 Advanced/C2 Proficiency", "tier": "CBT", "sections": ["Reading", "Writing", "Listening", "Speaking"], "questions": 52, "duration": "235 min", "fee_usd": 250}
                ]
            },
            "finance": {
                "name": "Finance & Accounting",
                "icon": "💰",
                "exams": [
                    {"id": "cfa", "name": "CFA", "full_name": "Chartered Financial Analyst", "tier": "CBT", "sections": ["Ethics", "Quant", "Economics", "FRA"], "questions": 180, "duration": "270 min", "fee_usd": 940},
                    {"id": "frm", "name": "FRM", "full_name": "Financial Risk Manager", "tier": "CBT", "sections": ["Risk", "Quant", "Markets"], "questions": 100, "duration": "240 min", "fee_usd": 750},
                    {"id": "caia", "name": "CAIA", "full_name": "Alternative Investment Analyst", "tier": "CBT", "sections": ["Alternatives", "Ethics"], "questions": 200, "duration": "240 min", "fee_usd": 1250},
                    {"id": "us_cpa", "name": "US CPA", "full_name": "Certified Public Accountant", "tier": "CBT", "sections": ["AUD", "BEC", "FAR", "REG"], "questions": 72, "duration": "240 min", "fee_usd": 225},
                    {"id": "acca", "name": "ACCA", "full_name": "Chartered Certified Accountants", "tier": "CBE", "sections": ["Accounting", "Tax", "Audit"], "questions": 50, "duration": "180 min", "fee_usd": 150},
                    {"id": "cima", "name": "CIMA", "full_name": "Management Accountants", "tier": "CBT", "sections": ["Management", "Finance", "Strategy"], "questions": 60, "duration": "90 min", "fee_usd": 120},
                    {"id": "cia", "name": "CIA", "full_name": "Certified Internal Auditor", "tier": "CBT", "sections": ["Audit", "Risk", "Governance"], "questions": 125, "duration": "150 min", "fee_usd": 380},
                    {"id": "cma_us", "name": "CMA (US)", "full_name": "Management Accountant", "tier": "CBT", "sections": ["Planning", "Analysis"], "questions": 100, "duration": "240 min", "fee_usd": 415},
                    {"id": "soa", "name": "SOA Exams", "full_name": "Society of Actuaries", "tier": "CBT", "sections": ["Probability", "Financial Math"], "questions": 35, "duration": "180 min", "fee_usd": 225},
                    {"id": "cas", "name": "CAS Exams", "full_name": "Casualty Actuarial Society", "tier": "CBT", "sections": ["MAS-I", "MAS-II"], "questions": 45, "duration": "240 min", "fee_usd": 450}
                ]
            },
            "it_cloud": {
                "name": "IT, Cloud & Technical",
                "icon": "💻",
                "exams": [
                    {"id": "aws_saa", "name": "AWS Solutions Architect", "full_name": "Associate", "tier": "CBT", "sections": ["Architecture", "Security"], "questions": 65, "duration": "130 min", "fee_usd": 150},
                    {"id": "aws_dev", "name": "AWS Developer", "full_name": "Associate", "tier": "CBT", "sections": ["Development", "Deployment"], "questions": 65, "duration": "130 min", "fee_usd": 150},
                    {"id": "azure_104", "name": "Azure Administrator", "full_name": "AZ-104", "tier": "CBT", "sections": ["Identity", "Storage"], "questions": 50, "duration": "120 min", "fee_usd": 165},
                    {"id": "azure_305", "name": "Azure Architect", "full_name": "AZ-305", "tier": "CBT", "sections": ["Design", "Security"], "questions": 50, "duration": "150 min", "fee_usd": 165},
                    {"id": "gcp_ace", "name": "GCP Associate Engineer", "full_name": "Google Cloud", "tier": "CBT", "sections": ["Cloud", "K8s"], "questions": 50, "duration": "120 min", "fee_usd": 125},
                    {"id": "gcp_pca", "name": "GCP Cloud Architect", "full_name": "Professional", "tier": "CBT", "sections": ["Architecture", "Security"], "questions": 60, "duration": "120 min", "fee_usd": 200},
                    {"id": "cissp", "name": "CISSP", "full_name": "Security Professional", "tier": "CAT", "sections": ["Security", "Risk"], "questions": 150, "duration": "180 min", "fee_usd": 749},
                    {"id": "ceh", "name": "CEH", "full_name": "Ethical Hacker", "tier": "CBT", "sections": ["Hacking", "Tools"], "questions": 125, "duration": "240 min", "fee_usd": 1199},
                    {"id": "comptia_sec", "name": "CompTIA Security+", "full_name": "Security+", "tier": "CBT", "sections": ["Security", "Threats"], "questions": 90, "duration": "90 min", "fee_usd": 392},
                    {"id": "ccna", "name": "CCNA", "full_name": "Cisco Network Associate", "tier": "CBT", "sections": ["Networking", "Security"], "questions": 100, "duration": "120 min", "fee_usd": 300},
                    {"id": "rhcsa", "name": "RHCSA", "full_name": "Red Hat Administrator", "tier": "Hands-on", "sections": ["Linux", "Shell"], "questions": 20, "duration": "180 min", "fee_usd": 400},
                    {"id": "cka", "name": "CKA", "full_name": "Kubernetes Administrator", "tier": "Hands-on", "sections": ["K8s", "Troubleshooting"], "questions": 17, "duration": "120 min", "fee_usd": 375},
                    {"id": "istqb", "name": "ISTQB", "full_name": "Software Testing", "tier": "CBT", "sections": ["Testing", "QA"], "questions": 40, "duration": "60 min", "fee_usd": 229},
                    {"id": "salesforce", "name": "Salesforce Admin", "full_name": "Administrator", "tier": "CBT", "sections": ["CRM", "Automation"], "questions": 60, "duration": "105 min", "fee_usd": 200}
                ]
            },
            "project_management": {
                "name": "Project Management",
                "icon": "📊",
                "exams": [
                    {"id": "pmp", "name": "PMP", "full_name": "Project Management Professional", "tier": "CBT", "sections": ["People", "Process", "Business"], "questions": 180, "duration": "230 min", "fee_usd": 555},
                    {"id": "capm", "name": "CAPM", "full_name": "Certified Associate in PM", "tier": "CBT", "sections": ["PM Fundamentals"], "questions": 150, "duration": "180 min", "fee_usd": 300},
                    {"id": "pmi_acp", "name": "PMI-ACP", "full_name": "Agile Practitioner", "tier": "CBT", "sections": ["Agile", "Scrum"], "questions": 120, "duration": "180 min", "fee_usd": 495},
                    {"id": "prince2", "name": "PRINCE2", "full_name": "Foundation & Practitioner", "tier": "Digital", "sections": ["Principles", "Themes"], "questions": 60, "duration": "60 min", "fee_usd": 350},
                    {"id": "psm", "name": "PSM I/II/III", "full_name": "Professional Scrum Master", "tier": "Online", "sections": ["Scrum", "Agile"], "questions": 80, "duration": "60 min", "fee_usd": 150},
                    {"id": "itil4", "name": "ITIL 4", "full_name": "Service Management", "tier": "CBT", "sections": ["Service", "Practices"], "questions": 40, "duration": "60 min", "fee_usd": 350}
                ]
            },
            "medical_licensing": {
                "name": "Medical Licensing",
                "icon": "⚕️",
                "exams": [
                    {"id": "usmle_step1", "name": "USMLE Step 1", "full_name": "Basic Sciences", "tier": "CBT", "sections": ["Anatomy", "Pathology"], "questions": 280, "duration": "480 min", "fee_usd": 660},
                    {"id": "usmle_step2", "name": "USMLE Step 2 CK", "full_name": "Clinical Knowledge", "tier": "CBT", "sections": ["Medicine", "Surgery"], "questions": 318, "duration": "540 min", "fee_usd": 660},
                    {"id": "nclex", "name": "NCLEX-RN/PN", "full_name": "Nursing Licensure", "tier": "CAT", "sections": ["Nursing", "Patient Care"], "questions": 145, "duration": "300 min", "fee_usd": 200},
                    {"id": "inbde", "name": "INBDE", "full_name": "Dental Board", "tier": "CBT", "sections": ["Dental", "Clinical"], "questions": 500, "duration": "480 min", "fee_usd": 700},
                    {"id": "amc", "name": "AMC Exams", "full_name": "Australian Medical Council", "tier": "CAT", "sections": ["Medicine", "Surgery"], "questions": 150, "duration": "210 min", "fee_usd": 1800},
                    {"id": "plab1", "name": "PLAB Part 1", "full_name": "UK Medical License", "tier": "CBT", "sections": ["Medicine", "Clinical"], "questions": 180, "duration": "180 min", "fee_usd": 255}
                ]
            }
        }
    
    def get_all_categories(self) -> Dict:
        """Get all global exam categories."""
        categories = []
        total_exams = 0
        for cat_id, cat_data in self.categories.items():
            categories.append({
                "id": cat_id,
                "name": cat_data["name"],
                "icon": cat_data["icon"],
                "exam_count": len(cat_data["exams"])
            })
            total_exams += len(cat_data["exams"])
        return {"status": "success", "total_categories": len(categories), "total_exams": total_exams, "categories": categories}
    
    def get_exams_by_category(self, category_id: str) -> Dict:
        """Get exams by category."""
        if category_id not in self.categories:
            return {"status": "error", "message": "Category not found"}
        return {"status": "success", "category": self.categories[category_id]["name"], "icon": self.categories[category_id]["icon"], "exams": self.categories[category_id]["exams"]}
    
    def get_exam_details(self, exam_id: str) -> Dict:
        """Get details for specific exam."""
        for cat_data in self.categories.values():
            for exam in cat_data["exams"]:
                if exam["id"] == exam_id:
                    return {"status": "success", "exam": exam, "category": cat_data["name"]}
        return {"status": "error", "message": f"Exam {exam_id} not found"}

global_exams_engine = GlobalExamsEngine()