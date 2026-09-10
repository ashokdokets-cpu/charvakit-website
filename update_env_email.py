import os

env_path = '.env'
with open(env_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add FROM_EMAIL if not present
if 'FROM_EMAIL' not in content:
    with open(env_path, 'a', encoding='utf-8') as f:
        f.write('\n# Email Sender\nFROM_EMAIL=charvakit@gmail.com\nADMIN_EMAIL=charvakit@gmail.com\n')
    print('✅ FROM_EMAIL added to .env')
else:
    # Update FROM_EMAIL
    import re
    content = re.sub(r'FROM_EMAIL=.*', 'FROM_EMAIL=charvakit@gmail.com', content)
    content = re.sub(r'ADMIN_EMAIL=.*', 'ADMIN_EMAIL=charvakit@gmail.com', content)
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ FROM_EMAIL updated in .env')
