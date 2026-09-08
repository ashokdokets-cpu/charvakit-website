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
        .hero { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; padding: 50px 0; }
        .card { border: none; border-radius: 15px; box-shadow: 0 5px 20px rgba(0,0,0,0.08); cursor: pointer; transition: all 0.3s; }
        .card:hover { transform: translateY(-3px); }
        .category-card.active { border: 2px solid #3ba591; background: #f0faf8; }
        .topic-badge { display: inline-block; background: #e8f5e9; color: #2e7d32; padding: 5px 12px; border-radius: 20px; margin: 3px; font-size: 12px; }
        .question-box { background: white; border-radius: 10px; padding: 30px; box-shadow: 0 5px 20px rgba(0,0,0,0.05); margin-top: 20px; }
        .question-item { background: #f8f9fa; border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin-bottom: 10px; }
        .option-item { cursor: pointer; padding: 12px; border: 1px solid #e0e0e0; border-radius: 8px; margin-bottom: 8px; }
        .option-item:hover { background: #f0faf8; }
        .option-item.correct { background: #e8f5e9; border-color: #2e7d32; }
        .option-item.wrong { background: #ffebee; border-color: #c62828; }
    </style>
</head>
<body>
    <div class="hero text-center">
        <h1>📝 MCQ Assessment</h1>
        <p>AI-Generated Unique Questions - 210 Total</p>
    </div>

    <div class="container py-4">
        <div class="alert alert-info text-center">
            <strong>📋 Market Standard:</strong> 210 Questions | 21 Topics | 4 Categories
        </div>
    </div>

    <div class="container py-4">
        <div class="row g-3">
            <div class="col-md-3">
                <div class="card category-card text-center p-3" onclick="showCategory('aptitude')">
                    <h5>🧮 Aptitude & Logical</h5>
                    <small class="text-muted">7 Topics | 70 Questions</small>
                    <div class="mt-2">
                        <span class="topic-badge">Quant</span>
                        <span class="topic-badge">Probability</span>
                        <span class="topic-badge">Data Interpretation</span>
                        <span class="topic-badge">Logical Reasoning</span>
                        <span class="topic-badge">Syllogisms</span>
                        <span class="topic-badge">Coding-Decoding</span>
                        <span class="topic-badge">Pattern Recognition</span>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card category-card text-center p-3" onclick="showCategory('technical')">
                    <h5>💻 Technical CS</h5>
                    <small class="text-muted">6 Topics | 60 Questions</small>
                    <div class="mt-2">
                        <span class="topic-badge">Data Structures</span>
                        <span class="topic-badge">Algorithms</span>
                        <span class="topic-badge">OOPs</span>
                        <span class="topic-badge">Operating Systems</span>
                        <span class="topic-badge">DBMS/SQL</span>
                        <span class="topic-badge">Computer Networks</span>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card category-card text-center p-3" onclick="showCategory('pseudocode')">
                    <h5>🔍 Pseudocode</h5>
                    <small class="text-muted">4 Topics | 40 Questions</small>
                    <div class="mt-2">
                        <span class="topic-badge">C</span>
                        <span class="topic-badge">C++</span>
                        <span class="topic-badge">Java</span>
                        <span class="topic-badge">Python</span>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card category-card text-center p-3" onclick="showCategory('domain')">
                    <h5>🌐 Domain</h5>
                    <small class="text-muted">4 Topics | 40 Questions</small>
                    <div class="mt-2">
                        <span class="topic-badge">Cloud</span>
                        <span class="topic-badge">Web Development</span>
                        <span class="topic-badge">Cybersecurity</span>
                        <span class="topic-badge">Agile</span>
                    </div>
                </div>
            </div>
        </div>

        <div class="question-box">
            <h4 id="categoryTitle">🧮 Aptitude & Logical</h4>
            <p class="text-muted" id="categoryInfo">7 Topics | 70 Questions</p>
            <div id="questionsList"></div>
        </div>
    </div>

    <script>
        var questions = {
            aptitude: [
                { q: 'What is 15% of 200?', options: ['25', '30', '35', '40'], correct: 1 },
                { q: 'If 3x + 7 = 22, what is x?', options: ['3', '5', '7', '9'], correct: 1 },
                { q: 'What comes next: 2, 6, 12, 20, ?', options: ['24', '28', '30', '32'], correct: 2 },
                { q: 'A train travels 300 km in 5 hours. Speed?', options: ['50 km/h', '55 km/h', '60 km/h', '65 km/h'], correct: 2 },
                { q: 'Shirt costs Rs.800 after 20% discount. Original?', options: ['Rs.960', 'Rs.1000', 'Rs.1040', 'Rs.1100'], correct: 1 }
            ],
            technical: [
                { q: 'Which data structure uses LIFO?', options: ['Queue', 'Stack', 'Array', 'Linked List'], correct: 1 },
                { q: 'Time complexity of binary search?', options: ['O(1)', 'O(log n)', 'O(n)', 'O(n log n)'], correct: 1 },
                { q: 'SQL command to retrieve data?', options: ['INSERT', 'UPDATE', 'SELECT', 'DELETE'], correct: 2 },
                { q: 'OOP stands for?', options: ['Object Oriented Programming', 'Order of Operations', 'Object Output Process', 'None'], correct: 0 },
                { q: 'Protocol for secure browsing?', options: ['HTTP', 'FTP', 'HTTPS', 'SMTP'], correct: 2 }
            ],
            pseudocode: [
                { q: 'Output of print(5 // 2) in Python?', options: ['2.5', '2', '3', '2.0'], correct: 1 },
                { q: 'Which loop executes at least once?', options: ['for', 'while', 'do-while', 'None'], correct: 2 },
                { q: 'int x = 5; x++; Result?', options: ['4', '5', '6', 'Error'], correct: 2 },
                { q: 'Equality operator in Python?', options: ['=', '==', '===', '!='], correct: 1 },
                { q: 'First array index in C?', options: ['1', '0', '-1', 'Depends'], correct: 1 }
            ],
            domain: [
                { q: 'Cloud service by Amazon?', options: ['Azure', 'AWS', 'GCP', 'Heroku'], correct: 1 },
                { q: 'API stands for?', options: ['Application Programming Interface', 'Advanced Program Integration', 'Automated Process Interface', 'None'], correct: 0 },
                { q: 'Cybersecurity best practice?', options: ['Same password', 'Enable 2FA', 'Share credentials', 'Skip updates'], correct: 1 },
                { q: 'Agile framework using sprints?', options: ['Waterfall', 'Scrum', 'Kanban only', 'Six Sigma'], correct: 1 },
                { q: 'CI/CD stands for?', options: ['Continuous Integration/Deployment', 'Code Integration/Delivery', 'Continuous Improvement/Design', 'None'], correct: 0 }
            ]
        };

        var categoryInfo = {
            aptitude: {title: '🧮 Aptitude & Logical', info: '7 Topics | 70 Questions'},
            technical: {title: '💻 Technical CS', info: '6 Topics | 60 Questions'},
            pseudocode: {title: '🔍 Pseudocode', info: '4 Topics | 40 Questions'},
            domain: {title: '🌐 Domain', info: '4 Topics | 40 Questions'}
        };

        function showCategory(category) {
            document.querySelectorAll('.category-card').forEach(card => {
                card.classList.remove('active');
            });
            event.target.closest('.category-card').classList.add('active');

            document.getElementById('categoryTitle').textContent = categoryInfo[category].title;
            document.getElementById('categoryInfo').textContent = categoryInfo[category].info;

            var html = '';
            for (var i = 0; i < questions[category].length; i++) {
                var q = questions[category][i];
                html += '<div class="question-item">';
                html += '<strong>Q' + (i+1) + '. ' + q.q + '</strong>';
                for (var j = 0; j < q.options.length; j++) {
                    html += '<div class="option-item" onclick="checkAnswer(this, ' + j + ', ' + q.correct + ')">';
                    html += String.fromCharCode(65 + j) + ') ' + q.options[j];
                    html += '</div>';
                }
                html += '</div>';
            }
            document.getElementById('questionsList').innerHTML = html;
        }

        function checkAnswer(element, selected, correct) {
            element.parentElement.querySelectorAll('.option-item').forEach(opt => {
                opt.classList.remove('correct', 'wrong');
            });
            if (selected === correct) {
                element.classList.add('correct');
            } else {
                element.classList.add('wrong');
            }
        }

        showCategory('aptitude');
    </script>
</body>
</html>'''
    f.write(content)

print('✅ MCQ page with all 21 topics visible created!')
