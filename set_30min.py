with open('password_reset.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Change from 1 hour/24 hours to 30 minutes
content = content.replace(
    'expires_at = datetime.now() + timedelta(hours=1)',
    'expires_at = datetime.now() + timedelta(minutes=30)'
)

content = content.replace(
    'expires_at = datetime.now() + timedelta(hours=24)',
    'expires_at = datetime.now() + timedelta(minutes=30)'
)

# Update email text
content = content.replace('Link expires in 1 hour', 'Link expires in 30 minutes')
content = content.replace('Link expires in 24 hours', 'Link expires in 30 minutes')
content = content.replace('This link expires in 1 hour', 'This link expires in 30 minutes')

with open('password_reset.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Reset link expiry set to 30 minutes')
