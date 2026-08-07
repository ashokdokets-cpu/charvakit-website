"""
Charvak North America - Semantic Vector Matching Engine
AI-powered matching beyond basic keyword search
"""
import json
import re
from typing import Dict, List, Tuple
from datetime import datetime

class VectorMatcher:
    """Semantic vector matching for candidate-job pairing"""
    
    # Skill embeddings (simplified - in production, use pgvector/Pinecone)
    SKILL_EMBEDDINGS = {
        # Java ecosystem
        "java": ["spring boot", "microservices", "kafka", "hibernate", "jpa", "rest api", "j2ee", "maven", "gradle", "jenkins"],
        "spring boot": ["java", "microservices", "rest api", "kafka", "jpa", "spring cloud", "docker"],
        
        # Frontend
        "react": ["javascript", "typescript", "redux", "next.js", "graphql", "html", "css", "node.js", "webpack"],
        "angular": ["typescript", "javascript", "rxjs", "ngrx", "html", "css"],
        
        # Cloud/DevOps
        "aws": ["lambda", "ec2", "s3", "dynamodb", "cloudformation", "terraform", "docker", "kubernetes"],
        "kubernetes": ["docker", "helm", "aws", "azure", "gcp", "terraform", "ci/cd", "jenkins", "argocd"],
        "terraform": ["aws", "azure", "gcp", "infrastructure as code", "iac", "docker", "kubernetes"],
        
        # Data
        "python": ["django", "flask", "fastapi", "pandas", "numpy", "tensorflow", "pytorch", "data science", "ml"],
        "machine learning": ["python", "tensorflow", "pytorch", "scikit-learn", "deep learning", "nlp", "data science"],
        "data science": ["python", "r", "sql", "pandas", "numpy", "tableau", "power bi", "machine learning"],
    }
    
    def __init__(self):
        self.match_history = []
    
    def expand_skills(self, skills: List[str]) -> List[str]:
        """Expand skills with related technologies"""
        expanded = set()
        for skill in skills:
            skill_lower = skill.lower().strip()
            expanded.add(skill_lower)
            
            # Add related skills from embeddings
            if skill_lower in self.SKILL_EMBEDDINGS:
                for related in self.SKILL_EMBEDDINGS[skill_lower]:
                    expanded.add(related)
        
        return list(expanded)
    
    def calculate_match_score(self, candidate_skills: List[str], 
                               job_skills: List[str],
                               candidate_rate: float = 0,
                               job_rate_min: float = 0,
                               job_rate_max: float = 0) -> Dict:
        """Calculate comprehensive match score"""
        
        # Expand skills for semantic matching
        expanded_candidate = self.expand_skills(candidate_skills)
        expanded_job = self.expand_skills(job_skills)
        
        # Direct skill match
        direct_matches = set(s.lower() for s in candidate_skills) & set(s.lower() for s in job_skills)
        direct_score = len(direct_matches) / max(len(job_skills), 1) * 50  # 50% weight
        
        # Semantic/related skill match
        semantic_matches = set(expanded_candidate) & set(expanded_job)
        semantic_score = len(semantic_matches) / max(len(expanded_job), 1) * 30  # 30% weight
        
        # Rate compatibility (20% weight)
        rate_score = 0
        if candidate_rate > 0 and job_rate_min > 0:
            if job_rate_min <= candidate_rate <= job_rate_max:
                rate_score = 20
            elif candidate_rate < job_rate_min:
                # Candidate is cheaper (good for client)
                rate_score = 15
            elif candidate_rate <= job_rate_max * 1.1:
                # Within 10% above range
                rate_score = 10
            else:
                rate_score = 0
        
        total_score = min(round(direct_score + semantic_score + rate_score), 100)
        
        result = {
            "total_score": total_score,
            "direct_match_pct": round(len(direct_matches) / max(len(job_skills), 1) * 100),
            "semantic_match_pct": round(len(semantic_matches) / max(len(expanded_job), 1) * 100),
            "rate_compatible": rate_score > 0,
            "direct_matches": list(direct_matches),
            "semantic_matches": list(set(expanded_candidate) & set(expanded_job) - direct_matches),
            "missing_skills": list(set(s.lower() for s in job_skills) - set(s.lower() for s in candidate_skills)),
            "match_level": self._get_match_level(total_score)
        }
        
        return result
    
    def _get_match_level(self, score: int) -> str:
        if score >= 85: return "Excellent Match - Submit Immediately"
        if score >= 70: return "Strong Match - Recommend Submission"
        if score >= 55: return "Good Match - Consider Submitting"
        if score >= 40: return "Partial Match - Upskill Recommended"
        return "Weak Match - Not Recommended"
    
    def match_candidate_to_jobs(self, candidate: Dict, jobs: List[Dict]) -> List[Dict]:
        """Match a candidate against all available jobs"""
        matches = []
        
        for job in jobs:
            score = self.calculate_match_score(
                candidate_skills=candidate.get("skills", []),
                job_skills=job.get("skills_required", []),
                candidate_rate=candidate.get("rate", 0),
                job_rate_min=job.get("rate_range", {}).get("min", 0),
                job_rate_max=job.get("rate_range", {}).get("max", 0)
            )
            
            if score["total_score"] >= 40:  # Only return viable matches
                matches.append({
                    "job_id": job["job_id"],
                    "job_title": job["title"],
                    "client": job["client"],
                    "location": job["location"],
                    "match_score": score,
                    "rate_range": job.get("rate_range"),
                })
        
        # Sort by score descending
        matches.sort(key=lambda x: x["match_score"]["total_score"], reverse=True)
        
        self.match_history.append({
            "candidate_id": candidate.get("id"),
            "matches": len(matches),
            "top_score": matches[0]["match_score"]["total_score"] if matches else 0,
            "timestamp": datetime.now().isoformat()
        })
        
        return matches
    
    def get_match_analytics(self) -> Dict:
        """Get matching analytics"""
        if not self.match_history:
            return {"total_matches": 0, "avg_score": 0, "top_skills": []}
        
        total = len(self.match_history)
        avg_score = sum(m["top_score"] for m in self.match_history) / total
        
        return {
            "total_matches": total,
            "average_top_score": round(avg_score, 1),
            "recent_matches": self.match_history[-5:]
        }

# Initialize matcher
vector_matcher = VectorMatcher()

print("✅ Vector Matching Engine ready")
print(f"   Skill embeddings: {len(VectorMatcher.SKILL_EMBEDDINGS)} categories")