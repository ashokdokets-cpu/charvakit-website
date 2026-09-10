with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Increase limits for AI/Versant endpoints
content = content.replace('@limiter.limit("5/minute")', '@limiter.limit("30/minute")')
content = content.replace('@limiter.limit("10/minute")', '@limiter.limit("60/minute")')

# Also fix the global rate limit
content = content.replace(
    'return JSONResponse({"error": "Too many requests"}, status_code=429)',
    'return JSONResponse({"error": "Rate limit exceeded. Please try again shortly."}, status_code=429)'
)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Rate limits increased!')
