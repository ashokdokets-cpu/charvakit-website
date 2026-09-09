"""
Charvak Bench Matrix - Module 6
"""
import logging
from datetime import datetime

logger = logging.getLogger("charvakit.bench_matrix")

class BenchMatrix:
    def __init__(self):
        self.consultants = {}
        logger.info("Bench Matrix ready")
    
    def add_consultant(self, email, corporate_name, tax_id, work_auth, tech_stack, min_rate):
        consultant_id = f"CON-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.consultants[consultant_id] = {
            "consultant_id": consultant_id, "email": email,
            "corporate_name": corporate_name, "tax_id": tax_id,
            "work_authorization": work_auth, "tech_stack": tech_stack,
            "min_hourly_rate": min_rate, "status": "ACTIVE_BENCH"
        }
        return {"status": "success", "consultant": self.consultants[consultant_id]}
    
    def get_active_bench(self):
        active = [c for c in self.consultants.values() if c["status"] == "ACTIVE_BENCH"]
        return {"status": "success", "total": len(active), "consultants": active}

bench_matrix = BenchMatrix()
