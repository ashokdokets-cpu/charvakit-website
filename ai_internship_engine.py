"""
Charvak AI Internship Program
2-week AI-powered internship with real-world scenarios
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List

logger = logging.getLogger("charvakit.ai_internship")

class AIInternshipEngine:
    def __init__(self):
        self.programs = self._initialize_programs()
        self.enrollments = {}
        self.progress = {}
        logger.info("AI Internship Engine ready")
    def _initialize_programs(self):
        """Initialize 20+ internship programs across all disciplines."""
        return {
            # ENGINEERING (6)
            "ai_ml": {
                "name": "AI/ML Engineer Internship",
                "duration": "2 weeks",
                "price": 2999,
                "category": "Engineering",
                "skills": ["Python", "ML", "Deep Learning", "Cloud"],
                "deliverables": ["ML Model", "API", "Documentation"],
                "scenarios": self._generate_scenarios("AI/ML Engineer")
            },
            "full_stack": {
                "name": "Full Stack Developer Internship",
                "duration": "2 weeks",
                "price": 2499,
                "category": "Engineering",
                "skills": ["React", "Node.js", "Database", "API"],
                "deliverables": ["Web App", "API", "Database"],
                "scenarios": self._generate_scenarios("Full Stack Developer")
            },
            "data_engineer": {
                "name": "Data Engineer Internship",
                "duration": "2 weeks",
                "price": 2799,
                "category": "Engineering",
                "skills": ["Python", "SQL", "ETL", "Big Data"],
                "deliverables": ["Data Pipeline", "Dashboard"],
                "scenarios": self._generate_scenarios("Data Engineer")
            },
            "devops": {
                "name": "DevOps Engineer Internship",
                "duration": "2 weeks",
                "price": 2499,
                "category": "Engineering",
                "skills": ["Docker", "K8s", "CI/CD", "Cloud"],
                "deliverables": ["Pipeline", "Deployment"],
                "scenarios": self._generate_scenarios("DevOps Engineer")
            },
            "cybersecurity": {
                "name": "Cybersecurity Analyst Internship",
                "duration": "2 weeks",
                "price": 2999,
                "category": "Engineering",
                "skills": ["Security", "Networking", "Ethical Hacking"],
                "deliverables": ["Security Audit", "Report"],
                "scenarios": self._generate_scenarios("Cybersecurity Analyst")
            },
            "cloud_architect": {
                "name": "Cloud Architect Internship",
                "duration": "2 weeks",
                "price": 2799,
                "category": "Engineering",
                "skills": ["AWS", "Azure", "GCP", "Architecture"],
                "deliverables": ["Architecture Design"],
                "scenarios": self._generate_scenarios("Cloud Architect")
            },
            
            # SCIENCE (4)
            "data_scientist": {
                "name": "Data Scientist Internship",
                "duration": "2 weeks",
                "price": 2999,
                "category": "Science",
                "skills": ["Python", "Statistics", "ML", "Visualization"],
                "deliverables": ["Analysis Report", "Models"],
                "scenarios": self._generate_scenarios("Data Scientist")
            },
            "research_scientist": {
                "name": "Research Scientist Internship",
                "duration": "2 weeks",
                "price": 2499,
                "category": "Science",
                "skills": ["Research Methods", "Data Analysis", "Writing"],
                "deliverables": ["Research Paper", "Presentation"],
                "scenarios": self._generate_scenarios("Research Scientist")
            },
            "bioinformatics": {
                "name": "Bioinformatics Analyst Internship",
                "duration": "2 weeks",
                "price": 2799,
                "category": "Science",
                "skills": ["Biology", "Python", "Genomics"],
                "deliverables": ["Genomic Analysis", "Report"],
                "scenarios": self._generate_scenarios("Bioinformatics Analyst")
            },
            "environmental": {
                "name": "Environmental Scientist Internship",
                "duration": "2 weeks",
                "price": 2299,
                "category": "Science",
                "skills": ["Environmental Data", "GIS", "Analysis"],
                "deliverables": ["Environmental Report"],
                "scenarios": self._generate_scenarios("Environmental Scientist")
            },
            
            # MANAGEMENT (4)
            "business_analyst": {
                "name": "Business Analyst Internship",
                "duration": "2 weeks",
                "price": 2499,
                "category": "Management",
                "skills": ["Requirements", "Analysis", "Communication"],
                "deliverables": ["Requirements Doc", "Analysis"],
                "scenarios": self._generate_scenarios("Business Analyst")
            },
            "product_manager": {
                "name": "Product Manager Internship",
                "duration": "2 weeks",
                "price": 2999,
                "category": "Management",
                "skills": ["Product Strategy", "UX", "Roadmap"],
                "deliverables": ["PRD", "Roadmap"],
                "scenarios": self._generate_scenarios("Product Manager")
            },
            "marketing_manager": {
                "name": "Marketing Manager Internship",
                "duration": "2 weeks",
                "price": 2299,
                "category": "Management",
                "skills": ["Digital Marketing", "Analytics", "Content"],
                "deliverables": ["Campaign Plan", "Report"],
                "scenarios": self._generate_scenarios("Marketing Manager")
            },
            "financial_analyst": {
                "name": "Financial Analyst Internship",
                "duration": "2 weeks",
                "price": 2799,
                "category": "Management",
                "skills": ["Finance", "Excel", "Modeling"],
                "deliverables": ["Financial Model", "Report"],
                "scenarios": self._generate_scenarios("Financial Analyst")
            },
            
            # MASTERS (6)
            "mtech_ai": {
                "name": "MTech AI Internship",
                "duration": "2 weeks",
                "price": 3499,
                "category": "Masters",
                "skills": ["Advanced ML", "Deep Learning", "Research"],
                "deliverables": ["Research Paper", "Model"],
                "scenarios": self._generate_scenarios("MTech AI")
            },
            "mtech_software": {
                "name": "MTech Software Internship",
                "duration": "2 weeks",
                "price": 2999,
                "category": "Masters",
                "skills": ["Architecture", "Systems Design", "Coding"],
                "deliverables": ["System Design", "Code"],
                "scenarios": self._generate_scenarios("MTech Software")
            },
            "mba_strategy": {
                "name": "MBA Strategy Internship",
                "duration": "2 weeks",
                "price": 3499,
                "category": "Masters",
                "skills": ["Business Strategy", "Leadership", "Analysis"],
                "deliverables": ["Strategy Doc", "Presentation"],
                "scenarios": self._generate_scenarios("MBA Strategy")
            },
            "msc_data": {
                "name": "MSc Data Science Internship",
                "duration": "2 weeks",
                "price": 2999,
                "category": "Masters",
                "skills": ["Statistics", "ML", "Big Data"],
                "deliverables": ["Research Paper", "Dashboard"],
                "scenarios": self._generate_scenarios("MSc Data Science")
            },
            "msc_psychology": {
                "name": "MSc Psychology Internship",
                "duration": "2 weeks",
                "price": 2499,
                "category": "Masters",
                "skills": ["Research", "Counseling", "Analysis"],
                "deliverables": ["Research Report", "Case Study"],
                "scenarios": self._generate_scenarios("MSc Psychology")
            },
            "ma_economics": {
                "name": "MA Economics Internship",
                "duration": "2 weeks",
                "price": 2299,
                "category": "Masters",
                "skills": ["Econometrics", "Policy", "Analysis"],
                "deliverables": ["Economic Analysis", "Report"],
                "scenarios": self._generate_scenarios("MA Economics")
            }
        }
    
    def _generate_scenarios(self, role):
        """Generate 14-day scenarios for any role."""
        return [
            {"day": 1, "task": "Onboarding & Setup", "scenario": f"You join as {role} intern. Set up environment."},
            {"day": 2, "task": "Research & Analysis", "scenario": f"Research industry trends for {role}."},
            {"day": 3, "task": "First Assignment", "scenario": f"Complete first {role} task."},
            {"day": 4, "task": "Deep Dive", "scenario": f"Dive deeper into {role} skills."},
            {"day": 5, "task": "Practical Project", "scenario": f"Start practical {role} project."},
            {"day": 6, "task": "Review & Feedback", "scenario": f"Submit work for AI mentor review."},
            {"day": 7, "task": "Week 1 Review", "scenario": f"Present progress to AI team lead."},
            {"day": 8, "task": "Advanced Topics", "scenario": f"Learn advanced {role} concepts."},
            {"day": 9, "task": "Real Project Work", "scenario": f"Work on real {role} project."},
            {"day": 10, "task": "Testing & Quality", "scenario": f"Ensure quality in deliverables."},
            {"day": 11, "task": "Optimization", "scenario": f"Optimize {role} work."},
            {"day": 12, "task": "Documentation", "scenario": f"Document project and processes."},
            {"day": 13, "task": "Final Presentation", "scenario": f"Prepare final presentation."},
            {"day": 14, "task": "Graduation", "scenario": f"Complete internship. Receive badge."}
        ]
    def get_programs(self):
        """Get all internship programs."""
        programs = []
        for key, prog in self.programs.items():
            programs.append({
                "id": key,
                "name": prog["name"],
                "duration": prog["duration"],
                "price": prog["price"],
                "category": prog.get("category", "General"),
                "skills": prog["skills"],
                "deliverables": prog["deliverables"]
            })
        return {"status": "success", "programs": programs}
    
    def enroll(self, email, program_id):
        """Enroll student in internship."""
        if program_id not in self.programs:
            return {"status": "error", "message": "Program not found"}
        
        enrollment_id = f"INT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.enrollments[enrollment_id] = {
            "enrollment_id": enrollment_id,
            "email": email,
            "program_id": program_id,
            "start_date": datetime.now().isoformat(),
            "status": "active",
            "current_day": 1
        }
        return {"status": "success", "enrollment_id": enrollment_id}
    
    def get_daily_scenario(self, enrollment_id, day):
        """Get daily scenario for intern."""
        if enrollment_id not in self.enrollments:
            return {"status": "error", "message": "Enrollment not found"}
        
        enrollment = self.enrollments[enrollment_id]
        program = self.programs[enrollment["program_id"]]
        
        if day > len(program["scenarios"]):
            return {"status": "error", "message": "Internship completed"}
        
        scenario = program["scenarios"][day - 1]
        return {"status": "success", "day": day, "scenario": scenario}
    
    def complete_internship(self, enrollment_id):
        """Complete internship and generate badge."""
        if enrollment_id not in self.enrollments:
            return {"status": "error", "message": "Enrollment not found"}
        
        enrollment = self.enrollments[enrollment_id]
        program = self.programs[enrollment["program_id"]]
        
        badge = f"CHARVAK-{program['name'][:10].upper().replace(' ', '')}-{datetime.now().strftime('%Y%m')}"
        
        synopsis = f"""
        AI Internship Synopsis
        ======================
        Student: {enrollment['email']}
        Program: {program['name']}
        Duration: {program['duration']}
        Skills: {', '.join(program['skills'])}
        Deliverables: {', '.join(program['deliverables'])}
        Badge: {badge}
        Completed: {datetime.now().isoformat()}
        """
        
        return {
            "status": "success",
            "badge": badge,
            "synopsis": synopsis,
            "skills": program["skills"],
            "deliverables": program["deliverables"]
        }

ai_internship_engine = AIInternshipEngine()
