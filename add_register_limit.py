with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add rate limit to registration
old_register = '@app.post("/api/auth/register")'
new_register = '@app.post("/api/auth/register")\n@limiter.limit("3/hour")'

if old_register in content and '@limiter.limit("3/hour")\n@app.post("/api/auth/register")' not in content:
    content = content.replace(old_register, new_register, 1)
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ Rate limit added to registration (3/hour)')
else:
    print('Already has rate limit or pattern not found')
