with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

if 'company_assessment' not in content:
    routes = '''
from company_assessment import company_assessment

@app.get("/api/company/{company_id}")
async def get_company_details(company_id: str):
    return company_assessment.get_company_details(company_id)

@app.post("/api/company/start-mock")
async def start_company_mock(request: Request):
    data = await request.json()
    return company_assessment.start_company_mock(
        data.get("email"),
        data.get("company_id"),
        data.get("pattern")
    )

@app.get("/api/company/{company_id}/questions/{section}")
async def get_company_questions(company_id: str, section: str):
    return company_assessment.generate_company_questions(company_id, section)

@app.post("/api/company/submit-answer")
async def submit_company_answer(request: Request):
    data = await request.json()
    return company_assessment.submit_company_answer(
        data.get("session_id"),
        data.get("question_id"),
        data.get("answer")
    )

@app.post("/api/company/complete-mock")
async def complete_company_mock(request: Request):
    data = await request.json()
    return company_assessment.complete_company_mock(data.get("session_id"))

@app.get("/api/company/results/{session_id}")
async def get_company_results(session_id: str):
    return company_assessment.get_company_results(session_id)

'''
    content = content.replace('if __name__', routes + '\nif __name__', 1)
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ Company assessment routes added')
else:
    print('Already exists')
