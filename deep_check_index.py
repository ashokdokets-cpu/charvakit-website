import urllib.request

response = urllib.request.urlopen('http://127.0.0.1:8000/')
content = response.read().decode('utf-8')
lines = content.split('\n')

print(f'Total lines: {len(lines)}')
print(f'\n=== Line 880-890 ===')
for i in range(879, min(890, len(lines))):
    print(f'{i+1}: {lines[i].rstrip()[:150]}')
