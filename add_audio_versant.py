with open('templates/versant.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add audio recording functionality
audio_script = '''
<script>
var mediaRecorder = null;
var recordedChunks = [];
var isRecording = false;
var currentAudio = null;

// Audio Recording
async function startRecording(questionId) {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        recordedChunks = [];
        
        mediaRecorder.ondataavailable = function(e) {
            if (e.data.size > 0) recordedChunks.push(e.data);
        };
        
        mediaRecorder.onstop = function() {
            const blob = new Blob(recordedChunks, {type: 'audio/webm'});
            const audioUrl = URL.createObjectURL(blob);
            
            // Show playback
            var playback = document.getElementById('playback-' + questionId);
            if (playback) {
                playback.src = audioUrl;
                playback.style.display = 'block';
            }
            
            // Save recording
            saveRecording(questionId, blob);
        };
        
        mediaRecorder.start();
        isRecording = true;
        
        // Update button
        var btn = document.getElementById('recordBtn-' + questionId);
        if (btn) {
            btn.textContent = '⏹ Stop Recording';
            btn.classList.add('recording');
        }
    } catch (err) {
        alert('Microphone access denied. Please allow microphone access to record.');
    }
}

function stopRecording(questionId) {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        isRecording = false;
        
        var btn = document.getElementById('recordBtn-' + questionId);
        if (btn) {
            btn.textContent = '🎤 Record Again';
            btn.classList.remove('recording');
        }
    }
}

function toggleRecording(questionId) {
    if (isRecording) {
        stopRecording(questionId);
    } else {
        startRecording(questionId);
    }
}

function saveRecording(questionId, blob) {
    // Convert to base64 and save
    const reader = new FileReader();
    reader.readAsDataURL(blob);
    reader.onloadend = function() {
        // Save to backend
        fetch('/api/versant/record-audio', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                question_id: questionId,
                audio_data: reader.result
            })
        })
        .then(function(r) { return r.json(); })
        .then(function(result) {
            console.log('Recording saved:', result);
        })
        .catch(function(e) {
            console.error('Save failed:', e);
        });
    };
}

// Audio Playback for Repeats section
function playAudio(audioText, questionId) {
    // Use Web Speech API for text-to-speech
    if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(audioText);
        utterance.lang = 'en-US';
        utterance.rate = 0.9;
        speechSynthesis.speak(utterance);
        
        // Show playing indicator
        var btn = document.getElementById('playBtn-' + questionId);
        if (btn) {
            btn.textContent = '🔊 Playing...';
            setTimeout(function() {
                btn.textContent = '🔊 Play Audio';
            }, 2000);
        }
    }
}
</script>'''

# Add the script before </body>
if 'mediaRecorder' not in content:
    content = content.replace('</body>', audio_script + '\n</body>', 1)
    with open('templates/versant.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ Audio recording and playback added!')
else:
    print('Audio already exists')
