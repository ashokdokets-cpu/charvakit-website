from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Charvakit - Digital Solutions")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "Charvakit - Digital Solutions"})

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request, "title": "About Charvakit"})

@app.get("/services", response_class=HTMLResponse)
async def services(request: Request):
    services_data = [
        {
            "name": "Dokets VouchAI",
            "description": "AI-powered escrow platform with intelligent payment protection",
            "features": ["1% Transaction Fee", "WhatsApp Integration", "34 Languages Support", "13 Currencies", "AI-Powered Dispute Resolution", "Real-time Transaction Tracking"],
            "link": "https://dokets.com",
            "icon": "shield-check",
            "highlight": True
        },
        {
            "name": "Web Development",
            "description": "Modern web applications built with cutting-edge technology",
            "features": ["Responsive Design", "FastAPI Backend", "Cloud Deployment", "SEO Optimization"],
            "icon": "code"
        },
        {
            "name": "Digital Consulting",
            "description": "Strategic guidance for your digital transformation",
            "features": ["Technology Strategy", "Process Automation", "Cloud Migration", "Security Assessment"],
            "icon": "lightbulb"
        }
    ]
    return templates.TemplateResponse("services.html", {"request": request, "title": "Our Services", "services": services_data})

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
    return templates.TemplateResponse("products.html", {"request": request, "title": "Dokets VouchAI", "product": product})

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

@app.get("/health")
async def health_check():
    return {"status": "healthy"}