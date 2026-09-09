with open('templates/base.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re

# Find the complete cookie banner div
match = re.search(r'<div id="cookieBanner".*?</div>\s*</div>', content, re.DOTALL)

if match:
    old_banner = match.group()
    
    # Create clean banner with proper quoting
    new_banner = '''<div id="cookieBanner" class="fixed-bottom bg-dark text-white p-3" style="z-index:9999; display:none;">
        <div class="container">
            <div class="row align-items-center">
                <div class="col-md-8">
                    <p class="mb-0 small">🍪 We use cookies. By continuing, you agree to our <a href="/privacy" class="text-primary">Privacy Policy</a> and <a href="/terms" class="text-primary">Terms</a>.</p>
                </div>
                <div class="col-md-4 text-end">
                    <button class="btn btn-primary btn-sm me-2" onclick="acceptCookies()">Accept</button>
                    <a href="/privacy" class="btn btn-outline-light btn-sm">Learn More</a>
                </div>
            </div>
        </div>
    </div>'''
    
    content = content.replace(old_banner, new_banner)
    
    with open('templates/base.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ Cookie banner completely rewritten clean!')
else:
    print('Cookie banner not found')
