with open('templates/base.html', 'r', encoding='utf-8') as f:
    content = f.read()

if '/ai-courses' not in content:
    content = content.replace(
        '📚 Training</a></li>',
        '📚 Training</a></li>\n                <li class="nav-item"><a class="nav-link" href="/ai-courses">🤖 AI Courses</a></li>',
        1
    )
    with open('templates/base.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ AI Courses added to navigation')
else:
    print('Already in nav')
