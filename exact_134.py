with open('static/js/currency-utils.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Check line 134 specifically
lines = content.split('\n')
line134 = lines[133] if len(lines) > 133 else 'NOT FOUND'
print(f'Line 134: {repr(line134[:100])}')

# Check previous lines
for i in range(128, 135):
    if i < len(lines):
        print(f'Line {i+1}: {repr(lines[i].rstrip()[:100])}')
