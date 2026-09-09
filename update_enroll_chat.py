with open('templates/ai-courses.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Update enrollCourse to start AI chat instead of just alert
old_enroll = """function enrollCourse(i) {
    var c = coursesData[i];
    var email = prompt('Enter your email to enroll in ' + c.name + ':');
    if (!email) return;
    var inst = getInstallments(c.duration);
    var symbol = getCurrencySymbol();
    var rate = getCurrencyRate();
    var priceDisplay = Math.round(c.price / rate);
    var instDisplay = Math.round(c.price / inst / rate);
    alert('Enrollment created for ' + c.name + '! Complete payment of ' + symbol + instDisplay + ' to start.');
}"""

new_enroll = """function enrollCourse(i) {
    var c = coursesData[i];
    var email = prompt('Enter your email to enroll in ' + c.name + ':');
    if (!email) return;
    
    var confirmMsg = 'Enroll in ' + c.name + '?\nDuration: ' + c.duration + ' weeks\n\nAI Tutor will start teaching you immediately after enrollment!';
    if (!confirm(confirmMsg)) return;
    
    fetch('/api/ai-course/start-chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            email: email,
            course_name: c.name,
            duration_weeks: c.duration
        })
    })
    .then(function(r) { return r.json(); })
    .then(function(result) {
        if (result.status === 'success') {
            alert('✅ Enrolled! AI Tutor started!\n\nAI: ' + result.ai_message);
            
            // Open chat window with AI Tutor
            openCourseChat(result);
        }
    })
    .catch(function(e) { alert('Error: ' + e.message); });
}

function openCourseChat(result) {
    var chatHtml = '<div id="chatModal" style="position:fixed;bottom:20px;right:20px;width:380px;height:500px;background:white;border-radius:15px;box-shadow:0 20px 60px rgba(0,0,0,0.3);z-index:9999;display:flex;flex-direction:column;">';
    chatHtml += '<div style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:15px;border-radius:15px 15px 0 0;display:flex;justify-content:space-between;align-items:center;">';
    chatHtml += '<strong>🤖 AI Tutor - ' + result.curriculum.course + '</strong>';
    chatHtml += '<button onclick="closeCourseChat()" style="background:none;border:none;color:white;font-size:20px;cursor:pointer;">×</button>';
    chatHtml += '</div>';
    chatHtml += '<div id="chatMessages" style="flex:1;overflow-y:auto;padding:15px;background:#f8f9fa;">';
    chatHtml += '<div style="background:#e8f5e9;padding:10px;border-radius:10px;margin-bottom:10px;"><strong>AI:</strong> ' + result.ai_message + '</div>';
    chatHtml += '</div>';
    chatHtml += '<div style="padding:10px;border-top:1px solid #e0e0e0;display:flex;">';
    chatHtml += '<input type="text" id="chatInput" placeholder="Type your reply..." style="flex:1;border:1px solid #e0e0e0;border-radius:20px;padding:10px;outline:none;">';
    chatHtml += '<button onclick="sendCourseMessage(' + result.tutor_session_id + ')" style="background:#3ba591;color:white;border:none;border-radius:50%;width:40px;height:40px;margin-left:10px;cursor:pointer;">➤</button>';
    chatHtml += '</div></div>';
    document.body.insertAdjacentHTML('beforeend', chatHtml);
}

function closeCourseChat() {
    var modal = document.getElementById('chatModal');
    if (modal) modal.remove();
}

function sendCourseMessage(sessionId) {
    var input = document.getElementById('chatInput');
    var message = input.value.trim();
    if (!message) return;
    input.value = '';
    
    var messagesDiv = document.getElementById('chatMessages');
    messagesDiv.innerHTML += '<div style="background:#e3f2fd;padding:10px;border-radius:10px;margin-bottom:10px;margin-left:auto;max-width:80%;"><strong>You:</strong> ' + message + '</div>';
    messagesDiv.innerHTML += '<div id="typing" style="color:#999;font-size:12px;">AI typing...</div>';
    
    fetch('/api/tutor/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({session_id: sessionId, user_message: message})
    })
    .then(function(r) { return r.json(); })
    .then(function(result) {
        var typing = document.getElementById('typing');
        if (typing) typing.remove();
        if (result.status === 'success') {
            messagesDiv.innerHTML += '<div style="background:#e8f5e9;padding:10px;border-radius:10px;margin-bottom:10px;"><strong>AI:</strong> ' + result.ai_response + '</div>';
        }
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    });
}"""

if old_enroll in content:
    content = content.replace(old_enroll, new_enroll)
    with open('templates/ai-courses.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ Enroll now starts AI Chat Tutor!')
else:
    print('Pattern not found')
