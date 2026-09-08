with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

if 'ai_versant' not in content:
    routes = '''
from ai_versant import ai_versant

@app.post("/api/versant/start-session")
async def start_versant_session(request: Request):
    data = await request.json()
    return ai_versant.start_user_session(data.get("email"))

@app.get("/api/versant/session/{session_id}/{section_id}")
async def get_session_questions(session_id: str, section_id: str):
    return ai_versant.get_session_questions(session_id, section_id)

'''
    content = content.replace('if __name__', routes + '\nif __name__', 1)
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ AI Versant routes added')
else:
    print('Already exists')
