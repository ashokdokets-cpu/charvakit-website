import re
import json

with open('templates/base.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract all script sections
scripts = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
print(f'Total scripts: {len(scripts)}')

# Check each script for issues
for i, script in enumerate(scripts):
    lines = script.split('\n')
    for j, line in enumerate(lines):
        # Check for non-ASCII characters that might break JS
        non_ascii = [(c, ord(c)) for c in line if ord(c) > 127 and c not in '₹€£✓✅🎯🚀💻📊🔒☁️📱🤖👨‍🏫📝🎧💬📖✏️📄🗣️🏢⭐']
        if non_ascii:
            print(f'Script {i+1}, Line {j+1}: Non-ASCII chars: {non_ascii[:3]}')
            print(f'  Content: {line.strip()[:100]}')
