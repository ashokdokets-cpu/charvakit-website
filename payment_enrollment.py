"""
Charvak Payment-Gated Course Enrollment
Installments, access control, extension handling
"""
import logging
import json
import os
from datetime import datetime, timedelta

logger = logging.getLogger("charvakit.payment_gated")

class PaymentGatedEnrollment:
    def __init__(self):
        self.enrollments = {}
        self.payments = {}
        logger.info("Payment Gated Enrollment ready")
    
    def calculate_installments(self, course_price, duration_weeks):
        """Calculate installment plan based on duration."""
        # 2 installments for courses up to 8 weeks
        # 3 installments for 9-16 weeks
        # 4 installments for 16+ weeks
        if duration_weeks <= 8:
            num_installments = 2
        elif duration_weeks <= 14:
            num_installments = 3
        else:
            num_installments = 4
        
        installment_amount = course_price / num_installments
        installment_interval = duration_weeks / num_installments
        
        installments = []
        for i in range(num_installments):
            installments.append({
                "installment_number": i + 1,
                "amount": round(installment_amount, 2),
                "due_week": round((i + 1) * installment_interval),
                "due_date": (datetime.now() + timedelta(weeks=i * installment_interval)).isoformat()
            })
        
        return {
            "status": "success",
            "total_price": course_price,
            "num_installments": num_installments,
            "installments": installments
        }
    
    def enroll_with_payment(self, email, course_name, duration_weeks, payment_method="razorpay"):
        """Enroll with first installment payment."""
        # Get course price
        course_prices = {
            "Full Stack Web Development": 4999,
            "Data Science & ML": 5999,
            "Python Programming": 999,
            "AWS Cloud Computing": 3999,
            "DevOps Engineering": 4999,
            "Cybersecurity": 4999,
            "Java Development": 2999,
            "React & Frontend": 2499,
            "SQL & Database": 999,
            "Docker & Kubernetes": 2499,
            "AI & Deep Learning": 6999,
            "Mobile App Development": 3999,
            "Blockchain Development": 4999,
            "Data Analytics": 2999,
            "UI/UX Design": 1999,
            "Cloud Architecture": 5999,
            "Node.js Backend": 2499,
            "Python for Data Science": 3999,
            "Machine Learning Ops": 4999,
            "Spring Boot": 2499,
            "Angular Development": 1999,
            "Ethical Hacking": 5999,
            "Big Data": 4999,
            "Software Testing": 999,
            "Git & DevOps Tools": 499
        }
        
        price = course_prices.get(course_name, 999)
        installments = self.calculate_installments(price, duration_weeks)
        
        enrollment_id = f"ENROLL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        self.enrollments[enrollment_id] = {
            "enrollment_id": enrollment_id,
            "email": email,
            "course": course_name,
            "duration_weeks": duration_weeks,
            "total_price": price,
            "installments": installments["installments"],
            "paid_installments": 0,
            "access_granted": False,
            "status": "pending_payment",
            "enrolled_at": datetime.now().isoformat()
        }
        
        return {
            "status": "success",
            "enrollment_id": enrollment_id,
            "total_price": price,
            "installment_plan": installments
        }
    
    def pay_installment(self, enrollment_id, installment_number):
        """Process installment payment and grant access."""
        if enrollment_id not in self.enrollments:
            return {"status": "error", "message": "Enrollment not found"}
        
        enrollment = self.enrollments[enrollment_id]
        
        # Process payment (simulated)
        payment_id = f"PAY-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        self.payments[payment_id] = {
            "payment_id": payment_id,
            "enrollment_id": enrollment_id,
            "installment_number": installment_number,
            "amount": enrollment["installments"][installment_number - 1]["amount"],
            "paid_at": datetime.now().isoformat()
        }
        
        enrollment["paid_installments"] = installment_number
        
        # Grant access after first installment
        if installment_number >= 1:
            enrollment["access_granted"] = True
            enrollment["status"] = "active"
        
        # Check if all installments paid
        if installment_number >= len(enrollment["installments"]):
            enrollment["status"] = "fully_paid"
        
        return {
            "status": "success",
            "payment_id": payment_id,
            "access_granted": enrollment["access_granted"],
            "paid_installments": enrollment["paid_installments"],
            "total_installments": len(enrollment["installments"])
        }
    
    def check_access(self, enrollment_id):
        """Check if user has access."""
        if enrollment_id not in self.enrollments:
            return {"status": "error", "message": "Enrollment not found"}
        
        enrollment = self.enrollments[enrollment_id]
        
        # Check if access is still valid (within duration)
        enrolled_date = datetime.fromisoformat(enrollment["enrolled_at"])
        access_end = enrolled_date + timedelta(weeks=enrollment["duration_weeks"])
        
        if datetime.now() > access_end:
            enrollment["status"] = "expired"
            return {
                "status": "success",
                "access_granted": False,
                "message": "Course duration completed. Request extension to continue."
            }
        
        return {
            "status": "success",
            "access_granted": enrollment["access_granted"],
            "weeks_remaining": max(0, (access_end - datetime.now()).days // 7)
        }
    
    def request_extension(self, enrollment_id, additional_weeks):
        """Handle extension request."""
        if enrollment_id not in self.enrollments:
            return {"status": "error", "message": "Enrollment not found"}
        
        enrollment = self.enrollments[enrollment_id]
        
        # Calculate extension cost (weekly rate)
        weekly_rate = enrollment["total_price"] / enrollment["duration_weeks"]
        extension_cost = weekly_rate * additional_weeks
        
        return {
            "status": "success",
            "message": f"Extension for {additional_weeks} weeks costs ₹{round(extension_cost, 2)}",
            "extension_cost": round(extension_cost, 2),
            "weekly_rate": round(weekly_rate, 2)
        }
    
    def pay_extension(self, enrollment_id, additional_weeks):
        """Pay for extension and extend access."""
        if enrollment_id not in self.enrollments:
            return {"status": "error", "message": "Enrollment not found"}
        
        enrollment = self.enrollments[enrollment_id]
        weekly_rate = enrollment["total_price"] / enrollment["duration_weeks"]
        extension_cost = weekly_rate * additional_weeks
        
        # Process payment
        payment_id = f"EXT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        enrollment["duration_weeks"] += additional_weeks
        enrollment["extension_paid"] = True
        
        return {
            "status": "success",
            "payment_id": payment_id,
            "new_duration": enrollment["duration_weeks"],
            "extension_cost": round(extension_cost, 2),
            "message": f"Extended by {additional_weeks} weeks"
        }

payment_enrollment = PaymentGatedEnrollment()
