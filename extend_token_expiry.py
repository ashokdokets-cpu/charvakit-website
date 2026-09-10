with open('password_reset.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Change from 1 hour to 24 hours
content = content.replace(
    'expires_at = datetime.now() + timedelta(hours=1)',
    'expires_at = datetime.now() + timedelta(hours=24)'
)

# Update email message
content = content.replace(
    'Link expires in 1 hour',
    'Link expires in 24 hours'
)

content = content.replace(
    'This link expires in 1 hour',
    'This link expires in 24 hours'
)

with open('password_reset.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Token expiry extended to 24 hours')
