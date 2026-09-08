with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Update /trainers to redirect to /ai-courses
old_route = '''@app.get("/trainers", response_class=HTMLResponse)
async def trainers_page(request: Request):
    return template_response("trainers.html", request, "Expert Trainers - Charvak")'''

new_route = '''@app.get("/trainers", response_class=HTMLResponse)
async def trainers_page(request: Request):
    return template_response("ai-courses.html", request, "AI Courses - Charvak")'''

if old_route in content:
    content = content.replace(old_route, new_route)
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ /trainers now redirects to AI courses')
else:
    print('Pattern not found')
