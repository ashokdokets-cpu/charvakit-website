with open('templates/base.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace Trainers link with AI Courses (if exists)
content = content.replace(
    '<li class="nav-item"><a class="nav-link" href="/trainers">👨‍🏫 Trainers</a></li>',
    '<li class="nav-item"><a class="nav-link" href="/ai-courses">🤖 AI Courses</a></li>'
)

with open('templates/base.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('✅ Navigation updated')
