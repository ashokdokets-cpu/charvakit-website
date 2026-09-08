"""
Charvak AI-Driven Skill Analysis
OpenAI analyzes resume, education, certifications and generates recommendations
"""
import logging
import json
import os
from datetime import datetime

logger = logging.getLogger("charvakit.ai_analysis")

class AISkillAnalysis:
    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv()
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.analysis_history = {}
        logger.info(f"AI Skill Analysis - OpenAI: {'ENABLED' if self.openai_api_key else 'DISABLED'}")
    
    def analyze_user_profile(self, email, data):
        """AI analyzes complete user profile."""
        resume_text = data.get("resume_text", "")
        education = data.get("education", "")
        certifications = data.get("certifications", [])
        experience = data.get("experience", "")
        skills = data.get("skills", [])
        
        # Call OpenAI for AI analysis
        ai_analysis = self._call_openai_analysis(resume_text, education, certifications, experience, skills)
        
        if ai_analysis:
            report = ai_analysis
        else:
            # Fallback analysis
            report = self._fallback_analysis(skills, education, certifications, experience)
        
        report["email"] = email
        report["generated_at"] = datetime.now().isoformat()
        report["ai_generated"] = bool(self.openai_api_key)
        
        self.analysis_history[email] = report
        return {"status": "success", "report": report}
    
    def _call_openai_analysis(self, resume_text, education, certifications, experience, skills):
        """OpenAI analyzes the profile and generates recommendations."""
        if not self.openai_api_key:
            return None
        
        try:
            import requests
            
            prompt = f"""Analyze this candidate profile and provide career recommendations:

            RESUME: {resume_text[:500] if resume_text else 'Not provided'}
            EDUCATION: {education if education else 'Not provided'}
            CERTIFICATIONS: {', '.join(certifications) if certifications else 'None'}
            EXPERIENCE: {experience if experience else 'Fresher'}
            SKILLS: {', '.join(skills) if skills else 'Not provided'}

            Provide:
            1. Top 3 recommended career roles with match percentage
            2. Skills matched for each role
            3. Skill gaps to work on
            4. Learning recommendations
            5. Overall career advice

            Return JSON with structure:
            {{"recommended_roles": [{{"role": "", "match_percentage": 0, "matched_skills": [], "gaps": []}}], "learning_recommendations": [], "career_advice": ""}}
            """
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.openai_api_key}"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.8,
                    "max_tokens": 2000
                },
                timeout=20
            )
            
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            
            import re
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception as e:
            logger.error(f"OpenAI analysis failed: {e}")
        
        return None
    
    def _fallback_analysis(self, skills, education, certifications, experience):
        """Fallback analysis when AI unavailable."""
        from dynamic_role_engine import dynamic_role_engine
        
        recommendations = dynamic_role_engine.analyze_skills_and_recommend(
            "user@example.com", skills, None, experience or "fresher"
        )
        
        roles = recommendations.get("profile", {}).get("recommendations", [])[:3]
        
        return {
            "recommended_roles": [
                {
                    "role": r.get("role_name", ""),
                    "match_percentage": r.get("match_percentage", 0),
                    "matched_skills": r.get("matched_skills", []),
                    "gaps": r.get("skill_gaps", [])
                }
                for r in roles
            ],
            "learning_recommendations": ["Focus on skill gaps", "Practice daily", "Take mock tests"],
            "career_advice": "Build projects and get certified."
        }
    
    def get_analysis_report(self, email):
        """Get AI analysis report."""
        if email not in self.analysis_history:
            return {"status": "error", "message": "No analysis found"}
        return {"status": "success", "report": self.analysis_history[email]}

ai_analysis = AISkillAnalysis()
