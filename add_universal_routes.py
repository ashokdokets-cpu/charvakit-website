with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

if 'universal_company' not in content:
    routes = '''
from universal_company import universal_company

@app.post("/api/company/custom/add")
async def add_custom_company(request: Request):
    data = await request.json()
    return universal_company.add_custom_company(
        data.get("company_name"),
        data.get("pattern_name"),
        data.get("sections"),
        data.get("cutoff", 65),
        data.get("difficulty", "Moderate")
    )

@app.post("/api/company/content-request")
async def request_content(request: Request):
    data = await request.json()
    return universal_company.request_content(
        data.get("email"),
        data.get("company_name"),
        data.get("content_type"),
        data.get("topic"),
        data.get("description")
    )

@app.post("/api/company/contact-admin")
async def contact_admin(request: Request):
    data = await request.json()
    return universal_company.contact_admin(
        data.get("email"),
        data.get("subject"),
        data.get("message")
    )

@app.get("/api/company/content-requests")
async def get_content_requests():
    return universal_company.get_content_requests()

@app.post("/api/company/update-request")
async def update_request(request: Request):
    data = await request.json()
    return universal_company.update_content_request(
        data.get("request_id"),
        data.get("status"),
        data.get("admin_note")
    )

@app.get("/api/company/custom/all")
async def get_custom_companies():
    return universal_company.get_custom_companies()

@app.post("/api/company/generate-content")
async def generate_content(request: Request):
    data = await request.json()
    return universal_company.generate_content_for_any_company(
        data.get("company_name"),
        data.get("topic"),
        data.get("count", 5)
    )

@app.get("/api/company/all-combined")
async def get_all_companies():
    return universal_company.get_all_companies_combined()

'''
    content = content.replace('if __name__', routes + '\nif __name__', 1)
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ Universal company routes added')
else:
    print('Already exists')
