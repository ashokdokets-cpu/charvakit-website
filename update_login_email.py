with open('login_notifications.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace from email
content = content.replace('hr@charvakit.com', 'charvakit@gmail.com')

with open('login_notifications.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ login_notifications.py updated')
