with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Update admin email in all places
content = content.replace(
    'ADMIN_EMAIL = "hr@charvakit.com"',
    'ADMIN_EMAIL = "charvakit@gmail.com"'
)
content = content.replace(
    '"hr@charvakit.com"',
    '"charvakit@gmail.com"'
)
content = content.replace(
    "hr@charvakit.com",
    "charvakit@gmail.com"
)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ main.py updated with charvakit@gmail.com")
