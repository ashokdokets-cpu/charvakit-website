with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

if '/request-content' not in content:
    route = '''
@app.get("/request-content", response_class=HTMLResponse)
async def request_content_page(request: Request):
    return template_response("request-content.html", request, "Request Content - Charvak")

'''
    content = content.replace('if __name__', route + '\nif __name__', 1)
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ Request content route added')
else:
    print('Already exists')
