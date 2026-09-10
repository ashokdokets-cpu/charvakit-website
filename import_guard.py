with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Import guard
if 'registration_guard' not in content:
    content = content.replace(
        'from admin_cleanup import cleanup_suspicious_users',
        'from admin_cleanup import cleanup_suspicious_users\nfrom registration_guard import validate_registration'
    )
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ Registration guard imported')
else:
    print('Already imported')
