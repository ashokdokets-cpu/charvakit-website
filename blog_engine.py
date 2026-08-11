"""
Charvak Blog Engine
Simple markdown-based blog with SEO optimization
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
import secrets

logger = logging.getLogger("charvakit.blog")

class BlogEngine:
    """Simple blog system for SEO and content marketing."""
    
    def __init__(self):
        self.posts = self._seed_posts()
        logger.info(f"✅ Blog Engine ready with {len(self.posts)} posts")
    
    def _seed_posts(self) -> List[Dict]:
        """Seed with initial blog posts for SEO."""
        return [
            {
                "id": "ai-staffing-2026",
                "slug": "ai-staffing-trends-2026",
                "title": "How AI is Transforming IT Staffing in 2026",
                "excerpt": "Discover how artificial intelligence is reshaping the IT recruitment landscape with 19 AI models powering the future of hiring.",
                "content": "The IT staffing industry is undergoing a massive transformation...",
                "author": "Charvak Team",
                "category": "AI & Technology",
                "tags": ["AI", "Staffing", "HR Tech", "Future of Work"],
                "image": "/static/images/blog/ai-staffing.jpg",
                "read_time": "5 min",
                "published_at": datetime.now().isoformat(),
                "seo_title": "AI in IT Staffing 2026 | Charvak IT Consulting",
                "seo_description": "Explore how AI-powered staffing solutions are reducing time-to-hire by 60% and cutting costs by 40%."
            },
            {
                "id": "us-visa-guide",
                "slug": "us-work-visa-guide-indian-developers",
                "title": "Complete Guide to US Work Visas for Indian Developers",
                "excerpt": "Navigate H-1B, OPT, CPT, L-1 and 13 other visa types with our comprehensive guide.",
                "content": "Getting a US work visa as an Indian developer can be complex...",
                "author": "Charvak NA Team",
                "category": "North America",
                "tags": ["Visa", "H-1B", "US Jobs", "Immigration"],
                "image": "/static/images/blog/us-visa.jpg",
                "read_time": "8 min",
                "published_at": datetime.now().isoformat(),
                "seo_title": "US Work Visa Guide for Indian Developers 2026 | Charvak",
                "seo_description": "Complete guide to 17 US work visa types for Indian IT professionals. H-1B, OPT, CPT, L-1 explained."
            },
            {
                "id": "remote-hiring",
                "slug": "remote-hiring-best-practices-2026",
                "title": "Remote Hiring Best Practices for 2026",
                "excerpt": "Learn how to build world-class remote teams across 34 languages and 13 currencies.",
                "content": "Remote hiring has evolved significantly...",
                "author": "Charvak Team",
                "category": "Hiring",
                "tags": ["Remote Work", "Global Teams", "Hiring"],
                "image": "/static/images/blog/remote.jpg",
                "read_time": "6 min",
                "published_at": datetime.now().isoformat(),
                "seo_title": "Remote Hiring Best Practices 2026 | Charvak IT Consulting",
                "seo_description": "Master remote hiring across time zones. Best practices for sourcing, interviewing, and onboarding global talent."
            },
            {
                "id": "skill-gap",
                "slug": "bridge-skill-gap-ai-assessment",
                "title": "How to Bridge the Skill Gap with AI-Powered Assessments",
                "excerpt": "Use Skill-Twin and AI assessment tools to identify and close skill gaps in your team.",
                "content": "The global IT skills gap costs companies billions annually...",
                "author": "Charvak Team",
                "category": "Skills & Training",
                "tags": ["Skills", "AI Assessment", "Upskilling"],
                "image": "/static/images/blog/skills.jpg",
                "read_time": "4 min",
                "published_at": datetime.now().isoformat(),
                "seo_title": "Bridge the IT Skill Gap with AI | Charvak Skill-Twin",
                "seo_description": "Close your team's skill gaps with AI-powered assessments. Identify, measure, and upskill your workforce."
            },
            {
                "id": "escrow-payments",
                "slug": "escrow-payments-freelance-safe",
                "title": "Why Escrow Payments Are Essential for Freelance Projects",
                "excerpt": "Protect both clients and freelancers with Dokets VouchAI escrow — just 1% fee.",
                "content": "Payment disputes are the #1 problem in freelancing...",
                "author": "Charvak Team",
                "category": "Business",
                "tags": ["Escrow", "Payments", "Freelance", "Security"],
                "image": "/static/images/blog/escrow.jpg",
                "read_time": "5 min",
                "published_at": datetime.now().isoformat(),
                "seo_title": "Escrow Payments for Safe Freelancing | Dokets VouchAI",
                "seo_description": "Secure your freelance projects with escrow payments. Only 1% fee via Dokets VouchAI. Protect both parties."
            }
        ]
    
    def get_all_posts(self, category: str = None, tag: str = None) -> Dict:
        """Get all blog posts, optionally filtered."""
        posts = self.posts
        if category:
            posts = [p for p in posts if p["category"].lower() == category.lower()]
        if tag:
            posts = [p for p in posts if tag.lower() in [t.lower() for t in p.get("tags", [])]]
        
        return {
            "status": "success",
            "posts": posts,
            "count": len(posts),
            "categories": list(set(p["category"] for p in self.posts)),
            "tags": list(set(t for p in self.posts for t in p.get("tags", [])))
        }
    
    def get_post(self, slug: str) -> Dict:
        """Get a single post by slug."""
        for post in self.posts:
            if post["slug"] == slug:
                # Get related posts
                related = [p for p in self.posts if p["id"] != post["id"] and (
                    p["category"] == post["category"] or 
                    any(t in post["tags"] for t in p["tags"])
                )][:3]
                
                return {
                    "status": "success",
                    "post": post,
                    "related": related
                }
        return {"status": "error", "message": "Post not found"}
    
    def get_sitemap_posts(self) -> List[Dict]:
        """Get posts for sitemap generation."""
        return [
            {"slug": p["slug"], "published_at": p["published_at"], "title": p["seo_title"]}
            for p in self.posts
        ]


blog_engine = BlogEngine()