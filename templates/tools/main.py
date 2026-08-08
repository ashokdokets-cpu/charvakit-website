# Tools Suite
@app.get("/tools", response_class=HTMLResponse)
async def tools_index(request: Request):
    return templates.TemplateResponse("tools/index.html", {"request": request, "title": "AI Tools Suite - Charvak"})

@app.get("/tools/resume-roast", response_class=HTMLResponse)
async def resume_roast(request: Request):
    return templates.TemplateResponse("tools/resume-roast.html", {"request": request, "title": "Resume Roast - Charvak"})

@app.get("/tools/ghost-bounty", response_class=HTMLResponse)
async def ghost_bounty(request: Request):
    return templates.TemplateResponse("tools/ghost-bounty.html", {"request": request, "title": "GhostBounty AI - Charvak"})

@app.get("/tools/ref-check", response_class=HTMLResponse)
async def ref_check(request: Request):
    return templates.TemplateResponse("tools/ref-check.html", {"request": request, "title": "Ref-Check Roulette - Charvak"})

@app.get("/tools/role-mirror", response_class=HTMLResponse)
async def role_mirror(request: Request):
    return templates.TemplateResponse("tools/role-mirror.html", {"request": request, "title": "Role-Mirror AI - Charvak"})

@app.get("/tools/bounty-swap", response_class=HTMLResponse)
async def bounty_swap(request: Request):
    return templates.TemplateResponse("tools/bounty-swap.html", {"request": request, "title": "BountySwap AI - Charvak"})

@app.get("/tools/micro-trial", response_class=HTMLResponse)
async def micro_trial(request: Request):
    return templates.TemplateResponse("tools/micro-trial.html", {"request": request, "title": "Micro-Trial Engine - Charvak"})

@app.get("/tools/offer-matcher", response_class=HTMLResponse)
async def offer_matcher(request: Request):
    return templates.TemplateResponse("tools/offer-matcher.html", {"request": request, "title": "Offer Matcher - Charvak"})

@app.get("/tools/ghost-job-shield", response_class=HTMLResponse)
async def ghost_job_shield(request: Request):
    return templates.TemplateResponse("tools/ghost-job-shield.html", {"request": request, "title": "Ghost-Job Shield - Charvak"})

@app.get("/tools/counter-offer", response_class=HTMLResponse)
async def counter_offer(request: Request):
    return templates.TemplateResponse("tools/counter-offer.html", {"request": request, "title": "Counter-Offer Shield - Charvak"})

@app.get("/tools/ref-swap", response_class=HTMLResponse)
async def ref_swap(request: Request):
    return templates.TemplateResponse("tools/ref-swap.html", {"request": request, "title": "Reference Check Swap - Charvak"})

@app.get("/tools/ghost-tracker", response_class=HTMLResponse)
async def ghost_tracker(request: Request):
    return templates.TemplateResponse("tools/ghost-tracker.html", {"request": request, "title": "Ghosted Tracker - Charvak"})

@app.get("/tools/pitch-roast", response_class=HTMLResponse)
async def pitch_roast(request: Request):
    return templates.TemplateResponse("tools/pitch-roast.html", {"request": request, "title": "Recruiter Pitch Roast - Charvak"})