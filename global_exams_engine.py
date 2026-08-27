"""
Charvak Global Exams - International Exam Preparation
Covers: Higher Education, English Proficiency, Finance, IT, PM, Medical
"""
import logging
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger("charvakit.global_exams")

class GlobalExamsEngine:
    def __init__(self):
        self.categories = self._initialize_global_exams()
        logger.info("Global Exams Engine ready")
    
    def _initialize_global_exams(self) -> Dict:
        return {
            # ============================================================
            # CATEGORY 9: INTERNATIONAL HIGHER EDUCATION
            # ============================================================
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
            
            # ============================================================
            # CATEGORY 10: ENGLISH LANGUAGE PROFICIENCY
            # ============================================================
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
            
            # ============================================================
            # CATEGORY 11: FINANCE & ACCOUNTING
            # ============================================================
            "finance": {
                "name": "Finance & Accounting",
                "icon": "💰",
                "exams": [
                    {"id": "cfa", "name": "CFA", "full_name": "Chartered Financial Analyst", "tier": "CBT (Prometric)", "sections": ["Ethics", "Quant", "Economics", "FRA"], "questions": 180, "duration": "270 min", "fee_usd": 940},
                    {"id": "frm", "name": "FRM", "full_name": "Financial Risk Manager", "tier": "CBT (Pearson VUE)", "sections": ["Risk Management", "Quant", "Markets"], "questions": 100, "duration": "240 min", "fee_usd": 750},
                    {"id": "caia", "name": "CAIA", "full_name": "Chartered Alternative Investment", "tier": "CBT", "sections": ["Alternative Investments", "Ethics"], "questions": 200, "duration": "240 min", "fee_usd": 1250},
                    {"id": "us_cpa", "name": "US CPA", "full_name": "Certified Public Accountant", "tier": "CBT (Prometric)", "sections": ["AUD", "BEC", "FAR", "REG"], "questions": 72, "duration": "240 min", "fee_usd": 225},
                    {"id": "acca", "name": "ACCA", "full_name": "Association of Chartered Accountants", "tier": "On-demand CBE", "sections": ["Accounting", "Taxation", "Audit"], "questions": 50, "duration": "180 min", "fee_usd": 150},
                    {"id": "cima", "name": "CIMA", "full_name": "Management Accountants", "tier": "CBT (Pearson VUE)", "sections": ["Management", "Finance", "Strategy"], "questions": 60, "duration": "90 min", "fee_usd": 120},
                    {"id": "cia", "name": "CIA", "full_name": "Certified Internal Auditor", "tier": "CBT", "sections": ["Internal Audit", "Risk", "Governance"], "questions": 125, "duration": "150 min", "fee_usd": 380},
                    {"id": "cma_us", "name": "CMA (US)", "full_name": "Certified Management Accountant", "tier": "CBT", "sections": ["Financial Planning", "Analysis"], "questions": 100, "duration": "240 min", "fee_usd": 415},
                    {"id": "soa", "name": "SOA Exams", "full_name": "Society of Actuaries", "tier": "CBT", "sections": ["Probability", "Financial Math", "Statistics"], "questions": 35, "duration": "180 min", "fee_usd": 225},
                    {"id": "cas", "name": "CAS Exams", "full_name": "Casualty Actuarial Society", "tier": "CBT", "sections": ["MAS-I", "MAS-II", "Exams 5-9"], "questions": 45, "duration": "240 min", "fee_usd": 450}
                ]
            },
            
            # ============================================================
            # CATEGORY 12: IT & CLOUD CERTIFICATIONS
            # ============================================================
            "it_cloud": {
                "name": "IT, Cloud & Technical",
                "icon": "💻",
                "exams": [
                    {"id": "aws_saa", "name": "AWS Solutions Architect", "full_name": "Associate Level", "tier": "CBT (Pearson VUE)", "sections": ["Architecture", "Security", "Cost"], "questions": 65, "duration": "130 min", "fee_usd": 150},
                    {"id": "aws_dev", "name": "AWS Developer", "full_name": "Associate Level", "tier": "CBT", "sections": ["Development", "Deployment", "Debugging"], "questions": 65, "duration": "130 min", "fee_usd": 150},
                    {"id": "azure_104", "name": "Azure Administrator", "full_name": "AZ-104", "tier": "CBT", "sections": ["Identity", "Storage", "Compute"], "questions": 50, "duration": "120 min", "fee_usd": 165},
                    {"id": "azure_305", "name": "Azure Architect", "full_name": "AZ-305", "tier": "CBT", "sections": ["Design", "Security", "Migration"], "questions": 50, "duration": "150 min", "fee_usd": 165},
                    {"id": "gcp_ace", "name": "GCP Associate Engineer", "full_name": "Google Cloud", "tier": "CBT", "sections": ["Cloud", "Kubernetes", "Storage"], "questions": 50, "duration": "120 min", "fee_usd": 125},
                    {"id": "gcp_pca", "name": "GCP Cloud Architect", "full_name": "Professional Level", "tier": "CBT", "sections": ["Architecture", "Security", "Optimization"], "questions": 60, "duration": "120 min", "fee_usd": 200},
                    {"id": "cissp", "name": "CISSP", "full_name": "Certified Information Systems Security", "tier": "CAT", "sections": ["Security", "Risk", "Asset Security"], "questions": 150, "duration": "180 min", "fee_usd": 749},
                    {"id": "ceh", "name": "CEH", "full_name": "Certified Ethical Hacker", "tier": "CBT", "sections": ["Ethical Hacking", "Tools", "Methodology"], "questions": 125, "duration": "240 min", "fee_usd": 1199},
                    {"id": "comptia_sec", "name": "CompTIA Security+", "full_name": "Security+", "tier": "CBT", "sections": ["Security", "Threats", "Architecture"], "questions": 90, "duration": "90 min", "fee_usd": 392},
                    {"id": "ccna", "name": "CCNA", "full_name": "Cisco Certified Network Associate", "tier": "CBT", "sections": ["Networking", "Security", "Automation"], "questions": 100, "duration": "120 min", "fee_usd": 300},
                    {"id": "rhcsa", "name": "RHCSA", "full_name": "Red Hat System Administrator", "tier": "Hands-on", "sections": ["Linux", "Shell", "Services"], "questions": 20, "duration": "180 min", "fee_usd": 400},
                    {"id": "cka", "name": "CKA", "full_name": "Certified Kubernetes Administrator", "tier": "Hands-on", "sections": ["Kubernetes", "Troubleshooting", "Networking"], "questions": 17, "duration": "120 min", "fee_usd": 375},
                    {"id": "istqb", "name": "ISTQB", "full_name": "Software Testing", "tier": "CBT", "sections": ["Testing", "QA", "Agile"], "questions": 40, "duration": "60 min", "fee_usd": 229},
                    {"id": "salesforce", "name": "Salesforce Admin", "full_name": "Administrator Certification", "tier": "CBT", "sections": ["Salesforce", "CRM", "Automation"], "questions": 60, "duration": "105 min", "fee_usd": 200}
                ]
            },
            
            # ============================================================
            # CATEGORY 13: PROJECT MANAGEMENT & GOVERNANCE
            # ============================================================
            "project_management": {
                "name": "Project Management",
                "icon": "📊",
                "exams": [
                    {"id": "pmp", "name": "PMP", "full_name": "Project Management Professional", "tier": "CBT (Pearson VUE)", "sections": ["People", "Process", "Business"], "questions": 180, "duration": "230 min", "fee_usd": 555},
                    {"id": "capm", "name": "CAPM", "full_name": "Certified Associate in PM", "tier": "CBT", "sections": ["PM Fundamentals", "Process"], "questions": 150, "duration": "180 min", "fee_usd": 300},
                    {"id": "pmi_acp", "name": "PMI-ACP", "full_name": "Agile Certified Practitioner", "tier": "CBT", "sections": ["Agile", "Scrum", "Lean"], "questions": 120, "duration": "180 min", "fee_usd": 495},
                    {"id": "prince2", "name": "PRINCE2", "full_name": "Foundation & Practitioner", "tier": "Digital Proctoring", "sections": ["Principles", "Themes", "Processes"], "questions": 60, "duration": "60 min", "fee_usd": 350},
                    {"id": "psm", "name": "PSM I/II/III", "full_name": "Professional Scrum Master", "tier": "Online", "sections": ["Scrum", "Agile", "Team"], "questions": 80, "duration": "60 min", "fee_usd": 150},
                    {"id": "itil4", "name": "ITIL 4", "full_name": "Foundation & Managing Professional", "tier": "CBT", "sections": ["Service Management", "Practices"], "questions": 40, "duration": "60 min", "fee_usd": 350}
                ]
            },
            
            # ============================================================
            # CATEGORY 14: MEDICAL LICENSING
            # ============================================================
            "medical_licensing": {
                "name": "Medical Licensing",
                "icon": "⚕️",
                "exams": [
                    {"id": "usmle_step1", "name": "USMLE Step 1", "full_name": "Medical Licensing - Basic Sciences", "tier": "CBT", "sections": ["Anatomy", "Physiology", "Pathology"], "questions": 280, "duration": "480 min", "fee_usd": 660},
                    {"id": "usmle_step2", "name": "USMLE Step 2 CK", "full_name": "Clinical Knowledge", "tier": "CBT", "sections": ["Medicine", "Surgery", "Pediatrics"], "questions": 318, "duration": "540 min", "fee_usd": 660},
                    {"id": "nclex", "name": "NCLEX-RN/PN", "full_name": "Nursing Licensure", "tier": "CAT", "sections": ["Nursing", "Patient Care", "Safety"], "questions": 145, "duration": "300 min", "fee_usd": 200},
                    {"id": "inbde", "name": "INBDE", "full_name": "Dental Board Examination", "tier": "CBT", "sections": ["Dental Sciences", "Clinical"], "questions": 500, "duration": "480 min", "fee_usd": 700},
                    {"id": "amc", "name": "AMC Exams", "full_name": "Australian Medical Council", "tier": "CAT", "sections": ["Medicine", "Surgery"], "questions": 150, "duration": "210 min", "fee_usd": 1800},
                    {"id": "plab1", "name": "PLAB Part 1", "full_name": "UK Medical License", "tier": "CBT", "sections": ["Medicine", "Surgery", "Clinical"], "questions": 180, "duration": "180 min", "fee_usd": 255}
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

global_exams_engine = GlobalExamsEngine()