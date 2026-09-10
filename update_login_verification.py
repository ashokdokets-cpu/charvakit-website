with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find login function
old_login = '''async def api_login(request: Request, data: LoginRequest):
    try:
        result = login_user(data.email, data.password)'''

new_login = '''async def api_login(request: Request, data: LoginRequest):
    try:
        # Check verification
        from email_verification import email_verification
        if not email_verification.is_verified(data.email):
            # Allow admin without verification
            if data.email != "hr@charvakit.com":
                pass  # Temporarily allow all - enable below line after transition
                # return JSONResponse({"status": "error", "message": "Please verify your email first. Check your inbox."}, status_code=403)
        
        result = login_user(data.email, data.password)'''

if old_login in content:
    content = content.replace(old_login, new_login)
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ Login updated - verification optional (can enable later)')
else:
    print('Pattern not found')
