"""
Charvak Admin Role Management
Only admins can add roles - users can view and analyze
"""
import logging
from datetime import datetime

logger = logging.getLogger("charvakit.admin_roles")

class AdminRoleManager:
    def __init__(self):
        self.admin_emails = ["charvakit@gmail.com", "admin@charvakit.com"]
        logger.info("Admin Role Manager ready")
    
    def is_admin(self, email):
        """Check if user is admin."""
        return email in self.admin_emails
    
    def add_role_as_admin(self, admin_email, role_name, category, skills, description=None):
        """Add role - only if admin."""
        if not self.is_admin(admin_email):
            return {
                "status": "error", 
                "message": "Unauthorized. Only admins can add roles."
            }
        
        from role_manager import role_manager
        return role_manager.add_new_role(role_name, category, skills, description)
    
    def add_role_with_ai_as_admin(self, admin_email, role_name, category, description=None):
        """Add role with AI - only if admin."""
        if not self.is_admin(admin_email):
            return {
                "status": "error", 
                "message": "Unauthorized. Only admins can add roles."
            }
        
        from role_manager import role_manager
        return role_manager.add_role_with_ai(role_name, category, description)

admin_role_manager = AdminRoleManager()
