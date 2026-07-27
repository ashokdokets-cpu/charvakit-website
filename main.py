from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import json

app = FastAPI(title="Charvak IT Consulting Pvt Ltd - Web Designing | Staff Augmentation")

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
        {
            "name": "Dokets VouchAI",
            "description": "AI-powered escrow platform with intelligent payment protection",
            "features": ["1% Transaction Fee", "WhatsApp Integration", "34 Languages", "13 Currencies", "AI Dispute Resolution"],
            "link": "https://dokets.com",
            "icon": "shield-check",
            "badge": "Featured"
        },
        {
            "name": "Dokets Shop",
            "description": "Modern e-commerce store solution for your business",
            "features": ["Easy Setup", "Secure Payments", "Inventory Management", "Mobile Ready"],
            "link": "https://dokets.shop",
            "icon": "cart",
            "badge": "New"
        },
        {
            "name": "Dokets RB",
            "description": "Professional resume builder to land your dream job",
            "features": ["AI-Powered Templates", "ATS-Friendly", "Quick Export", "Multiple Formats"],
            "link": "https://doketsrb.com",
            "icon": "file-text",
            "badge": "New"
        }
    ]
    return templates.TemplateResponse("products-list.html", {"request": request, "title": "Our Products - Dokets Suite", "products": products_data})

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
from whatsapp_bot import whatsapp_handler, VERIFY_TOKEN
import json

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

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
