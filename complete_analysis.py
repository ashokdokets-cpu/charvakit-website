"""
Charvak Complete Skill Analysis
Resume upload, education background, certifications, detailed reporting
"""
import logging
import json
import os
from datetime import datetime

logger = logging.getLogger("charvakit.complete_analysis")

class CompleteSkillAnalysis:
    def __init__(self):
        self.user_profiles = {}
        self.analysis_reports = {}
        logger.info("Complete Skill Analysis ready")
    
    def analyze_complete_profile(self, email, data):
        """Analyze complete user profile including resume, education, certifications."""
        skills = data.get("skills", [])
        education = data.get("education", [])
        certifications = data.get("certifications", [])
        experience = data.get("experience", "")
        resume_text = data.get("resume_text", "")
        
        # Extract skills from resume if provided
        if resume_text:
            extracted_skills = self._extract_skills_from_resume(resume_text)
            skills = list(set(skills + extracted_skills))
        
        # Analyze against roles
        from dynamic_role_engine import dynamic_role_engine
        recommendations = dynamic_role_engine.analyze_skills_and_recommend(
            email, skills, None, experience or "fresher"
        )
        
        # Generate detailed report
        report = {
            "email": email,
            "skills_analyzed": skills,
            "education": education,
            "certifications": certifications,
            "experience_level": experience,
            "recommendations": recommendations.get("profile", {}).get("recommendations", []),
            "ai_insights": recommendations.get("profile", {}).get("ai_insights", []),
            "generated_at": datetime.now().isoformat()
        }
        
        self.analysis_reports[email] = report
        
        return {"status": "success", "report": report}
    
    def _extract_skills_from_resume(self, resume_text):
        """Extract skills from resume text."""
        skill_keywords = [
            "Python", "Java", "JavaScript", "SQL", "React", "Node.js", "AWS",
            "Docker", "Kubernetes", "Machine Learning", "Data Science", "HTML",
            "CSS", "Git", "Linux", "DSA", "Algorithms", "OOPs", "DBMS",
            "Networks", "Cloud", "DevOps", "Cybersecurity", "Testing", "Selenium"
        ]
        
        found_skills = []
        resume_lower = resume_text.lower()
        
        for skill in skill_keywords:
            if skill.lower() in resume_lower:
                found_skills.append(skill)
        
        return found_skills
    
    def get_user_report(self, email):
        """Get complete analysis report for user."""
        if email not in self.analysis_reports:
            return {"status": "error", "message": "No analysis found"}
        return {"status": "success", "report": self.analysis_reports[email]}
    
    def get_skill_gap_report(self, email, target_role):
        """Get skill gap report for a specific role."""
        if email not in self.analysis_reports:
            return {"status": "error", "message": "No analysis found"}
        
        report = self.analysis_reports[email]
        user_skills = set(report["skills_analyzed"])
        
        # Get target role skills
        from dynamic_role_engine import dynamic_role_engine
        if target_role in dynamic_role_engine.role_database:
            role = dynamic_role_engine.role_database[target_role]
            required_skills = set(role["skills"])
            
            matched = user_skills & required_skills
            gaps = required_skills - user_skills
            
            return {
                "status": "success",
                "role": role["name"],
                "matched_skills": list(matched),
                "skill_gaps": list(gaps),
                "match_percentage": round(len(matched) / len(required_skills) * 100, 1) if required_skills else 0
            }
        
        return {"status": "error", "message": "Role not found"}

complete_analysis = CompleteSkillAnalysis()
