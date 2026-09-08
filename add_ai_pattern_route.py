with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

if 'ai_pattern_questions' not in content:
    routes = '''
from ai_pattern_questions import ai_pattern_questions

@app.post("/api/ai-pattern/generate-questions")
async def generate_pattern_questions(request: Request):
    data = await request.json()
    return {
        "status": "success",
        "sections": ai_pattern_questions.generate_pattern_questions(
            data.get("company_name"),
            data.get("pattern_name"),
            data.get("sections")
        )
    }

'''
    content = content.replace('if __name__', routes + '\nif __name__', 1)
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ AI pattern questions route added')
else:
    print('Already exists')
