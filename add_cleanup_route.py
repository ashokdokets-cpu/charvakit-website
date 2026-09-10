with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

if 'admin_cleanup' not in content:
    routes = '''
from admin_cleanup import cleanup_suspicious_users

@app.get("/admin/cleanup-users")
async def admin_cleanup_users():
    """Remove suspicious users - ADMIN ONLY."""
    return cleanup_suspicious_users()

'''
    content = content.replace('if __name__', routes + '\nif __name__', 1)
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ Cleanup route added to main.py')
else:
    print('Already exists')
