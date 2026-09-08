with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

if 'assessment_system' not in content:
    routes = '''
from assessment_complete import assessment_system

@app.post("/api/assessment/start")
async def start_assessment(request: Request):
    data = await request.json()
    return assessment_system.start_assessment(
        data.get("email"),
        data.get("assessment_type")
    )

@app.post("/api/assessment/submit-answer")
async def submit_answer(request: Request):
    data = await request.json()
    return assessment_system.submit_answer(
        data.get("assessment_id"),
        data.get("question_id"),
        data.get("answer")
    )

@app.post("/api/assessment/complete")
async def complete_assessment(request: Request):
    data = await request.json()
    return assessment_system.complete_assessment(data.get("assessment_id"))

@app.get("/api/assessment/results/{assessment_id}")
async def get_results(assessment_id: str):
    return assessment_system.get_results(assessment_id)

@app.get("/api/assessment/user-results/{email}")
async def get_user_results(email: str):
    return assessment_system.get_user_results(email)

'''
    content = content.replace('if __name__', routes + '\nif __name__', 1)
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ Assessment system routes added')
else:
    print('Already exists')
