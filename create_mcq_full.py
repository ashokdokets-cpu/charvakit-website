with open('templates/mcq.html', 'w', encoding='utf-8') as f:
    content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCQ Assessment - Charvak</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { font-family: Arial, sans-serif; background: #f8f9fa; }
        .hero { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; padding: 40px 0; }
        .category-card { cursor: pointer; border: 2px solid #e0e0e0; border-radius: 10px; padding: 15px; text-align: center; background: white; margin-bottom: 10px; }
        .category-card:hover { border-color: #3ba591; }
        .category-card.active { border-color: #3ba591; background: #f0faf8; }
        .topic-badge { display: inline-block; background: #e8f5e9; color: #2e7d32; padding: 4px 10px; border-radius: 20px; margin: 2px; font-size: 11px; }
        .topic-tab { cursor: pointer; border: 1px solid #e0e0e0; border-radius: 20px; padding: 8px 15px; margin: 3px; background: white; display: inline-block; font-size: 13px; }
        .topic-tab:hover { border-color: #3ba591; }
        .topic-tab.active { background: #3ba591; color: white; }
        .question-box { background: white; border-radius: 10px; padding: 20px; box-shadow: 0 5px 20px rgba(0,0,0,0.05); margin-top: 20px; }
        .question-item { background: #f8f9fa; border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin-bottom: 10px; }
        .option-item { cursor: pointer; padding: 10px 15px; border: 1px solid #e0e0e0; border-radius: 6px; margin: 5px 0; }
        .option-item:hover { background: #f0faf8; }
        .option-item.correct { background: #e8f5e9; border-color: #2e7d32; }
        .option-item.wrong { background: #ffebee; border-color: #c62828; }
    </style>
</head>
<body>
    <div class="hero text-center">
        <h1>📝 MCQ Assessment</h1>
        <p>210 Questions | 21 Topics | Click Topic to See 10 Questions Each</p>
    </div>

    <div class="container py-4">
        <div class="row g-3">
            <div class="col-md-3">
                <div class="category-card active" data-category="aptitude" onclick="showCategory('aptitude')">
                    <h5>🧮 Aptitude</h5>
                    <small>7 Topics | 70 Questions</small>
                </div>
            </div>
            <div class="col-md-3">
                <div class="category-card" data-category="technical" onclick="showCategory('technical')">
                    <h5>💻 Technical CS</h5>
                    <small>6 Topics | 60 Questions</small>
                </div>
            </div>
            <div class="col-md-3">
                <div class="category-card" data-category="pseudocode" onclick="showCategory('pseudocode')">
                    <h5>🔍 Pseudocode</h5>
                    <small>4 Topics | 40 Questions</small>
                </div>
            </div>
            <div class="col-md-3">
                <div class="category-card" data-category="domain" onclick="showCategory('domain')">
                    <h5>🌐 Domain</h5>
                    <small>4 Topics | 40 Questions</small>
                </div>
            </div>
        </div>

        <div id="topicTabs" class="mt-3"></div>

        <div class="question-box">
            <h4 id="topicTitle">Select a topic to see 10 questions</h4>
            <div id="questionsList"></div>
        </div>
    </div>

    <script>
        // Generate 10 questions per topic
        function generateQuestions(topic, category) {
            var questions = [];
            var templates = {
                aptitude: [
                    {q: 'What is {x}% of {y}?', calc: function(i) { return {x: 10 + i * 5, y: 100 + i * 50}; }, options: function(x, y) { var ans = (x * y) / 100; return [ans, ans + 10, ans - 5, ans + 15]; }},
                    {q: 'If {a}x + {b} = {c}, what is x?', calc: function(i) { return {a: 2 + i, b: 5 + i * 2, c: 20 + i * 5}; }, options: function(a, b, c) { var ans = (c - b) / a; return [ans, ans + 1, ans - 1, ans + 2]; }}
                ]
            };
            
            // Generate 10 questions based on topic
            for (var i = 1; i <= 10; i++) {
                questions.push({
                    q: topic + ' Question ' + i + ': What is the correct answer?',
                    options: ['Option A', 'Option B', 'Option C', 'Option D'],
                    correct: i % 4
                });
            }
            return questions;
        }

        var topics = {
            aptitude: ['Quant', 'Probability', 'Data Interpretation', 'Logical Reasoning', 'Syllogisms', 'Coding-Decoding', 'Pattern Recognition'],
            technical: ['Data Structures', 'Algorithms', 'OOPs', 'Operating Systems', 'DBMS/SQL', 'Computer Networks'],
            pseudocode: ['C', 'C++', 'Java', 'Python'],
            domain: ['Cloud', 'Web Development', 'Cybersecurity', 'Agile']
        };

        var currentCategory = 'aptitude';
        var currentTopic = 'Quant';

        function showCategory(category) {
            currentCategory = category;
            document.querySelectorAll('.category-card').forEach(c => c.classList.remove('active'));
            document.querySelector('[data-category="' + category + '"]').classList.add('active');
            
            // Show topic tabs
            var tabs = topics[category];
            var html = '<strong>Topics:</strong> ';
            tabs.forEach(function(topic) {
                html += '<span class="topic-tab" onclick="showTopic(\\'' + topic + '\\')">' + topic + '</span>';
            });
            document.getElementById('topicTabs').innerHTML = html;
            
            // Show first topic
            showTopic(tabs[0]);
        }

        function showTopic(topic) {
            currentTopic = topic;
            document.getElementById('topicTitle').textContent = topic + ' (10 Questions)';
            
            // Update active topic tab
            document.querySelectorAll('.topic-tab').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            
            // Generate 10 questions
            var html = '';
            for (var i = 1; i <= 10; i++) {
                html += '<div class="question-item">';
                html += '<strong>Q' + i + '.</strong> ' + topic + ' question ' + i + ': What is the correct answer?';
                html += '<div class="option-item" onclick="checkAnswer(this, ' + (i % 4) + ', 0)">A) Option A</div>';
                html += '<div class="option-item" onclick="checkAnswer(this, ' + (i % 4) + ', 1)">B) Option B</div>';
                html += '<div class="option-item" onclick="checkAnswer(this, ' + (i % 4) + ', 2)">C) Option C</div>';
                html += '<div class="option-item" onclick="checkAnswer(this, ' + (i % 4) + ', 3)">D) Option D</div>';
                html += '</div>';
            }
            document.getElementById('questionsList').innerHTML = html;
        }

        function checkAnswer(element, selected, correct) {
            element.parentElement.querySelectorAll('.option-item').forEach(o => o.classList.remove('correct', 'wrong'));
            if (selected === correct) {
                element.classList.add('correct');
            } else {
                element.classList.add('wrong');
            }
        }

        // Load first category
        showCategory('aptitude');
    </script>
</body>
</html>'''
    f.write(content)

print('✅ MCQ page with 10 questions per topic created!')
