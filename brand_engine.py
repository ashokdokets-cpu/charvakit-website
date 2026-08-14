"""
Charvak Brand Engine
Company brand pages, reviews, promoted jobs
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional
import secrets

logger = logging.getLogger("charvakit.brand")


class BrandEngine:
    """Company brand pages and employer reviews."""
    
    def __init__(self):
        self.companies = []
        self.reviews = []
        self.promoted_jobs = []
        logger.info("✅ Brand Engine ready")
    
    def create_brand_page(self, data: Dict) -> Dict:
        """
        Create a company brand page.
        
        data = {
            "company_name": str,
            "industry": str,
            "description": str,
            "logo_url": str,
            "website": str,
            "location": str,
            "size": str,
            "culture_tags": List[str]
        }
        """
        brand_id = f"BRAND-{secrets.token_hex(4).upper()}"
        
        company = {
            "brand_id": brand_id,
            "company_name": data.get("company_name"),
            "industry": data.get("industry", ""),
            "description": data.get("description", ""),
            "logo_url": data.get("logo_url", ""),
            "website": data.get("website", ""),
            "location": data.get("location", ""),
            "size": data.get("size", ""),
            "culture_tags": data.get("culture_tags", []),
            "average_rating": 0,
            "review_count": 0,
            "created_at": datetime.now().isoformat()
        }
        
        self.companies.append(company)
        logger.info(f"Brand page created: {brand_id} - {data.get('company_name')}")
        
        return {
            "status": "success",
            "brand_id": brand_id,
            "message": "Brand page created!",
            "brand_url": f"https://charvakit.com/companies/{brand_id}"
        }
    
    def post_review(self, data: Dict) -> Dict:
        """
        Post an employer review.
        
        data = {
            "company_id": str,
            "reviewer_name": str,
            "reviewer_type": "intern" / "employee" / "candidate",
            "rating": int (1-5),
            "title": str,
            "review": str,
            "would_recommend": bool
        }
        """
        review_id = f"REV-{secrets.token_hex(4).upper()}"
        
        review = {
            "review_id": review_id,
            "company_id": data.get("company_id"),
            "reviewer_name": data.get("reviewer_name"),
            "reviewer_type": data.get("reviewer_type", "candidate"),
            "rating": int(data.get("rating", 5)),
            "title": data.get("title", ""),
            "review": data.get("review", ""),
            "would_recommend": data.get("would_recommend", True),
            "created_at": datetime.now().isoformat()
        }
        
        self.reviews.append(review)
        
        # Update company rating
        for company in self.companies:
            if company["brand_id"] == data.get("company_id"):
                company["review_count"] += 1
                all_reviews = [r for r in self.reviews if r["company_id"] == company["brand_id"]]
                company["average_rating"] = round(sum(r["rating"] for r in all_reviews) / len(all_reviews), 1)
        
        logger.info(f"Review posted: {review_id}")
        
        return {"status": "success", "review_id": review_id, "message": "Review posted!"}
    
    def get_brand_page(self, brand_id: str) -> Dict:
        """Get company brand page with reviews."""
        company = None
        for c in self.companies:
            if c["brand_id"] == brand_id:
                company = c
                break
        
        if not company:
            return {"status": "error", "message": "Company not found"}
        
        company_reviews = [r for r in self.reviews if r["company_id"] == brand_id]
        
        return {
            "status": "success",
            "company": company,
            "reviews": company_reviews,
            "review_count": len(company_reviews),
            "recommendation_rate": len([r for r in company_reviews if r["would_recommend"]]) / len(company_reviews) * 100 if company_reviews else 0
        }
    
    def promote_job(self, job_id: str, company_id: str) -> Dict:
        """Promote a job posting."""
        promotion_id = f"PROMO-{secrets.token_hex(4).upper()}"
        
        promotion = {
            "promotion_id": promotion_id,
            "job_id": job_id,
            "company_id": company_id,
            "starts_at": datetime.now().isoformat(),
            "ends_at": (datetime.now() + timedelta(days=7)).isoformat(),
            "views": 0,
            "clicks": 0
        }
        
        self.promoted_jobs.append(promotion)
        
        return {
            "status": "success",
            "promotion_id": promotion_id,
            "message": "Job promoted! It will appear in candidate feeds.",
            "duration": "7 days"
        }
    
    def get_all_brands(self) -> Dict:
        """Get all company brand pages."""
        return {
            "status": "success",
            "companies": self.companies,
            "count": len(self.companies),
            "total_reviews": len(self.reviews)
        }
    
    def get_stats(self) -> Dict:
        """Get brand engine statistics."""
        return {
            "status": "success",
            "stats": {
                "total_companies": len(self.companies),
                "total_reviews": len(self.reviews),
                "promoted_jobs": len(self.promoted_jobs),
                "average_rating": round(sum(c["average_rating"] for c in self.companies) / len(self.companies), 1) if self.companies else 0
            }
        }


brand_engine = BrandEngine()