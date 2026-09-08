with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

if 'company_content_engine' not in content:
    routes = '''
from company_content_engine import company_content_engine

@app.get("/api/company-pattern/{company_id}")
async def get_company_pattern(company_id: str):
    return company_content_engine.get_company_test_pattern(company_id)

@app.get("/api/company-pattern/{company_id}/sections/{section_id}")
async def get_section_topics(company_id: str, section_id: str):
    return company_content_engine.get_section_topics(company_id, section_id)

@app.get("/api/company-pattern/{company_id}/questions/{section_id}")
async def get_company_questions(company_id: str, section_id: str):
    return company_content_engine.generate_company_questions(company_id, section_id)

@app.get("/api/company-pattern/{company_id}/roadmap")
async def get_placement_roadmap(company_id: str):
    return company_content_engine.get_placement_roadmap(company_id)

@app.post("/api/company-pattern/track-progress")
async def track_progress(request: Request):
    data = await request.json()
    return company_content_engine.track_user_progress(
        data.get("email"),
        data.get("company_id"),
        data.get("section_score")
    )

@app.get("/api/company-pattern/readiness/{email}/{company_id}")
async def get_readiness(email: str, company_id: str):
    return company_content_engine.get_user_readiness(email, company_id)

'''
    content = content.replace('if __name__', routes + '\nif __name__', 1)
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ Company content routes added')
else:
    print('Already exists')
