with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

if '/ai-courses' not in content:
    route = '''
@app.get("/ai-courses", response_class=HTMLResponse)
async def ai_courses_page(request: Request):
    return template_response("ai-courses.html", request, "AI Courses - Charvak")

'''
    content = content.replace('if __name__', route + '\nif __name__', 1)
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ AI courses route added')
else:
    print('Already exists')
