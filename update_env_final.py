import os
import re

env_path = '.env'
with open(env_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Update or add FROM_EMAIL
if 'FROM_EMAIL' in content:
    content = re.sub(r'FROM_EMAIL=.*', 'FROM_EMAIL=charvakit@gmail.com', content)
else:
    content += '\nFROM_EMAIL=charvakit@gmail.com\n'

# Update or add ADMIN_EMAIL  
if 'ADMIN_EMAIL' in content:
    content = re.sub(r'ADMIN_EMAIL=.*', 'ADMIN_EMAIL=charvakit@gmail.com', content)
else:
    content += 'ADMIN_EMAIL=charvakit@gmail.com\n'

with open(env_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ .env updated')
print('\n=== CURRENT .env (email settings) ===')
for line in content.split('\n'):
    if 'EMAIL' in line.upper() or 'SENDGRID' in line.upper():
        if 'SENDGRID' in line:
            print(f'{line.split("=")[0]}=***')
        else:
            print(line)
