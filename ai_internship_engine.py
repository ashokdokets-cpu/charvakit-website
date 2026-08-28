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
        """Initialize internship programs."""
        return {
            "ai_ml": {
                "name": "AI/ML Engineer Internship",
                "duration": "2 weeks",
                "price": 2999,
                "scenarios": [
                    {"day": 1, "task": "Set up development environment", "scenario": "You join a startup as AI intern. Set up Python, Git, and ML libraries."},
                    {"day": 2, "task": "Data collection & cleaning", "scenario": "Collect customer data from CSV. Clean and preprocess for ML."},
                    {"day": 3, "task": "Exploratory data analysis", "scenario": "Analyze patterns in customer churn data. Create visualizations."},
                    {"day": 4, "task": "Feature engineering", "scenario": "Create features for churn prediction model."},
                    {"day": 5, "task": "Model building", "scenario": "Train classification model for churn prediction."},
                    {"day": 6, "task": "Model evaluation", "scenario": "Evaluate model performance. Improve accuracy."},
                    {"day": 7, "task": "Week 1 review", "scenario": "Present findings to 'team lead' (AI). Get feedback."},
                    {"day": 8, "task": "API development", "scenario": "Create REST API for your ML model using FastAPI."},
                    {"day": 9, "task": "Frontend integration", "scenario": "Build simple UI to interact with your model."},
                    {"day": 10, "task": "Testing & debugging", "scenario": "Write unit tests. Fix bugs found by 'QA team' (AI)."},
                    {"day": 11, "task": "Deployment", "scenario": "Deploy your model to cloud. Make it production-ready."},
                    {"day": 12, "task": "Documentation", "scenario": "Write technical documentation for your project."},
                    {"day": 13, "task": "Final presentation", "scenario": "Prepare final presentation for 'stakeholders' (AI)."},
                    {"day": 14, "task": "Graduation & badge", "scenario": "Complete internship. Receive verified badge and synopsis."}
                ],
                "skills": ["Python", "ML", "FastAPI", "Git", "Cloud"],
                "deliverables": ["ML Model", "API", "Documentation", "Presentation"]
            },
            "web_dev": {
                "name": "Full Stack Developer Internship",
                "duration": "2 weeks",
                "price": 2499,
                "scenarios": [
                    {"day": 1, "task": "Setup & planning", "scenario": "You join a tech startup. Plan your project architecture."},
                    {"day": 2, "task": "Frontend basics", "scenario": "Build responsive UI with HTML/CSS/JavaScript."},
                    {"day": 3, "task": "React introduction", "scenario": "Convert static pages to React components."},
                    {"day": 4, "task": "State management", "scenario": "Implement state management for your app."},
                    {"day": 5, "task": "Backend setup", "scenario": "Create Node.js/Python backend with REST APIs."},
                    {"day": 6, "task": "Database design", "scenario": "Design and implement database schema."},
                    {"day": 7, "task": "Week 1 demo", "scenario": "Demo your progress to 'team' (AI). Get feedback."},
                    {"day": 8, "task": "Authentication", "scenario": "Implement user authentication and authorization."},
                    {"day": 9, "task": "API integration", "scenario": "Connect frontend to backend APIs."},
                    {"day": 10, "task": "Testing", "scenario": "Write tests. Fix bugs."},
                    {"day": 11, "task": "Performance optimization", "scenario": "Optimize your app for speed and efficiency."},
                    {"day": 12, "task": "Deployment", "scenario": "Deploy to cloud. Configure CI/CD."},
                    {"day": 13, "task": "Final polish", "scenario": "Polish UI/UX. Fix remaining issues."},
                    {"day": 14, "task": "Graduation", "scenario": "Present final project. Receive badge."}
                ],
                "skills": ["React", "Node.js", "Database", "API", "Cloud"],
                "deliverables": ["Web App", "API", "Database", "Documentation"]
            },
            "data_science": {
                "name": "Data Science Internship",
                "duration": "2 weeks",
                "price": 2799,
                "scenarios": [
                    {"day": 1, "task": "Environment setup", "scenario": "Set up Python data science environment (Jupyter, Pandas)."},
                    {"day": 2, "task": "Data collection", "scenario": "Collect data from multiple sources."},
                    {"day": 3, "task": "Data cleaning", "scenario": "Clean messy real-world data."},
                    {"day": 4, "task": "EDA", "scenario": "Explore data. Find insights and patterns."},
                    {"day": 5, "task": "Visualization", "scenario": "Create compelling visualizations with Plotly."},
                    {"day": 6, "task": "Statistical analysis", "scenario": "Perform hypothesis testing and statistical analysis."},
                    {"day": 7, "task": "Week 1 report", "scenario": "Create insights report for 'stakeholders' (AI)."},
                    {"day": 8, "task": "ML basics", "scenario": "Build first ML model for prediction."},
                    {"day": 9, "task": "Model tuning", "scenario": "Tune hyperparameters. Improve model."},
                    {"day": 10, "task": "Advanced ML", "scenario": "Try ensemble methods. Compare models."},
                    {"day": 11, "task": "Dashboard", "scenario": "Build interactive dashboard with Streamlit."},
                    {"day": 12, "task": "Storytelling", "scenario": "Create data story with insights."},
                    {"day": 13, "task": "Final presentation", "scenario": "Prepare final data presentation."},
                    {"day": 14, "task": "Graduation", "scenario": "Present findings. Receive badge."}
                ],
                "skills": ["Python", "Pandas", "Visualization", "Statistics", "ML"],
                "deliverables": ["Analysis Report", "Dashboard", "Models", "Presentation"]
            },
            "digital_marketing": {
                "name": "Digital Marketing Internship",
                "duration": "2 weeks",
                "price": 1999,
                "scenarios": [
                    {"day": 1, "task": "Market research", "scenario": "Research target audience and competitors."},
                    {"day": 2, "task": "SEO basics", "scenario": "Optimize website content for search engines."},
                    {"day": 3, "task": "Content strategy", "scenario": "Create content calendar and strategy."},
                    {"day": 4, "task": "Social media", "scenario": "Create social media campaign plan."},
                    {"day": 5, "task": "Email marketing", "scenario": "Design email marketing campaign."},
                    {"day": 6, "task": "Paid ads", "scenario": "Create Google/Facebook ad campaign."},
                    {"day": 7, "task": "Week 1 review", "scenario": "Review metrics. Optimize campaigns."},
                    {"day": 8, "task": "Analytics", "scenario": "Set up Google Analytics. Track performance."},
                    {"day": 9, "task": "Content creation", "scenario": "Create blog posts and social content."},
                    {"day": 10, "task": "A/B testing", "scenario": "Run A/B tests on campaigns."},
                    {"day": 11, "task": "Influencer marketing", "scenario": "Plan influencer collaboration."},
                    {"day": 12, "task": "ROI analysis", "scenario": "Analyze campaign ROI. Optimize budget."},
                    {"day": 13, "task": "Final report", "scenario": "Create marketing performance report."},
                    {"day": 14, "task": "Graduation", "scenario": "Present results. Receive badge."}
                ],
                "skills": ["SEO", "Social Media", "Analytics", "Content", "Ads"],
                "deliverables": ["Campaign Plan", "Content", "Analytics Report"]
            }
        }
    
    def get_programs(self):
        """Get all internship programs."""
        programs = []
        for key, prog in self.programs.items():
            programs.append({
                "id": key,
                "name": prog["name"],
                "duration": prog["duration"],
                "price": prog["price"],
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