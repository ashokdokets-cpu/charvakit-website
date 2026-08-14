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
                "content": """The IT staffing industry is undergoing its biggest transformation since the rise of job boards. Artificial intelligence is no longer a buzzword — it's the engine driving every stage of talent acquisition.

At Charvak, we've built 19 AI models that handle everything from skill verification to visa compliance. Here's what's changing:

**AI-Powered Screening**
Traditional resume screening is dead. Our Skill-Twin engine assesses candidates on actual abilities — not keywords. This eliminates human bias and cuts screening time from days to minutes.

**Vector-Based Matching**
Semantic matching goes beyond keyword matching. "Spring Boot + Kafka" correctly matches "Senior Java Backend Developer" because the AI understands context.

**Escrow-Protected Payments**
Dokets VouchAI ensures freelancers get paid and companies get work — 1% fee. No disputes, no delays.

**Global Reach**
34 languages and 13 currencies mean talent knows no borders.

The future of staffing is AI-first, and Charvak is leading it.""",
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
                "content": """Getting a US work visa as an Indian developer is complex — but it doesn't have to be confusing. Charvak's North America module handles 17 visa types automatically.

**H-1B (Specialty Occupation)**
The most common visa for IT professionals. Requires a bachelor's degree and employer sponsorship. 85,000 visas annually (65,000 regular + 20,000 master's cap).

**OPT / STEM OPT**
Students on F-1 visas can work for 12 months (36 months for STEM) after graduation. No employer sponsorship needed initially.

**L-1 (Intracompany Transfer)**
For employees transferring to a US office. Requires 1 year of prior employment with the company.

**TN (USMCA)**
For Canadian and Mexican citizens in specific professions including computer systems analysts.

**EAD (All Categories)**
Employment Authorization Document — work permit for spouses, asylum seekers, and other eligible categories.

Charvak's Work Authorization Engine auto-classifies your visa status and checks compliance instantly.""",
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
                "content": """Remote hiring has evolved far beyond posting a job and hoping for the best. In 2026, the best companies use AI-powered platforms to find, verify, and hire global talent.

**Write Clear Role Descriptions**
Vague job posts attract vague candidates. Specify skills, tools, and success metrics.

**Use AI Skill Assessments**
Resumes lie. Skills don't. Use Skill-Twin to verify what candidates can actually do.

**Test Before You Hire**
Micro-internships let candidates prove themselves on real projects before you commit.

**Pay Through Escrow**
Dokets VouchAI protects both parties. Release payment only when work is approved.

**Support Multiple Languages**
With Charvak's 34-language support, you can hire from any country without communication barriers.

**Measure Everything**
Track time-to-hire, candidate quality, and retention. Data beats intuition.""",
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
                "content": """The global IT skills gap costs companies billions annually. By 2026, an estimated 85 million jobs may go unfilled due to skills shortages.

**Identify Your Gaps**
Start with a team skills audit. What technologies do you lack? What's coming in the next 12 months?

**Use AI Assessments**
Skill-Twin evaluates candidates on 20+ technology stacks with verified scores — not self-claimed expertise.

**Create Micro-Learning Paths**
Don't wait for formal training. Assign 2-week micro-internships that build specific skills through real work.

**Verify Progress**
Earn verified badges that prove competency. Share them on LinkedIn for credibility.

**Hire for Adjacent Skills**
A React developer can learn Vue quickly. AI matching finds candidates with transferable skills.

Charvak's Training Engine plus Badge Engine creates a complete upskilling loop.""",
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
                "content": """Payment disputes are the #1 problem in freelancing. 58% of freelancers report being paid late or not at all. Escrow fixes this.

**What is Escrow?**
A neutral third party holds funds until both parties fulfill their obligations. No trust required.

**How Dokets VouchAI Works**
1. Client deposits funds
2. Freelancer delivers work
3. Client reviews and approves
4. Funds released automatically

**1% Fee**
Traditional escrow services charge 5-15%. Dokets VouchAI charges just 1%.

**AI Dispute Resolution**
If there's a disagreement, AI analyzes the work against the original requirements and recommends a fair resolution.

**Global Support**
34 currencies supported. Works in 50+ countries.

Escrow isn't just for freelancers — it's for any transaction where trust matters.""",
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