with open('templates/versant.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the question rendering to add buttons
old_render = "html += '<div class=\"question-item\"><strong>Question ' + (i + 1) + ':</strong> ' + section.questions[i] + '</div>';"

new_render = """html += '<div class="question-item">';
        html += '<strong>Question ' + (i + 1) + ':</strong> ' + section.questions[i];
        html += '<br>';
        
        // Add Play button for Repeats section
        if (sectionId === 'repeats') {
            html += '<button class="btn btn-primary btn-sm mt-2 me-2" id="playBtn-' + i + '" onclick="playAudio(\\'' + section.questions[i] + '\\', ' + i + ')">🔊 Play Audio</button>';
        }
        
        // Add Record button for all sections
        html += '<button class="btn btn-danger btn-sm mt-2 me-2" id="recordBtn-' + i + '" onclick="toggleRecording(' + i + ')">🎤 Record</button>';
        
        // Add playback audio element
        html += '<audio id="playback-' + i + '" controls style="display:none; margin-top:10px; width:100%;"></audio>';
        
        html += '</div>';"""

if old_render in content:
    content = content.replace(old_render, new_render)
    with open('templates/versant.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ Record and Play buttons added to questions!')
else:
    print('Pattern not found - trying alternative')
    # Find the question rendering
    import re
    pattern = r"html \+= '<div class=\"question-item\">.*?</div>';"
    content = re.sub(pattern, new_render.replace('\\n', '\n'), content, flags=re.DOTALL)
    with open('templates/versant.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ Fixed with regex')
