"""
Application Kit Engine - Session 119.2
Generates AI-powered application materials for a specific job.
"""
import os
import json
import logging
from typing import Dict
from openai import OpenAI

logger = logging.getLogger("charvakit.application_kit")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ApplicationKitEngine:
    def generate_kit(self, job_title: str, company: str, job_description: str, student_name: str, student_skills: str) -> Dict:
        """Generate a complete application kit."""
        
        # 1. Cover Letter
        cover_letter_prompt = f"""
        Write a 4-sentence cover letter for the role of {job_title} at {company}.
        Candidate Name: {student_name}
        Candidate Skills: {student_skills}
        Job Description: {job_description[:2000]}
        
        Rules:
        - Sentence 1: The single most relevant result/skill.
        - Sentence 2: Why this specific company (use real details from the JD).
        - Sentence 3: What they would do in the first 90 days.
        - Sentence 4: Plain ask for a conversation.
        - No buzzwords. No "I am excited to apply."
        """
        
        # 2. Resume Optimizer
        resume_prompt = f"""
        Based on this job description and the candidate's skills, rewrite 3 resume bullet points.
        Format them using the Google XYZ formula: "Accomplished [X] as measured by [Y], by doing [Z]."
        Candidate Skills: {student_skills}
        Job Description: {job_description[:2000]}
        Output ONLY the 3 bullet points, one per line.
        """
        
        # 3. Interview Prep (STAR format)
        interview_prompt = f"""
        Generate the 3 most likely interview questions for a {job_title} at {company}.
        For each question, provide a STAR-format answer (Situation, Task, Action, Result).
        Use the candidate's skills where possible.
        Candidate Skills: {student_skills}
        Job Description: {job_description[:2000]}
        Format clearly with Question, Situation, Task, Action, Result.
        """
        
        # 4. Cold Email
        email_prompt = f"""
        Write a short (under 150 words) cold email to the hiring manager for the {job_title} role at {company}.
        It should open with a genuine observation about the company, bridge to one candidate skill, and ask for a 15-minute call.
        Candidate Skills: {student_skills}
        """

        try:
            # Make the API calls
            cover = client.chat.completions.create(
                model="gpt-4o-mini", messages=[{"role": "user", "content": cover_letter_prompt}], max_tokens=300
            ).choices[0].message.content.strip()

            resume = client.chat.completions.create(
                model="gpt-4o-mini", messages=[{"role": "user", "content": resume_prompt}], max_tokens=300
            ).choices[0].message.content.strip()

            interview = client.chat.completions.create(
                model="gpt-4o-mini", messages=[{"role": "user", "content": interview_prompt}], max_tokens=800
            ).choices[0].message.content.strip()

            email = client.chat.completions.create(
                model="gpt-4o-mini", messages=[{"role": "user", "content": email_prompt}], max_tokens=300
            ).choices[0].message.content.strip()

            return {
                "status": "success",
                "cover_letter": cover,
                "resume_bullets": resume,
                "interview_prep": interview,
                "cold_email": email,
                # Refinement links to Dokets Resume Builder
                "refine_links": {
                    "cover_letter": "https://www.doketsrb.com/#cover-letter",
                    "resume_builder": "https://www.doketsrb.com/#builder",
                    "linkedin": "https://www.doketsrb.com/#linkedin",
                }
            }
        except Exception as e:
            logger.error(f"Failed to generate kit: {e}")
            return {"status": "error", "message": str(e)}

application_kit_engine = ApplicationKitEngine()