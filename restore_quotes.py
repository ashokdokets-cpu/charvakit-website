with open('templates/base.html', 'r', encoding='utf-8') as f:
    content = f.read()

# The lines that were incorrectly changed have HTML attributes
# Restore HTML double quotes for class, onclick, style attributes

# Fix the social login buttons
content = content.replace("<button class='btn btn-outline-danger btn-sm w-100 mb-2 text-white' onclick='alert('", '<button class="btn btn-outline-danger btn-sm w-100 mb-2 text-white" onclick="alert(\'')
content = content.replace("')' style='", ")\' style=\"")

# Fix payment modal buttons
content = content.replace("<p class='mb-3'>", '<p class="mb-3">')
content = content.replace("<button class='btn btn-primary btn-lg'", '<button class="btn btn-primary btn-lg"')
content = content.replace("<button class='btn btn-warning btn-lg'", '<button class="btn btn-warning btn-lg"')
content = content.replace("<button class='btn btn-secondary'", '<button class="btn btn-secondary"')

with open('templates/base.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ HTML quotes restored, JS strings fixed')
