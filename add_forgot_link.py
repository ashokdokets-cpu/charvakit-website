with open('templates/login.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add forgot password link
if 'forgot-password' not in content:
    content = content.replace(
        'Don\'t have an account?',
        '<a href="/forgot-password" class="text-primary">Forgot Password?</a><br>Don\'t have an account?'
    )
    with open('templates/login.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ Forgot password link added to login')
else:
    print('Already has forgot password link')
