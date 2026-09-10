with open('templates/reset-password.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Update the expired message with reset option
content = content.replace(
    '<div class="alert alert-danger">Reset link expired. Please request a new one</div>',
    '''<div class="alert alert-danger">
        Reset link expired (links are valid for 30 minutes for security)
        <br><br>
        <a href="/forgot-password" class="btn btn-primary btn-sm">Request New Link</a>
    </div>'''
)

with open('templates/reset-password.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Reset expired message improved')
