with open('email_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find where content type is set
if 'text/plain' in content:
    print('Found text/plain - needs fix')
    content = content.replace('text/plain', 'text/html')
    with open('email_engine.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ Changed to text/html')
else:
    print('Already using text/html or no plain text found')
