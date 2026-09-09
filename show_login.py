with open('templates/login.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
match = re.search(r'async function loginUser.*?\n\s*\}', content, re.DOTALL)
if match:
    print(match.group())
