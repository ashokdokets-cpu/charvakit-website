with open('templates/na-client-signup.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Check if there's a registerClient function
if 'function registerClient' in content:
    print('registerClient function exists')
    # Update it to include C2C fields
    content = content.replace(
        "benchCount: document.getElementById('benchCount').value",
        "benchCount: document.getElementById('benchCount').value,\n                taxId: document.getElementById('taxId').value,\n                corporateName: document.getElementById('corporateName').value,\n                workAuth: document.getElementById('workAuth').value,\n                minRate: document.getElementById('minRate').value,\n                techStack: document.getElementById('techStack').value"
    )
    with open('templates/na-client-signup.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ registerClient updated with C2C fields!')
else:
    print('registerClient function not found')
