with open('templates/versant.html', 'w', encoding='utf-8') as f:
    content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Versant English Assessment - Charvak</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { font-family: Arial, sans-serif; background: #f8f9fa; }
        .hero { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 50px 0; }
        .section-tab { cursor: pointer; border: 2px solid #e0e0e0; border-radius: 10px; padding: 15px; text-align: center; margin-bottom: 10px; background: white; }
        .section-tab:hover { border-color: #3ba591; }
        .section-tab.active { border-color: #3ba591; background: #f0faf8; }
        .question-box { background: white; border-radius: 10px; padding: 30px; box-shadow: 0 5px 20px rgba(0,0,0,0.05); margin-top: 20px; }
        .question-item { background: #f8f9fa; border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin-bottom: 10px; }
        .alert-info { border-radius: 10px; }
    </style>
</head>
<body>
    <div class="hero text-center">
        <h1>🗣️ Versant English Assessment</h1>
        <p>AI-Scored English Communication Test - 50 Minutes</p>
    </div>

    <div class="container py-4">
        <div class="alert alert-info text-center">
            <strong>📋 Market Standard (Pearson Versant):</strong> 48 Total Questions | Read Aloud (8Q) | Repeats (16Q) | Sentence Builds (10Q) | Conversations (10Q) | Story Retelling (3Q) | Summary (1Q)
        </div>
    </div>

    <div class="container py-4">
        <div class="row g-2">
            <div class="col-6 col-md-2"><div class="section-tab" onclick="showSection('read_aloud')">📖 Read Aloud<br><small>8 Questions</small></div></div>
            <div class="col-6 col-md-2"><div class="section-tab" onclick="showSection('repeats')">🎧 Repeats<br><small>16 Questions</small></div></div>
            <div class="col-6 col-md-2"><div class="section-tab" onclick="showSection('sentence_builds')">✏️ Sentence Builds<br><small>10 Questions</small></div></div>
            <div class="col-6 col-md-2"><div class="section-tab" onclick="showSection('conversations')">💬 Conversations<br><small>10 Questions</small></div></div>
            <div class="col-6 col-md-2"><div class="section-tab" onclick="showSection('story_retelling')">📝 Story Retelling<br><small>3 Questions</small></div></div>
            <div class="col-6 col-md-2"><div class="section-tab" onclick="showSection('summary_opinion')">📄 Summary<br><small>1 Question</small></div></div>
        </div>

        <div class="question-box">
            <h4 id="sectionTitle">📖 Read Aloud</h4>
            <p class="text-muted" id="sectionInstruction"></p>
            <div id="questionsList"></div>
        </div>
    </div>

    <script>
        var data = {
            read_aloud: {
                title: '📖 Read Aloud (8 Questions)',
                instruction: 'Read the following sentences aloud clearly and naturally.',
                questions: [
                    'The company will announce quarterly results next week.',
                    'Please submit your assignment by Friday afternoon.',
                    'The new software update includes several improvements.',
                    'Our team meeting has been rescheduled to Monday.',
                    'Customer satisfaction is our top priority for this quarter.',
                    'The annual report will be published in March next year.',
                    'Please review the document carefully before signing it.',
                    'The training session starts at nine o\'clock sharp tomorrow.'
                ]
            },
            repeats: {
                title: '🎧 Repeats (16 Questions)',
                instruction: 'Listen to the audio, then repeat exactly what you heard.',
                questions: [
                    'The meeting has been rescheduled to Thursday afternoon.',
                    'Please submit your report by the end of this week.',
                    'The new policy takes effect from the first of next month.',
                    'We need to review the proposal before making a decision.',
                    'The training session will be held in the main conference room.',
                    'Customer feedback is essential for improving our services.',
                    'The project deadline has been extended by two weeks.',
                    'Please ensure all documents are submitted on time.',
                    'The team achieved remarkable results this quarter.',
                    'We should schedule a follow-up meeting next week.',
                    'The budget approval process takes about two weeks.',
                    'Please contact the support team if you need assistance.',
                    'The annual performance review will be in December.',
                    'We need to analyze the data before presenting it.',
                    'The company is expanding its operations internationally.',
                    'Please review the document carefully before signing.'
                ]
            },
            sentence_builds: {
                title: '✏️ Sentence Builds (10 Questions)',
                instruction: 'Rearrange the words to form a grammatically correct sentence.',
                questions: [
                    'the / meeting / starts / at / nine / sharp',
                    'please / submit / the / report / by / Friday',
                    'the / team / completed / the / project / successfully',
                    'we / will / discuss / the / budget / next / week',
                    'she / has / been / working / here / since / 2020',
                    'the / new / policy / takes / effect / from / Monday',
                    'they / are / planning / to / launch / the / product',
                    'the / manager / approved / the / proposal / yesterday',
                    'we / need / to / improve / customer / satisfaction',
                    'the / training / program / begins / next / month'
                ]
            },
            conversations: {
                title: '💬 Conversations (10 Questions)',
                instruction: 'Listen to the question and record your spoken answer.',
                questions: [
                    'Would you find a stove in a kitchen or a bedroom?',
                    'What would you do if you missed an important deadline?',
                    'How do you prioritize tasks when everything is urgent?',
                    'What is the best way to handle a difficult customer?',
                    'Describe your ideal work environment and why.',
                    'How would you explain a complex idea to a colleague?',
                    'What qualities do you think make a good team leader?',
                    'How do you handle constructive criticism from your supervisor?',
                    'What steps would you take to improve customer satisfaction?',
                    'How do you stay organized when managing multiple tasks?'
                ]
            },
            story_retelling: {
                title: '📝 Story Retelling (3 Questions)',
                instruction: 'Read the passage, then retell it in your own words.',
                questions: [
                    'A young software engineer joined a startup and within six months developed an innovative mobile application that attracted over a million users. Her dedication to learning and willingness to take risks led to rapid career growth.',
                    'The marketing team launched an ambitious campaign during the holiday season. By analyzing customer data and personalizing their approach, they managed to double the customer base in three months.',
                    'A manufacturing company was struggling with declining productivity. After implementing automation and providing training to employees, they saw a forty percent increase in output within one year.'
                ]
            },
            summary_opinion: {
                title: '📄 Summary & Opinion (1 Question)',
                instruction: 'Write a summary and your opinion on the topic. This is the only section where you type.',
                questions: [
                    'Write a summary of the impact of artificial intelligence on modern workplaces. Include your opinion on whether AI will create more jobs than it eliminates. (18 minutes)'
                ]
            }
        };

        function showSection(sectionId) {
            var section = data[sectionId];
            if (!section) return;

            // Update active tab
            var tabs = document.querySelectorAll('.section-tab');
            for (var i = 0; i < tabs.length; i++) {
                tabs[i].classList.remove('active');
            }
            event.target.closest('.section-tab').classList.add('active');

            document.getElementById('sectionTitle').textContent = section.title;
            document.getElementById('sectionInstruction').textContent = section.instruction;

            var html = '';
            for (var j = 0; j < section.questions.length; j++) {
                html += '<div class="question-item">';
                html += '<strong>Question ' + (j + 1) + ':</strong> ' + section.questions[j];
                html += '</div>';
            }
            document.getElementById('questionsList').innerHTML = html;
        }

        // Load first section
        showSection('read_aloud');
    </script>
</body>
</html>'''
    f.write(content)

print('✅ Versant page with ALL questions visible created!')
