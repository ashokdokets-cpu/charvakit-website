with open('templates/login.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add userName after userEmail is saved
if 'userEmail' in content and 'userName' not in content:
    content = content.replace(
        "localStorage.setItem('userEmail',",
        "localStorage.setItem('userName', email.split('@')[0]); localStorage.setItem('userEmail',"
    )
    with open('templates/login.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ userName saving added!')
else:
    print('Already has userName or no userEmail found')
