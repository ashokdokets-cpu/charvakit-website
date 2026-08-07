from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, PlainTextResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import json
from api_sync import (
    handle_resume_sync, handle_application_sync, handle_get_jobs,
    handle_skill_sync, handle_get_status, api_health,
    ResumeSync, ApplicationSync, SkillGapSync, verify_api_key
)
from auth import register_user, login_user, logout_user, verify_token, get_current_user
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
from fastapi.middleware.cors import CORSMiddleware
from na_module.work_auth import work_auth_engine, VisaType

app = FastAPI(title="Charvak IT Consulting Pvt Ltd - Web Designing | Staff Augmentation")

# CORS - Allow DoketsRB to access Charvakit API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://www.doketsrb.com",
        "https://doketsrb.com",
        "http://localhost:3000",
        "http://127.0.0.1:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "Charvak IT Consulting Pvt Ltd - Web Designing | Staff Augmentation"})

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request, "title": "About Charvak IT Consulting Pvt Ltd"})

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
    return templates.TemplateResponse("services.html", {"request": request, "title": "Our Services", "services": services_data})

@app.get("/services/web-design", response_class=HTMLResponse)
async def web_design(request: Request):
    return templates.TemplateResponse("web-design.html", {"request": request, "title": "Web Designing Services"})

@app.get("/services/staff-augmentation", response_class=HTMLResponse)
async def staff_augmentation(request: Request):
    return templates.TemplateResponse("staff-augmentation.html", {"request": request, "title": "Staff Augmentation Services"})

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
    return templates.TemplateResponse("products-list.html", {"request": request, "title": "All Products - Charvak", "products": products_data})

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
    return templates.TemplateResponse("products.html", {"request": request, "title": "Dokets VouchAI - AI Escrow Platform", "product": product})

@app.get("/team", response_class=HTMLResponse)
async def team(request: Request):
    return templates.TemplateResponse("team.html", {"request": request, "title": "Our Team"})

@app.get("/careers", response_class=HTMLResponse)
async def careers(request: Request):
    return templates.TemplateResponse("careers.html", {"request": request, "title": "Careers at Charvak"})

@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request, "title": "Contact Us"})

@app.get("/terms", response_class=HTMLResponse)
async def terms(request: Request):
    return templates.TemplateResponse("terms.html", {"request": request, "title": "Terms & Conditions"})

@app.get("/privacy", response_class=HTMLResponse)
async def privacy(request: Request):
    return templates.TemplateResponse("privacy.html", {"request": request, "title": "Privacy Policy"})

@app.get("/refund", response_class=HTMLResponse)
async def refund(request: Request):
    return templates.TemplateResponse("refund.html", {"request": request, "title": "Refund & Cancellation Policy"})

@app.get("/voice-to-web", response_class=HTMLResponse)
async def voice_to_web(request: Request):
    return templates.TemplateResponse("voice-to-web.html", {"request": request, "title": "Voice-to-Web Engine - Charvak"})

# WhatsApp Webhook - Verification
@app.get("/webhook/whatsapp")
async def verify_whatsapp(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return PlainTextResponse(challenge)
    return JSONResponse({"error": "Verification failed"}, status_code=403)

# WhatsApp Webhook - Messages
@app.post("/webhook/whatsapp")
async def receive_whatsapp(request: Request):
    data = await request.json()
    await whatsapp_handler(data)
    return {"status": "ok"}

# Serve generated sites
@app.get("/sites/{site_id}")
async def view_site(site_id: str):
    site_path = f"static/sites/{site_id}.html"
    if os.path.exists(site_path):
        return FileResponse(site_path)
    return HTMLResponse("<h1>Site not found</h1>", status_code=404)

@app.get("/cloud-waste-calculator", response_class=HTMLResponse)
async def cloud_waste_calculator(request: Request):
    return templates.TemplateResponse("cloud-waste-calculator.html", {"request": request, "title": "Cloud Waste Calculator - Charvak"})

@app.get("/lock-in-breaker", response_class=HTMLResponse)
async def lock_in_breaker(request: Request):
    return templates.TemplateResponse("lock-in-breaker.html", {"request": request, "title": "Vendor Lock-In Breaker - Charvak"})

@app.get("/lock-in-breaker-pricing", response_class=HTMLResponse)
async def lock_in_breaker_pricing(request: Request):
    return templates.TemplateResponse("lock-in-breaker-pricing.html", {"request": request, "title": "Lock-In Breaker Plans - Charvak"})

@app.get("/reverse-staffing", response_class=HTMLResponse)
async def reverse_staffing(request: Request):
    return templates.TemplateResponse("reverse-staffing.html", {"request": request, "title": "Reverse Staffing - Charvak"})

@app.get("/code-quality-checker", response_class=HTMLResponse)
async def code_quality_checker(request: Request):
    return templates.TemplateResponse("code-quality-checker.html", {"request": request, "title": "Code Quality Checker - Charvak"})

@app.get("/developer-signup", response_class=HTMLResponse)
async def developer_signup(request: Request):
    return templates.TemplateResponse("developer-signup.html", {"request": request, "title": "Join Developer Pool - Charvak"})

@app.get("/hire-talent", response_class=HTMLResponse)
async def hire_talent(request: Request):
    return templates.TemplateResponse("hire-talent.html", {"request": request, "title": "Hire Vetted Talent - Charvak"})

@app.get("/auditbot", response_class=HTMLResponse)
async def auditbot(request: Request):
    return templates.TemplateResponse("auditbot.html", {"request": request, "title": "AuditBot - Charvak"})

@app.get("/digital-health-checker", response_class=HTMLResponse)
async def digital_health_checker(request: Request):
    return templates.TemplateResponse("digital-health-checker.html", {"request": request, "title": "Digital Health Checker - Charvak"})

@app.get("/neural-wireframe", response_class=HTMLResponse)
async def neural_wireframe(request: Request):
    return templates.TemplateResponse("neural-wireframe.html", {"request": request, "title": "Neural Wireframe-to-Prod - Charvak"})

@app.get("/napkin-challenge", response_class=HTMLResponse)
async def napkin_challenge(request: Request):
    return templates.TemplateResponse("napkin-challenge.html", {"request": request, "title": "Napkin-to-Live Challenge - Charvak"})

@app.get("/skill-twin", response_class=HTMLResponse)
async def skill_twin(request: Request):
    return templates.TemplateResponse("skill-twin.html", {"request": request, "title": "Skill-Twin Engine - Charvak"})

@app.get("/skill-check", response_class=HTMLResponse)
async def skill_check(request: Request):
    return templates.TemplateResponse("skill-check.html", {"request": request, "title": "Free Skill Check - Charvak"})

@app.get("/globalize", response_class=HTMLResponse)
async def globalize_ai(request: Request):
    return templates.TemplateResponse("globalize.html", {"request": request, "title": "Globalize.ai - Charvak"})

@app.get("/revenue-leak-detector", response_class=HTMLResponse)
async def revenue_leak_detector(request: Request):
    return templates.TemplateResponse("revenue-leak-detector.html", {"request": request, "title": "Revenue Leak Detector - Charvak"})

@app.get("/micro-squads", response_class=HTMLResponse)
async def micro_squads(request: Request):
    return templates.TemplateResponse("micro-squads.html", {"request": request, "title": "Micro-Squads - Charvak"})

@app.get("/scope-simulator", response_class=HTMLResponse)
async def scope_simulator(request: Request):
    return templates.TemplateResponse("scope-simulator.html", {"request": request, "title": "Scope Simulator - Charvak"})

@app.get("/agency-twin", response_class=HTMLResponse)
async def agency_twin(request: Request):
    return templates.TemplateResponse("agency-twin.html", {"request": request, "title": "Agency-Twin - Charvak"})

@app.get("/burnout-calculator", response_class=HTMLResponse)
async def burnout_calculator(request: Request):
    return templates.TemplateResponse("burnout-calculator.html", {"request": request, "title": "Burnout Calculator - Charvak"})

@app.get("/geo-compliance", response_class=HTMLResponse)
async def geo_compliance(request: Request):
    return templates.TemplateResponse("geo-compliance.html", {"request": request, "title": "Geo-Compliance Shield - Charvak"})

@app.get("/contract-risk-radar", response_class=HTMLResponse)
async def contract_risk_radar(request: Request):
    return templates.TemplateResponse("contract-risk-radar.html", {"request": request, "title": "Contract Risk Radar - Charvak"})

@app.get("/design-token-sentinel", response_class=HTMLResponse)
async def design_token_sentinel(request: Request):
    return templates.TemplateResponse("design-token-sentinel.html", {"request": request, "title": "Design-Token Sentinel - Charvak"})

@app.get("/brand-drift-inspector", response_class=HTMLResponse)
async def brand_drift_inspector(request: Request):
    return templates.TemplateResponse("brand-drift-inspector.html", {"request": request, "title": "Brand Drift Inspector - Charvak"})

@app.get("/legacy-shift", response_class=HTMLResponse)
async def legacy_shift(request: Request):
    return templates.TemplateResponse("legacy-shift.html", {"request": request, "title": "Legacy-Shift Archaeologist - Charvak"})

@app.get("/time-machine-checker", response_class=HTMLResponse)
async def time_machine_checker(request: Request):
    return templates.TemplateResponse("time-machine-checker.html", {"request": request, "title": "Time Machine Checker - Charvak"})

@app.get("/agent-ready", response_class=HTMLResponse)
async def agent_ready(request: Request):
    return templates.TemplateResponse("agent-ready.html", {"request": request, "title": "Agent-Ready Wrapper - Charvak"})

@app.get("/ai-commerce-scorecard", response_class=HTMLResponse)
async def ai_commerce_scorecard(request: Request):
    return templates.TemplateResponse("ai-commerce-scorecard.html", {"request": request, "title": "AI Commerce Scorecard - Charvak"})

@app.get("/silent-killer", response_class=HTMLResponse)
async def silent_killer(request: Request):
    return templates.TemplateResponse("silent-killer.html", {"request": request, "title": "Silent-Killer Sentinel - Charvak"})

@app.get("/dead-link-auditor", response_class=HTMLResponse)
async def dead_link_auditor(request: Request):
    return templates.TemplateResponse("dead-link-auditor.html", {"request": request, "title": "Dead Link Auditor - Charvak"})

@app.get("/ai-slop-quarantine", response_class=HTMLResponse)
async def ai_slop_quarantine(request: Request):
    return templates.TemplateResponse("ai-slop-quarantine.html", {"request": request, "title": "AI-Slop Quarantine - Charvak"})

@app.get("/ai-contamination-detector", response_class=HTMLResponse)
async def ai_contamination_detector(request: Request):
    return templates.TemplateResponse("ai-contamination-detector.html", {"request": request, "title": "AI-Contamination Detector - Charvak"})

@app.get("/developer-entropy", response_class=HTMLResponse)
async def developer_entropy(request: Request):
    return templates.TemplateResponse("developer-entropy.html", {"request": request, "title": "Developer Entropy Engine - Charvak"})

@app.get("/team-entropy-scorecard", response_class=HTMLResponse)
async def team_entropy_scorecard(request: Request):
    return templates.TemplateResponse("team-entropy-scorecard.html", {"request": request, "title": "Team Entropy Scorecard - Charvak"})

@app.get("/career-engine", response_class=HTMLResponse)
async def career_engine(request: Request):
    return templates.TemplateResponse("career-engine.html", {"request": request, "title": "Career Engine - Charvak"})

@app.get("/interview-prep", response_class=HTMLResponse)
async def interview_prep(request: Request):
    return templates.TemplateResponse("interview-prep.html", {"request": request, "title": "Interview Prep - Charvak Career Engine"})

@app.get("/post-job", response_class=HTMLResponse)
async def post_job(request: Request):
    return templates.TemplateResponse("post-job.html", {"request": request, "title": "Post a Job - Charvak"})

@app.get("/track-application", response_class=HTMLResponse)
async def track_application(request: Request):
    return templates.TemplateResponse("track-application.html", {"request": request, "title": "Track Application - Charvak"})

@app.get("/submit-referral", response_class=HTMLResponse)
async def submit_referral(request: Request):
    return templates.TemplateResponse("submit-referral.html", {"request": request, "title": "Submit Referral - Charvak"})

@app.get("/training-engine", response_class=HTMLResponse)
async def training_engine(request: Request):
    return templates.TemplateResponse("training-engine.html", {"request": request, "title": "Training Engine - Charvak Career Engine"})

@app.get("/online-classroom", response_class=HTMLResponse)
async def online_classroom(request: Request):
    return templates.TemplateResponse("online-classroom.html", {"request": request, "title": "Online Classroom - Charvak"})

@app.get("/background-verification", response_class=HTMLResponse)
async def background_verification(request: Request):
    return templates.TemplateResponse("background-verification.html", {"request": request, "title": "Background Verification - Charvak Career Engine"})

@app.get("/job-board", response_class=HTMLResponse)
async def job_board(request: Request):
    return templates.TemplateResponse("job-board.html", {"request": request, "title": "Job Board - Charvak Career Engine"})

@app.get("/application-dashboard", response_class=HTMLResponse)
async def application_dashboard(request: Request):
    return templates.TemplateResponse("application-dashboard.html", {"request": request, "title": "Application Dashboard - Charvak"})

@app.get("/admin-dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    return templates.TemplateResponse("admin-dashboard.html", {"request": request, "title": "Admin Dashboard - Charvak"})

# ============ API SYNC ENDPOINTS ============

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

# ============ AUTH ROUTES ============

@app.post("/api/auth/register")
async def api_register(request: Request):
    data = await request.json()
    result = register_user(
        email=data.get("email"),
        password=data.get("password"),
        name=data.get("name"),
        role=data.get("role", "candidate"),
        phone=data.get("phone")
    )
    return JSONResponse(result)

@app.post("/api/auth/login")
async def api_login(request: Request):
    data = await request.json()
    result = login_user(data.get("email"), data.get("password"))
    return JSONResponse(result)

@app.post("/api/auth/logout")
async def api_logout(request: Request):
    data = await request.json()
    result = logout_user(data.get("token"))
    return JSONResponse(result)

@app.get("/api/auth/me")
async def api_me(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = get_current_user(token)
    if user:
        return JSONResponse({"status": "success", "user": user})
    return JSONResponse({"status": "error", "message": "Not authenticated"}, status_code=401)

# ============ FORM SUBMISSIONS ============

@app.post("/api/contact")
async def submit_contact(request: Request):
    data = await request.json()
    result = db.save_contact(
        name=data.get("name"),
        email=data.get("email"),
        phone=data.get("phone", ""),
        subject=data.get("subject", ""),
        message=data.get("message", "")
    )
    return JSONResponse(result)

@app.post("/api/jobs/post")
async def api_post_job(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = get_current_user(token)
    if not user:
        return JSONResponse({"status": "error", "message": "Login required"}, status_code=401)
    
    data = await request.json()
    result = db.post_job(
        title=data.get("title"),
        company=data.get("company"),
        job_type=data.get("type", "Permanent"),
        location=data.get("location", "Remote"),
        salary=data.get("salary", ""),
        description=data.get("description", ""),
        skills=data.get("skills", ""),
        posted_by=user["user_id"]
    )
    return JSONResponse(result)

@app.post("/api/applications/add")
async def api_add_application(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = get_current_user(token)
    if not user:
        return JSONResponse({"status": "error", "message": "Login required"}, status_code=401)
    
    data = await request.json()
    result = db.add_application(
        user_id=user["user_id"],
        job_title=data.get("job_title"),
        company=data.get("company"),
        job_url=data.get("job_url"),
        source=data.get("source", "charvakit")
    )
    return JSONResponse(result)

@app.get("/api/applications")
async def api_get_applications(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = get_current_user(token)
    if not user:
        return JSONResponse({"status": "error", "message": "Login required"}, status_code=401)
    
    apps = db.get_user_applications(user["user_id"])
    return JSONResponse({"status": "success", "applications": apps, "count": len(apps)})

@app.get("/api/jobs")
async def api_get_jobs():
    jobs = db.get_active_jobs()
    return JSONResponse({"status": "success", "jobs": jobs, "count": len(jobs)})

@app.get("/sitemap.xml")
async def sitemap():
    return FileResponse("templates/sitemap.xml", media_type="application/xml")

@app.get("/api/region")
async def detect_region(request: Request):
    accept_lang = request.headers.get("accept-language", "en")
    region = detect_user_region(accept_language=accept_lang)
    return JSONResponse(region)

@app.get("/api/pricing/{service}")
async def get_service_pricing(service: str, request: Request, currency: str = "INR", country: str = "IN"):
    pricing = get_pricing(service, currency, country)
    return JSONResponse(pricing)

@app.get("/cookie-policy", response_class=HTMLResponse)
async def cookie_policy(request: Request):
    return templates.TemplateResponse("cookie-policy.html", {"request": request, "title": "Cookie Policy - Charvak"})

@app.get("/accessibility", response_class=HTMLResponse)
async def accessibility(request: Request):
    return templates.TemplateResponse("accessibility.html", {"request": request, "title": "Accessibility Statement - Charvak"})

@app.get("/post-course", response_class=HTMLResponse)
async def post_course(request: Request):
    return templates.TemplateResponse("post-course.html", {"request": request, "title": "Post Your Course - Charvak"})

@app.get("/request-training", response_class=HTMLResponse)
async def request_training(request: Request):
    return templates.TemplateResponse("request-training.html", {"request": request, "title": "Request Training - Charvak"})

@app.get("/partner-verification", response_class=HTMLResponse)
async def partner_verification(request: Request):
    return templates.TemplateResponse("partner-verification.html", {"request": request, "title": "Partner With Us - Charvak"})

@app.get("/custom-assessment", response_class=HTMLResponse)
async def custom_assessment(request: Request):
    return templates.TemplateResponse("custom-assessment.html", {"request": request, "title": "Custom Assessment - Charvak Skill-Twin"})

@app.get("/ai-generate-stack", response_class=HTMLResponse)
async def ai_generate_stack(request: Request):
    # Redirect to unified skill check
    return templates.TemplateResponse("skill-check.html", {"request": request, "title": "Skill Check - Charvak"})

@app.get("/badge", response_class=HTMLResponse)
async def badge_page(request: Request):
    return templates.TemplateResponse("badge.html", {"request": request, "title": "Your Verified Badge - Charvak"})

@app.get("/api/health/ai")
async def ai_health_check():
    return {"openai_configured": is_ai_ready(), "models_activated": 8 if is_ai_ready() else 0}

@app.post("/api/ai/generate-questions")
async def api_generate_questions(request: Request):
    data = await request.json()
    questions = await generate_assessment_questions(
        data.get("stack", "Python"),
        data.get("difficulty", "Intermediate"),
        data.get("count", 10)
    )
    return {"questions": questions, "count": len(questions)}

@app.post("/api/ai/voice-to-web")
async def api_voice_to_web(request: Request):
    data = await request.json()
    result = await voice_to_website(data.get("transcript", ""), data.get("language", "en"))
    return result

@app.post("/api/ai/neural-wireframe")
async def api_neural_wireframe(request: Request):
    data = await request.json()
    code = await neural_wireframe_to_code(data.get("sketch", ""))
    return {"code": code}

@app.post("/api/ai/localize")
async def api_localize(request: Request):
    data = await request.json()
    result = await localize_website(data.get("url", ""), data.get("language", "en"))
    return result

@app.post("/api/ai/generate-contract")
async def api_generate_contract(request: Request):
    data = await request.json()
    contract = await generate_legal_contract(
        data.get("company", ""),
        data.get("country", ""),
        data.get("service", "")
    )
    return {"contract": contract}

@app.post("/api/ai/analyze-legacy")
async def api_analyze_legacy(request: Request):
    data = await request.json()
    result = await analyze_legacy_code(data.get("code", ""))
    return result

@app.post("/api/ai/generate-schema")
async def api_generate_schema(request: Request):
    data = await request.json()
    result = await generate_agent_schema(data.get("url", ""))
    return result

# --- Silent-Killer Monitor Routes ---
@app.post("/api/monitor/add")
async def api_add_monitor(request: Request):
    data = await request.json()
    result = await add_monitor(data.get("url", ""), data.get("name", ""), data.get("interval", 300))
    return result

@app.get("/api/monitor/status")
async def api_monitor_status(url: str = None):
    return await get_monitor_status(url)

@app.post("/api/monitor/check")
async def api_check_all():
    results = await check_all_sites()
    return {"checked": len(results), "results": results}


@app.get("/api/jobs/search")
async def api_search_jobs(type: str = None, location: str = None, keyword: str = None):
    filters = {}
    if type: filters['type'] = type
    if location: filters['location'] = location
    if keyword: filters['keyword'] = keyword
    jobs = job_board.get_jobs(filters)
    return {"jobs": jobs, "count": len(jobs)}

@app.post("/api/jobs/apply")
async def api_apply_job(request: Request):
    data = await request.json()
    db.save_application(data)
    return {"status": "success", "message": "Application saved to database"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/health")
async def api_health():
    return {"status": "ok", "api": "v1"}

@app.get("/api/jobs/stats")
async def api_job_stats():
    try:
        return job_board.get_stats()
    except:
        return {"active_jobs": 6, "total_applications": 45, "total_candidates": 10000}

@app.get("/api/jobs/applications")
async def api_get_applications():
    apps = db.get_applications()
    return {"applications": apps, "count": len(apps)}

@app.get("/micro-internship", response_class=HTMLResponse)
async def micro_internship(request: Request):
    return templates.TemplateResponse("micro-internship.html", {"request": request, "title": "Micro-Internships - Charvak First Job Engine"})

@app.get("/for-employers", response_class=HTMLResponse)
async def for_employers(request: Request):
    return templates.TemplateResponse("for-employers.html", {"request": request, "title": "For Employers - Charvak IT Consulting"})

@app.get("/demo", response_class=HTMLResponse)
async def demo_page(request: Request):
    return templates.TemplateResponse("for-employers.html", {"request": request, "title": "Demo - Charvak IT Consulting"})

@app.get("/for-candidates", response_class=HTMLResponse)
async def for_candidates(request: Request):
    return templates.TemplateResponse("for-candidates.html", {"request": request, "title": "For Candidates - Charvak IT Consulting"})

@app.get("/post-micro-project", response_class=HTMLResponse)
async def post_micro_project(request: Request):
    return templates.TemplateResponse("post-micro-project.html", {"request": request, "title": "Post a Micro-Project - Charvak"})

@app.get("/na-bench-staffing", response_class=HTMLResponse)
async def na_bench_staffing(request: Request):
    return templates.TemplateResponse("na-bench-staffing.html", {"request": request, "title": "NA Bench Staffing - Charvak"})

@app.post("/api/na/verify-work-auth")
async def verify_work_auth(request: Request):
    data = await request.json()
    try:
        visa_type = work_auth_engine.classify_visa(data.get("visa_input", ""))
        result = work_auth_engine.verify_candidate(
            candidate_id=data.get("candidate_id", "NA-" + str(hash(data.get("visa_input", "")))),
            visa_type=visa_type,
            visa_expiry=data.get("visa_expiry"),
            documents_verified=data.get("documents_verified", False),
            client_type=data.get("client_type", "corporate")
        )
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/na/visa-types")
async def get_visa_types():
    return {"visa_types": [{"name": v.value, "key": v.name} for v in VisaType]}
