with open('templates/training.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the current chat script with full chat interface
old_script = """<script>
document.getElementById('chatBtn').addEventListener('click', function() {
    var email = prompt('Enter your email to start AI chat:');
    if (!email) return;
    var topic = prompt('What topic do you want to learn? (e.g., Python, DSA, SQL):');
    if (!topic) return;
    
    fetch('/api/tutor/start', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({email: email, course_name: topic, topic: topic, user_level: 'beginner'})
    })
    .then(function(r) { return r.json(); })
    .then(function(result) {
        if (result.status === 'success') {
            alert('🤖 AI Tutor connected! | AI: ' + result.ai_message);
        }
    })
    .catch(function(e) { alert('Error: ' + e.message); });
});
</script>"""

new_script = """<script>
var chatSessionId = null;

document.getElementById('chatBtn').addEventListener('click', function() {
    var email = prompt('Enter your email to start AI chat:');
    if (!email) return;
    var topic = prompt('What topic do you want to learn? (e.g., Python, DSA, SQL):');
    if (!topic) return;
    
    openChatWindow(email, topic);
});

function openChatWindow(email, topic) {
    fetch('/api/tutor/start', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({email: email, course_name: topic, topic: topic, user_level: 'beginner'})
    })
    .then(function(r) { return r.json(); })
    .then(function(result) {
        if (result.status === 'success') {
            chatSessionId = result.session_id;
            
            var chatHtml = '<div id="chatModal" style="position:fixed;bottom:20px;right:20px;width:380px;height:500px;background:white;border-radius:15px;box-shadow:0 20px 60px rgba(0,0,0,0.3);z-index:9999;display:flex;flex-direction:column;">';
            chatHtml += '<div style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:15px;border-radius:15px 15px 0 0;display:flex;justify-content:space-between;align-items:center;">';
            chatHtml += '<strong>🤖 AI Tutor</strong>';
            chatHtml += '<button onclick="closeChat()" style="background:none;border:none;color:white;font-size:20px;cursor:pointer;">×</button>';
            chatHtml += '</div>';
            chatHtml += '<div id="chatMessages" style="flex:1;overflow-y:auto;padding:15px;background:#f8f9fa;">';
            chatHtml += '<div style="background:#e8f5e9;padding:10px;border-radius:10px;margin-bottom:10px;max-width:80%;"><strong>AI:</strong> ' + result.ai_message + '</div>';
            chatHtml += '</div>';
            chatHtml += '<div style="padding:10px;border-top:1px solid #e0e0e0;display:flex;">';
            chatHtml += '<input type="text" id="chatInput" placeholder="Type your reply..." style="flex:1;border:1px solid #e0e0e0;border-radius:20px;padding:10px 15px;outline:none;">';
            chatHtml += '<button onclick="sendChatMessage()" style="background:#3ba591;color:white;border:none;border-radius:50%;width:40px;height:40px;margin-left:10px;cursor:pointer;font-size:18px;">➤</button>';
            chatHtml += '</div>';
            chatHtml += '</div>';
            
            document.body.insertAdjacentHTML('beforeend', chatHtml);
        }
    })
    .catch(function(e) { alert('Error: ' + e.message); });
}

function closeChat() {
    var modal = document.getElementById('chatModal');
    if (modal) modal.remove();
    chatSessionId = null;
}

function sendChatMessage() {
    var input = document.getElementById('chatInput');
    var message = input.value.trim();
    if (!message || !chatSessionId) return;
    
    input.value = '';
    
    var messagesDiv = document.getElementById('chatMessages');
    
    // Show user message
    messagesDiv.innerHTML += '<div style="background:#e3f2fd;padding:10px;border-radius:10px;margin-bottom:10px;max-width:80%;margin-left:auto;"><strong>You:</strong> ' + message + '</div>';
    
    // Show typing indicator
    messagesDiv.innerHTML += '<div id="typingIndicator" style="color:#999;font-size:12px;margin-bottom:10px;">AI is typing...</div>';
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    
    fetch('/api/tutor/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({session_id: chatSessionId, user_message: message})
    })
    .then(function(r) { return r.json(); })
    .then(function(result) {
        // Remove typing indicator
        var typing = document.getElementById('typingIndicator');
        if (typing) typing.remove();
        
        if (result.status === 'success') {
            messagesDiv.innerHTML += '<div style="background:#e8f5e9;padding:10px;border-radius:10px;margin-bottom:10px;max-width:80%;"><strong>AI:</strong> ' + result.ai_response + '</div>';
        }
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    })
    .catch(function(e) {
        var typing = document.getElementById('typingIndicator');
        if (typing) typing.remove();
        messagesDiv.innerHTML += '<div style="color:red;">Error: ' + e.message + '</div>';
    });
}

// Allow Enter key to send message
document.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && document.getElementById('chatInput') && document.activeElement === document.getElementById('chatInput')) {
        sendChatMessage();
    }
});
</script>"""

if old_script in content:
    content = content.replace(old_script, new_script)
    with open('templates/training.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ Complete chat interface with reply functionality added!')
else:
    print('Old script not found - checking alternative')
    # Try to find and replace the chat button script
    import re
    pattern = r'<script>.*?chatBtn.*?</script>'
    content = re.sub(pattern, new_script, content, flags=re.DOTALL)
    with open('templates/training.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ Fixed with regex')
