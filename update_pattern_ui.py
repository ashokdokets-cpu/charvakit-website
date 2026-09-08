with open('templates/companies.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Update the selectCompany function to show patterns
old_select = '''        function selectCompany(companyId) {
            currentCompany = companyId;
            document.querySelectorAll('.company-card').forEach(c => c.classList.remove('active'));
            document.querySelector('[data-company="' + companyId + '"]').classList.add('active');
            
            var content = document.getElementById('mainContent');
            content.innerHTML = '<h4>Selected: ' + companyId.toUpperCase() + '</h4>';
            content.innerHTML += '<p class="text-muted">Click below to start your mock drive with AI-generated questions.</p>';
            content.innerHTML += '<button class="btn-custom" onclick="startMockDrive(\\'' + companyId + '\\')">🚀 Start ' + companyId.toUpperCase() + ' Mock Drive</button>';
        }'''

new_select = '''        async function selectCompany(companyId) {
            currentCompany = companyId;
            document.querySelectorAll('.company-card').forEach(c => c.classList.remove('active'));
            document.querySelector('[data-company="' + companyId + '"]').classList.add('active');
            
            var content = document.getElementById('mainContent');
            content.innerHTML = '<h4>Loading patterns for ' + companyId.toUpperCase() + '...</h4>';
            
            // Fetch patterns from API
            try {
                const response = await fetch('/api/company-patterns/' + companyId);
                const result = await response.json();
                
                if (result.status === 'success') {
                    var html = '<h4>' + result.company + ' - Available Patterns</h4>';
                    html += '<p class="text-muted">Select a pattern to start your mock drive:</p>';
                    
                    result.patterns.forEach(function(pattern) {
                        html += '<div class="question-item mb-3 p-3">';
                        html += '<strong>' + pattern.name + '</strong>';
                        html += '<span class="badge bg-' + getBadgeColor(pattern.difficulty) + ' ms-2">' + pattern.difficulty + '</span><br>';
                        html += '<small class="text-muted">' + pattern.description + '</small><br>';
                        html += '<small>Total Questions: ' + pattern.total_questions + '</small><br>';
                        html += '<button class="btn-custom mt-2" onclick="startPatternMock(\\'' + companyId + '\\', \\'' + pattern.id + '\\')">Start ' + pattern.name + ' →</button>';
                        html += '</div>';
                    });
                    
                    content.innerHTML = html;
                } else {
                    content.innerHTML = '<p class="text-danger">Company not found</p>';
                }
            } catch (error) {
                content.innerHTML = '<p class="text-danger">Error: ' + error.message + '</p>';
            }
        }

        function getBadgeColor(difficulty) {
            if (difficulty === 'Moderate') return 'success';
            if (difficulty === 'Hard') return 'warning';
            if (difficulty === 'Very Hard') return 'danger';
            return 'primary';
        }

        async function startPatternMock(companyId, patternId) {
            const email = prompt('Enter your email to start ' + patternId + ' mock drive:');
            if (!email) return;
            
            var content = document.getElementById('mainContent');
            content.innerHTML = '<p class="text-muted">Generating AI questions for ' + patternId + '...</p>';
            
            try {
                const response = await fetch('/api/company-patterns/start', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        email: email,
                        company_id: companyId,
                        pattern_id: patternId
                    })
                });
                const result = await response.json();
                
                if (result.status === 'success') {
                    var html = '<div class="alert alert-success">';
                    html += '<strong>✅ ' + result.pattern + ' Mock Drive Started!</strong><br>';
                    html += 'Company: ' + result.company + '<br>';
                    html += 'Difficulty: ' + result.difficulty + '<br>';
                    html += 'Description: ' + result.description + '<br>';
                    html += 'Total Questions: ' + result.total_questions;
                    html += '</div>';
                    
                    // Show sections
                    html += '<h5 class="mt-3">📋 Test Sections:</h5>';
                    result.sections.forEach(function(section) {
                        html += '<div class="section-item p-3 border rounded mb-2">';
                        html += '<strong>' + section.name + ':</strong> ' + section.count + ' Questions (' + section.time + ')<br>';
                        html += '<small class="text-muted">Topics: ' + section.topics.join(', ') + '</small>';
                        html += '</div>';
                    });
                    
                    html += '<p class="text-info mt-3">Questions will be AI-generated when you start the full test.</p>';
                    
                    content.innerHTML = html;
                }
            } catch (error) {
                content.innerHTML = '<p class="text-danger">Error: ' + error.message + '</p>';
            }
        }'''

if old_select in content:
    content = content.replace(old_select, new_select)
    with open('templates/companies.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ Pattern selection visible to users!')
else:
    print('Pattern not found')
