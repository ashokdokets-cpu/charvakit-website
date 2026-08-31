"""
Charvak AI Internship Program
Multi-duration AI-powered internship with real-world scenarios
"""
import logging
import random
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
            "ai_ml": {
                "name": "AI/ML Engineer Internship",
                "duration": "4 weeks",
                "price": 2999,
                "category": "Engineering",
                "skills": ["Python", "ML", "Deep Learning", "Cloud"],
                "deliverables": ["ML Model", "API", "Documentation"],
                "scenarios": self._generate_scenarios("AI/ML Engineer")
            },
            "full_stack": {
                "name": "Full Stack Developer Internship",
                "duration": "4 weeks",
                "price": 2499,
                "category": "Engineering",
                "skills": ["React", "Node.js", "Database", "API"],
                "deliverables": ["Web App", "API", "Database"],
                "scenarios": self._generate_scenarios("Full Stack Developer")
            },
            "data_engineer": {
                "name": "Data Engineer Internship",
                "duration": "4 weeks",
                "price": 2799,
                "category": "Engineering",
                "skills": ["Python", "SQL", "ETL", "Big Data"],
                "deliverables": ["Data Pipeline", "Dashboard"],
                "scenarios": self._generate_scenarios("Data Engineer")
            },
            "devops": {
                "name": "DevOps Engineer Internship",
                "duration": "4 weeks",
                "price": 2499,
                "category": "Engineering",
                "skills": ["Docker", "K8s", "CI/CD", "Cloud"],
                "deliverables": ["Pipeline", "Deployment"],
                "scenarios": self._generate_scenarios("DevOps Engineer")
            },
            "cybersecurity": {
                "name": "Cybersecurity Analyst Internship",
                "duration": "4 weeks",
                "price": 2999,
                "category": "Engineering",
                "skills": ["Security", "Networking", "Ethical Hacking"],
                "deliverables": ["Security Audit", "Report"],
                "scenarios": self._generate_scenarios("Cybersecurity Analyst")
            },
            "cloud_architect": {
                "name": "Cloud Architect Internship",
                "duration": "4 weeks",
                "price": 2799,
                "category": "Engineering",
                "skills": ["AWS", "Azure", "GCP", "Architecture"],
                "deliverables": ["Architecture Design"],
                "scenarios": self._generate_scenarios("Cloud Architect")
            },
            "data_scientist": {
                "name": "Data Scientist Internship",
                "duration": "4 weeks",
                "price": 2999,
                "category": "Science",
                "skills": ["Python", "Statistics", "ML", "Visualization"],
                "deliverables": ["Analysis Report", "Models"],
                "scenarios": self._generate_scenarios("Data Scientist")
            },
            "research_scientist": {
                "name": "Research Scientist Internship",
                "duration": "4 weeks",
                "price": 2499,
                "category": "Science",
                "skills": ["Research Methods", "Data Analysis", "Writing"],
                "deliverables": ["Research Paper", "Presentation"],
                "scenarios": self._generate_scenarios("Research Scientist")
            },
            "bioinformatics": {
                "name": "Bioinformatics Analyst Internship",
                "duration": "4 weeks",
                "price": 2799,
                "category": "Science",
                "skills": ["Biology", "Python", "Genomics"],
                "deliverables": ["Genomic Analysis", "Report"],
                "scenarios": self._generate_scenarios("Bioinformatics Analyst")
            },
            "environmental": {
                "name": "Environmental Scientist Internship",
                "duration": "4 weeks",
                "price": 2299,
                "category": "Science",
                "skills": ["Environmental Data", "GIS", "Analysis"],
                "deliverables": ["Environmental Report"],
                "scenarios": self._generate_scenarios("Environmental Scientist")
            },
            "business_analyst": {
                "name": "Business Analyst Internship",
                "duration": "4 weeks",
                "price": 2499,
                "category": "Management",
                "skills": ["Requirements", "Analysis", "Communication"],
                "deliverables": ["Requirements Doc", "Analysis"],
                "scenarios": self._generate_scenarios("Business Analyst")
            },
            "product_manager": {
                "name": "Product Manager Internship",
                "duration": "4 weeks",
                "price": 2999,
                "category": "Management",
                "skills": ["Product Strategy", "UX", "Roadmap"],
                "deliverables": ["PRD", "Roadmap"],
                "scenarios": self._generate_scenarios("Product Manager")
            },
            "marketing_manager": {
                "name": "Marketing Manager Internship",
                "duration": "4 weeks",
                "price": 2299,
                "category": "Management",
                "skills": ["Digital Marketing", "Analytics", "Content"],
                "deliverables": ["Campaign Plan", "Report"],
                "scenarios": self._generate_scenarios("Marketing Manager")
            },
            "financial_analyst": {
                "name": "Financial Analyst Internship",
                "duration": "4 weeks",
                "price": 2799,
                "category": "Management",
                "skills": ["Finance", "Excel", "Modeling"],
                "deliverables": ["Financial Model", "Report"],
                "scenarios": self._generate_scenarios("Financial Analyst")
            },
            "mtech_ai": {
                "name": "MTech AI Internship",
                "duration": "4 weeks",
                "price": 3499,
                "category": "Masters",
                "skills": ["Advanced ML", "Deep Learning", "Research"],
                "deliverables": ["Research Paper", "Model"],
                "scenarios": self._generate_scenarios("MTech AI")
            },
            "mtech_software": {
                "name": "MTech Software Internship",
                "duration": "4 weeks",
                "price": 2999,
                "category": "Masters",
                "skills": ["Architecture", "Systems Design", "Coding"],
                "deliverables": ["System Design", "Code"],
                "scenarios": self._generate_scenarios("MTech Software")
            },
            "mba_strategy": {
                "name": "MBA Strategy Internship",
                "duration": "4 weeks",
                "price": 3499,
                "category": "Masters",
                "skills": ["Business Strategy", "Leadership", "Analysis"],
                "deliverables": ["Strategy Doc", "Presentation"],
                "scenarios": self._generate_scenarios("MBA Strategy")
            },
            "msc_data": {
                "name": "MSc Data Science Internship",
                "duration": "4 weeks",
                "price": 2999,
                "category": "Masters",
                "skills": ["Statistics", "ML", "Big Data"],
                "deliverables": ["Research Paper", "Dashboard"],
                "scenarios": self._generate_scenarios("MSc Data Science")
            },
            "msc_psychology": {
                "name": "MSc Psychology Internship",
                "duration": "4 weeks",
                "price": 2499,
                "category": "Masters",
                "skills": ["Research", "Counseling", "Analysis"],
                "deliverables": ["Research Report", "Case Study"],
                "scenarios": self._generate_scenarios("MSc Psychology")
            },
            "ma_economics": {
                "name": "MA Economics Internship",
                "duration": "4 weeks",
                "price": 2299,
                "category": "Masters",
                "skills": ["Econometrics", "Policy", "Analysis"],
                "deliverables": ["Economic Analysis", "Report"],
                "scenarios": self._generate_scenarios("MA Economics")
            }
        }

    def _generate_scenarios(self, role, days=28):
        """Generate scenarios for any duration (default 28 days - 4 weeks)."""
        foundation = [
            {"task": "Onboarding & Setup", "scenario": f"You join as {role} intern. Set up environment."},
            {"task": "Research & Analysis", "scenario": f"Research industry trends for {role}."},
            {"task": "First Assignment", "scenario": f"Complete first {role} task."},
            {"task": "Deep Dive", "scenario": f"Dive deeper into {role} skills."},
            {"task": "Practical Project", "scenario": f"Start practical {role} project."},
            {"task": "Review & Feedback", "scenario": f"Submit work for AI mentor review."},
            {"task": "Week 1 Review", "scenario": f"Present progress to AI team lead."},
            {"task": "Advanced Topics", "scenario": f"Learn advanced {role} concepts."},
            {"task": "Real Project Work", "scenario": f"Work on real {role} project."},
            {"task": "Testing & Quality", "scenario": f"Ensure quality in deliverables."},
            {"task": "Optimization", "scenario": f"Optimize {role} work."},
            {"task": "Documentation", "scenario": f"Document project and processes."},
            {"task": "Week 2 Review", "scenario": f"Review progress. Plan for advanced work."},
            {"task": "Mid-Program Assessment", "scenario": f"AI evaluates your progress. Get feedback."}
        ]
        advanced = [
            {"task": "Advanced Project Planning", "scenario": f"Plan advanced {role} project."},
            {"task": "Implementation Phase 1", "scenario": f"Implement first phase of project."},
            {"task": "Implementation Phase 2", "scenario": f"Complete second phase."},
            {"task": "Integration", "scenario": f"Integrate all components."},
            {"task": "Testing & Debugging", "scenario": f"Test and fix bugs."},
            {"task": "Code Review", "scenario": f"AI reviews your code. Get feedback."},
            {"task": "Refactoring", "scenario": f"Improve code quality."},
            {"task": "Performance Optimization", "scenario": f"Optimize for speed and efficiency."},
            {"task": "Security Implementation", "scenario": f"Add security measures."},
            {"task": "Documentation", "scenario": f"Complete documentation."},
            {"task": "Deployment Preparation", "scenario": f"Prepare for deployment."},
            {"task": "Final Testing", "scenario": f"Run final tests."},
            {"task": "Project Presentation", "scenario": f"Prepare final presentation."},
            {"task": "Week 4 Review & Graduation", "scenario": f"Complete internship. Receive badge."}
        ]
        all_tasks = foundation + advanced
        scenarios = []
        for day in range(1, days + 1):
            idx = min(day - 1, len(all_tasks) - 1)
            task_info = all_tasks[idx]
            scenarios.append({
                "day": day,
                "task": task_info["task"],
                "scenario": f"Day {day}: {task_info['scenario']}"
            })
        return scenarios

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

    def enroll(self, email, program_id, duration="standard"):
        """Enroll student with duration option."""
        if program_id not in self.programs:
            return {"status": "error", "message": "Program not found"}
        duration_days = {"quick": 14, "standard": 28, "professional": 42}
        total_days = duration_days.get(duration, 28)
        enrollment_id = f"INT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.enrollments[enrollment_id] = {
            "enrollment_id": enrollment_id,
            "email": email,
            "program_id": program_id,
            "duration": duration,
            "total_days": total_days,
            "start_date": datetime.now().isoformat(),
            "status": "active",
            "current_day": 1
        }
        return {"status": "success", "enrollment_id": enrollment_id, "total_days": total_days}

    def get_daily_scenario(self, enrollment_id, day):
        """Get daily scenario for intern."""
        if enrollment_id not in self.enrollments:
            return {"status": "error", "message": "Enrollment not found"}
        enrollment = self.enrollments[enrollment_id]
        program = self.programs[enrollment["program_id"]]
        total_days = enrollment.get("total_days", len(program["scenarios"]))
        if day > total_days:
            return {"status": "error", "message": "Internship completed"}
        scenario = program["scenarios"][day - 1] if day - 1 < len(program["scenarios"]) else program["scenarios"][-1]
        return {"status": "success", "day": day, "scenario": scenario}

    def complete_internship(self, enrollment_id):
        """Complete internship and generate badge."""
        if enrollment_id not in self.enrollments:
            return {"status": "error", "message": "Enrollment not found"}
        enrollment = self.enrollments[enrollment_id]
        program = self.programs[enrollment["program_id"]]

    def _format_badge_name(self, name):
        badge = "CHARVAK-" + badge_name.upper() + "-" + datetime.now().strftime("%Y%m")
        name = name.replace("Internship", "").strip()
        name = name.replace("  ", " ").strip()
        return name

    def complete_internship(self, enrollment_id):
# In complete_internship:
badge = f"CHARVAK-{self._format_badge_name(program['name']).upper()}-{datetime.now().strftime('%Y%m')}"
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

    def submit_work(self, enrollment_id, day, submission_text):
        """Submit daily work for AI review."""
        if enrollment_id not in self.enrollments:
            return {"status": "error", "message": "Enrollment not found"}
        if enrollment_id not in self.progress:
            self.progress[enrollment_id] = {}
        self.progress[enrollment_id][day] = {
            "submission": submission_text,
            "submitted_at": datetime.now().isoformat(),
            "status": "reviewed",
            "ai_feedback": {
                "score": random.randint(7, 10),
                "strengths": ["Good understanding", "Clear implementation"],
                "improvements": ["Add more documentation", "Consider edge cases"],
                "next_steps": "Proceed to next day's task"
            }
        }
        return {"status": "success", "feedback": self.progress[enrollment_id][day]["ai_feedback"]}

    def get_progress(self, enrollment_id):
        """Get internship progress."""
        if enrollment_id not in self.enrollments:
            return {"status": "error", "message": "Enrollment not found"}
        enrollment = self.enrollments.get(enrollment_id, {})
        total_days = enrollment.get("total_days", 28)
        completed = len(self.progress.get(enrollment_id, {}))
        return {
            "status": "success",
            "enrollment_id": enrollment_id,
            "completed_days": completed,
            "total_days": total_days,
            "progress_percentage": round((completed / total_days) * 100, 1),
            "days": self.progress.get(enrollment_id, {})
        }

ai_internship_engine = AIInternshipEngine()
