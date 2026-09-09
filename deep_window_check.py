with open('static/js/currency-utils.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the window.addEventListener that's causing issue
import re
# Find all window statements
window_lines = []
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'window' in line:
        window_lines.append((i, line.strip()))

print('=== ALL window statements ===')
for i, line in window_lines:
    print(f'Line {i+1}: {line[:100]}')
    # Check previous line
    if i > 0:
        prev = lines[i-1].strip()
        print(f'  Prev: {prev[:80]}')
