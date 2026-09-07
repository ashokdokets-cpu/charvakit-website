"""
Charvak Dynamic Role Management
Add any role - system auto-generates skills, training plan, pricing
"""
import logging
import json
import os
from datetime import datetime

logger = logging.getLogger("charvakit.role_manager")

class RoleManager:
    def __init__(self):
        self.custom_roles = {}
        logger.info("Role Manager ready")
    
    def add_new_role(self, role_name, category, required_skills, description=None):
        """Add a new role dynamically."""
        role_id = role_name.lower().replace(" ", "_")
        
        # Auto-generate role data
        role_data = {
            "id": role_id,
            "name": role_name,
            "category": category,
            "skills": required_skills if isinstance(required_skills, list) else [required_skills],
            "description": description or f"{role_name} career path",
            "skills_count": len(required_skills) if isinstance(required_skills, list) else 1,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        self.custom_roles[role_id] = role_data
        
        # Auto-generate training plan
        training_plan = self._generate_training_plan(role_data)
        
        # Auto-generate pricing
        pricing = self._generate_pricing(role_data)
        
        return {
            "status": "success",
            "role": role_data,
            "training_plan": training_plan,
            "pricing": pricing,
            "message": f"Role '{role_name}' added successfully with auto-generated training plan and pricing"
        }
    
    def _generate_training_plan(self, role_data):
        """Auto-generate 4-phase training plan for any role."""
        skills = role_data["skills"]
        
        return {
            "phases": [
                {
                    "phase": 1,
                    "name": "Foundation",
                    "duration": "Weeks 1-2",
                    "focus": skills[:2] if len(skills) >= 2 else skills,
                    "activities": [f"Learn {skill} basics" for skill in skills[:2]]
                },
                {
                    "phase": 2,
                    "name": "Core Skills",
                    "duration": "Weeks 3-6",
                    "focus": skills[2:4] if len(skills) >= 4 else skills,
                    "activities": [f"Master {skill}" for skill in skills[2:4]]
                },
                {
                    "phase": 3,
                    "name": "Advanced",
                    "duration": "Weeks 7-10",
                    "focus": skills[4:] if len(skills) > 4 else skills,
                    "activities": [f"Apply {skill} in projects" for skill in skills[4:]]
                },
                {
                    "phase": 4,
                    "name": "Placement Prep",
                    "duration": "Weeks 11-12",
                    "focus": ["Mock Interviews", "Resume Building"],
                    "activities": ["Daily mock tests", "Company-specific preparation"]
                }
            ]
        }
    
    def _generate_pricing(self, role_data):
        """Auto-generate pricing based on role demand."""
        base_prices = {
            "Technology": 99,
            "Data & AI": 129,
            "Infrastructure": 119,
            "Security": 139,
            "Quality": 89,
            "Product": 109,
            "Business": 99,
            "Design": 89,
            "Custom": 99
        }
        
        base_price = base_prices.get(role_data["category"], 99)
        
        return {
            "basic": base_price * 0.7,
            "standard": base_price,
            "premium": base_price * 1.5,
            "enterprise": base_price * 2.0
        }
    
    def add_role_with_ai(self, role_name, category, description):
        """Add role with AI-generated skills."""
        skills = self._generate_skills_with_ai(role_name, category)
        return self.add_new_role(role_name, category, skills, description)
    
    def _generate_skills_with_ai(self, role_name, category):
        """Generate skills using AI based on role name."""
        # In production, use OpenAI to generate skills
        # For now, use category-based defaults
        category_skills = {
            "Technology": ["Programming", "Data Structures", "Algorithms", "SQL", "Git", "Problem Solving"],
            "Data & AI": ["Python", "Statistics", "Machine Learning", "SQL", "Data Visualization"],
            "Infrastructure": ["Linux", "Cloud", "Networking", "Scripting", "Monitoring"],
            "Security": ["Network Security", "Cryptography", "Risk Assessment", "Security Tools"],
            "Quality": ["Testing", "Automation", "Python", "API Testing"],
            "Product": ["Product Strategy", "User Research", "Agile", "Analytics"],
            "Business": ["Requirements", "SQL", "Excel", "Process Mapping"],
            "Design": ["UI Design", "UX Research", "Prototyping", "User Testing"]
        }
        
        return category_skills.get(category, ["Communication", "Problem Solving", "Teamwork"])
    
    def get_all_roles(self):
        """Get all roles including custom ones."""
        from dynamic_role_engine import dynamic_role_engine
        standard_roles = dynamic_role_engine.get_all_roles()
        
        all_roles = standard_roles["roles"]
        
        for role_id, role in self.custom_roles.items():
            all_roles.append({
                "id": role_id,
                "name": role["name"],
                "category": role["category"],
                "skills_count": role["skills_count"]
            })
        
        return {"status": "success", "total": len(all_roles), "roles": all_roles}
    
    def get_role_details(self, role_id):
        """Get details for any role."""
        from dynamic_role_engine import dynamic_role_engine
        
        # Check standard roles first
        if role_id in dynamic_role_engine.role_database:
            role = dynamic_role_engine.role_database[role_id]
            return {"status": "success", "role": role}
        
        # Check custom roles
        if role_id in self.custom_roles:
            role = self.custom_roles[role_id]
            return {"status": "success", "role": role, "training_plan": self._generate_training_plan(role)}
        
        return {"status": "error", "message": "Role not found"}

role_manager = RoleManager()
