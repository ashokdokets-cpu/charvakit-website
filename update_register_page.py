with open('templates/register.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Check if verification message exists
if 'verification' not in content.lower():
    # Add verification notice
    content = content.replace(
        '<button type="submit"',
        '''<div class="alert alert-info mt-3">
            <i class="bi bi-envelope-check me-2"></i>
            <strong>Email Verification Required:</strong> After registration, check your email to verify your account.
        </div>
        <button type="submit"''',
        1
    )
    with open('templates/register.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ Register page updated with verification notice')
else:
    print('Already has verification info')
