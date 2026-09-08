with open('company_mock_complete.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add missing topics to question bank
old_bank_start = '''            "Grammar": [
                {"q": "Which is correct?", "options": ["He go", "He goes", "He going", "He gone"], "correct": 1},
                {"q": "What is the past tense of 'run'?", "options": ["Ran", "Runned", "Running", "Runs"], "correct": 0},
                {"q": "Which is a preposition?", "options": ["Run", "In", "Beautiful", "Quickly"], "correct": 1}
            ]'''

new_bank_addition = '''            "Grammar": [
                {"q": "Which is correct?", "options": ["He go", "He goes", "He going", "He gone"], "correct": 1},
                {"q": "What is the past tense of 'run'?", "options": ["Ran", "Runned", "Running", "Runs"], "correct": 0},
                {"q": "Which is a preposition?", "options": ["Run", "In", "Beautiful", "Quickly"], "correct": 1}
            ],
            "Quantitative": [
                {"q": "What is 20% of 500?", "options": ["80", "100", "120", "150"], "correct": 1},
                {"q": "If a train travels 240 km in 4 hours, speed?", "options": ["50 km/h", "55 km/h", "60 km/h", "65 km/h"], "correct": 2},
                {"q": "What is the LCM of 8 and 12?", "options": ["16", "24", "32", "48"], "correct": 1},
                {"q": "If 8 workers complete a job in 12 days, how many for 16 workers?", "options": ["4", "6", "8", "10"], "correct": 1},
                {"q": "What is 35% of 800?", "options": ["240", "260", "280", "300"], "correct": 2}
            ],
            "Analytical": [
                {"q": "If all A are B, and all B are C, then?", "options": ["All A are C", "Some A are C", "No A are C", "Cannot say"], "correct": 0},
                {"q": "Which number comes next: 2, 6, 12, 20, 30, ?", "options": ["36", "40", "42", "44"], "correct": 2},
                {"q": "If P is brother of Q, Q is sister of R, then P is R's?", "options": ["Brother", "Sister", "Cousin", "Cannot say"], "correct": 0},
                {"q": "Complete: 5, 10, 20, 40, ?", "options": ["60", "80", "100", "120"], "correct": 1},
                {"q": "If CAT = 24, DOG = ?", "options": ["26", "27", "28", "29"], "correct": 1}
            ],
            "Verbal": [
                {"q": "What is the synonym of 'happy'?", "options": ["Sad", "Joyful", "Angry", "Tired"], "correct": 1},
                {"q": "What is the antonym of 'big'?", "options": ["Large", "Huge", "Small", "Giant"], "correct": 2},
                {"q": "Complete: 'The cat ___ on the mat.'", "options": ["sit", "sits", "sitting", "sat"], "correct": 1},
                {"q": "Which word is a noun?", "options": ["Run", "Beautiful", "Table", "Quickly"], "correct": 2},
                {"q": "What is the plural of 'child'?", "options": ["Childs", "Children", "Childes", "Childrens"], "correct": 1}
            ],
            "Speaking": [
                {"q": "Which sentence is grammatically correct?", "options": ["I am going to school", "I is going to school", "I are going to school", "I be going to school"], "correct": 0},
                {"q": "What is the correct pronunciation of 'schedule' in British English?", "options": ["SKED-ule", "SHED-ule", "SKED-yool", "SHED-yool"], "correct": 1},
                {"q": "Which is a formal greeting?", "options": ["Hey!", "Good morning", "Yo!", "What's up?"], "correct": 1},
                {"q": "What is the correct response to 'How are you?'", "options": ["I'm fine, thank you", "I are fine", "Me fine", "Good I"], "correct": 0}
            ],
            "SQL": [
                {"q": "Which SQL command retrieves data?", "options": ["INSERT", "UPDATE", "SELECT", "DELETE"], "correct": 2},
                {"q": "What is a primary key?", "options": ["Unique identifier", "Foreign key", "Index", "None"], "correct": 0},
                {"q": "Which is an aggregate function?", "options": ["WHERE", "SUM", "ORDER BY", "GROUP BY"], "correct": 1},
                {"q": "Which join returns all rows from left table?", "options": ["INNER", "LEFT", "RIGHT", "FULL"], "correct": 1},
                {"q": "What does SQL stand for?", "options": ["Structured Query Language", "Simple Query Language", "Standard Query Language", "None"], "correct": 0}
            ],
            "Debugging": [
                {"q": "What is a syntax error?", "options": ["Code writing error", "Runtime error", "Logic error", "None"], "correct": 0},
                {"q": "Which tool helps debug Python code?", "options": ["pdb", "npm", "pip", "git"], "correct": 0},
                {"q": "What is a breakpoint?", "options": ["Pause execution point", "Error", "Comment", "None"], "correct": 0},
                {"q": "What is a runtime error?", "options": ["Error during execution", "Error during writing", "Error during reading", "None"], "correct": 0}
            ]'''

if old_bank_start in content:
    content = content.replace(old_bank_start, new_bank_addition)
    with open('company_mock_complete.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ Cognizant topics added: Quantitative, Analytical, Verbal, Speaking, SQL, Debugging')
else:
    print('Pattern not found')
