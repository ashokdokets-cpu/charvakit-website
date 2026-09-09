with open('admin_role_manager.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Ensure hr@charvakit.com is admin
if 'hr@charvakit.com' not in content:
    content = content.replace(
        'self.admin_emails = ["admin@charvakit.com"]',
        'self.admin_emails = ["hr@charvakit.com", "admin@charvakit.com"]'
    )
    with open('admin_role_manager.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ hr@charvakit.com added as admin')
else:
    print('hr@charvakit.com already admin')
