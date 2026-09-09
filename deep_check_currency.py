with open('static/js/currency-utils.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f'Total lines: {len(lines)}')
print(f'\n=== Lines 125-140 ===')
for i in range(124, min(140, len(lines))):
    marker = ' ← ERROR' if i == 133 else ''
    print(f'{i+1}: {lines[i].rstrip()[:120]}{marker}')
