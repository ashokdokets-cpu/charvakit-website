with open('password_reset.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace from email
content = content.replace('hr@charvakit.com', 'charvakit@gmail.com')

with open('password_reset.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ password_reset.py updated')
