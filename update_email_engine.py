with open('email_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Update FROM_EMAIL
import re
content = re.sub(
    r'FROM_EMAIL\s*=\s*["\'][^"\']*["\']',
    'FROM_EMAIL = "charvakit@gmail.com"',
    content
)

content = re.sub(
    r'ADMIN_EMAIL\s*=\s*os\.getenv\(["\']ADMIN_EMAIL["\'],\s*["\'][^"\']*["\']\)',
    'ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "charvakit@gmail.com")',
    content
)

with open('email_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ email_engine.py updated')
