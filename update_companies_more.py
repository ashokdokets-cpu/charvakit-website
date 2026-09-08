with open('templates/companies.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace company cards section
old_cards = '''            <div class="col-6 col-md-3"><div class="company-card" data-company="tcs" onclick="selectCompany('tcs')"><h5>TCS</h5><small>NQT | 37 Questions</small></div></div>
            <div class="col-6 col-md-3"><div class="company-card" data-company="infosys" onclick="selectCompany('infosys')"><h5>Infosys</h5><small>InfyTQ | 38 Questions</small></div></div>
            <div class="col-6 col-md-3"><div class="company-card" data-company="cognizant" onclick="selectCompany('cognizant')"><h5>Cognizant</h5><small>GenC | 35 Questions</small></div></div>
            <div class="col-6 col-md-3"><div class="company-card" data-company="wipro" onclick="selectCompany('wipro')"><h5>Wipro</h5><small>Elite NTH | 24 Questions</small></div></div>
            <div class="col-6 col-md-3"><div class="company-card" data-company="accenture" onclick="selectCompany('accenture')"><h5>Accenture</h5><small>ASE | 50 Questions</small></div></div>
            <div class="col-6 col-md-3"><div class="company-card" data-company="capgemini" onclick="selectCompany('capgemini')"><h5>Capgemini</h5><small>Exceller | 37 Questions</small></div></div>
            <div class="col-6 col-md-3"><div class="company-card" data-company="ibm" onclick="selectCompany('ibm')"><h5>IBM</h5><small>32 Questions</small></div></div>
            <div class="col-6 col-md-3"><div class="company-card" data-company="hcl" onclick="selectCompany('hcl')"><h5>HCLTech</h5><small>TechBee | 37 Questions</small></div></div>'''

new_cards = '''            <div class="col-6 col-md-2"><div class="company-card" data-company="tcs" onclick="selectCompany('tcs')"><h5>TCS</h5><small>37 Q</small></div></div>
            <div class="col-6 col-md-2"><div class="company-card" data-company="infosys" onclick="selectCompany('infosys')"><h5>Infosys</h5><small>38 Q</small></div></div>
            <div class="col-6 col-md-2"><div class="company-card" data-company="cognizant" onclick="selectCompany('cognizant')"><h5>Cognizant</h5><small>35 Q</small></div></div>
            <div class="col-6 col-md-2"><div class="company-card" data-company="wipro" onclick="selectCompany('wipro')"><h5>Wipro</h5><small>24 Q</small></div></div>
            <div class="col-6 col-md-2"><div class="company-card" data-company="accenture" onclick="selectCompany('accenture')"><h5>Accenture</h5><small>50 Q</small></div></div>
            <div class="col-6 col-md-2"><div class="company-card" data-company="capgemini" onclick="selectCompany('capgemini')"><h5>Capgemini</h5><small>37 Q</small></div></div>
            <div class="col-6 col-md-2"><div class="company-card" data-company="ibm" onclick="selectCompany('ibm')"><h5>IBM</h5><small>32 Q</small></div></div>
            <div class="col-6 col-md-2"><div class="company-card" data-company="hcl" onclick="selectCompany('hcl')"><h5>HCLTech</h5><small>37 Q</small></div></div>
            <div class="col-6 col-md-2"><div class="company-card" data-company="tech_mahindra" onclick="selectCompany('tech_mahindra')"><h5>Tech Mahindra</h5><small>32 Q</small></div></div>
            <div class="col-6 col-md-2"><div class="company-card" data-company="lti" onclick="selectCompany('lti')"><h5>LTI</h5><small>32 Q</small></div></div>
            <div class="col-6 col-md-2"><div class="company-card" data-company="mindtree" onclick="selectCompany('mindtree')"><h5>Mindtree</h5><small>32 Q</small></div></div>
            <div class="col-6 col-md-2"><div class="company-card" data-company="deloitte" onclick="selectCompany('deloitte')"><h5>Deloitte</h5><small>40 Q</small></div></div>
            <div class="col-6 col-md-2"><div class="company-card" data-company="kpmg" onclick="selectCompany('kpmg')"><h5>KPMG</h5><small>40 Q</small></div></div>
            <div class="col-6 col-md-2"><div class="company-card" data-company="ey" onclick="selectCompany('ey')"><h5>EY</h5><small>40 Q</small></div></div>
            <div class="col-6 col-md-2"><div class="company-card" data-company="pwc" onclick="selectCompany('pwc')"><h5>PwC</h5><small>40 Q</small></div></div>
            <div class="col-6 col-md-2"><div class="company-card" data-company="amazon" onclick="selectCompany('amazon')"><h5>Amazon</h5><small>37 Q</small></div></div>
            <div class="col-6 col-md-2"><div class="company-card" data-company="google" onclick="selectCompany('google')"><h5>Google</h5><small>37 Q</small></div></div>
            <div class="col-6 col-md-2"><div class="company-card" data-company="microsoft" onclick="selectCompany('microsoft')"><h5>Microsoft</h5><small>37 Q</small></div></div>'''

if old_cards in content:
    content = content.replace(old_cards, new_cards)
    with open('templates/companies.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ Companies page updated with 18 companies!')
else:
    print('Pattern not found - trying alternative')
    # Add more companies after hcl
    content = content.replace(
        '<div class="col-6 col-md-3"><div class="company-card" data-company="hcl" onclick="selectCompany(\'hcl\')"><h5>HCLTech</h5><small>TechBee | 37 Questions</small></div></div>',
        '<div class="col-6 col-md-3"><div class="company-card" data-company="hcl" onclick="selectCompany(\'hcl\')"><h5>HCLTech</h5><small>TechBee | 37 Questions</small></div></div>\n            <div class="col-6 col-md-3"><div class="company-card" data-company="amazon" onclick="selectCompany(\'amazon\')"><h5>Amazon</h5><small>SDE | 37 Questions</small></div></div>\n            <div class="col-6 col-md-3"><div class="company-card" data-company="google" onclick="selectCompany(\'google\')"><h5>Google</h5><small>SWE | 37 Questions</small></div></div>\n            <div class="col-6 col-md-3"><div class="company-card" data-company="microsoft" onclick="selectCompany(\'microsoft\')"><h5>Microsoft</h5><small>SWE | 37 Questions</small></div></div>',
        1
    )
    with open('templates/companies.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ Added Amazon, Google, Microsoft')
