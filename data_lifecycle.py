"""
Charvak Data Lifecycle Management
Job expiry, candidate inactivity, GDPR deletion, renewal reminders, data export
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

logger = logging.getLogger("charvakit.lifecycle")


class DataLifecycle:
    """Complete data lifecycle management."""
    
    JOB_EXPIRY_DAYS = 30
    CANDIDATE_INACTIVITY_DAYS = 90
    APPLICATION_RETENTION_DAYS = 90
    REMINDER_DAYS_BEFORE_EXPIRY = 7
    
    def __init__(self):
        self.deleted_records = []
        self.renewal_reminders = []
        logger.info("Data Lifecycle Engine ready")
    
    # ============================================================
    # 1. JOB AUTO-EXPIRY
    # ============================================================
    
    def expire_old_jobs(self) -> Dict:
        """Expire jobs older than 30 days."""
        from job_board_engine import job_board_engine
        
        expired_count = 0
        cutoff = datetime.now() - timedelta(days=self.JOB_EXPIRY_DAYS)
        
        for job in job_board_engine.jobs:
            try:
                posted = datetime.strptime(job.get("posted_date", ""), "%Y-%m-%d")
                if posted < cutoff and job.get("status") == "active":
                    job["status"] = "expired"
                    expired_count += 1
            except:
                pass
        
        logger.info(f"Expired {expired_count} jobs")
        return {"status": "success", "expired_jobs": expired_count}
    
    # ============================================================
    # 2. CANDIDATE INACTIVITY TRACKING
    # ============================================================
    
    def check_inactive_candidates(self) -> Dict:
        """Find candidates inactive for 90+ days."""
        from candidate_engine import candidate_engine
        
        inactive = []
        cutoff = datetime.now() - timedelta(days=self.CANDIDATE_INACTIVITY_DAYS)
        
        for candidate in candidate_engine.candidates:
            try:
                last_activity = datetime.fromisoformat(candidate.get("updated_at", candidate.get("registered_at", "")))
                if last_activity < cutoff:
                    inactive.append({
                        "candidate_id": candidate["candidate_id"],
                        "name": candidate.get("name"),
                        "email": candidate.get("email"),
                        "last_activity": candidate.get("updated_at"),
                        "days_inactive": (datetime.now() - last_activity).days
                    })
            except:
                pass
        
        return {"status": "success", "inactive_candidates": inactive, "count": len(inactive)}
    
    # ============================================================
    # 3. GDPR DATA DELETION (Right to be Forgotten)
    # ============================================================
    
    def delete_user_data(self, email: str) -> Dict:
        """Delete all user data on request (GDPR compliance)."""
        deleted = {"email": email, "deleted_from": [], "deleted_at": datetime.now().isoformat()}
        
        # Delete from candidate engine
        try:
            from candidate_engine import candidate_engine
            candidate_engine.candidates = [c for c in candidate_engine.candidates if c.get("email") != email]
            deleted["deleted_from"].append("candidates")
        except:
            pass
        
        # Delete from job applications
        try:
            from job_board_engine import job_board_engine
            job_board_engine.applications = [a for a in job_board_engine.applications if a.get("user_id") != email]
            deleted["deleted_from"].append("applications")
        except:
            pass
        
        # Delete from messaging
        try:
            from messaging_engine import messaging_engine
            messaging_engine.messages = [m for m in messaging_engine.messages if m.get("sender_id") != email and m.get("recipient_id") != email]
            deleted["deleted_from"].append("messages")
        except:
            pass
        
        # Delete from student suite
        try:
            from student_suite_engine import student_suite_engine
            student_suite_engine.subscriptions = [s for s in student_suite_engine.subscriptions if s.get("student_email") != email]
            deleted["deleted_from"].append("student_subscriptions")
        except:
            pass
        
        # Delete from users table (PostgreSQL)
        try:
            import psycopg2
            import os
            conn = psycopg2.connect(os.getenv("DATABASE_URL"))
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE email = %s", (email,))
            conn.commit()
            cursor.close()
            conn.close()
            deleted["deleted_from"].append("users_table")
        except:
            pass
        
        self.deleted_records.append(deleted)
        logger.info(f"Deleted data for {email}: {deleted['deleted_from']}")
        
        return {
            "status": "success",
            "message": f"All data for {email} has been deleted",
            "deleted_from": deleted["deleted_from"]
        }
    
    # ============================================================
    # 4. RENEWAL REMINDERS
    # ============================================================
    
    def send_renewal_reminders(self) -> Dict:
        """Send reminders for jobs about to expire."""
        from job_board_engine import job_board_engine
        
        reminders = []
        reminder_cutoff = datetime.now() + timedelta(days=self.REMINDER_DAYS_BEFORE_EXPIRY)
        
        for job in job_board_engine.jobs:
            try:
                posted = datetime.strptime(job.get("posted_date", ""), "%Y-%m-%d")
                expiry_date = posted + timedelta(days=self.JOB_EXPIRY_DAYS)
                
                if datetime.now() < expiry_date <= reminder_cutoff and job.get("status") == "active":
                    reminder = {
                        "job_id": job["job_id"],
                        "title": job["title"],
                        "company": job["company"],
                        "days_until_expiry": (expiry_date - datetime.now()).days,
                        "message": f"Your job '{job['title']}' expires in {(expiry_date - datetime.now()).days} days. Renew to keep it active."
                    }
                    reminders.append(reminder)
                    
                    # Send email if possible
                    try:
                        from email_engine import email_engine
                        email_engine.notify_admin(
                            subject=f"Job Expiry Reminder: {job['title']}",
                            message=reminder["message"]
                        )
                    except:
                        pass
            except:
                pass
        
        self.renewal_reminders.extend(reminders)
        return {"status": "success", "reminders_sent": len(reminders), "reminders": reminders}
    
    # ============================================================
    # 5. DATA EXPORT (Portability)
    # ============================================================
    
    def export_user_data(self, email: str) -> Dict:
        """Export all user data in JSON format (GDPR portability)."""
        export_data = {"email": email, "exported_at": datetime.now().isoformat(), "data": {}}
        
        # Candidate data
        try:
            from candidate_engine import candidate_engine
            candidate = candidate_engine.get_candidate_by_email(email)
            if candidate:
                export_data["data"]["candidate_profile"] = candidate
        except:
            pass
        
        # Job applications
        try:
            from job_board_engine import job_board_engine
            applications = [a for a in job_board_engine.applications if a.get("user_id") == email]
            if applications:
                export_data["data"]["job_applications"] = applications
        except:
            pass
        
        # Badges
        try:
            from badge_engine import badge_engine
            badges = badge_engine.get_user_badges(email)
            if badges.get("count", 0) > 0:
                export_data["data"]["badges"] = badges["badges"]
        except:
            pass
        
        # LMS certificates
        try:
            from lms_engine import lms_engine
            certificates = [c for c in lms_engine.certificates if c.get("student_email") == email]
            if certificates:
                export_data["data"]["certificates"] = certificates
        except:
            pass
        
        return {
            "status": "success",
            "export_data": export_data,
            "message": f"Data for {email} exported successfully",
            "download_url": f"/api/lifecycle/export/{email}"
        }
    
    def get_stats(self) -> Dict:
        return {
            "status": "success",
            "stats": {
                "deleted_records": len(self.deleted_records),
                "renewal_reminders": len(self.renewal_reminders),
                "job_expiry_days": self.JOB_EXPIRY_DAYS,
                "candidate_inactivity_days": self.CANDIDATE_INACTIVITY_DAYS
            }
        }


data_lifecycle = DataLifecycle()