with open('password_reset.py', 'r', encoding='utf-8') as f:
    content = f.read()

print("Before:", 'minutes=30' in content, 'hours=1' in content, 'hours=24' in content)

# Force update to 30 minutes
content = content.replace('timedelta(hours=1)', 'timedelta(minutes=30)')
content = content.replace('timedelta(hours=24)', 'timedelta(minutes=30)')

with open('password_reset.py', 'w', encoding='utf-8') as f:
    f.write(content)

# Verify
with open('password_reset.py', 'r', encoding='utf-8') as f:
    new_content = f.read()

print("After:", 'minutes=30' in new_content)
print("Has 30 minutes:", 'minutes=30' in new_content)

# Show the expiry line
import re
match = re.search(r'expires_at\s*=\s*datetime\.now\(\)\s*\+\s*timedelta\([^)]+\)', new_content)
if match:
    print(f"Expiry line: {match.group()}")
