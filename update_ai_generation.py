with open('templates/companies.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Update startPatternMock to call AI generation
old_fetch = "fetch('/api/company-patterns/start'"
new_fetch = "fetch('/api/ai-pattern/generate-questions'"

if old_fetch in content:
    content = content.replace(old_fetch, new_fetch)
    
    # Update request body
    old_body = """body: JSON.stringify({
                        email: email,
                        company_id: companyId,
                        pattern_id: patternId
                    })"""
    
    new_body = """body: JSON.stringify({
                        company_name: companyId.toUpperCase(),
                        pattern_name: patternId,
                        sections: [
                            {name: 'Aptitude', count: 20, topics: ['Quant', 'Logical']},
                            {name: 'Technical', count: 15, topics: ['DSA', 'Algorithms']},
                            {name: 'Coding', count: 2, topics: ['DSA', 'Problem Solving']}
                        ]
                    })"""
    
    if old_body in content:
        content = content.replace(old_body, new_body)
    
    with open('templates/companies.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ Companies page updated to use AI generation')
else:
    print('Pattern not found')
