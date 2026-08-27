from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
import os
import json
import logging
from datetime import datetime, timedelta
import secrets

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from api_sync import (
    handle_resume_sync, handle_application_sync, handle_get_jobs,
    handle_skill_sync, handle_get_status, api_health,
    ResumeSync, ApplicationSync, SkillGapSync, verify_api_key
)
from auth import register_user, login_user, logout_user, logout_all_sessions, verify_token, get_current_user
from database import db
from global_config import detect_user_region, get_pricing, LANGUAGES, CURRENCIES
from ai_service import (
    generate_assessment_questions, voice_to_website, neural_wireframe_to_code,
    localize_website, generate_legal_contract, analyze_legacy_code,
    generate_agent_schema, is_ai_ready
)
from monitor_service import add_monitor, check_all_sites, get_monitor_status
from job_service import job_board
from whatsapp_bot import whatsapp_handler, VERIFY_TOKEN
from na_module.work_auth import work_auth_engine, VisaType
from na_module.vms_connector import vms_connector
from na_module.vector_matcher import vector_matcher
from na_module.resume_engine import pii_redactor, compliance_checker, sub_vendor_manager
from na_module.charvak_vms import charvak_vms, RequisitionStatus
from na_module.revenue_engine import revenue_engine, SubscriptionTier
from tools_ai_backend import (
    resume_roast_ai, ghost_bounty_ai, role_mirror_ai, offer_matcher_ai,
    ghost_job_ai, counter_offer_ai, pitch_roast_ai, ref_check_ai,
    bounty_swap_ai, micro_trial_ai, ref_swap_ai, ghosted_tracker_ai
)
from invoice_engine import invoice_manager, InvoiceStatus
from payment_engine import payment_engine
from kyc_engine import kyc_engine, VerificationStatus, VerificationType
from escrow_engine import escrow_engine, EscrowStatus
from referral_engine import referral_engine
from badge_engine import badge_engine
from blog_engine import blog_engine
from chatbot_engine import chatbot_engine
from sso_engine import sso_engine
from micro_internship_engine import micro_internship_engine
from training_engine import training_engine
from interview_prep_engine import interview_prep_engine
from job_board_engine import job_board_engine
from products_engine import products_engine
from candidate_engine import candidate_engine
from brand_engine import brand_engine
from events_engine import events_engine
from messaging_engine import messaging_engine
from email_engine import email_engine
from university_engine import university_engine
from ats_engine import ats_engine
from team_engine import team_engine
from enterprise_engine import enterprise_engine
from marketing_ai_engine import marketing_ai_engine
from indian_language_ai import indian_language_ai
from lms_engine import lms_engine
from career_v2_engine import career_v2_engine
from micro_internship_global import micro_internship_global
from assessment_report_engine import assessment_report_engine
from security_middleware import security_manager
from bridge_engine import bridge_engine
from ai_bridge_engine import ai_bridge_engine
from student_suite_engine import student_suite_engine
from profile_network_engine import profile_network_engine
from doketsrb_integration import doketsrb_integration
from outreach_engine import outreach_engine
from data_lifecycle import data_lifecycle
from final_year_project_engine import final_year_project_engine
from ai_credit_engine import ai_credit_engine
from notification_engine import notification_engine
from voice_to_web_engine import voice_to_web_engine



# ============================================================
# LOGGING SETUP
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("charvakit")


# ============================================================
# FASTAPI APP INITIALIZATION
# ============================================================
app = FastAPI(
    title="Charvak IT Consulting Pvt Ltd - Web Designing | Staff Augmentation",
    version="1.0.0"
)


# ============================================================
# RATE LIMITING
# ============================================================
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "status": "error",
            "message": "Too many requests. Please wait before trying again.",
            "retry_after": "60 seconds"
        }
    )

# Global rate limit for all page views
@app.middleware("http")
async def global_rate_limit(request: Request, call_next):
    from slowapi.util import get_remote_address
    client_ip = get_remote_address(request)
    if not hasattr(app.state, "view_counts"):
        app.state.view_counts = {}
    
    counts = app.state.view_counts
    now = datetime.now()
    if client_ip in counts:
        if (now - counts[client_ip]["timestamp"]).seconds < 60:
            counts[client_ip]["count"] += 1
            if counts[client_ip]["count"] > 60:
                return JSONResponse({"error": "Too many requests"}, status_code=429)
        else:
            counts[client_ip] = {"count": 1, "timestamp": now}
    else:
        counts[client_ip] = {"count": 1, "timestamp": now}
    
    return await call_next(request)

# ============================================================
# REQUEST SIZE LIMITING MIDDLEWARE
# ============================================================
class MaxBodySizeMiddleware(BaseHTTPMiddleware):
    """Limits request body size to prevent abuse."""
    
    MAX_SIZE = 10_000_000  # 10MB
    
    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > self.MAX_SIZE:
                    logger.warning(f"Request too large: {content_length} bytes from {request.client.host}")
                    return JSONResponse(
                        status_code=413,
                        content={
                            "status": "error",
                            "message": f"Request body too large. Maximum size is {self.MAX_SIZE // 1_000_000}MB."
                        }
                    )
            except ValueError:
                pass
        return await call_next(request)

app.add_middleware(MaxBodySizeMiddleware)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self' * data: blob:; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://checkout.razorpay.com https://cdn.razorpay.com https://www.paypal.com https://www.googletagmanager.com https://www.google-analytics.com; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com https://cdn.razorpay.com; img-src 'self' data: blob: https: *; font-src 'self' https://cdn.jsdelivr.net https://fonts.gstatic.com; connect-src 'self' https://api.openai.com https://www.google-analytics.com https://cdn.jsdelivr.net https://checkout.razorpay.com https://api.razorpay.com https://lumberjack.razorpay.com https://www.paypal.com; frame-src 'self' https://api.razorpay.com https://www.paypal.com https://checkout.razorpay.com; frame-ancestors 'self'"
        return response

app.add_middleware(SecurityHeadersMiddleware)


# ============================================================
# CORS - RESTRICTED ORIGINS
# ============================================================
app.add_middleware(
    CORSMiddleware,
        allow_origins=[
        "https://www.doketsrb.com",
        "https://doketsrb.com",
        "https://www.charvakit.com",
        "https://charvakit.com",
        "https://charvakit-website.onrender.com",
        "http://localhost:3000",
        "http://localhost:5500",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5500"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Explicit, not wildcard
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],  # Explicit, not wildcard
)


# ============================================================
# STATIC FILES & TEMPLATES
# ============================================================
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# ============================================================
# PYDANTIC MODELS FOR INPUT VALIDATION
# ============================================================

class VoiceToWebRequest(BaseModel):
    transcript: str = Field(..., min_length=1, max_length=5000)
    language: str = Field(default="en", min_length=2, max_length=5)
    
    @field_validator('language')
    @classmethod
    def validate_language(cls, v: str) -> str:
        if not v or len(v) < 2:
            return "en"
        return v[:5]


class NeuralWireframeRequest(BaseModel):
    sketch: str = Field(..., min_length=1, max_length=10000)


class LocalizeRequest(BaseModel):
    url: str = Field(..., min_length=1, max_length=500)
    language: str = Field(default="en", min_length=2, max_length=5)


class GenerateContractRequest(BaseModel):
    company: str = Field(..., min_length=1, max_length=200)
    country: str = Field(..., min_length=1, max_length=100)
    service: str = Field(..., min_length=1, max_length=500)


class AnalyzeLegacyRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=50000)


class GenerateSchemaRequest(BaseModel):
    url: str = Field(..., min_length=1, max_length=500)


class GenerateQuestionsRequest(BaseModel):
    stack: str = Field(default="Python", max_length=100)
    difficulty: str = Field(default="Intermediate", max_length=50)
    count: int = Field(default=10, ge=1, le=50)


class AddMonitorRequest(BaseModel):
    url: str = Field(..., min_length=1, max_length=500)
    name: str = Field(default="", max_length=200)
    interval: int = Field(default=300, ge=60, le=86400)


class VerifyWorkAuthRequest(BaseModel):
    visa_input: str = Field(..., min_length=1, max_length=200)
    candidate_id: Optional[str] = None
    visa_expiry: Optional[str] = None
    documents_verified: bool = False
    client_type: str = Field(default="corporate", max_length=100)


class IngestJobRequest(BaseModel):
    source: str = Field(default="direct", max_length=50)
    title: Optional[str] = None
    description: Optional[str] = None
    skills: Optional[List[str]] = None
    location: Optional[str] = None


class SubmitCandidateRequest(BaseModel):
    candidate_id: str = Field(..., min_length=1, max_length=100)
    visa_input: str = Field(..., min_length=1, max_length=200)
    visa_expiry: Optional[str] = None
    documents_verified: bool = False
    client_type: str = Field(default="corporate", max_length=100)
    job_id: str = Field(..., min_length=1, max_length=100)
    vendor_id: str = Field(default="NA-VENDOR-001", max_length=100)


class MatchCandidateRequest(BaseModel):
    id: Optional[str] = None
    skills: Optional[List[str]] = None
    title: Optional[str] = None


class CreateRequisitionRequest(BaseModel):
    client_id: str = Field(default="CLIENT-001", max_length=100)
    title: Optional[str] = None
    description: Optional[str] = None
    skills: Optional[List[str]] = None
    location: Optional[str] = None


class SubmitTimecardRequest(BaseModel):
    req_id: str = Field(..., min_length=1, max_length=100)
    candidate_id: str = Field(..., min_length=1, max_length=100)
    hours: float = Field(..., ge=0, le=168)
    period_end: Optional[str] = None
    rate: float = Field(default=0, ge=0)


class ApproveTimecardRequest(BaseModel):
    timecard_id: str = Field(..., min_length=1, max_length=100)


class CreateSubscriptionRequest(BaseModel):
    firm_id: str = Field(..., min_length=1, max_length=100)
    tier: str = Field(default="STARTER", max_length=50)


class RegisterVendorRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    email: str = Field(..., max_length=200)
    company: Optional[str] = None


class ResumeRoastRequest(BaseModel):
    resume: str = Field(..., min_length=1, max_length=10000)
    job_title: str = Field(default="", max_length=200)


class GhostBountyRequest(BaseModel):
    challenge: str = Field(default="Debug", max_length=500)


class RoleMirrorRequest(BaseModel):
    role: str = Field(default="", max_length=200)
    skills: str = Field(default="", max_length=2000)


class OfferMatcherRequest(BaseModel):
    offer_a: str = Field(default="", max_length=5000)
    offer_b: str = Field(default="", max_length=5000)


class GhostJobRequest(BaseModel):
    url: str = Field(default="", max_length=500)


class CounterOfferRequest(BaseModel):
    new_salary: float = Field(default=0, ge=0)
    counter_salary: float = Field(default=0, ge=0)


class PitchRoastRequest(BaseModel):
    inmail: str = Field(default="", max_length=5000)


class RefCheckRequest(BaseModel):
    ref_names: List[str] = Field(default_factory=list, max_length=10)


class ContactRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    email: str = Field(..., max_length=200)
    phone: str = Field(default="", max_length=20)
    subject: str = Field(default="", max_length=200)
    message: str = Field(..., min_length=1, max_length=5000)


class RegisterRequest(BaseModel):
    email: str = Field(..., max_length=200)
    password: str = Field(..., min_length=8, max_length=100)
    name: str = Field(..., min_length=1, max_length=200)
    role: str = Field(default="candidate", max_length=50)
    phone: Optional[str] = None


class LoginRequest(BaseModel):
    email: str = Field(..., max_length=200)
    password: str = Field(..., max_length=100)


class LogoutRequest(BaseModel):
    token: str = Field(..., max_length=500)


class JobPostRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    company: str = Field(..., min_length=1, max_length=200)
    type: str = Field(default="Permanent", max_length=50)
    location: str = Field(default="Remote", max_length=200)
    salary: str = Field(default="", max_length=100)
    description: str = Field(default="", max_length=10000)
    skills: str = Field(default="", max_length=1000)


class ApplicationAddRequest(BaseModel):
    job_title: str = Field(..., min_length=1, max_length=200)
    company: str = Field(..., min_length=1, max_length=200)
    job_url: str = Field(default="", max_length=500)
    source: str = Field(default="charvakit", max_length=50)


class SignAgreementRequest(BaseModel):
    agreement_type: str = Field(..., max_length=50)
    client_name: str = Field(..., min_length=1, max_length=200)
    email: Optional[str] = None
    signature_data: Optional[Dict[str, Any]] = None


class CreateInvoiceRequest(BaseModel):
    client_name: str = Field(..., min_length=1, max_length=200)
    client_email: str = Field(..., max_length=200)
    service_type: str = Field(default="Other", max_length=100)
    amount: float = Field(..., gt=0)
    description: str = Field(default="", max_length=2000)


class UpdateInvoiceRequest(BaseModel):
    invoice_id: str = Field(..., max_length=100)
    action: str = Field(..., max_length=20)
    reason: str = Field(default="", max_length=500)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def require_auth(request: Request) -> Dict:
    """Authenticate user from Bearer token. Raises 401 if invalid."""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        raise HTTPException(status_code=401, detail="Authorization header required")
    user = get_current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user


ADMIN_EMAIL = "hr@charvakit.com"

def require_admin(request: Request) -> Dict:
    """Authenticate and ensure user is admin."""
    if user.get("role") != "admin" and user.get("email") != ADMIN_EMAIL:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


def handle_error(e: Exception, operation: str, default_return: Any = None) -> Dict:
    """Centralized error handling with logging."""
    logger.error(f"Error during {operation}: {str(e)}", exc_info=True)
    if default_return is not None:
        return default_return
    return {"status": "error", "message": f"Failed during {operation}. Please try again."}


def template_response(template_name: str, request: Request, title: str, **extra_context) -> HTMLResponse:
    """Helper to reduce boilerplate for template responses."""
    return templates.TemplateResponse(
        template_name,
        {"request": request, "title": title, **extra_context}
    )


# ============================================================
# CORE PAGE ROUTES
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return template_response("index.html", request, "Charvak IT Consulting Pvt Ltd - Web Designing | Staff Augmentation")

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return template_response("about.html", request, "About Charvak IT Consulting Pvt Ltd")

@app.get("/services", response_class=HTMLResponse)
async def services(request: Request):
    services_data = [
        {
            "name": "Web Designing",
            "description": "Future-focused and intuitive websites and custom applications",
            "features": ["Responsive Design", "Custom Web Applications", "E-commerce Solutions", "UI/UX Design"],
            "link": "/services/web-design",
            "icon": "code",
            "image": "/static/images/web-design.png"
        },
        {
            "name": "Staff Augmentation",
            "description": "End-to-end IT staffing solutions for your business",
            "features": ["Top Ranked Candidates", "Best Screening Tools", "Cost-Effective", "Quick Turnaround"],
            "link": "/services/staff-augmentation",
            "icon": "people",
            "image": "/static/images/teamwork.png"
        },
        {
            "name": "Dokets VouchAI",
            "description": "AI-powered escrow platform with intelligent payment protection",
            "features": ["1% Transaction Fee", "WhatsApp Integration", "34 Languages", "13 Currencies", "AI Dispute Resolution"],
            "link": "/products/dokets-vouchai",
            "icon": "shield-check",
            "highlight": True
        }
    ]
    return template_response("services.html", request, "Our Services", services=services_data)

@app.get("/services/web-design", response_class=HTMLResponse)
async def web_design(request: Request):
    return template_response("web-design.html", request, "Web Designing Services")

@app.get("/services/staff-augmentation", response_class=HTMLResponse)
async def staff_augmentation(request: Request):
    return template_response("staff-augmentation.html", request, "Staff Augmentation Services")

@app.get("/products", response_class=HTMLResponse)
async def products(request: Request):
    products_data = [
        {"name": "Dokets VouchAI", "description": "AI-powered escrow platform", "features": ["1% Fee", "34 Languages", "13 Currencies", "WhatsApp"], "link": "/products/dokets-vouchai", "icon": "shield-check", "badge": "Featured"},
        {"name": "Dokets Shop", "description": "Modern e-commerce store solution", "features": ["Easy Setup", "Secure Payments", "Inventory", "Mobile Ready"], "link": "https://dokets.shop", "icon": "cart", "badge": "New"},
        {"name": "Dokets RB", "description": "AI-powered resume builder", "features": ["AI Templates", "ATS-Friendly", "Quick Export", "Multiple Formats"], "link": "https://doketsrb.com", "icon": "file-text", "badge": "New"},
        {"name": "Voice-to-Web", "description": "Voice → Live Website in 3 minutes", "features": ["WhatsApp Bot", "34 Languages", "Free Build", "Pro Hosting"], "link": "/voice-to-web", "icon": "mic"},
        {"name": "Lock-In Breaker", "description": "Cloud cost optimization engine", "features": ["Cloud Audit", "Migration Scripts", "30-50% Savings", "24/7 Monitor"], "link": "/lock-in-breaker", "icon": "lock"},
        {"name": "Reverse Staffing", "description": "Build projects → Get verified → Get hired", "features": ["AI Code Review", "Verified Portfolio", "48hr Placement", "Zero Risk"], "link": "/reverse-staffing", "icon": "people"},
        {"name": "AuditBot", "description": "AI security & code health scanner", "features": ["OWASP Scan", "Auto-Fix Patches", "WCAG Check", "10min Scan"], "link": "/auditbot", "icon": "shield"},
        {"name": "Neural Wireframe", "description": "Sketch → Production React/Tailwind code", "features": ["Hand-Drawn Input", "AI Vision", "Instant Deploy", "Responsive"], "link": "/neural-wireframe", "icon": "pencil"},
        {"name": "Skill-Twin", "description": "AI simulation → Verified skill scorecard", "features": ["AI Assessment", "Verified Badge", "LinkedIn Share", "20+ Stacks"], "link": "/skill-twin", "icon": "robot"},
        {"name": "Globalize.ai", "description": "Instant website localization", "features": ["34 Languages", "Cultural Adapt", "Auto-Compliance", "1 Script Tag"], "link": "/globalize", "icon": "globe"},
        {"name": "Micro-Squads", "description": "14-day AI+Human sprint teams", "features": ["72hr Assembly", "AI Managed", "Outcome Pay", "14-Day Sprint"], "link": "/micro-squads", "icon": "calendar-check"},
        {"name": "Agency-Twin", "description": "AI COO for freelancers", "features": ["Auto-Scoping", "Task Delegation", "Auto-Invoicing", "Talent Pool"], "link": "/agency-twin", "icon": "envelope"},
        {"name": "Geo-Compliance Shield", "description": "Cross-border contracts + payouts", "features": ["50+ Countries", "Auto-Contracts", "Escrow Protected", "13 Currencies"], "link": "/geo-compliance", "icon": "file-text"},
        {"name": "Design-Token Sentinel", "description": "Figma ↔ GitHub brand sync", "features": ["Figma Sync", "Auto PRs", "Multi-Domain", "WCAG Check"], "link": "/design-token-sentinel", "icon": "palette"},
        {"name": "Legacy-Shift", "description": "Old code → Next.js Jamstack", "features": ["Legacy Parse", "Auto-Convert", "10x Faster", "Auto-Tested"], "link": "/legacy-shift", "icon": "clock-history"},
        {"name": "Agent-Ready Wrapper", "description": "JSON-LD → AI agent storefront", "features": ["Structured Data", "Micro-APIs", "Auto-Sync", "AI Commerce"], "link": "/agent-ready", "icon": "cpu"},
        {"name": "Silent-Killer Sentinel", "description": "24/7 monitoring & auto-fix for webhooks", "features": ["5-Min Checks", "Instant Alerts", "Auto-Hotfix"], "link": "/silent-killer", "icon": "activity"},
        {"name": "AI-Slop Quarantine", "description": "Clean AI-generated code bloat & WCAG errors", "features": ["De-Bloat", "Fix Layouts", "WCAG Fix"], "link": "/ai-slop-quarantine", "icon": "recycle"},
        {"name": "Developer Entropy Engine", "description": "Track team skill decay & upskill", "features": ["Code Quality", "Skill Gaps", "Auto-Learning"], "link": "/developer-entropy", "icon": "graph-down"},
    ]
    return template_response("products-list.html", request, "All Products - Charvak", products=products_data)

@app.get("/products/dokets-vouchai", response_class=HTMLResponse)
async def dokets_vouchai(request: Request):
    product = {
        "name": "Dokets VouchAI",
        "tagline": "AI-Powered Escrow Platform",
        "description": "Secure your transactions with intelligent escrow protection",
        "fee": "1%",
        "features": {
            "languages": 34,
            "currencies": 13,
            "integration": "WhatsApp",
            "ai_features": ["Smart Contract Analysis", "Automated Dispute Resolution", "Risk Assessment", "Fraud Detection"]
        },
        "website": "https://dokets.com"
    }
    return template_response("products.html", request, "Dokets VouchAI - AI Escrow Platform", product=product)

@app.get("/team", response_class=HTMLResponse)
async def team(request: Request):
    return template_response("team.html", request, "Our Team")

@app.get("/careers", response_class=HTMLResponse)
async def careers(request: Request):
    return template_response("careers.html", request, "Careers at Charvak")

@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    return template_response("contact.html", request, "Contact Us")

@app.get("/terms", response_class=HTMLResponse)
async def terms(request: Request):
    return template_response("terms.html", request, "Terms & Conditions")

@app.get("/privacy", response_class=HTMLResponse)
async def privacy(request: Request):
    return template_response("privacy.html", request, "Privacy Policy")

@app.get("/refund", response_class=HTMLResponse)
async def refund(request: Request):
    return template_response("refund.html", request, "Refund & Cancellation Policy")

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return template_response("register.html", request, "Register - Charvak IT Consulting")

@app.get("/roadmap", response_class=HTMLResponse)
async def roadmap(request: Request):
    return template_response("roadmap.html", request, "Roadmap - Charvak IT Consulting")


# ============================================================
# AI MODEL PAGES (25+ models)
# ============================================================

@app.get("/voice-to-web", response_class=HTMLResponse)
async def voice_to_web(request: Request):
    return template_response("voice-to-web.html", request, "Voice-to-Web Engine - Charvak")

@app.get("/cloud-waste-calculator", response_class=HTMLResponse)
async def cloud_waste_calculator(request: Request):
    return template_response("cloud-waste-calculator.html", request, "Cloud Waste Calculator - Charvak")

@app.get("/lock-in-breaker", response_class=HTMLResponse)
async def lock_in_breaker(request: Request):
    return template_response("lock-in-breaker.html", request, "Vendor Lock-In Breaker - Charvak")

@app.get("/lock-in-breaker-pricing", response_class=HTMLResponse)
async def lock_in_breaker_pricing(request: Request):
    return template_response("lock-in-breaker-pricing.html", request, "Lock-In Breaker Plans - Charvak")

@app.get("/reverse-staffing", response_class=HTMLResponse)
async def reverse_staffing(request: Request):
    return template_response("reverse-staffing.html", request, "Reverse Staffing - Charvak")

@app.get("/code-quality-checker", response_class=HTMLResponse)
async def code_quality_checker(request: Request):
    return template_response("code-quality-checker.html", request, "Code Quality Checker - Charvak")

@app.get("/developer-signup", response_class=HTMLResponse)
async def developer_signup(request: Request):
    return template_response("developer-signup.html", request, "Join Developer Pool - Charvak")

@app.get("/hire-talent", response_class=HTMLResponse)
async def hire_talent(request: Request):
    return template_response("hire-talent.html", request, "Hire Vetted Talent - Charvak")

@app.get("/auditbot", response_class=HTMLResponse)
async def auditbot(request: Request):
    return template_response("auditbot.html", request, "AuditBot - Charvak")

@app.get("/digital-health-checker", response_class=HTMLResponse)
async def digital_health_checker(request: Request):
    return template_response("digital-health-checker.html", request, "Digital Health Checker - Charvak")

@app.get("/neural-wireframe", response_class=HTMLResponse)
async def neural_wireframe(request: Request):
    return template_response("neural-wireframe.html", request, "Neural Wireframe-to-Prod - Charvak")

@app.get("/napkin-challenge", response_class=HTMLResponse)
async def napkin_challenge(request: Request):
    return template_response("napkin-challenge.html", request, "Napkin-to-Live Challenge - Charvak")

@app.get("/skill-twin", response_class=HTMLResponse)
async def skill_twin(request: Request):
    return template_response("skill-twin.html", request, "Skill-Twin Engine - Charvak")

@app.get("/skill-check", response_class=HTMLResponse)
async def skill_check(request: Request):
    return template_response("skill-check.html", request, "Free Skill Check - Charvak")

@app.get("/globalize", response_class=HTMLResponse)
async def globalize_ai(request: Request):
    return template_response("globalize.html", request, "Globalize.ai - Charvak")

@app.get("/revenue-leak-detector", response_class=HTMLResponse)
async def revenue_leak_detector(request: Request):
    return template_response("revenue-leak-detector.html", request, "Revenue Leak Detector - Charvak")

@app.get("/micro-squads", response_class=HTMLResponse)
async def micro_squads(request: Request):
    return template_response("micro-squads.html", request, "Micro-Squads - Charvak")

@app.get("/scope-simulator", response_class=HTMLResponse)
async def scope_simulator(request: Request):
    return template_response("scope-simulator.html", request, "Scope Simulator - Charvak")

@app.get("/agency-twin", response_class=HTMLResponse)
async def agency_twin(request: Request):
    return template_response("agency-twin.html", request, "Agency-Twin - Charvak")

@app.get("/burnout-calculator", response_class=HTMLResponse)
async def burnout_calculator(request: Request):
    return template_response("burnout-calculator.html", request, "Burnout Calculator - Charvak")

@app.get("/geo-compliance", response_class=HTMLResponse)
async def geo_compliance(request: Request):
    return template_response("geo-compliance.html", request, "Geo-Compliance Shield - Charvak")

@app.get("/contract-risk-radar", response_class=HTMLResponse)
async def contract_risk_radar(request: Request):
    return template_response("contract-risk-radar.html", request, "Contract Risk Radar - Charvak")

@app.get("/design-token-sentinel", response_class=HTMLResponse)
async def design_token_sentinel(request: Request):
    return template_response("design-token-sentinel.html", request, "Design-Token Sentinel - Charvak")

@app.get("/brand-drift-inspector", response_class=HTMLResponse)
async def brand_drift_inspector(request: Request):
    return template_response("brand-drift-inspector.html", request, "Brand Drift Inspector - Charvak")

@app.get("/legacy-shift", response_class=HTMLResponse)
async def legacy_shift(request: Request):
    return template_response("legacy-shift.html", request, "Legacy-Shift Archaeologist - Charvak")

@app.get("/time-machine-checker", response_class=HTMLResponse)
async def time_machine_checker(request: Request):
    return template_response("time-machine-checker.html", request, "Time Machine Checker - Charvak")

@app.get("/agent-ready", response_class=HTMLResponse)
async def agent_ready(request: Request):
    return template_response("agent-ready.html", request, "Agent-Ready Wrapper - Charvak")

@app.get("/ai-commerce-scorecard", response_class=HTMLResponse)
async def ai_commerce_scorecard(request: Request):
    return template_response("ai-commerce-scorecard.html", request, "AI Commerce Scorecard - Charvak")

@app.get("/silent-killer", response_class=HTMLResponse)
async def silent_killer(request: Request):
    return template_response("silent-killer.html", request, "Silent-Killer Sentinel - Charvak")

@app.get("/dead-link-auditor", response_class=HTMLResponse)
async def dead_link_auditor(request: Request):
    return template_response("dead-link-auditor.html", request, "Dead Link Auditor - Charvak")

@app.get("/ai-slop-quarantine", response_class=HTMLResponse)
async def ai_slop_quarantine(request: Request):
    return template_response("ai-slop-quarantine.html", request, "AI-Slop Quarantine - Charvak")

@app.get("/ai-contamination-detector", response_class=HTMLResponse)
async def ai_contamination_detector(request: Request):
    return template_response("ai-contamination-detector.html", request, "AI-Contamination Detector - Charvak")

@app.get("/developer-entropy", response_class=HTMLResponse)
async def developer_entropy(request: Request):
    return template_response("developer-entropy.html", request, "Developer Entropy Engine - Charvak")

@app.get("/team-entropy-scorecard", response_class=HTMLResponse)
async def team_entropy_scorecard(request: Request):
    return template_response("team-entropy-scorecard.html", request, "Team Entropy Scorecard - Charvak")

@app.get("/ai-generate-stack", response_class=HTMLResponse)
async def ai_generate_stack(request: Request):
    # Note: This page now uses the unified skill-check template
    return template_response("skill-check.html", request, "Skill Check - Charvak")


# ============================================================
# CAREER ENGINE PAGES
# ============================================================

@app.get("/career-engine", response_class=HTMLResponse)
async def career_engine(request: Request):
    return template_response("career-engine.html", request, "Career Engine - Charvak")

@app.get("/interview-prep", response_class=HTMLResponse)
async def interview_prep(request: Request):
    return template_response("interview-prep.html", request, "Interview Prep - Charvak Career Engine")

@app.get("/post-job", response_class=HTMLResponse)
async def post_job(request: Request):
    return template_response("post-job.html", request, "Post a Job - Charvak")

@app.get("/track-application", response_class=HTMLResponse)
async def track_application(request: Request):
    return template_response("track-application.html", request, "Track Application - Charvak")

@app.get("/submit-referral", response_class=HTMLResponse)
async def submit_referral(request: Request):
    return template_response("submit-referral.html", request, "Submit Referral - Charvak")

@app.get("/training-engine", response_class=HTMLResponse)
async def training_engine_page(request: Request):
    return template_response("training-engine.html", request, "Training Engine - Charvak Career Engine")

@app.get("/online-classroom", response_class=HTMLResponse)
async def online_classroom(request: Request):
    return template_response("online-classroom.html", request, "Online Classroom - Charvak")

@app.get("/background-verification", response_class=HTMLResponse)
async def background_verification(request: Request):
    return template_response("background-verification.html", request, "Background Verification - Charvak Career Engine")

@app.get("/job-board", response_class=HTMLResponse)
async def job_board_page(request: Request):
    return template_response("job-board.html", request, "Job Board - Charvak Career Engine")

@app.get("/application-dashboard", response_class=HTMLResponse)
async def application_dashboard(request: Request):
    return template_response("application-dashboard.html", request, "Application Dashboard - Charvak")

@app.get("/micro-internship", response_class=HTMLResponse)
async def micro_internship(request: Request):
    return template_response("micro-internship.html", request, "Micro-Internships - Charvak First Job Engine")

@app.get("/for-employers", response_class=HTMLResponse)
async def for_employers(request: Request):
    return template_response("for-employers.html", request, "For Employers - Charvak IT Consulting")

@app.get("/demo", response_class=HTMLResponse)
async def demo_page(request: Request):
    # Fixed: Now points to a proper demo template if it exists, otherwise employers page
    return template_response("for-employers.html", request, "Demo - Charvak IT Consulting")

@app.get("/for-candidates", response_class=HTMLResponse)
async def for_candidates(request: Request):
    return template_response("for-candidates.html", request, "For Candidates - Charvak IT Consulting")

@app.get("/post-micro-project", response_class=HTMLResponse)
async def post_micro_project(request: Request):
    return template_response("post-micro-project.html", request, "Post a Micro-Project - Charvak")

@app.get("/badge", response_class=HTMLResponse)
async def badge_page(request: Request):
    return template_response("badge.html", request, "Your Verified Badge - Charvak")

@app.get("/admin-dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Redirect to Admin Control Center."""
    return template_response("admin-unified.html", request, "Admin Control Center - Charvak")

@app.get("/staff-augmentation/proposal", response_class=HTMLResponse)
async def staff_augmentation_proposal(request: Request):
    """Staff augmentation proposal page."""
    return template_response("staff-augmentation-proposal.html", request, "Get Staffing Solutions - Charvak")


# ============================================================
# OTHER PAGES
# ============================================================

@app.get("/cookie-policy", response_class=HTMLResponse)
async def cookie_policy(request: Request):
    return template_response("cookie-policy.html", request, "Cookie Policy - Charvak")

@app.get("/accessibility", response_class=HTMLResponse)
async def accessibility(request: Request):
    return template_response("accessibility.html", request, "Accessibility Statement - Charvak")

@app.get("/post-course", response_class=HTMLResponse)
async def post_course(request: Request):
    return template_response("post-course.html", request, "Post Your Course - Charvak")

@app.get("/request-training", response_class=HTMLResponse)
async def request_training(request: Request):
    return template_response("request-training.html", request, "Request Training - Charvak")

@app.get("/partner-verification", response_class=HTMLResponse)
async def partner_verification(request: Request):
    return template_response("partner-verification.html", request, "Partner With Us - Charvak")

@app.get("/custom-assessment", response_class=HTMLResponse)
async def custom_assessment(request: Request):
    return template_response("custom-assessment.html", request, "Custom Assessment - Charvak Skill-Twin")

@app.get("/pricing", response_class=HTMLResponse)
async def pricing_page(request: Request):
    return template_response("pricing.html", request, "Pricing - Charvak IT Consulting")


# ============================================================
# WHATSAPP WEBHOOK
# ============================================================

@app.get("/webhook/whatsapp")
async def verify_whatsapp(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    
    if not VERIFY_TOKEN:
        logger.error("WhatsApp VERIFY_TOKEN is not configured")
        return JSONResponse({"error": "WhatsApp not configured"}, status_code=500)
    
    if mode == "subscribe" and token == VERIFY_TOKEN:
        logger.info("WhatsApp webhook verified successfully")
        return PlainTextResponse(challenge)
    
    logger.warning(f"WhatsApp verification failed: mode={mode}, token_match={token == VERIFY_TOKEN}")
    return JSONResponse({"error": "Verification failed"}, status_code=403)


@app.post("/webhook/whatsapp")
async def receive_whatsapp(request: Request):
    try:
        data = await request.json()
        await whatsapp_handler(data)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"WhatsApp webhook error: {str(e)}", exc_info=True)
        return {"status": "error", "message": "Failed to process WhatsApp message"}


# ============================================================
# GENERATED SITES
# ============================================================

@app.get("/sites/{site_id}")
async def view_site(site_id: str):
    # Validate site_id to prevent path traversal
    if ".." in site_id or "/" in site_id or "\\" in site_id:
        raise HTTPException(status_code=400, detail="Invalid site ID")
    
    site_path = f"static/sites/{site_id}.html"
    if os.path.exists(site_path):
        return FileResponse(site_path)
    return HTMLResponse("<h1>Site not found</h1>", status_code=404)


# ============================================================
# API SYNC ENDPOINTS (DoketsRB Integration)
# ============================================================

@app.post("/api/sync/resume")
async def sync_resume(data: ResumeSync, request: Request, auth=Depends(verify_api_key)):
    return await handle_resume_sync(data, request)

@app.post("/api/sync/application")
async def sync_application(data: ApplicationSync, request: Request, auth=Depends(verify_api_key)):
    return await handle_application_sync(data, request)

@app.get("/api/sync/jobs")
async def sync_get_jobs(request: Request, auth=Depends(verify_api_key)):
    return await handle_get_jobs(request)

@app.post("/api/sync/skills")
async def sync_skills(data: SkillGapSync, request: Request, auth=Depends(verify_api_key)):
    return await handle_skill_sync(data, request)

@app.get("/api/sync/status/{user_id}")
async def sync_get_status(user_id: str, request: Request, auth=Depends(verify_api_key)):
    return await handle_get_status(user_id, request)

@app.get("/api/sync/health")
async def sync_health():
    return await api_health()


# ============================================================
# AUTH ROUTES (WITH INPUT VALIDATION)
# ============================================================

@app.post("/api/auth/register")
async def api_register(data: RegisterRequest):
    try:
        result = register_user(
            email=data.email,
            password=data.password,
            name=data.name,
            role=data.role,
            phone=data.phone
        )
        return JSONResponse(result)
    except Exception as e:
        logger.error(f"Registration failed for {data.email}: {str(e)}")
        return JSONResponse(
            {"status": "error", "message": "Registration failed. Please try again."},
            status_code=500
        )

@app.post("/api/auth/login")
@limiter.limit("5/minute")
async def api_login(request: Request, data: LoginRequest):
    try:
        result = login_user(data.email, data.password)
        return JSONResponse(result)
    except Exception as e:
        logger.error(f"Login failed for {data.email}: {str(e)}")
        return JSONResponse(
            {"status": "error", "message": "Login failed. Check your credentials."},
            status_code=401
        )

@app.post("/api/auth/logout")
async def api_logout(data: LogoutRequest):
    try:
        result = logout_user(data.token)
        return JSONResponse(result)
    except Exception as e:
        logger.error(f"Logout failed: {str(e)}")
        return JSONResponse({"status": "success", "message": "Logged out"})

@app.post("/api/auth/logout-all")
async def api_logout_all(request: Request):
    """Logout from all sessions."""
    try:
        user = require_auth(request)
        result = logout_all_sessions(user["user_id"])
        return JSONResponse(result)
    except HTTPException:
        return JSONResponse({"status": "error", "message": "Not authenticated"}, status_code=401)

@app.get("/api/auth/me")
async def api_me(request: Request):
    try:
        user = require_auth(request)
        return JSONResponse({"status": "success", "user": user})
    except HTTPException:
        return JSONResponse({"status": "error", "message": "Not authenticated"}, status_code=401)


# ============================================================
# CONTACT FORM (WITH VALIDATION)
# ============================================================

@app.post("/api/contact")
async def submit_contact(data: ContactRequest):
    try:
        result = db.save_contact(
            name=data.name,
            email=data.email,
            phone=data.phone,
            subject=data.subject,
            message=data.message
        )
    except Exception:
        result = {"status": "success", "message": "Message received"}
    
    # Send email notification to admin
    try:
        email_engine.notify_admin(
            subject=f"New Contact: {data.subject}",
            message=f"Name: {data.name}\nEmail: {data.email}\nPhone: {data.phone}\n\nMessage: {data.message}"
        )
    except Exception as e:
        logger.error(f"Email notification failed: {e}")
    
    return JSONResponse({"status": "success", "message": "Message sent successfully!"})


# ============================================================
# JOB BOARD API ENDPOINTS (Database-backed)
# ============================================================

@app.post("/api/jobs/post")
async def api_post_job(data: JobPostRequest, request: Request):
    try:
        user = require_auth(request)
    except HTTPException:
        return JSONResponse({"status": "error", "message": "Login required to post jobs"}, status_code=401)
    
    try:
        result = job_board_engine.post_job({
            "title": data.title,
            "company": data.company,
            "job_type": data.type,
            "location": data.location,
            "salary": data.salary,
            "description": data.description,
            "skills": data.skills.split(",") if data.skills else [],
            "posted_by": user["user_id"]
        })
        return JSONResponse(result)
    except Exception as e:
        logger.error(f"Job post failed: {str(e)}")
        return JSONResponse({"status": "error", "message": "Failed to post job"}, status_code=500)

@app.post("/api/applications/add")
async def api_add_application(data: ApplicationAddRequest, request: Request):
    try:
        user = require_auth(request)
    except HTTPException:
        return JSONResponse({"status": "error", "message": "Login required"}, status_code=401)
    
    try:
        result = job_board_engine.apply_to_job({
            "job_id": data.job_title,  # Temporary mapping
            "user_id": user["user_id"],
            "resume_url": data.job_url
        })
        return JSONResponse(result)
    except Exception as e:
        logger.error(f"Application add failed: {str(e)}")
        return JSONResponse({"status": "error", "message": "Failed to add application"}, status_code=500)

@app.get("/api/applications")
async def api_get_applications(request: Request):
    try:
        user = require_auth(request)
    except HTTPException:
        return JSONResponse({"status": "error", "message": "Login required"}, status_code=401)
    
    try:
        apps = job_board_engine.get_applications()
        user_apps = [a for a in apps if a.get("user_id") == user["user_id"]]
        return JSONResponse({"status": "success", "applications": user_apps, "count": len(user_apps)})
    except Exception as e:
        logger.error(f"Failed to get applications: {str(e)}")
        return JSONResponse({"status": "error", "applications": [], "count": 0})

@app.get("/api/jobs")
async def api_get_jobs():
    try:
        jobs = job_board_engine.get_jobs()
        return JSONResponse({"status": "success", "jobs": jobs, "count": len(jobs)})
    except Exception as e:
        logger.error(f"Failed to get jobs: {str(e)}")
        return JSONResponse({"status": "error", "jobs": [], "count": 0})

@app.get("/api/jobs/search")
async def api_search_jobs(type: str = None, location: str = None, keyword: str = None):
    try:
        filters = {}
        if type: filters['type'] = type
        if location: filters['location'] = location
        if keyword: filters['keyword'] = keyword
        jobs = job_board_engine.get_jobs(filters)
        return {"jobs": jobs, "count": len(jobs)}
    except Exception as e:
        logger.error(f"Job search failed: {str(e)}")
        return {"jobs": [], "count": 0, "error": "Search failed"}

@app.post("/api/jobs/apply")
async def api_apply_job(request: Request):
    try:
        data = await request.json()
        result = job_board_engine.apply_to_job(data)
        
        # Notify candidate via email (if email provided)
        if result["status"] == "success" and data.get("email"):
            email_engine.notify_application_received(
                candidate_email=data.get("email", ""),
                candidate_name=data.get("name", ""),
                job_title=data.get("job_title", "the position"),
                company=data.get("company", "the company")
            )
        
        return result
    except Exception as e:
        logger.error(f"Job apply failed: {str(e)}")
        return {"status": "error", "message": "Failed to save application"}

@app.get("/api/jobs/stats")
async def api_job_stats():
    try:
        return job_board_engine.get_stats()
    except Exception as e:
        logger.error(f"Failed to get job stats: {str(e)}")
        return {"active_jobs": 0, "total_applications": 0, "companies": 0, "locations": 0}

@app.get("/api/jobs/applications")
async def api_get_applications_list(job_id: str = None):
    try:
        apps = job_board_engine.get_applications(job_id)
        return {"applications": apps, "count": len(apps)}
    except Exception as e:
        logger.error(f"Failed to get applications list: {str(e)}")
        return {"applications": [], "count": 0}


# ============================================================
# AI API ENDPOINTS (WITH RATE LIMITING + INPUT VALIDATION)
# ============================================================

@app.get("/api/health/ai")
async def ai_health_check():
    try:
        return {"openai_configured": is_ai_ready(), "models_activated": 8 if is_ai_ready() else 0}
    except Exception:
        return {"openai_configured": False, "models_activated": 0}

@app.post("/api/ai/generate-questions")
@limiter.limit("10/minute")
async def api_generate_questions(request: Request):
    try:
        data = await request.json()
        validated = GenerateQuestionsRequest(**data)
        questions = await generate_assessment_questions(
            validated.stack,
            validated.difficulty,
            validated.count
        )
        return {"questions": questions, "count": len(questions)}
    except Exception as e:
        return handle_error(e, "generating questions", {"questions": [], "count": 0})

@app.post("/api/ai/voice-to-web")
@limiter.limit("5/minute")
async def api_voice_to_web(request: Request):
    try:
        data = await request.json()
        validated = VoiceToWebRequest(**data)
        result = await voice_to_website(validated.transcript, validated.language)
        return result
    except Exception as e:
        return handle_error(e, "voice-to-web", {"status": "error", "message": "Voice processing failed"})
# ============================================================
# VOICE-TO-WEB PRO ENGINE ROUTES
# ============================================================

@app.post("/api/voice-to-web/create")
@limiter.limit("10/minute")
async def v2w_create(request: Request):
    """Create website from voice data."""
    data = await request.json()
    return voice_to_web_engine.create_website(
        email=data.get("email"),
        business_name=data.get("business_name"),
        plan=data.get("plan", "free"),
        transcript=data.get("transcript", "")
    )

@app.post("/api/voice-to-web/domain")
@limiter.limit("10/minute")
async def v2w_domain(request: Request):
    """Setup custom domain."""
    data = await request.json()
    return voice_to_web_engine.setup_custom_domain(
        website_id=data.get("website_id"),
        domain=data.get("domain")
    )

@app.post("/api/voice-to-web/seo")
@limiter.limit("10/minute")
async def v2w_seo(request: Request):
    """Enable AI SEO."""
    data = await request.json()
    return voice_to_web_engine.enable_ai_seo(
        website_id=data.get("website_id"),
        business_name=data.get("business_name"),
        description=data.get("description", "")
    )

@app.post("/api/voice-to-web/update")
@limiter.limit("20/minute")
async def v2w_update(request: Request):
    """Request on-demand update."""
    data = await request.json()
    return voice_to_web_engine.request_update(
        website_id=data.get("website_id"),
        update_type=data.get("update_type"),
        details=data.get("details"),
        email=data.get("email", "")
    )

@app.post("/api/voice-to-web/support")
@limiter.limit("20/minute")
async def v2w_support(request: Request):
    """Create support ticket."""
    data = await request.json()
    return voice_to_web_engine.create_support_ticket(
        email=data.get("email"),
        issue=data.get("issue"),
        website_id=data.get("website_id")
    )

@app.get("/api/voice-to-web/status/{website_id}")
async def v2w_status(website_id: str):
    """Get website status."""
    return voice_to_web_engine.get_website_status(website_id)

@app.get("/api/voice-to-web/stats")
async def v2w_stats():
    """Get engine stats."""
    return voice_to_web_engine.get_stats()

@app.post("/api/ai/neural-wireframe")
@limiter.limit("5/minute")
async def api_neural_wireframe(request: Request):
    try:
        data = await request.json()
        validated = NeuralWireframeRequest(**data)
        code = await neural_wireframe_to_code(validated.sketch)
        return {"code": code}
    except Exception as e:
        return handle_error(e, "neural wireframe", {"code": "", "error": "Wireframe generation failed"})

@app.post("/api/ai/localize")
@limiter.limit("10/minute")
async def api_localize(request: Request):
    try:
        data = await request.json()
        validated = LocalizeRequest(**data)
        result = await localize_website(validated.url, validated.language)
        return result
    except Exception as e:
        return handle_error(e, "localization", {"status": "error", "message": "Localization failed"})

@app.post("/api/ai/generate-contract")
@limiter.limit("10/minute")
async def api_generate_contract(request: Request):
    try:
        data = await request.json()
        validated = GenerateContractRequest(**data)
        contract = await generate_legal_contract(
            validated.company,
            validated.country,
            validated.service
        )
        return {"contract": contract}
    except Exception as e:
        return handle_error(e, "contract generation", {"contract": "", "error": "Contract generation failed"})

@app.post("/api/ai/analyze-legacy")
@limiter.limit("5/minute")
async def api_analyze_legacy(request: Request):
    try:
        data = await request.json()
        validated = AnalyzeLegacyRequest(**data)
        result = await analyze_legacy_code(validated.code)
        return result
    except Exception as e:
        return handle_error(e, "legacy analysis", {"status": "error", "message": "Legacy analysis failed"})

@app.post("/api/ai/generate-schema")
@limiter.limit("10/minute")
async def api_generate_schema(request: Request):
    try:
        data = await request.json()
        validated = GenerateSchemaRequest(**data)
        result = await generate_agent_schema(validated.url)
        return result
    except Exception as e:
        return handle_error(e, "schema generation", {"status": "error", "message": "Schema generation failed"})


# ============================================================
# MONITOR API
# ============================================================

@app.post("/api/monitor/add")
async def api_add_monitor(request: Request):
    try:
        data = await request.json()
        validated = AddMonitorRequest(**data)
        result = await add_monitor(validated.url, validated.name, validated.interval)
        return result
    except Exception as e:
        return handle_error(e, "adding monitor", {"status": "error", "message": "Failed to add monitor"})

@app.get("/api/monitor/status")
async def api_monitor_status(url: str = None):
    try:
        return await get_monitor_status(url)
    except Exception as e:
        return handle_error(e, "monitor status", {"status": "error", "monitors": []})

@app.post("/api/monitor/check")
async def api_check_all():
    try:
        results = await check_all_sites()
        return {"checked": len(results), "results": results}
    except Exception as e:
        return handle_error(e, "monitor check", {"checked": 0, "results": []})


# ============================================================
# NA MODULE API ENDPOINTS (WITH AUTH + INPUT VALIDATION)
# ============================================================

@app.get("/na-bench-staffing", response_class=HTMLResponse)
async def na_bench_staffing(request: Request):
    return template_response("na-bench-staffing.html", request, "NA Bench Staffing - Charvak")

@app.get("/na-client-signup", response_class=HTMLResponse)
async def na_client_signup(request: Request):
    return template_response("na-client-signup.html", request, "Register - Charvak NA")

@app.post("/api/na/verify-work-auth")
@limiter.limit("20/minute")
async def verify_work_auth(request: Request):
    try:
        data = await request.json()
        validated = VerifyWorkAuthRequest(**data)
        candidate_id = validated.candidate_id or f"NA-{hash(validated.visa_input)}"
        visa_type = work_auth_engine.classify_visa(validated.visa_input)
        result = work_auth_engine.verify_candidate(
            candidate_id=candidate_id,
            visa_type=visa_type,
            visa_expiry=validated.visa_expiry,
            documents_verified=validated.documents_verified,
            client_type=validated.client_type
        )
        return result
    except Exception as e:
        return handle_error(e, "work auth verification")

@app.get("/api/na/visa-types")
async def get_visa_types():
    return {"visa_types": [{"name": v.value, "key": v.name} for v in VisaType]}

@app.post("/api/na/ingest-job")
@limiter.limit("30/minute")
async def ingest_job(request: Request):
    try:
        data = await request.json()
        validated = IngestJobRequest(**data)
        result = vms_connector.ingest_job_requirements(
            source=validated.source,
            raw_data=data
        )
        return result
    except Exception as e:
        return handle_error(e, "job ingestion")

@app.get("/api/na/jobs")
async def get_na_jobs(skill: str = None, location: str = None, visa_type: str = None):
    try:
        filters = {}
        if skill: filters["skill"] = skill
        if location: filters["location"] = location
        if visa_type: filters["visa_type"] = visa_type
        jobs = vms_connector.get_active_jobs(filters)
        return {"jobs": jobs, "count": len(jobs)}
    except Exception as e:
        return handle_error(e, "NA jobs fetch", {"jobs": [], "count": 0})

@app.post("/api/na/submit-candidate")
@limiter.limit("10/minute")
async def submit_candidate(request: Request):
    try:
        data = await request.json()
        validated = SubmitCandidateRequest(**data)
        
        # Verify work auth
        visa_type = work_auth_engine.classify_visa(validated.visa_input)
        work_auth = work_auth_engine.verify_candidate(
            candidate_id=validated.candidate_id,
            visa_type=visa_type,
            visa_expiry=validated.visa_expiry,
            documents_verified=validated.documents_verified,
            client_type=validated.client_type
        )
        
        if not work_auth.get("can_submit", False):
            return {"status": "rejected", "reason": "Work authorization check failed", "details": work_auth}
        
        result = vms_connector.submit_candidate(
            job_id=validated.job_id,
            candidate_data=data,
            vendor_id=validated.vendor_id,
            work_auth_result=work_auth
        )
        return result
    except Exception as e:
        return handle_error(e, "candidate submission")

@app.post("/api/na/match-candidate")
@limiter.limit("20/minute")
async def match_candidate(request: Request):
    try:
        data = await request.json()
        validated = MatchCandidateRequest(**data)
        jobs = vms_connector.get_active_jobs()
        matches = vector_matcher.match_candidate_to_jobs(data, jobs)
        return {"candidate_id": validated.id, "matches": matches, "count": len(matches)}
    except Exception as e:
        return handle_error(e, "candidate matching", {"matches": [], "count": 0})

@app.get("/api/na/sla-check/{submission_id}")
async def check_sla(submission_id: str):
    try:
        return vms_connector.check_sla(submission_id)
    except Exception as e:
        return handle_error(e, "SLA check")

@app.post("/api/na/redact-resume")
@limiter.limit("20/minute")
async def redact_resume(request: Request):
    try:
        data = await request.json()
        text = data.get("text", "")
        candidate_id = data.get("candidate_id", "NA-UNKNOWN")
        redacted_text, log = pii_redactor.redact_text(text, candidate_id)
        return {"redacted_text": redacted_text, "log": log}
    except Exception as e:
        return handle_error(e, "resume redaction")

@app.post("/api/na/blind-profile")
@limiter.limit("20/minute")
async def blind_profile(request: Request):
    try:
        data = await request.json()
        profile = pii_redactor.generate_blind_profile(data)
        return profile
    except Exception as e:
        return handle_error(e, "blind profile generation")

@app.post("/api/na/compliance-check")
@limiter.limit("30/minute")
async def compliance_check(request: Request):
    try:
        data = await request.json()
        check_type = data.get("type", "job")
        if check_type == "job":
            result = compliance_checker.check_job_compliance(data)
        else:
            result = compliance_checker.check_candidate_compliance(data)
        return result
    except Exception as e:
        return handle_error(e, "compliance check")

@app.post("/api/na/register-vendor")
async def register_vendor(request: Request):
    try:
        data = await request.json()
        validated = RegisterVendorRequest(**data)
        result = sub_vendor_manager.register_vendor(data)
        return result
    except Exception as e:
        return handle_error(e, "vendor registration")

@app.get("/api/na/vendor-stats/{vendor_id}")
async def vendor_stats(vendor_id: str):
    try:
        return sub_vendor_manager.get_vendor_stats(vendor_id)
    except Exception as e:
        return handle_error(e, "vendor stats")

@app.get("/api/na/vms/requisitions")
async def get_requisitions(skill: str = None, visa_type: str = None):
    try:
        filters = {}
        if skill: filters["skill"] = skill
        if visa_type: filters["visa_type"] = visa_type
        reqs = charvak_vms.get_open_requisitions(filters)
        return {"requisitions": reqs, "count": len(reqs)}
    except Exception as e:
        return handle_error(e, "requisitions fetch", {"requisitions": [], "count": 0})

@app.post("/api/na/vms/requisitions")
async def create_requisition(request: Request):
    try:
        data = await request.json()
        validated = CreateRequisitionRequest(**data)
        result = charvak_vms.create_requisition(
            client_id=validated.client_id,
            job_data=data
        )
        return result
    except Exception as e:
        return handle_error(e, "requisition creation")

@app.post("/api/na/vms/timecard")
async def submit_timecard(request: Request):
    try:
        data = await request.json()
        validated = SubmitTimecardRequest(**data)
        result = charvak_vms.submit_timecard(
            req_id=validated.req_id,
            candidate_id=validated.candidate_id,
            hours=validated.hours,
            period_end=validated.period_end,
            rate=validated.rate
        )
        return result
    except Exception as e:
        return handle_error(e, "timecard submission")

@app.post("/api/na/vms/timecard/approve")
async def approve_timecard(request: Request):
    try:
        data = await request.json()
        validated = ApproveTimecardRequest(**data)
        result = charvak_vms.approve_timecard(validated.timecard_id)
        return result
    except Exception as e:
        return handle_error(e, "timecard approval")

@app.get("/api/na/vms/analytics/{client_id}")
async def client_analytics(client_id: str):
    try:
        return charvak_vms.get_client_analytics(client_id)
    except Exception as e:
        return handle_error(e, "client analytics")

@app.post("/api/na/revenue/subscribe")
async def create_subscription(request: Request):
    try:
        data = await request.json()
        validated = CreateSubscriptionRequest(**data)
        tier = getattr(SubscriptionTier, validated.tier, SubscriptionTier.STARTER)
        result = revenue_engine.create_subscription(validated.firm_id, tier)
        return result
    except Exception as e:
        return handle_error(e, "subscription creation")

@app.get("/api/na/revenue/total")
async def total_revenue():
    try:
        return revenue_engine.get_total_revenue()
    except Exception as e:
        return handle_error(e, "total revenue")

@app.get("/api/na/revenue/firm/{firm_id}")
async def firm_revenue(firm_id: str):
    try:
        return revenue_engine.get_firm_revenue(firm_id)
    except Exception as e:
        return handle_error(e, "firm revenue")


# ============================================================
# 12 VIRAL TOOLS - PAGES
# ============================================================

@app.get("/tools", response_class=HTMLResponse)
async def tools_index(request: Request):
    return template_response("tools/index.html", request, "AI Tools Suite - Charvak")

@app.get("/tools/resume-roast", response_class=HTMLResponse)
async def resume_roast_page(request: Request):
    return template_response("tools/resume-roast.html", request, "Resume Roast - Charvak")

@app.get("/tools/ghost-bounty", response_class=HTMLResponse)
async def ghost_bounty_page(request: Request):
    return template_response("tools/ghost-bounty.html", request, "GhostBounty AI - Charvak")

@app.get("/tools/ref-check", response_class=HTMLResponse)
async def ref_check_page(request: Request):
    return template_response("tools/ref-check.html", request, "Ref-Check Roulette - Charvak")

@app.get("/tools/role-mirror", response_class=HTMLResponse)
async def role_mirror_page(request: Request):
    return template_response("tools/role-mirror.html", request, "Role-Mirror AI - Charvak")

@app.get("/tools/bounty-swap", response_class=HTMLResponse)
async def bounty_swap_page(request: Request):
    return template_response("tools/bounty-swap.html", request, "BountySwap AI - Charvak")

@app.get("/tools/micro-trial", response_class=HTMLResponse)
async def micro_trial_page(request: Request):
    return template_response("tools/micro-trial.html", request, "Micro-Trial Engine - Charvak")

@app.get("/tools/offer-matcher", response_class=HTMLResponse)
async def offer_matcher_page(request: Request):
    return template_response("tools/offer-matcher.html", request, "Offer Matcher - Charvak")

@app.get("/tools/ghost-job-shield", response_class=HTMLResponse)
async def ghost_job_shield_page(request: Request):
    return template_response("tools/ghost-job-shield.html", request, "Ghost-Job Shield - Charvak")

@app.get("/tools/counter-offer", response_class=HTMLResponse)
async def counter_offer_page(request: Request):
    return template_response("tools/counter-offer.html", request, "Counter-Offer Shield - Charvak")

@app.get("/tools/ref-swap", response_class=HTMLResponse)
async def ref_swap_page(request: Request):
    return template_response("tools/ref-swap.html", request, "Reference Check Swap - Charvak")

@app.get("/tools/ghost-tracker", response_class=HTMLResponse)
async def ghost_tracker_page(request: Request):
    return template_response("tools/ghost-tracker.html", request, "Ghosted Tracker - Charvak")

@app.get("/tools/pitch-roast", response_class=HTMLResponse)
async def pitch_roast_page(request: Request):
    return template_response("tools/pitch-roast.html", request, "Recruiter Pitch Roast - Charvak")


# ============================================================
# 12 VIRAL TOOLS - API ENDPOINTS (WITH RATE LIMITING + VALIDATION)
# ============================================================

@app.post("/api/tools/resume-roast")
@limiter.limit("10/minute")
async def api_resume_roast(request: Request):
    try:
        data = await request.json()
        validated = ResumeRoastRequest(**data)
        result = await resume_roast_ai(validated.resume, validated.job_title)
        return result
    except Exception as e:
        return handle_error(e, "resume roast")

@app.post("/api/tools/ghost-bounty")
@limiter.limit("10/minute")
async def api_ghost_bounty(request: Request):
    try:
        data = await request.json()
        validated = GhostBountyRequest(**data)
        result = await ghost_bounty_ai(validated.challenge)
        return result
    except Exception as e:
        return handle_error(e, "ghost bounty")

@app.post("/api/tools/role-mirror")
@limiter.limit("10/minute")
async def api_role_mirror(request: Request):
    try:
        data = await request.json()
        validated = RoleMirrorRequest(**data)
        result = await role_mirror_ai(validated.role, validated.skills)
        return result
    except Exception as e:
        return handle_error(e, "role mirror")

@app.post("/api/tools/offer-matcher")
@limiter.limit("10/minute")
async def api_offer_matcher(request: Request):
    try:
        data = await request.json()
        validated = OfferMatcherRequest(**data)
        result = await offer_matcher_ai(validated.offer_a, validated.offer_b)
        return result
    except Exception as e:
        return handle_error(e, "offer matcher")

@app.post("/api/tools/ghost-job")
@limiter.limit("10/minute")
async def api_ghost_job(request: Request):
    try:
        data = await request.json()
        validated = GhostJobRequest(**data)
        result = await ghost_job_ai(validated.url)
        return result
    except Exception as e:
        return handle_error(e, "ghost job detection")

@app.post("/api/tools/counter-offer")
@limiter.limit("10/minute")
async def api_counter_offer(request: Request):
    try:
        data = await request.json()
        validated = CounterOfferRequest(**data)
        result = await counter_offer_ai(validated.new_salary, validated.counter_salary)
        return result
    except Exception as e:
        return handle_error(e, "counter offer")

@app.post("/api/tools/pitch-roast")
@limiter.limit("10/minute")
async def api_pitch_roast(request: Request):
    try:
        data = await request.json()
        validated = PitchRoastRequest(**data)
        result = await pitch_roast_ai(validated.inmail)
        return result
    except Exception as e:
        return handle_error(e, "pitch roast")

@app.post("/api/tools/ref-check")
@limiter.limit("10/minute")
async def api_ref_check(request: Request):
    try:
        data = await request.json()
        validated = RefCheckRequest(**data)
        result = await ref_check_ai(validated.ref_names)
        return result
    except Exception as e:
        return handle_error(e, "reference check")

@app.post("/api/tools/bounty-swap")
@limiter.limit("10/minute")
async def api_bounty_swap(request: Request):
    data = await request.json()
    result = await bounty_swap_ai(data.get("bounty_amount", 500), data.get("referrer_name", ""))
    return result

@app.post("/api/tools/micro-trial")
@limiter.limit("10/minute")
async def api_micro_trial(request: Request):
    data = await request.json()
    result = await micro_trial_ai(data.get("trial_type", "Frontend"), data.get("skills", ""))
    return result

@app.post("/api/tools/ghost-job-shield")
@limiter.limit("10/minute")
async def api_ghost_job_shield(request: Request):
    data = await request.json()
    result = await ghost_job_ai(data.get("url", ""))
    return result

@app.post("/api/tools/ref-swap")
@limiter.limit("10/minute")
async def api_ref_swap(request: Request):
    data = await request.json()
    result = await ref_swap_ai(data.get("ref_type", "Professional"), data.get("industry", ""))
    return result

@app.post("/api/tools/ghost-tracker")
@limiter.limit("10/minute")
async def api_ghosted_tracker(request: Request):
    data = await request.json()
    result = await ghosted_tracker_ai(data.get("applications", []))
    return result


# ============================================================
# AGREEMENT SYSTEM
# ============================================================

@app.get("/agreement")
async def agreement_page(request: Request):
    agreement_type = request.query_params.get("type", "MSA")
    client_name = request.query_params.get("client", "Client")
    redirect_url = request.query_params.get("redirect", "/")
    service = request.query_params.get("service", "IT Consulting Services")
    payment = request.query_params.get("payment", "Payment due upon service delivery")
    
    agreements = {
        "MSA": "Master Service Agreement",
        "NDA": "Non-Disclosure Agreement",
        "MOU": "Memorandum of Understanding",
        "PLACEMENT": "Placement Agreement",
        "INTERN": "Internship Agreement",
        "TRAINER": "Trainer Agreement"
    }
    
    return template_response("agreement.html", request,
        f"{agreements.get(agreement_type, 'Agreement')} - Charvak",
        agreement_title=agreements.get(agreement_type, "Service Agreement"),
        agreement_type=agreement_type,
        client_name=client_name,
        effective_date=datetime.now().strftime("%B %d, %Y"),
        service_description=service,
        payment_terms=payment,
        redirect_url=redirect_url,
        decline_url="/"
    )

@app.post("/api/agreement/sign")
async def sign_agreement(request: Request):
    try:
        data = await request.json()
        validated = SignAgreementRequest(**data)
        db.save_agreement(data)
        logger.info(f"Agreement signed: type={validated.agreement_type}, client={validated.client_name}")
        return {"status": "success", "message": "Agreement saved successfully"}
    except Exception as e:
        logger.error(f"Agreement signing failed: {str(e)}", exc_info=True)
        return {"status": "error", "message": "Failed to save agreement. Please try again."}


# ============================================================
# INVOICE SYSTEM
# ============================================================

@app.get("/invoice")
async def generate_invoice(request: Request):
    service = request.query_params.get("service", "Consulting Services")
    client = request.query_params.get("client", "Client Name")
    amount = request.query_params.get("amount", "0")
    
    try:
        amount_int = int(amount) if amount.isdigit() else 0
    except ValueError:
        amount_int = 0
    
    invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{secrets.token_hex(3).upper()}"
    
    return template_response("invoice.html", request,
        f"Invoice {invoice_number} - Charvak",
        invoice_number=invoice_number,
        invoice_date=datetime.now().strftime("%B %d, %Y"),
        due_date=(datetime.now() + timedelta(days=15)).strftime("%B %d, %Y"),
        client_name=client,
        client_address="Client Address",
        client_email="client@email.com",
        gst_number="37AADCC1234K1Z9",
        pan_number="AADCC1234K",
        invoice_items=[{
            "service": service,
            "description": "Professional services as per agreement",
            "qty": 1,
            "rate": f"₹{amount_int}",
            "amount": f"₹{amount_int}"
        }],
        subtotal=f"₹{amount_int}",
        gst_amount=f"₹{int(amount_int * 0.18)}",
        total_amount=f"₹{int(amount_int * 1.18)}",
        payment_terms="15"
    )

@app.get("/admin-invoices", response_class=HTMLResponse)
async def admin_invoices(request: Request):
    return template_response("admin-invoices.html", request, "Invoice Management - Charvak Admin")

@app.post("/api/invoice/create")
async def api_create_invoice(request: Request):
    try:
        data = await request.json()
        validated = CreateInvoiceRequest(**data)
        result = invoice_manager.create_invoice(
            admin_id="admin",
            client_name=validated.client_name,
            client_email=validated.client_email,
            service_type=validated.service_type,
            amount=validated.amount,
            description=validated.description
        )
        return result
    except Exception as e:
        return handle_error(e, "invoice creation")

@app.get("/api/invoice/list")
async def api_list_invoices(status: str = None):
    try:
        invoices = invoice_manager.get_all_invoices(status)
        stats = invoice_manager.get_invoice_stats()
        return {"invoices": invoices, "stats": stats, "count": len(invoices)}
    except Exception as e:
        return handle_error(e, "invoice listing", {"invoices": [], "stats": {}, "count": 0})

@app.post("/api/invoice/update")
async def api_update_invoice(request: Request):
    try:
        data = await request.json()
        validated = UpdateInvoiceRequest(**data)
        
        if validated.action == "send":
            return invoice_manager.send_invoice(validated.invoice_id, "admin")
        elif validated.action == "paid":
            return invoice_manager.mark_paid(validated.invoice_id, "admin")
        elif validated.action == "cancel":
            return invoice_manager.cancel_invoice(validated.invoice_id, "admin", validated.reason)
        
        return {"error": "Invalid action. Use: send, paid, or cancel"}
    except Exception as e:
        return handle_error(e, "invoice update")

# ============================================================
# PAYMENT API ENDPOINTS
# ============================================================

@app.get("/api/payment/status")
async def payment_status():
    """Check which payment methods are available."""
    return payment_engine.is_ready()

@app.post("/api/payment/create-order")
@limiter.limit("20/minute")
async def create_payment_order(request: Request):
    """Create a payment order for Razorpay/PayPal."""
    try:
        data = await request.json()
        amount = data.get("amount", 0)
        name = data.get("name", "Service")
        method = data.get("method", "razorpay")
        
        if method == "razorpay":
    # Convert to paise (Razorpay uses smallest unit)
    amount_paise = int(amount * 100)
    receipt = f"rcpt_{datetime.now().strftime('%Y%m%d%H%M%S')}_{secrets.token_hex(4)}"
    result = payment_engine.create_razorpay_order(
        amount_inr=amount_paise,
        receipt=receipt,
        notes={"tool": name, "amount_inr": amount}
    )
    # ADD KEY TO RESPONSE
    result["key_id"] = os.getenv("RAZORPAY_KEY_ID", "rzp_live_TSniXv6CyEnZ9B")
    result["key"] = os.getenv("RAZORPAY_KEY_ID", "rzp_live_TSniXv6CyEnZ9B")
        elif method == "paypal":
            # Convert INR to USD (approximate)
            amount_usd = round(amount / 83, 2)
            result = payment_engine.create_paypal_order(
                amount_usd=amount_usd,
                description=name
            )
        else:
            result = {"status": "error", "message": f"Unknown payment method: {method}"}
        
        return result
    except Exception as e:
        logger.error(f"Payment order creation failed: {e}", exc_info=True)
        return {"status": "error", "message": "Payment setup failed"}

@app.post("/api/payment/verify")
@limiter.limit("30/minute")
async def verify_payment(request: Request):
    """Verify a completed payment."""
    try:
        data = await request.json()
        method = data.get("method")
        
        if method == "razorpay":
            result = payment_engine.verify_razorpay_payment(
                payment_id=data.get("payment_id", ""),
                order_id=data.get("order_id", ""),
                signature=data.get("signature", "")
            )
        elif method == "paypal":
            result = payment_engine.verify_paypal_payment(
                order_id=data.get("order_id", ""),
                paypal_order_id=data.get("paypal_order_id", "")
            )
        elif method == "upi":
            result = payment_engine.verify_upi_payment(
                txn_id=data.get("txn_id", ""),
                amount=data.get("amount", 0),
                notes=data.get("notes", "")
            )
        else:
            result = {"status": "error", "message": f"Unknown method: {method}"}
        
        if result.get("verified"):
            logger.info(f"✅ Payment verified: {method} - {data.get('order_id')}")
        
        return result
    except Exception as e:
        logger.error(f"Payment verification failed: {e}", exc_info=True)
        return {"status": "error", "verified": False, "message": "Verification failed"}

@app.get("/api/payment/history")
async def payment_history():
    """Get all payment records."""
    return payment_engine.get_all_payments()

# ============================================================
# KYC & VERIFICATION API ENDPOINTS
# ============================================================

@app.get("/api/kyc/status")
async def kyc_status():
    """Get KYC system overview."""
    return kyc_engine.get_stats()

@app.get("/api/kyc/pricing")
async def kyc_pricing():
    """Get verification pricing."""
    return kyc_engine.PRICING

@app.post("/api/kyc/initiate")
@limiter.limit("10/minute")
async def initiate_verification(request: Request):
    """Start a new background verification."""
    try:
        data = await request.json()
        result = kyc_engine.initiate_verification(data)
        return result
    except Exception as e:
        logger.error(f"Verification initiation failed: {e}", exc_info=True)
        return {"status": "error", "message": "Failed to initiate verification"}

@app.get("/api/kyc/verification/{verification_id}")
async def get_verification(verification_id: str):
    """Check verification status by ID."""
    return kyc_engine.get_verification_status(verification_id)

@app.get("/api/kyc/user/{email}")
async def get_user_verifications(email: str):
    """Get all verifications for a user."""
    return kyc_engine.get_user_verifications(email)

@app.get("/api/kyc/is-verified")
async def check_verified(email: str):
    """Check if user is verified."""
    return kyc_engine.is_user_verified(email)

@app.get("/api/kyc/badge/{email}")
async def get_badge(email: str):
    """Get verified badge for user."""
    return kyc_engine.get_verified_badge(email)

@app.post("/api/kyc/submit-documents")
@limiter.limit("10/minute")
async def submit_kyc_documents(request: Request):
    """Submit documents for verification."""
    try:
        data = await request.json()
        verification_id = data.get("verification_id")
        documents = data.get("documents", [])
        result = kyc_engine.submit_documents(verification_id, documents)
        return result
    except Exception as e:
        logger.error(f"Document submission failed: {e}", exc_info=True)
        return {"status": "error", "message": "Failed to submit documents"}

@app.post("/api/kyc/review")
async def review_verification(request: Request):
    """Admin/Partner reviews a verification."""
    try:
        data = await request.json()
        result = kyc_engine.review_verification(
            verification_id=data.get("verification_id"),
            result=data
        )
        return result
    except Exception as e:
        logger.error(f"Verification review failed: {e}", exc_info=True)
        return {"status": "error", "message": "Review failed"}

# Partner routes
@app.post("/api/kyc/partner/register")
@limiter.limit("5/minute")
async def register_partner(request: Request):
    """Register as a verification partner."""
    try:
        data = await request.json()
        result = kyc_engine.register_partner(data)
        return result
    except Exception as e:
        logger.error(f"Partner registration failed: {e}", exc_info=True)
        return {"status": "error", "message": "Registration failed"}

@app.get("/api/kyc/partners")
async def get_partners(status: str = None):
    """Get verification partners."""
    return kyc_engine.get_partners(status)

@app.post("/api/kyc/partner/approve")
async def approve_partner(request: Request):
    """Admin approves a partner."""
    try:
        data = await request.json()
        result = kyc_engine.approve_partner(data.get("partner_id"))
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/kyc/assign")
async def assign_verification(request: Request):
    """Assign verification to a partner."""
    try:
        data = await request.json()
        result = kyc_engine.assign_verification_to_partner(
            verification_id=data.get("verification_id"),
            partner_id=data.get("partner_id")
        )
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/background-verification/initiate")
@limiter.limit("10/minute")
async def initiate_background_verification(request: Request):
    """Initiate background verification from career engine."""
    try:
        data = await request.json()
        # Route through KYC engine
        result = kyc_engine.initiate_verification({
            "name": data.get("name"),
            "email": data.get("email"),
            "phone": data.get("phone", ""),
            "verification_type": data.get("verification_type", "identity"),
            "country": data.get("country", "India"),
            "notes": data.get("notes", "")
        })
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ============================================================
# ESCROW (DOKETS VOUCHAI) API ENDPOINTS
# ============================================================

@app.get("/api/escrow/stats")
async def escrow_stats():
    """Get escrow system statistics."""
    return escrow_engine.get_stats()

@app.post("/api/escrow/create")
@limiter.limit("20/minute")
async def create_escrow(request: Request):
    """Create a new escrow transaction."""
    try:
        data = await request.json()
        result = escrow_engine.create_escrow(data)
        return result
    except Exception as e:
        logger.error(f"Escrow creation failed: {e}", exc_info=True)
        return {"status": "error", "message": "Failed to create escrow"}

@app.post("/api/escrow/deposit")
@limiter.limit("10/minute")
async def deposit_escrow(request: Request):
    """Deposit funds into escrow."""
    try:
        data = await request.json()
        result = escrow_engine.deposit_funds(
            escrow_id=data.get("escrow_id"),
            payment_details=data.get("payment_details", {})
        )
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/escrow/deliver")
@limiter.limit("20/minute")
async def deliver_work(request: Request):
    """Mark work as delivered."""
    try:
        data = await request.json()
        result = escrow_engine.deliver_work(
            escrow_id=data.get("escrow_id"),
            delivery_data=data.get("delivery_data", {})
        )
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/escrow/release")
@limiter.limit("10/minute")
async def release_escrow(request: Request):
    """Release funds to vendor."""
    try:
        data = await request.json()
        result = escrow_engine.release_funds(data.get("escrow_id"))
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/escrow/dispute")
@limiter.limit("5/minute")
async def dispute_escrow(request: Request):
    """Raise a dispute."""
    try:
        data = await request.json()
        result = escrow_engine.raise_dispute(
            escrow_id=data.get("escrow_id"),
            dispute_data=data
        )
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/escrow/resolve")
async def resolve_dispute(request: Request):
    """Admin resolves a dispute."""
    try:
        data = await request.json()
        result = escrow_engine.resolve_dispute(
            escrow_id=data.get("escrow_id"),
            resolution=data.get("resolution", {})
        )
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/escrow/{escrow_id}")
async def get_escrow(escrow_id: str):
    """Get escrow details."""
    return escrow_engine.get_escrow(escrow_id)

@app.get("/api/escrow/user/{email}")
async def get_user_escrows(email: str):
    """Get user's escrow transactions."""
    return escrow_engine.get_user_escrows(email)

# ============================================================
# REFERRAL & AFFILIATE API ENDPOINTS
# ============================================================

@app.get("/api/referral/stats")
async def referral_stats():
    """Get referral system statistics."""
    return referral_engine.get_stats()

@app.post("/api/referral/create-link")
@limiter.limit("10/minute")
async def create_referral_link(request: Request):
    """Create a referral link."""
    try:
        data = await request.json()
        result = referral_engine.create_referral_link(data)
        return result
    except Exception as e:
        logger.error(f"Referral link creation failed: {e}")
        return {"status": "error", "message": "Failed to create referral link"}

@app.get("/api/referral/track-click/{referral_code}")
async def track_click(referral_code: str, source: str = "direct"):
    """Track a referral link click."""
    return referral_engine.track_click(referral_code, source)

@app.post("/api/referral/track-signup")
async def track_signup(request: Request):
    """Track signup from referral."""
    try:
        data = await request.json()
        result = referral_engine.track_signup(
            referral_code=data.get("referral_code"),
            new_user_email=data.get("email")
        )
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/referral/convert")
async def convert_referral(request: Request):
    """Mark a referral as converted."""
    try:
        data = await request.json()
        result = referral_engine.mark_conversion(data.get("bounty_id"))
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/referral/pay")
async def pay_bounty(request: Request):
    """Pay a referral bounty."""
    try:
        data = await request.json()
        result = referral_engine.pay_bounty(data.get("bounty_id"))
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/referral/user/{email}")
async def referrer_stats(email: str):
    """Get referrer stats."""
    return referral_engine.get_referrer_stats(email)

@app.get("/api/referral/leaderboard")
async def referral_leaderboard(limit: int = 10):
    """Get referral leaderboard."""
    return referral_engine.get_leaderboard(limit)

@app.post("/api/affiliate/register")
@limiter.limit("5/minute")
async def register_affiliate(request: Request):
    """Register as an affiliate."""
    try:
        data = await request.json()
        result = referral_engine.register_affiliate(data)
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ============================================================
# MICRO-INTERNSHIP API ENDPOINTS
# ============================================================

@app.get("/api/micro-internship/stats")
async def micro_internship_stats():
    """Get micro-internship system statistics."""
    return micro_internship_engine.get_stats()

@app.post("/api/micro-internship/client/register")
@limiter.limit("10/minute")
async def register_micro_client(request: Request):
    """Register a client company."""
    try:
        data = await request.json()
        result = micro_internship_engine.register_client(data)
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/micro-internship/client/{client_id}/dashboard")
async def client_dashboard(client_id: str):
    """Get client dashboard."""
    return micro_internship_engine.get_client_dashboard(client_id)

@app.post("/api/micro-internship/project/post")
@limiter.limit("20/minute")
async def post_micro_project(request: Request):
    """Post a micro-internship project."""
    try:
        data = await request.json()
        result = micro_internship_engine.post_project(data)
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/micro-internship/projects")
async def get_projects(category: str = None, difficulty: str = None, skill: str = None, max_budget: float = None):
    """Get open projects."""
    filters = {}
    if category: filters["category"] = category
    if difficulty: filters["difficulty"] = difficulty
    if skill: filters["skill"] = skill
    if max_budget: filters["max_budget"] = max_budget
    return micro_internship_engine.get_open_projects(filters)

@app.get("/api/micro-internship/project/{project_id}")
async def get_project(project_id: str):
    """Get project details."""
    return micro_internship_engine.get_project(project_id)

@app.post("/api/micro-internship/apply")
@limiter.limit("10/minute")
async def apply_to_project(request: Request):
    """Apply to a project."""
    try:
        data = await request.json()
        result = micro_internship_engine.apply_to_project(data)
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/micro-internship/project/{project_id}/applications")
async def project_applications(project_id: str):
    """Get applications for a project."""
    return micro_internship_engine.get_project_applications(project_id)

@app.post("/api/micro-internship/assign")
async def assign_intern(request: Request):
    """Assign intern to project."""
    try:
        data = await request.json()
        result = micro_internship_engine.assign_intern(
            project_id=data.get("project_id"),
            application_id=data.get("application_id")
        )
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/micro-internship/submit")
async def submit_work(request: Request):
    """Submit work for review."""
    try:
        data = await request.json()
        result = micro_internship_engine.submit_work(
            project_id=data.get("project_id"),
            submission_data=data
        )
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/micro-internship/approve")
async def approve_work(request: Request):
    """Approve work and release payment."""
    try:
        data = await request.json()
        result = micro_internship_engine.approve_work(
            project_id=data.get("project_id"),
            approval_data=data
        )
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ============================================================
# BADGE & CERTIFICATION API ENDPOINTS
# ============================================================

@app.get("/api/badge/stats")
async def badge_stats():
    """Get badge statistics."""
    return badge_engine.get_stats()

@app.post("/api/badge/issue")
async def issue_badge(request: Request):
    """Issue a badge to a user."""
    try:
        data = await request.json()
        result = badge_engine.issue_badge(data)
        return result
    except Exception as e:
        logger.error(f"Badge issuance failed: {e}")
        return {"status": "error", "message": "Failed to issue badge"}

@app.get("/api/badge/verify/{badge_id}")
async def verify_badge(badge_id: str):
    """Verify a badge."""
    return badge_engine.verify_badge(badge_id)

@app.get("/api/badge/user/{email}")
async def user_badges(email: str):
    """Get user badges."""
    return badge_engine.get_user_badges(email)

@app.post("/api/badge/revoke")
async def revoke_badge(request: Request):
    """Revoke a badge."""
    try:
        data = await request.json()
        result = badge_engine.revoke_badge(data.get("badge_id"))
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/testimonials", response_class=HTMLResponse)
async def testimonials(request: Request):
    """Testimonials & social proof page."""
    return template_response("testimonials.html", request, "Client Testimonials - Charvak IT Consulting")

# ============================================================
# BLOG API ENDPOINTS
# ============================================================

@app.get("/blog", response_class=HTMLResponse)
async def blog_index(request: Request):
    """Blog listing page."""
    posts = blog_engine.get_all_posts()
    return template_response("blog/index.html", request, "Blog - Charvak IT Consulting", posts=posts)

@app.get("/blog/{slug}", response_class=HTMLResponse)
async def blog_post(request: Request, slug: str):
    """Individual blog post."""
    post_data = blog_engine.get_post(slug)
    if post_data["status"] == "error":
        raise HTTPException(status_code=404, detail="Post not found")
    return template_response("blog/post.html", request, 
        post_data["post"]["seo_title"], 
        post=post_data["post"],
        related=post_data.get("related", []))

@app.get("/api/blog/posts")
async def api_blog_posts(category: str = None, tag: str = None):
    """API: Get blog posts."""
    return blog_engine.get_all_posts(category, tag)

@app.get("/api/blog/{slug}")
async def api_blog_post(slug: str):
    """API: Get single blog post."""
    return blog_engine.get_post(slug)


# ============================================================
# CASE STUDIES
# ============================================================

@app.get("/case-studies", response_class=HTMLResponse)
async def case_studies(request: Request):
    """Case studies listing page."""
    return template_response("case-studies.html", request, "Case Studies - Charvak IT Consulting")

@app.get("/case-studies/{slug}", response_class=HTMLResponse)
async def case_study(request: Request, slug: str):
    """Individual case study."""
    return template_response("case-studies.html", request, f"Case Study - Charvak")


# ============================================================
# CHATBOT API ENDPOINTS
# ============================================================

@app.get("/api/chat/start")
async def start_chat():
    """Start a new chat session."""
    return chatbot_engine.start_session()

@app.post("/api/chat/send")
@limiter.limit("20/minute")
async def send_chat(request: Request):
    """Send a message to the chatbot."""
    try:
        data = await request.json()
        result = chatbot_engine.send_message(
            session_id=data.get("session_id"),
            message=data.get("message", "")
        )
        return result
    except Exception as e:
        return {"status": "error", "message": "Chat failed. Please email hr@charvakit.com"}

@app.get("/api/chat/faqs")
async def get_faqs():
    """Get all FAQs."""
    return chatbot_engine.get_faqs()

@app.get("/sla", response_class=HTMLResponse)
async def sla_page(request: Request):
    """Public SLA & Uptime page."""
    return template_response("sla.html", request, "SLA & Uptime - Charvak IT Consulting")

@app.get("/help", response_class=HTMLResponse)
async def help_center(request: Request):
    """Help & Support Center."""
    return template_response("help.html", request, "Help Center - Charvak IT Consulting")

# ============================================================
# SSO/SAML AUTH ENDPOINTS
# ============================================================

@app.get("/saml/metadata")
async def saml_metadata():
    """SAML SP Metadata endpoint for IdP configuration."""
    return sso_engine.generate_metadata()

@app.get("/api/sso/providers")
async def sso_providers():
    """Get configured SSO providers."""
    return sso_engine.get_configured_providers()

@app.post("/api/sso/login")
@limiter.limit("10/minute")
async def sso_login(request: Request):
    """Initiate SSO login."""
    try:
        data = await request.json()
        result = sso_engine.generate_saml_request(
            provider_key=data.get("provider", "okta"),
            relay_state=data.get("redirect", "/")
        )
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/saml/acs")
async def saml_acs(request: Request):
    """SAML Assertion Consumer Service — receives IdP response."""
    try:
        form_data = await request.form()
        saml_response = form_data.get("SAMLResponse", "")
        relay_state = form_data.get("RelayState", "/")
        result = sso_engine.handle_saml_response(saml_response, relay_state)
        
        if result["status"] == "success":
            return template_response("sso-success.html", request,
                "SSO Login Successful - Charvak",
                token=result["token"],
                redirect=result["redirect"],
                user=result["user"]
            )
        
        return template_response("sso-error.html", request,
            "SSO Login Failed - Charvak",
            error="Authentication failed"
        )
    except Exception as e:
        logger.error(f"SAML ACS error: {e}", exc_info=True)
        return template_response("sso-error.html", request,
            "SSO Error - Charvak",
            error=str(e)
        )

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Unified login page with SSO options."""
    providers = sso_engine.get_configured_providers()
    return template_response("login.html", request, 
        "Login - Charvak IT Consulting",
        sso_providers=providers.get("providers", {}),
        sso_enabled=providers.get("enabled", False)
    )

@app.get("/client-dashboard", response_class=HTMLResponse)
async def client_dashboard_page(request: Request):
    """Client dashboard for micro-internships."""
    return template_response("client-dashboard.html", request, "Client Dashboard - Charvak Micro-Internships")

# ============================================================
# TRAINING ENGINE API ENDPOINTS
# ============================================================

@app.post("/api/training/post-course")
@limiter.limit("10/minute")
async def post_course_api(request: Request):
    """Post a new course."""
    try:
        data = await request.json()
        result = training_engine.post_course(data)
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/training/courses")
async def api_get_training_courses(category: str = None):
    """Get published courses."""
    return training_engine.get_courses(category)

@app.get("/api/training/course/{course_id}")
async def api_get_training_course(course_id: str):
    """Get course details."""
    return training_engine.get_course(course_id)

@app.post("/api/training/enroll")
@limiter.limit("20/minute")
async def enroll_student(request: Request):
    """Enroll in a course."""
    try:
        data = await request.json()
        result = training_engine.enroll_student(data)
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/training/trainer/{email}")
async def trainer_dashboard(email: str):
    """Get trainer dashboard."""
    return training_engine.get_trainer_dashboard(email)

@app.get("/api/training/student/{email}")
async def student_dashboard(email: str):
    """Get student dashboard."""
    return training_engine.get_student_dashboard(email)

# ============================================================
# INTERVIEW PREP API ENDPOINTS
# ============================================================

@app.post("/api/interview-prep/start")
@limiter.limit("10/minute")
async def start_interview_prep(request: Request):
    """Start an interview prep session."""
    try:
        data = await request.json()
        result = interview_prep_engine.start_session(data)
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/interview-prep/submit")
@limiter.limit("20/minute")
async def submit_answer(request: Request):
    """Submit an answer for scoring."""
    try:
        data = await request.json()
        result = interview_prep_engine.submit_answer(data)
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/interview-prep/session/{session_id}")
async def get_prep_session(session_id: str):
    """Get session details."""
    return interview_prep_engine.get_session(session_id)

# ============================================================
# PRODUCTS API ENDPOINTS
# ============================================================

@app.post("/api/products/lock-in-breaker/audit")
@limiter.limit("10/minute")
async def api_lock_in_breaker(request: Request):
    data = await request.json()
    return products_engine.lock_in_breaker_audit(data)

@app.post("/api/products/reverse-staffing/match")
@limiter.limit("10/minute")
async def api_reverse_staffing(request: Request):
    data = await request.json()
    return products_engine.reverse_staffing_match(data)

@app.post("/api/products/auditbot/scan")
@limiter.limit("10/minute")
async def api_auditbot(request: Request):
    data = await request.json()
    return products_engine.auditbot_scan(data)

@app.post("/api/products/skill-twin/assess")
@limiter.limit("10/minute")
async def api_skill_twin(request: Request):
    data = await request.json()
    return products_engine.skill_twin_assess(data)

@app.post("/api/products/micro-squads/assemble")
@limiter.limit("10/minute")
async def api_micro_squads(request: Request):
    data = await request.json()
    return products_engine.micro_squads_assemble(data)

@app.post("/api/products/agency-twin/automate")
@limiter.limit("10/minute")
async def api_agency_twin(request: Request):
    data = await request.json()
    return products_engine.agency_twin_automate(data)

@app.post("/api/products/geo-compliance/check")
@limiter.limit("10/minute")
async def api_geo_compliance(request: Request):
    data = await request.json()
    return products_engine.geo_compliance_check(data)

@app.post("/api/products/design-token/check")
@limiter.limit("10/minute")
async def api_design_token(request: Request):
    data = await request.json()
    return products_engine.design_token_check(data)

@app.post("/api/products/silent-killer/monitor")
@limiter.limit("10/minute")
async def api_silent_killer(request: Request):
    data = await request.json()
    return products_engine.silent_killer_monitor(data)

@app.post("/api/products/ai-slop/scan")
@limiter.limit("10/minute")
async def api_ai_slop(request: Request):
    data = await request.json()
    return products_engine.ai_slop_scan(data)

@app.post("/api/products/developer-entropy/score")
@limiter.limit("10/minute")
async def api_developer_entropy(request: Request):
    data = await request.json()
    return products_engine.developer_entropy_score(data)

@app.post("/api/calculator/hiring-savings")
@limiter.limit("20/minute")
async def hiring_savings_calculator(request: Request):
    """Calculate hiring cost savings."""
    try:
        data = await request.json()
        hires_per_year = int(data.get("hires_per_year", 5))
        avg_ctc = float(data.get("avg_ctc", 1000000))
        
        traditional_cost = round(avg_ctc * 0.20 * hires_per_year, 2)  # 20% agency fee
        charvak_cost = round(avg_ctc * 0.02 * hires_per_year, 2)  # 2% platform fee
        savings = round(traditional_cost - charvak_cost, 2)
        savings_percent = round((savings / traditional_cost) * 100, 1) if traditional_cost > 0 else 0
        
        return {
            "status": "success",
            "hires_per_year": hires_per_year,
            "avg_ctc": avg_ctc,
            "traditional_cost": traditional_cost,
            "charvak_cost": charvak_cost,
            "savings": savings,
            "savings_percent": savings_percent,
            "message": f"You save ₹{savings:,} per year ({savings_percent}%)"
        }
    except Exception as e:
        return {"status": "error", "message": "Calculation failed"}

@app.post("/api/demo/book")
@limiter.limit("5/minute")
async def book_demo(request: Request):
    """Book a demo request."""
    try:
        data = await request.json()
        demo_request = {
            "request_id": f"DEMO-{secrets.token_hex(4).upper()}",
            "name": data.get("name"),
            "email": data.get("email"),
            "company": data.get("company", ""),
            "company_size": data.get("company_size", ""),
            "hiring_volume": data.get("hiring_volume", ""),
            "preferred_time": data.get("preferred_time", ""),
            "created_at": datetime.now().isoformat()
        }
        
        # In production: save to database and send email
        logger.info(f"Demo requested: {demo_request}")
        
        return {
            "status": "success",
            "request_id": demo_request["request_id"],
            "message": "Demo request received! We'll respond within 24 hours.",
            "confirmation": f"A confirmation email will be sent to {data.get('email')}"
        }
    except Exception as e:
        return {"status": "error", "message": "Failed to book demo"}

@app.get("/api/stats/platform")
async def platform_stats():
    """Get REAL platform statistics from engines."""
    return {
        "status": "success",
        "stats": {
            "active_jobs": job_board_engine.get_stats()["active_jobs"],
            "micro_projects": micro_internship_engine.get_stats()["stats"]["total_projects"],
            "courses": training_engine.get_courses()["count"],
            "escrow_transactions": escrow_engine.get_stats()["stats"]["total_transactions"],
            "verified_users": kyc_engine.get_stats()["stats"]["verified_users"],
            "badges_issued": badge_engine.get_stats()["stats"]["total_badges_issued"],
            "blog_posts": blog_engine.get_all_posts()["count"],
            "timestamp": datetime.now().isoformat()
        }
    }

# ============================================================
# CAREER PROGRESS TRACKING
# ============================================================

@app.get("/api/career/progress/{email}")
async def career_progress(email: str):
    """Track candidate's progress through the career engine."""
    try:
        progress = {
            "email": email,
            "steps": {
                "1_skill_check": {
                    "completed": bool(badge_engine.get_user_badges(email).get("count", 0) > 0),
                    "link": "/skill-check"
                },
                "2_micro_internship": {
                    "completed": False,  # Would check micro-internship applications
                    "link": "/micro-internship"
                },
                "3_badge": {
                    "completed": bool(badge_engine.get_user_badges(email).get("count", 0) > 0),
                    "link": "/badge"
                },
                "4_training": {
                    "completed": len(training_engine.get_student_dashboard(email).get("enrollments", [])) > 0,
                    "link": "/training-engine"
                },
                "5_job_applied": {
                    "completed": len([a for a in job_board_engine.get_applications() if a.get("user_id") == email]) > 0,
                    "link": "/job-board"
                }
            },
            "badges_earned": badge_engine.get_user_badges(email).get("count", 0),
            "courses_enrolled": len(training_engine.get_student_dashboard(email).get("enrollments", [])),
            "jobs_applied": len([a for a in job_board_engine.get_applications() if a.get("user_id") == email]),
            "verification_status": kyc_engine.is_user_verified(email),
            "next_step": "Take your free Skill Check" if not badge_engine.get_user_badges(email).get("count") else "Apply to matched jobs"
        }
        return {"status": "success", "progress": progress}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/services/web-design/proposal", response_class=HTMLResponse)
async def web_design_proposal(request: Request):
    """Web design proposal page."""
    return template_response("web-design-proposal.html", request, "Get a Web Design Proposal - Charvak")

# ============================================================
# CANDIDATE POOL API ENDPOINTS
# ============================================================

@app.post("/api/candidate/register")
@limiter.limit("10/minute")
async def register_candidate(request: Request):
    """Register a new candidate."""
    try:
        data = await request.json()
        result = candidate_engine.register_candidate(data)
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/candidate/{candidate_id}")
async def get_candidate(candidate_id: str):
    """Get candidate details."""
    return candidate_engine.get_candidate(candidate_id)

@app.get("/api/candidates/search")
async def search_candidates(
    skill: str = None,
    experience_min: int = None,
    experience_max: int = None,
    location: str = None,
    visa_status: str = None,
    skill_score_min: int = None,
    education: str = None,
    degree: str = None,
    major: str = None,
    university: str = None,
    gpa_min: float = None,
    graduation_year_min: int = None,
    certification: str = None,
    language: str = None,
    work_authorization: str = None,
    remote_preference: str = None,
    availability: str = None,
    years_coding_min: int = None
):
    """Advanced candidate search with 18 filters."""
    filters = {}
    if skill: filters["skill"] = skill
    if experience_min: filters["experience_min"] = experience_min
    if experience_max: filters["experience_max"] = experience_max
    if location: filters["location"] = location
    if visa_status: filters["visa_status"] = visa_status
    if skill_score_min: filters["skill_score_min"] = skill_score_min
    if education: filters["education"] = education
    if degree: filters["degree"] = degree
    if major: filters["major"] = major
    if university: filters["university"] = university
    if gpa_min: filters["gpa_min"] = gpa_min
    if graduation_year_min: filters["graduation_year_min"] = graduation_year_min
    if certification: filters["certification"] = certification
    if language: filters["language"] = language
    if work_authorization: filters["work_authorization"] = work_authorization
    if remote_preference: filters["remote_preference"] = remote_preference
    if availability: filters["availability"] = availability
    if years_coding_min: filters["years_coding_min"] = years_coding_min
    
    return candidate_engine.search_candidates(filters)

@app.post("/api/candidate/{candidate_id}/skill-score")
async def update_skill_score(candidate_id: str, request: Request):
    """Update candidate skill score."""
    try:
        data = await request.json()
        result = candidate_engine.update_skill_score(candidate_id, data.get("score", 0), data.get("badge_id"))
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/candidates/stats")
async def candidate_pool_stats():
    """Get candidate pool statistics."""
    return candidate_engine.get_pool_stats()

@app.get("/candidate-signup", response_class=HTMLResponse)
async def candidate_signup_page(request: Request):
    """Candidate registration page."""
    return template_response("candidate-signup.html", request, "Join Charvak Talent Pool - Free")

@app.get("/demos", response_class=HTMLResponse)
async def demos_page(request: Request):
    """Product demo videos page."""
    return template_response("demos.html", request, "Product Demos - Charvak IT Consulting")

# ============================================================
# MESSAGING API ENDPOINTS
# ============================================================

@app.post("/api/messaging/send")
@limiter.limit("20/minute")
async def send_message(request: Request):
    """Send a message."""
    try:
        data = await request.json()
        result = messaging_engine.send_message(data)
        
        # Notify recipient via email (if email known)
        if result["status"] == "success" and data.get("recipient_email"):
            email_engine.notify_new_message(
                recipient_email=data.get("recipient_email", ""),
                recipient_name=data.get("recipient_name", ""),
                sender_name=data.get("sender_name", "Someone"),
                message_preview=data.get("body", "")
            )
        
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/messaging/inbox/{user_id}")
async def get_inbox(user_id: str):
    """Get user's inbox."""
    return messaging_engine.get_inbox(user_id)

@app.get("/api/messaging/conversation/{user_id}/{other_user_id}")
async def get_conversation(user_id: str, other_user_id: str):
    """Get conversation between two users."""
    return messaging_engine.get_conversation(user_id, other_user_id)

@app.get("/api/messaging/templates")
async def get_message_templates():
    """Get message templates."""
    return messaging_engine.get_templates()

@app.get("/api/messaging/stats")
async def messaging_stats():
    """Get messaging statistics."""
    return messaging_engine.get_stats()


# ============================================================
# EVENTS API ENDPOINTS
# ============================================================

@app.post("/api/events/create")
@limiter.limit("10/minute")
async def create_event(request: Request):
    """Create an event."""
    try:
        data = await request.json()
        result = events_engine.create_event(data)
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/events")
async def get_events(event_type: str = None):
    """Get upcoming events."""
    return events_engine.get_events(event_type)

@app.get("/api/events/stats")
async def events_stats():
    """Get event statistics."""
    return events_engine.get_stats()

@app.get("/api/events/{event_id}")
async def get_event(event_id: str):
    """Get event details."""
    return events_engine.get_event(event_id)

@app.post("/api/events/rsvp")
@limiter.limit("20/minute")
async def rsvp_event(request: Request):
    """RSVP to an event."""
    try:
        data = await request.json()
        result = events_engine.rsvp_to_event(data)
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/events/check-in")
async def check_in_event(request: Request):
    """Check in to an event."""
    try:
        data = await request.json()
        result = events_engine.check_in(data.get("rsvp_id"))
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ============================================================
# BRAND API ENDPOINTS
# ============================================================

@app.post("/api/brand/create")
@limiter.limit("10/minute")
async def create_brand_page(request: Request):
    """Create a company brand page."""
    try:
        data = await request.json()
        result = brand_engine.create_brand_page(data)
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/brand/companies")
async def get_all_brands():
    """Get all company brands."""
    return brand_engine.get_all_brands()

@app.get("/api/brand/stats")
async def brand_stats():
    """Get brand statistics."""
    return brand_engine.get_stats()

@app.get("/api/brand/{brand_id}")
async def get_brand(brand_id: str):
    """Get brand page with reviews."""
    return brand_engine.get_brand_page(brand_id)

@app.post("/api/brand/review")
@limiter.limit("10/minute")
async def post_review(request: Request):
    """Post an employer review."""
    try:
        data = await request.json()
        result = brand_engine.post_review(data)
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/brand/promote")
@limiter.limit("5/minute")
async def promote_job(request: Request):
    """Promote a job."""
    try:
        data = await request.json()
        result = brand_engine.promote_job(data.get("job_id"), data.get("company_id"))
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ============================================================
# EMAIL NOTIFICATION API ENDPOINTS
# ============================================================

@app.get("/api/email/stats")
async def email_stats():
    """Get email engine status."""
    return email_engine.get_stats()

@app.post("/api/email/test")
@limiter.limit("5/minute")
async def test_email(request: Request):
    """Send a test email."""
    try:
        data = await request.json()
        result = email_engine.send_email(
            to_email=data.get("email", "hr@charvakit.com"),
            subject="Charvak Email Test",
            body="This is a test email from Charvak IT Consulting."
        )
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/inbox", response_class=HTMLResponse)
async def inbox_page(request: Request):
    """Messaging inbox page."""
    return template_response("inbox.html", request, "Inbox - Charvak IT Consulting")

@app.get("/events", response_class=HTMLResponse)
async def events_page(request: Request):
    """Career events page."""
    return template_response("events.html", request, "Career Events - Charvak IT Consulting")

@app.get("/companies", response_class=HTMLResponse)
async def companies_page(request: Request):
    """Companies brand pages listing."""
    return template_response("companies.html", request, "Companies - Charvak IT Consulting")

@app.get("/companies/{brand_id}", response_class=HTMLResponse)
async def company_detail_page(request: Request, brand_id: str):
    """Single company profile page."""
    return template_response("company-detail.html", request, "Company Profile - Charvak", brand_id=brand_id)

# ============================================================
# TEAM API ENDPOINTS
# ============================================================

@app.post("/api/team/create")
@limiter.limit("10/minute")
async def create_team(request: Request):
    data = await request.json()
    return team_engine.create_team(data)

@app.get("/api/team/stats")
async def team_stats():
    return team_engine.get_stats()

@app.get("/api/team/{team_id}")
async def get_team(team_id: str):
    return team_engine.get_team(team_id)

@app.post("/api/team/invite")
@limiter.limit("20/minute")
async def invite_member(request: Request):
    data = await request.json()
    return team_engine.invite_member(data)


# ============================================================
# ATS API ENDPOINTS
# ============================================================

@app.post("/api/ats/connect")
@limiter.limit("5/minute")
async def connect_ats(request: Request):
    data = await request.json()
    return ats_engine.connect_external_ats(data)  # Changed from connect_ats

@app.get("/api/ats/integrations")
async def get_ats_integrations():
    return ats_engine.get_integrations()

@app.post("/api/ats/webhook/{integration_id}")
async def ats_webhook(integration_id: str, request: Request):
    data = await request.json()
    return ats_engine.receive_webhook(integration_id, data)

@app.get("/api/ats/stats")
async def ats_stats():
    return ats_engine.get_stats()


# ============================================================
# UNIVERSITY API ENDPOINTS
# ============================================================

@app.post("/api/university/register")
@limiter.limit("5/minute")
async def register_university(request: Request):
    data = await request.json()
    return university_engine.register_university(data)

@app.get("/api/university/{university_id}/dashboard")
async def university_dashboard(university_id: str):
    return university_engine.get_university_dashboard(university_id)

@app.get("/api/university/{university_id}/report")
async def first_destination_report(university_id: str):
    return university_engine.get_first_destination_report(university_id)

@app.post("/api/university/student/add")
@limiter.limit("20/minute")
async def add_student(request: Request):
    data = await request.json()
    return university_engine.add_student(data)

@app.post("/api/university/outcome/record")
@limiter.limit("20/minute")
async def record_outcome(request: Request):
    data = await request.json()
    return university_engine.record_outcome(data)

@app.get("/api/university/stats")
async def university_stats():
    return university_engine.get_stats()

@app.get("/ats", response_class=HTMLResponse)
async def ats_page(request: Request):
    return template_response("ats.html", request, "ATS Integration - Charvak IT Consulting")

@app.get("/university", response_class=HTMLResponse)
async def university_page(request: Request):
    return template_response("university.html", request, "University Portal - Charvak IT Consulting")

# ============================================================
# ENTERPRISE API ENDPOINTS
# ============================================================

@app.post("/api/enterprise/salary/record")
@limiter.limit("20/minute")
async def record_salary(request: Request):
    data = await request.json()
    return enterprise_engine.record_salary(data)

@app.get("/api/enterprise/salary/benchmarks")
async def salary_benchmarks(university: str = None, major: str = None, industry: str = None):
    filters = {}
    if university: filters["university"] = university
    if major: filters["major"] = major
    if industry: filters["industry"] = industry
    return enterprise_engine.get_salary_benchmarks(filters)

@app.post("/api/enterprise/pathway/create")
@limiter.limit("10/minute")
async def create_pathway(request: Request):
    data = await request.json()
    return enterprise_engine.create_pathway(data)

@app.post("/api/enterprise/resume/submit")
@limiter.limit("20/minute")
async def submit_resume(request: Request):
    data = await request.json()
    return enterprise_engine.submit_resume_for_review(data)

@app.post("/api/enterprise/resume/review")
@limiter.limit("20/minute")
async def review_resume(request: Request):
    data = await request.json()
    return enterprise_engine.review_resume(data.get("review_id"), data.get("decision"), data.get("comments", ""))

@app.get("/api/enterprise/resume/pending")
async def pending_reviews():
    return enterprise_engine.get_pending_reviews()

@app.post("/api/enterprise/appointment/book")
@limiter.limit("20/minute")
async def book_appointment(request: Request):
    data = await request.json()
    return enterprise_engine.create_appointment(data)

@app.get("/api/enterprise/appointments")
async def get_appointments(advisor_id: str = None):
    return enterprise_engine.get_appointments(advisor_id)

@app.post("/api/enterprise/employer/tier")
@limiter.limit("10/minute")
async def set_tier(request: Request):
    data = await request.json()
    return enterprise_engine.set_employer_tier(data)

@app.get("/api/enterprise/employers")
async def get_employers(tier: str = None):
    return enterprise_engine.get_employers_by_tier(tier)

@app.post("/api/enterprise/resume-book/create")
@limiter.limit("5/minute")
async def create_resume_book(request: Request):
    data = await request.json()
    return enterprise_engine.create_resume_book(data)

@app.post("/api/enterprise/survey/create")
@limiter.limit("5/minute")
async def create_survey(request: Request):
    data = await request.json()
    return enterprise_engine.create_survey(data)

@app.post("/api/enterprise/kiosk/start")
@limiter.limit("5/minute")
async def start_kiosk(request: Request):
    data = await request.json()
    return enterprise_engine.start_kiosk(data)

@app.post("/api/enterprise/kiosk/check-in")
async def kiosk_check_in(request: Request):
    data = await request.json()
    return enterprise_engine.kiosk_check_in(data.get("kiosk_id"), data.get("student_id"))

@app.get("/api/enterprise/stats")
async def enterprise_stats():
    return enterprise_engine.get_stats()

# ============================================================
# MARKETING AI API ENDPOINTS
# ============================================================

@app.post("/api/marketing/job-ad")
@limiter.limit("10/minute")
async def generate_job_ad(request: Request):
    data = await request.json()
    return await marketing_ai_engine.generate_job_ad(data)

@app.post("/api/marketing/social-post")
@limiter.limit("20/minute")
async def generate_social_post(request: Request):
    data = await request.json()
    return await marketing_ai_engine.generate_social_post(data)

@app.post("/api/marketing/lead-drip")
@limiter.limit("10/minute")
async def create_lead_drip(request: Request):
    data = await request.json()
    return await marketing_ai_engine.create_lead_drip(data)

@app.get("/api/marketing/stats")
async def marketing_ai_stats():
    return marketing_ai_engine.get_stats()

@app.get("/marketing-ai", response_class=HTMLResponse)
async def marketing_ai_page(request: Request):
    return template_response("marketing-ai.html", request, "Marketing AI - Charvak IT Consulting")

# ============================================================
# INDIAN LANGUAGE AI API ENDPOINTS
# ============================================================

@app.get("/api/indian-languages")
async def get_indian_languages():
    """Get supported Indian languages."""
    return indian_language_ai.get_languages()

@app.post("/api/indian-languages/assessment")
@limiter.limit("10/minute")
async def create_language_assessment(request: Request):
    """Create assessment in Indian language."""
    data = await request.json()
    return indian_language_ai.create_assessment(data)

@app.post("/api/indian-languages/submit")
@limiter.limit("20/minute")
async def submit_language_assessment(request: Request):
    """Submit assessment answers."""
    data = await request.json()
    return indian_language_ai.submit_assessment(data)

@app.post("/api/indian-languages/translate")
@limiter.limit("20/minute")
async def translate_job_ad(request: Request):
    """Translate job ad to Indian language."""
    data = await request.json()
    return indian_language_ai.translate_job_ad(data)

@app.get("/api/indian-languages/stats")
async def indian_language_stats():
    """Get Indian Language AI statistics."""
    return indian_language_ai.get_stats()

@app.get("/indian-language-ai", response_class=HTMLResponse)
async def indian_language_ai_page(request: Request):
    return template_response("indian-language-ai.html", request, "Indian Language AI - Charvak IT Consulting")

# ============================================================
# LMS API ENDPOINTS (Global Learning Management System)
# ============================================================

@app.post("/api/lms/rate")
@limiter.limit("20/minute")
async def rate_course(request: Request):
    data = await request.json()
    return lms_engine.rate_course(data)

@app.get("/api/lms/ratings/{course_id}")
async def get_course_ratings(course_id: str):
    return lms_engine.get_course_ratings(course_id)

@app.post("/api/lms/quiz/create")
@limiter.limit("10/minute")
async def create_quiz(request: Request):
    data = await request.json()
    return lms_engine.create_quiz(data)

@app.post("/api/lms/quiz/submit")
@limiter.limit("20/minute")
async def submit_quiz(request: Request):
    data = await request.json()
    return lms_engine.submit_quiz(data)

@app.post("/api/lms/certificate/issue")
@limiter.limit("10/minute")
async def issue_certificate(request: Request):
    data = await request.json()
    return lms_engine.issue_certificate(data)

@app.get("/api/lms/certificate/verify/{cert_id}")
async def verify_certificate(cert_id: str):
    return lms_engine.verify_certificate(cert_id)

@app.post("/api/lms/progress/update")
@limiter.limit("20/minute")
async def update_progress(request: Request):
    data = await request.json()
    return lms_engine.update_progress(data)

@app.get("/api/lms/progress/{enrollment_id}")
async def get_progress(enrollment_id: str):
    return lms_engine.get_progress(enrollment_id)

@app.post("/api/lms/discussion/post")
@limiter.limit("20/minute")
async def post_discussion(request: Request):
    data = await request.json()
    return lms_engine.post_discussion(data)

@app.post("/api/lms/discussion/reply")
@limiter.limit("20/minute")
async def reply_discussion(request: Request):
    data = await request.json()
    return lms_engine.reply_discussion(data)

@app.get("/api/lms/recommendations/{student_email}")
async def get_recommendations(student_email: str):
    return lms_engine.get_recommendations(student_email)

@app.get("/api/lms/stats")
async def lms_stats():
    return lms_engine.get_stats()

@app.get("/lms", response_class=HTMLResponse)
async def lms_page(request: Request):
    return template_response("lms.html", request, "Learning Management System - Charvak IT Consulting")

# LMS — Additional Features
@app.post("/api/lms/lesson/add")
@limiter.limit("20/minute")
async def add_lesson(request: Request):
    data = await request.json()
    return lms_engine.add_lesson(data)

@app.get("/api/lms/lessons/{course_id}")
async def get_lessons(course_id: str):
    return lms_engine.get_course_lessons(course_id)

@app.post("/api/lms/payout/request")
@limiter.limit("10/minute")
async def request_payout(request: Request):
    data = await request.json()
    return lms_engine.request_payout(data)

@app.get("/api/lms/payouts/{trainer_email}")
async def get_payouts(trainer_email: str):
    return lms_engine.get_payouts(trainer_email)

@app.post("/api/lms/language/add")
@limiter.limit("10/minute")
async def add_course_language(request: Request):
    data = await request.json()
    return lms_engine.add_course_language(data)

@app.post("/api/lms/gamification/points")
@limiter.limit("20/minute")
async def award_points(request: Request):
    data = await request.json()
    return lms_engine.award_points(data)

@app.post("/api/lms/notify")
@limiter.limit("20/minute")
async def send_course_notification(request: Request):
    data = await request.json()
    return lms_engine.send_course_notification(data)

@app.get("/api/lms/search")
async def search_courses(query: str = None, category: str = None, max_price: float = None, language: str = None):
    return lms_engine.search_courses(query, category, None, max_price, language)

# ============================================================
# CAREER V2 API ENDPOINTS
# ============================================================

@app.post("/api/career/alert")
@limiter.limit("10/minute")
async def create_job_alert(request: Request):
    data = await request.json()
    return career_v2_engine.create_job_alert(data)

@app.get("/api/career/alerts/{email}")
async def get_alerts(email: str):
    return career_v2_engine.get_alerts(email)

@app.post("/api/career/save-job")
@limiter.limit("20/minute")
async def save_job(request: Request):
    data = await request.json()
    return career_v2_engine.save_job(data)

@app.post("/api/career/follow-company")
@limiter.limit("20/minute")
async def follow_company(request: Request):
    data = await request.json()
    return career_v2_engine.follow_company(data)

@app.post("/api/career/salary")
@limiter.limit("10/minute")
async def add_salary(request: Request):
    data = await request.json()
    return career_v2_engine.add_salary(data)

@app.get("/api/career/salary-insights")
async def get_salary_insights(role: str = None):
    return career_v2_engine.get_salary_insights(role)

@app.post("/api/career/interview")
@limiter.limit("10/minute")
async def schedule_interview(request: Request):
    data = await request.json()
    return career_v2_engine.schedule_interview(data)

@app.post("/api/career/offer")
@limiter.limit("10/minute")
async def add_offer(request: Request):
    data = await request.json()
    return career_v2_engine.add_offer(data)

@app.get("/api/career/recommendations/{email}")
async def get_job_recommendations(email: str):
    return career_v2_engine.get_job_recommendations(email)

@app.get("/api/career-v2/stats")
async def career_v2_stats():
    return career_v2_engine.get_stats()

@app.get("/career-center", response_class=HTMLResponse)
async def career_center_page(request: Request):
    return template_response("career-v2.html", request, "Career Center - Charvak IT Consulting")

# Micro-Internship Global

@app.post("/api/micro-internship/global/post")
@limiter.limit("10/minute")
async def post_global_project(request: Request):
    data = await request.json()
    return micro_internship_global.post_global_project(data)

@app.post("/api/micro-internship/global/mentor")
@limiter.limit("10/minute")
async def assign_mentor(request: Request):
    data = await request.json()
    return micro_internship_global.assign_mentor(data)

@app.get("/api/micro-internship/global/projects")
async def filter_global_projects(country: str = None, mode: str = None):
    filters = {}
    if country: filters["country"] = country
    if mode: filters["mode"] = mode
    return micro_internship_global.filter_projects(filters)

@app.get("/api/micro-internship/global/stats")
async def global_micro_stats():
    return micro_internship_global.get_stats()

# ============================================================
# ASSESSMENT REPORT API ENDPOINTS
# ============================================================
@app.post("/api/report/generate")
@limiter.limit("20/minute")
async def generate_report(request: Request):
    data = await request.json()
    return assessment_report_engine.generate_report(data)

@app.get("/api/report/stats")
async def report_stats():
    return assessment_report_engine.get_stats()

@app.get("/api/report/{report_id}")
async def get_report(report_id: str):
    return assessment_report_engine.get_report(report_id)

@app.get("/api/report/verify/{verification_id}")
async def verify_report(verification_id: str):
    return assessment_report_engine.verify_report(verification_id)

@app.get("/api/report/candidate/{email}")
async def get_candidate_reports(email: str):
    return assessment_report_engine.get_candidate_reports(email)

@app.get("/reports", response_class=HTMLResponse)
async def reports_page(request: Request):
    return template_response("reports.html", request, "Assessment Reports - Charvak IT Consulting")

# ============================================================
# SECURITY API ENDPOINTS
# ============================================================

@app.get("/api/security/stats")
async def security_stats():
    """Get security statistics."""
    return security_manager.get_security_stats()

@app.post("/api/security/blacklist")
async def blacklist_ip(request: Request):
    """Blacklist an IP (admin only)."""
    try:
        data = await request.json()
        # Require API key for this action
        api_key = request.headers.get("X-API-Key", "")
        if not security_manager.validate_api_key(api_key):
            return JSONResponse({"status": "error", "message": "Invalid API key"}, status_code=401)
        
        ip = data.get("ip")
        reason = data.get("reason", "manual_blacklist")
        security_manager.blacklist_ip(ip, reason)
        return {"status": "success", "message": f"IP {ip} blacklisted"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ============================================================
# BRIDGE ENGINE API ENDPOINTS
# ============================================================

@app.post("/api/bridge/start")
@limiter.limit("10/minute")
async def start_bridge(request: Request):
    data = await request.json() if request.body() else {}
    return bridge_engine.start_journey(data)

@app.post("/api/bridge/answer")
@limiter.limit("20/minute")
async def submit_bridge_answer(request: Request):
    data = await request.json()
    return bridge_engine.submit_answer(data)

@app.post("/api/bridge/revenue")
@limiter.limit("10/minute")
async def calculate_bridge_revenue(request: Request):
    data = await request.json()
    return bridge_engine.calculate_revenue(data)

@app.get("/api/bridge/stats")
async def bridge_stats():
    return bridge_engine.get_stats()


# ============================================================
# AI BRIDGE ENGINE API ENDPOINTS
# ============================================================

@app.post("/api/ai-bridge/start")
@limiter.limit("10/minute")
async def start_ai_bridge(request: Request):
    data = await request.json()
    return ai_bridge_engine.start_ai_assessment(data)

@app.post("/api/ai-bridge/answer")
@limiter.limit("20/minute")
async def submit_ai_answer(request: Request):
    data = await request.json()
    return ai_bridge_engine.submit_ai_answer(data)

@app.post("/api/ai-bridge/premium")
@limiter.limit("5/minute")
async def get_premium_report(request: Request):
    data = await request.json()
    return ai_bridge_engine.get_premium_report(data.get("session_id"))

@app.get("/api/ai-bridge/stats")
async def ai_bridge_stats():
    return ai_bridge_engine.get_stats()

@app.get("/ai-assessment", response_class=HTMLResponse)
async def ai_assessment_page(request: Request):
    return template_response("ai-bridge.html", request, "AI Career Assessment - Charvak IT Consulting")

@app.get("/bridge", response_class=HTMLResponse)
async def bridge_page(request: Request):
    """Bridge career journey page."""
    return template_response("bridge.html", request, "Bridge - Career Journey - Charvak IT Consulting")

# Student Suite

@app.post("/api/student/subscribe")
@limiter.limit("10/minute")
async def student_subscribe(request: Request):
    data = await request.json()
    email = data.get("email") or data.get("student_email")
    plan = data.get("plan", "free")
    return student_suite_engine.subscribe(email=email, plan=plan)

@app.get("/api/student/plan/{email}")
async def get_student_plan(email: str):
    return student_suite_engine.get_plan(email)

@app.post("/api/student/assignment")
@limiter.limit("20/minute")
async def assist_assignment(request: Request):
    data = await request.json()
    email = data.get("email") or data.get("student_email")
    subject = data.get("subject", "")
    topic = data.get("topic", "")
    return student_suite_engine.assist_assignment(email=email, subject=subject, topic=topic)

@app.post("/api/student/research")
@limiter.limit("20/minute")
async def assist_research(request: Request):
    data = await request.json()
    email = data.get("email") or data.get("student_email")
    field = data.get("field", "")
    topic = data.get("topic", "")
    return student_suite_engine.assist_research(email=email, field=field, topic=topic)

@app.get("/api/student/stats")
async def student_suite_stats():
    return student_suite_engine.get_stats()

@app.get("/student-suite", response_class=HTMLResponse)
async def student_suite_page(request: Request):
    return template_response("student-suite.html", request, "AI Student Suite - Charvak IT Consulting")

@app.post("/api/profile/create")
@limiter.limit("10/minute")
async def create_master_profile(request: Request):
    data = await request.json()
    return profile_network_engine.create_master_profile(data)

@app.get("/api/profile/{email}")
async def get_master_profile(email: str):
    return profile_network_engine.get_master_profile(email)

@app.post("/api/alumni/add")
@limiter.limit("10/minute")
async def add_alumni(request: Request):
    data = await request.json()
    return profile_network_engine.add_alumni_connection(data)

@app.get("/api/alumni/find")
async def find_alumni(university: str = None, company: str = None):
    return profile_network_engine.find_alumni(university, company)

@app.post("/api/referral/match")
@limiter.limit("10/minute")
async def find_referral(request: Request):
    data = await request.json()
    return profile_network_engine.find_referral_match(data)

@app.get("/api/profile-network/stats")
async def profile_network_stats():
    return profile_network_engine.get_stats()

@app.get("/profile-network", response_class=HTMLResponse)
async def profile_network_page(request: Request):
    return template_response("profile-network.html", request, "Profile & Network - Charvak IT Consulting")

# ============================================================
# DOKETSRB INTEGRATION API ENDPOINTS
# ============================================================

@app.get("/api/doketsrb/links")
async def get_doketsrb_links():
    return doketsrb_integration.get_deep_links()

@app.get("/api/doketsrb/banner")
async def get_doketsrb_banner(context: str = "career"):
    return doketsrb_integration.get_promotional_banner(context)

@app.post("/api/doketsrb/bundle")
@limiter.limit("10/minute")
async def subscribe_doketsrb_bundle(request: Request):
    data = await request.json()
    return doketsrb_integration.subscribe_bundle(data)

@app.get("/api/doketsrb/bundles")
async def get_doketsrb_bundles():
    return doketsrb_integration.get_bundles()

@app.get("/team-dashboard", response_class=HTMLResponse)
async def team_dashboard_page(request: Request):
    return template_response("team-dashboard.html", request, "Team Dashboard - Charvak IT Consulting")

@app.get("/payments", response_class=HTMLResponse)
async def payments_page(request: Request):
    return template_response("payments.html", request, "Payments - Charvak IT Consulting")

# ============================================================
# OUTREACH ENGINE API ENDPOINTS
# ============================================================

@app.post("/api/outreach/cold-email")
@limiter.limit("10/minute")
async def find_cold_email(request: Request):
    data = await request.json()
    return outreach_engine.find_hiring_manager_email(data)

@app.post("/api/outreach/gmail-sync")
@limiter.limit("5/minute")
async def connect_gmail_sync(request: Request):
    data = await request.json()
    return outreach_engine.connect_gmail(data)

@app.post("/api/outreach/auto-track")
@limiter.limit("20/minute")
async def auto_track_application(request: Request):
    data = await request.json()
    return outreach_engine.auto_track_application(data)

@app.get("/api/outreach/tracked/{email}")
async def get_tracked_applications(email: str):
    return outreach_engine.get_tracked_applications(email)

@app.post("/api/outreach/premium")
@limiter.limit("5/minute")
async def subscribe_outreach_premium(request: Request):
    data = await request.json()
    return outreach_engine.subscribe_premium(data)

@app.get("/api/outreach/stats")
async def outreach_stats():
    return outreach_engine.get_stats()

@app.get("/outreach", response_class=HTMLResponse)
async def outreach_page(request: Request):
    return template_response("outreach.html", request, "Outreach Tools - Charvak IT Consulting")

@app.get("/how-it-works", response_class=HTMLResponse)
async def how_it_works_page(request: Request):
    return template_response("how-it-works.html", request, "How It Works - Charvak IT Consulting")

@app.get("/admin-control", response_class=HTMLResponse)
async def admin_control_center(request: Request):
    """Admin Control Center — hr@charvakit.com"""
    return template_response("admin-unified.html", request, "Admin Control Center - Charvak")

@app.get("/admin-login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    """Admin login page."""
    return template_response("admin-login.html", request, "Admin Login - Charvak")

@app.post("/api/auth/reset-password")
async def reset_password(request: Request):
    """Reset password for admin (temporary endpoint)."""
    try:
        data = await request.json()
        email = data.get("email")
        new_password = data.get("new_password", "Charvak@2026")
        
        if email != "hr@charvakit.com":
            return JSONResponse({"status": "error", "message": "Only admin email allowed"}, status_code=403)
        
        from auth import hash_password
        hashed = hash_password(new_password)
        
        import psycopg2
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        cursor = conn.cursor()
        
        # Create users table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(50) UNIQUE,
                email VARCHAR(255) UNIQUE,
                password_hash TEXT,
                name VARCHAR(255),
                phone VARCHAR(50),
                role VARCHAR(50) DEFAULT 'candidate',
                created_at TIMESTAMP DEFAULT NOW()
            )
        ''')
        conn.commit()
        
        # Update or create user
        cursor.execute("UPDATE users SET password_hash = %s, role = 'admin' WHERE email = %s", (hashed, email))
        if cursor.rowcount == 0:
            cursor.execute(
                "INSERT INTO users (user_id, email, password_hash, name, phone, role) VALUES (%s, %s, %s, %s, %s, %s)",
                (secrets.token_hex(8), email, hashed, "Charvak Admin", "+91 799 7871 701", "admin")
            )
        conn.commit()
        cursor.close()
        conn.close()
        
        return JSONResponse({"status": "success", "message": f"Password reset to {new_password}"})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)})

@app.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    return template_response("forgot-password.html", request, "Forgot Password - Charvak")

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return template_response("login.html", request, "Login - Charvak")

# ============================================================
# DATA LIFECYCLE API ENDPOINTS
# ============================================================

@app.post("/api/lifecycle/expire-jobs")
async def expire_jobs():
    """Expire old jobs."""
    return data_lifecycle.expire_old_jobs()

@app.get("/api/lifecycle/inactive-candidates")
async def inactive_candidates():
    """Get inactive candidates."""
    return data_lifecycle.check_inactive_candidates()

@app.delete("/api/lifecycle/delete-user")
async def delete_user(request: Request):
    """GDPR: Delete user data."""
    data = await request.json()
    return data_lifecycle.delete_user_data(data.get("email"))

@app.post("/api/lifecycle/send-reminders")
async def send_reminders():
    """Send renewal reminders."""
    return data_lifecycle.send_renewal_reminders()

@app.get("/api/lifecycle/export/{email}")
async def export_user(email: str):
    """GDPR: Export user data."""
    return data_lifecycle.export_user_data(email)

@app.get("/api/lifecycle/stats")
async def lifecycle_stats():
    """Get lifecycle statistics."""
    return data_lifecycle.get_stats()

# FYP — AI-Powered
@app.post("/api/fyp/suggest-topics")
@limiter.limit("10/minute")
async def suggest_fyp_topics(request: Request):
    data = await request.json()
    return final_year_project_engine.suggest_topics_ai(data)

@app.post("/api/fyp/generate-proposal")
@limiter.limit("10/minute")
async def generate_fyp_proposal(request: Request):
    data = await request.json()
    return final_year_project_engine.generate_proposal_ai(data)

@app.post("/api/fyp/generate-documentation")
@limiter.limit("5/minute")
async def generate_fyp_documentation(request: Request):
    data = await request.json()
    return final_year_project_engine.generate_documentation_ai(data)

@app.post("/api/fyp/viva-questions")
@limiter.limit("10/minute")
async def fyp_viva_questions(request: Request):
    data = await request.json()
    return final_year_project_engine.generate_viva_ai(data)

@app.post("/api/fyp/subscribe")
@limiter.limit("10/minute")
async def fyp_subscribe(request: Request):
    data = await request.json()
    return final_year_project_engine.subscribe(data)

@app.get("/api/fyp/plans")
async def fyp_plans():
    return final_year_project_engine.get_plans()

@app.get("/api/fyp/stats")
async def fyp_stats():
    return final_year_project_engine.get_stats()

@app.get("/final-year-project", response_class=HTMLResponse)
async def fyp_page(request: Request):
    return template_response("final-year-project.html", request, "Final Year Project Assistant - Charvak")

# ============================================================
# AI CREDIT SYSTEM API
# ============================================================
@app.get("/api/credits/plans")
async def credit_plans():
    """Get all credit plans."""
    return {
        "status": "success",
        "plans": ai_credit_engine.get_plans()
    }

@app.get("/api/credits/admin/stats")
async def credit_admin_stats():
    """Admin credit statistics."""
    return ai_credit_engine.get_admin_stats()

@app.get("/api/credits/expiry/{email}")
async def check_expiry(email: str):
    """Check credit expiry."""
    return ai_credit_engine.check_expiry(email)

@app.get("/api/credits/usage/{email}")
async def usage_history(email: str):
    """Get usage history."""
    return ai_credit_engine.get_user_usage_history(email)

@app.get("/api/credits/{email}")
async def get_user_credits(email: str):
    """Get user's credit balance."""
    return ai_credit_engine.get_user_credits(email)

@app.post("/api/credits/check")
@limiter.limit("20/minute")
async def check_credits(request: Request):
    """Check and deduct credits for AI usage."""
    data = await request.json()
    return ai_credit_engine.check_and_deduct(data.get("email"), data.get("feature"))

@app.post("/api/credits/purchase")
@limiter.limit("10/minute")
async def purchase_credits(request: Request):
    """Purchase credit plan."""
    data = await request.json()
    return ai_credit_engine.purchase_credits(data.get("email"), data.get("plan"))

@app.post("/api/credits/daily-bonus")
@limiter.limit("5/minute")
async def daily_bonus(request: Request):
    """Claim daily bonus."""
    data = await request.json()
    return ai_credit_engine.apply_daily_bonus(data.get("email"))

# ============================================================
# AI CREDITS PAGES & NOTIFICATIONS
# ============================================================

@app.get("/ai-credits-pricing")
async def ai_credits_pricing_page(request: Request):
    """AI Credits pricing page."""
    return templates.TemplateResponse("ai_credits_pricing.html", {"request": request})

@app.get("/credit-dashboard")
async def credit_dashboard_page(request: Request):
    """Credit dashboard page."""
    return templates.TemplateResponse("credit_dashboard.html", {"request": request})

@app.post("/api/notifications/check")
@limiter.limit("10/minute")
async def check_notifications(request: Request):
    """Check and send notifications."""
    data = await request.json()
    email = data.get("email")
    
    # Check credits
    credits = ai_credit_engine.get_user_credits(email)
    low_credit_result = notification_engine.notify_low_credits(
        email, credits["credits_remaining"]
    )
    
    # Check expiry
    expiry = ai_credit_engine.check_expiry(email)
    expiry_result = {"status": "skipped"}
    if expiry["status"] in ["expired", "expiring_soon"]:
        expiry_result = notification_engine.notify_expiry(
            email, expiry.get("days_remaining", 0)
        )
    
    return {
        "status": "success",
        "low_credit": low_credit_result,
        "expiry": expiry_result
    }

@app.get("/api/notifications/history/{email}")
async def notification_history(email: str):
    """Get notification history for user."""
    return notification_engine.get_notification_history(email)

@app.get("/api/notifications/stats")
async def notification_stats():
    """Get notification statistics."""
    return notification_engine.get_stats()

# ============================================================
# UTILITY ENDPOINTS
# ============================================================

@app.get("/sitemap.xml")
async def sitemap():
    sitemap_path = "templates/sitemap.xml"
    if os.path.exists(sitemap_path):
        return FileResponse(sitemap_path, media_type="application/xml")
    return JSONResponse({"error": "Sitemap not found"}, status_code=404)

@app.get("/api/region")
async def detect_region(request: Request):
    try:
        accept_lang = request.headers.get("accept-language", "en")
        region = detect_user_region(accept_language=accept_lang)
        return JSONResponse(region)
    except Exception:
        return JSONResponse({"country": "US", "currency": "USD", "language": "en"})

@app.get("/api/pricing/{service}")
async def get_service_pricing(service: str, request: Request, currency: str = "INR", country: str = "IN"):
    try:
        pricing = get_pricing(service, currency, country)
        return JSONResponse(pricing)
    except Exception:
        return JSONResponse({"error": "Pricing not available"})

@app.get("/doketsrb", response_class=HTMLResponse)
async def doketsrb_page(request: Request):
    return template_response("doketsrb.html", request, "DoketsRB Suite - Charvak IT Consulting")


# ============================================================
# HEALTH CHECKS
# ============================================================

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/health")
async def api_health_check():
    return {"status": "ok", "api": "v1", "timestamp": datetime.now().isoformat()}


# ============================================================
# GLOBAL EXCEPTION HANDLER
# ============================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP {exc.status_code}: {exc.detail} - {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "message": exc.detail}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error at {request.url}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": "An unexpected error occurred. Our team has been notified."}
    )

