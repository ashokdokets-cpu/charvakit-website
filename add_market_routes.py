with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

if 'market_standard' not in content:
    routes = '''
from market_standard import market_standard

@app.get("/api/market/versant-standard")
async def get_versant_standard():
    return market_standard.get_versant_market_standard()

@app.get("/api/market/mcq-standard")
async def get_mcq_standard():
    return market_standard.get_mcq_market_standard()

@app.get("/api/market/company-standard")
async def get_company_standard():
    return market_standard.get_company_market_standard()

@app.get("/api/market/versant-questions/{section_id}")
async def get_versant_questions(section_id: str):
    return market_standard.generate_versant_questions(section_id)

@app.post("/api/market/mcq-questions")
async def generate_mcq(request: Request):
    data = await request.json()
    return market_standard.generate_mcq_questions(
        data.get("category"),
        data.get("topic"),
        data.get("count", 10)
    )

@app.post("/api/market/generate-results")
async def generate_results(request: Request):
    data = await request.json()
    return market_standard.generate_results(
        data.get("email"),
        data.get("assessment_type"),
        data.get("answers"),
        data.get("total_questions")
    )

'''
    content = content.replace('if __name__', routes + '\nif __name__', 1)
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ Market standard routes added')
else:
    print('Already exists')
