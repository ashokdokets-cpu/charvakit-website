with open('complete_mock_drive.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the configs section and add more companies
old_config_end = '''            "accenture": {
                "name": "Accenture", "pattern": "ASE",
                "sections": [
                    {"name": "Cognitive", "count": 25, "time": "60 min", "topics": ["Aptitude", "Logical"]},
                    {"name": "Technical", "count": 15, "time": "30 min", "topics": ["CS Fundamentals"]},
                    {"name": "Communication", "count": 10, "time": "20 min", "topics": ["Grammar"]}
                ]
            }
        }'''

new_config_addition = '''            "accenture": {
                "name": "Accenture", "pattern": "ASE",
                "sections": [
                    {"name": "Cognitive", "count": 25, "time": "60 min", "topics": ["Aptitude", "Logical"]},
                    {"name": "Technical", "count": 15, "time": "30 min", "topics": ["CS Fundamentals"]},
                    {"name": "Communication", "count": 10, "time": "20 min", "topics": ["Grammar"]}
                ]
            },
            "capgemini": {
                "name": "Capgemini", "pattern": "Exceller",
                "sections": [
                    {"name": "Aptitude", "count": 20, "time": "60 min", "topics": ["Quant", "Logical"]},
                    {"name": "Technical", "count": 15, "time": "30 min", "topics": ["DSA", "DBMS"]},
                    {"name": "Coding", "count": 2, "time": "45 min", "topics": ["Basic"]}
                ]
            },
            "ibm": {
                "name": "IBM", "pattern": "Associate",
                "sections": [
                    {"name": "Aptitude", "count": 20, "time": "60 min", "topics": ["Quant", "Logical"]},
                    {"name": "Technical", "count": 10, "time": "30 min", "topics": ["DSA", "OOPs"]},
                    {"name": "Coding", "count": 2, "time": "45 min", "topics": ["Basic", "DSA"]}
                ]
            },
            "hcl": {
                "name": "HCLTech", "pattern": "TechBee",
                "sections": [
                    {"name": "Aptitude", "count": 20, "time": "60 min", "topics": ["Quant", "Verbal"]},
                    {"name": "Technical", "count": 15, "time": "30 min", "topics": ["CS Fundamentals"]},
                    {"name": "Coding", "count": 2, "time": "30 min", "topics": ["Basic"]}
                ]
            },
            "tech_mahindra": {
                "name": "Tech Mahindra", "pattern": "Talent",
                "sections": [
                    {"name": "Aptitude", "count": 20, "time": "60 min", "topics": ["Quant", "Logical"]},
                    {"name": "Technical", "count": 10, "time": "30 min", "topics": ["DSA"]},
                    {"name": "Coding", "count": 2, "time": "45 min", "topics": ["Basic"]}
                ]
            },
            "lti": {
                "name": "LTI", "pattern": "GET",
                "sections": [
                    {"name": "Aptitude", "count": 20, "time": "60 min", "topics": ["Quant", "Logical"]},
                    {"name": "Technical", "count": 10, "time": "30 min", "topics": ["DSA"]},
                    {"name": "Coding", "count": 2, "time": "45 min", "topics": ["Basic"]}
                ]
            },
            "mindtree": {
                "name": "Mindtree", "pattern": "Graduate",
                "sections": [
                    {"name": "Aptitude", "count": 20, "time": "60 min", "topics": ["Quant", "Logical"]},
                    {"name": "Technical", "count": 10, "time": "30 min", "topics": ["DSA"]},
                    {"name": "Coding", "count": 2, "time": "45 min", "topics": ["Basic"]}
                ]
            },
            "deloitte": {
                "name": "Deloitte", "pattern": "Analyst",
                "sections": [
                    {"name": "Aptitude", "count": 25, "time": "60 min", "topics": ["Quant", "Logical", "Verbal"]},
                    {"name": "Technical", "count": 10, "time": "30 min", "topics": ["CS Fundamentals"]},
                    {"name": "Communication", "count": 5, "time": "15 min", "topics": ["Grammar"]}
                ]
            },
            "kpmg": {
                "name": "KPMG", "pattern": "Analyst",
                "sections": [
                    {"name": "Aptitude", "count": 25, "time": "60 min", "topics": ["Quant", "Logical", "Verbal"]},
                    {"name": "Technical", "count": 10, "time": "30 min", "topics": ["CS Fundamentals"]},
                    {"name": "Communication", "count": 5, "time": "15 min", "topics": ["Grammar"]}
                ]
            },
            "ey": {
                "name": "EY", "pattern": "Associate",
                "sections": [
                    {"name": "Aptitude", "count": 25, "time": "60 min", "topics": ["Quant", "Logical", "Verbal"]},
                    {"name": "Technical", "count": 10, "time": "30 min", "topics": ["CS Fundamentals"]},
                    {"name": "Communication", "count": 5, "time": "15 min", "topics": ["Grammar"]}
                ]
            },
            "pwc": {
                "name": "PwC", "pattern": "Associate",
                "sections": [
                    {"name": "Aptitude", "count": 25, "time": "60 min", "topics": ["Quant", "Logical", "Verbal"]},
                    {"name": "Technical", "count": 10, "time": "30 min", "topics": ["CS Fundamentals"]},
                    {"name": "Communication", "count": 5, "time": "15 min", "topics": ["Grammar"]}
                ]
            },
            "amazon": {
                "name": "Amazon", "pattern": "SDE",
                "sections": [
                    {"name": "Aptitude", "count": 20, "time": "60 min", "topics": ["Quant", "Logical"]},
                    {"name": "Technical", "count": 15, "time": "30 min", "topics": ["DSA", "Algorithms"]},
                    {"name": "Coding", "count": 2, "time": "60 min", "topics": ["DSA", "Problem Solving"]}
                ]
            },
            "google": {
                "name": "Google", "pattern": "SWE",
                "sections": [
                    {"name": "Aptitude", "count": 20, "time": "60 min", "topics": ["Quant", "Logical"]},
                    {"name": "Technical", "count": 15, "time": "30 min", "topics": ["DSA", "Algorithms"]},
                    {"name": "Coding", "count": 2, "time": "60 min", "topics": ["DSA", "Problem Solving"]}
                ]
            },
            "microsoft": {
                "name": "Microsoft", "pattern": "SWE",
                "sections": [
                    {"name": "Aptitude", "count": 20, "time": "60 min", "topics": ["Quant", "Logical"]},
                    {"name": "Technical", "count": 15, "time": "30 min", "topics": ["DSA", "Algorithms"]},
                    {"name": "Coding", "count": 2, "time": "60 min", "topics": ["DSA", "Problem Solving"]}
                ]
            }
        }'''

if old_config_end in content:
    content = content.replace(old_config_end, new_config_addition)
    with open('complete_mock_drive.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ Added 12 more companies: Capgemini, IBM, HCL, Tech Mahindra, LTI, Mindtree, Deloitte, KPMG, EY, PwC, Amazon, Google, Microsoft')
else:
    print('Pattern not found')
