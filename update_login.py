with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find login endpoint and add user name saving
old_login = """@app.post("/api/auth/login")
async def api_login(request: Request, data: LoginRequest):"""

new_login = """@app.post("/api/auth/login")
async def api_login(request: Request, data: LoginRequest):
    # Return user name for display
    result = None"""

# The login already returns result with user data
# We just need to ensure frontend saves userName
