with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

if 'cbt_versant' not in content:
    routes = '''
from cbt_versant import cbt_versant

@app.get("/api/versant/section/{section_id}")
async def get_versant_section(section_id: str):
    return cbt_versant.get_section_questions(section_id)

@app.post("/api/versant/start-cbt")
async def start_cbt(request: Request):
    data = await request.json()
    return cbt_versant.start_cbt_session(data.get("email"))

@app.post("/api/versant/record-audio")
async def record_audio(request: Request):
    data = await request.json()
    return cbt_versant.save_audio_recording(
        data.get("session_id"),
        data.get("section_id"),
        data.get("question_id"),
        data.get("audio_blob")
    )

@app.post("/api/versant/submit-text")
async def submit_text(request: Request):
    data = await request.json()
    return cbt_versant.submit_text_answer(
        data.get("session_id"),
        data.get("section_id"),
        data.get("question_id"),
        data.get("answer")
    )

'''
    content = content.replace('if __name__', routes + '\nif __name__', 1)
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ CBT Versant routes added')
else:
    print('Already exists')
