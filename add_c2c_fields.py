with open('templates/na-client-signup.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add C2C fields after bench count section
old_bench = '<div class="mb-3"><label class="form-label">How many bench candidates do you have? (approx)</label><input type="number" class="form-control" id="benchCount" placeholder="e.g. 10"></div>'

new_bench = '''<div class="mb-3"><label class="form-label">How many bench candidates do you have? (approx)</label><input type="number" class="form-control" id="benchCount" placeholder="e.g. 10"></div>
            <div class="mb-3"><label class="form-label">Tax ID (EIN/CRA Number) *</label><input type="text" class="form-control" id="taxId" placeholder="XX-XXXXXXX" required></div>
            <div class="mb-3"><label class="form-label">Corporate Entity Name (LLC/Inc) *</label><input type="text" class="form-control" id="corporateName" placeholder="Your LLC/Inc Name" required></div>
            <div class="mb-3">
                <label class="form-label">Work Authorization Type *</label>
                <select class="form-select" id="workAuth" required>
                    <option value="">Select</option>
                    <option value="US_CITIZEN">US Citizen</option>
                    <option value="GC_HOLDER">Green Card Holder</option>
                    <option value="H1B_EMPLOYER_SPONSORED">H1B (Employer Sponsored)</option>
                    <option value="CA_CITIZEN">Canadian Citizen</option>
                    <option value="PR_HOLDER">Canadian PR</option>
                    <option value="OPEN_WORK_PERMIT">Open Work Permit</option>
                </select>
            </div>
            <div class="mb-3"><label class="form-label">Minimum Hourly Rate (USD) *</label><input type="number" class="form-control" id="minRate" placeholder="e.g., 75" required></div>
            <div class="mb-3"><label class="form-label">Tech Stack (comma separated) *</label><input type="text" class="form-control" id="techStack" placeholder="e.g., Python, React, AWS, SQL" required></div>'''

if old_bench in content:
    content = content.replace(old_bench, new_bench)
    with open('templates/na-client-signup.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ C2C compliance fields added!')
else:
    print('Pattern not found')
