with open('templates/versant.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace browser TTS with ElevenLabs
old_play = """function playAudio(audioText, questionId) {
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
}"""

new_play = """async function playAudio(audioText, questionId) {
    var btn = document.getElementById('playBtn-' + questionId);
    if (btn) btn.textContent = '🔊 Generating AI Voice...';
    
    try {
        const response = await fetch('/api/voice/tts', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({text: audioText})
        });
        const result = await response.json();
        
        if (result.status === 'success' && result.audio_base64) {
            // Play ElevenLabs AI voice
            const audio = new Audio('data:audio/mpeg;base64,' + result.audio_base64);
            audio.play();
            
            if (btn) {
                btn.textContent = '🔊 Playing AI Voice...';
                audio.onended = function() {
                    btn.textContent = '🔊 Play Audio';
                };
            }
        } else {
            // Fallback to browser TTS
            if ('speechSynthesis' in window) {
                const utterance = new SpeechSynthesisUtterance(audioText);
                utterance.lang = 'en-US';
                speechSynthesis.speak(utterance);
            }
            if (btn) btn.textContent = '🔊 Play Audio';
        }
    } catch (e) {
        // Fallback to browser TTS
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(audioText);
            utterance.lang = 'en-US';
            speechSynthesis.speak(utterance);
        }
        if (btn) btn.textContent = '🔊 Play Audio';
    }
}"""

if old_play in content:
    content = content.replace(old_play, new_play)
    with open('templates/versant.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ ElevenLabs integrated into Versant!')
else:
    print('Pattern not found')
