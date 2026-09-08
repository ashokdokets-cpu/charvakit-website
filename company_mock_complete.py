"""
Charvak Complete Company Mock Drive
Questions per section, answer tracking, AI results
"""
import logging
import json
import os
from datetime import datetime

logger = logging.getLogger("charvakit.company_mock_complete")

class CompanyMockDrive:
    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv()
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.mock_sessions = {}
        self.mock_results = {}
        logger.info("Company Mock Drive ready")
    
    def get_company_sections(self, company_id):
        """Get complete section details with questions."""
        companies = {
            "tcs": {
                "name": "TCS",
                "pattern": "NQT",
                "sections": [
                    {
                        "name": "Foundation",
                        "questions_count": 25,
                        "time": "75 min",
                        "topics": ["Aptitude", "Logical", "Verbal"],
                        "questions": self._generate_section_questions("Foundation", ["Aptitude", "Logical", "Verbal"], 10)
                    },
                    {
                        "name": "Advanced",
                        "questions_count": 10,
                        "time": "25 min",
                        "topics": ["Advanced Quant", "Advanced Logic"],
                        "questions": self._generate_section_questions("Advanced", ["Advanced Quant", "Logic"], 5)
                    },
                    {
                        "name": "Coding",
                        "questions_count": 2,
                        "time": "55 min",
                        "topics": ["DSA", "Problem Solving"],
                        "questions": self._generate_section_questions("Coding", ["DSA", "Algorithms"], 2)
                    }
                ]
            },
            "infosys": {
                "name": "Infosys",
                "pattern": "InfyTQ",
                "sections": [
                    {"name": "Aptitude", "questions_count": 20, "time": "60 min", "topics": ["Quant", "Logical"], "questions": self._generate_section_questions("Aptitude", ["Quant", "Logical"], 5)},
                    {"name": "Technical", "questions_count": 15, "time": "30 min", "topics": ["DSA", "DBMS", "OOPs"], "questions": self._generate_section_questions("Technical", ["DSA", "DBMS"], 3)},
                    {"name": "Coding", "questions_count": 3, "time": "90 min", "topics": ["DSA", "Algorithms"], "questions": self._generate_section_questions("Coding", ["DSA"], 2)}
                ]
            },
            "wipro": {
                "name": "Wipro",
                "pattern": "Elite NTH",
                "sections": [
                    {"name": "Aptitude", "questions_count": 20, "time": "48 min", "topics": ["Logical", "Quant"], "questions": self._generate_section_questions("Aptitude", ["Logical", "Quant"], 5)},
                    {"name": "Communication", "questions_count": 2, "time": "20 min", "topics": ["Essay", "Email"], "questions": self._generate_section_questions("Communication", ["Essay"], 2)},
                    {"name": "Coding", "questions_count": 2, "time": "45 min", "topics": ["Basic", "Intermediate"], "questions": self._generate_section_questions("Coding", ["Basic"], 2)}
                ]
            },
            "accenture": {
                "name": "Accenture",
                "pattern": "ASE",
                "sections": [
                    {"name": "Cognitive", "questions_count": 25, "time": "60 min", "topics": ["Aptitude", "Logical"], "questions": self._generate_section_questions("Cognitive", ["Aptitude"], 5)},
                    {"name": "Technical", "questions_count": 15, "time": "30 min", "topics": ["CS Fundamentals"], "questions": self._generate_section_questions("Technical", ["CS"], 3)},
                    {"name": "Communication", "questions_count": 10, "time": "20 min", "topics": ["Grammar"], "questions": self._generate_section_questions("Communication", ["Grammar"], 3)}
                ]
            }
        }
        
        return companies.get(company_id, companies.get("tcs"))
    
    def _generate_section_questions(self, section_name, topics, count):
        """Generate real market-standard questions."""
        question_bank = {
            "Aptitude": [
                {"q": "What is 25% of 400?", "options": ["80", "100", "120", "150"], "correct": 1},
                {"q": "If a train travels 360 km in 6 hours, what is its speed?", "options": ["50 km/h", "55 km/h", "60 km/h", "65 km/h"], "correct": 2},
                {"q": "What is the LCM of 12 and 18?", "options": ["24", "36", "48", "72"], "correct": 1},
                {"q": "If 5 workers complete a job in 10 days, how many days for 10 workers?", "options": ["3", "5", "7", "10"], "correct": 1},
                {"q": "What comes next: 3, 6, 12, 24, ?", "options": ["36", "48", "50", "52"], "correct": 1},
                {"q": "What is 15% of Rs. 2000?", "options": ["Rs. 250", "Rs. 300", "Rs. 350", "Rs. 400"], "correct": 1},
                {"q": "Average of 10, 20, 30, 40, 50?", "options": ["25", "30", "35", "40"], "correct": 1},
                {"q": "If a=5, b=3, what is a² + b²?", "options": ["25", "34", "36", "40"], "correct": 1}
            ],
            "Logical": [
                {"q": "If A > B and B > C, then?", "options": ["A > C", "A < C", "A = C", "Cannot say"], "correct": 0},
                {"q": "Which comes next: 1, 4, 9, 16, ?", "options": ["20", "25", "30", "36"], "correct": 1},
                {"q": "Complete: 2, 3, 5, 7, 11, ?", "options": ["13", "14", "15", "16"], "correct": 0},
                {"q": "Which is different: Apple, Banana, Carrot, Mango?", "options": ["Apple", "Banana", "Carrot", "Mango"], "correct": 2},
                {"q": "If today is Monday, what was 3 days ago?", "options": ["Thursday", "Friday", "Saturday", "Sunday"], "correct": 1}
            ],
            "Verbal": [
                {"q": "What is the synonym of 'happy'?", "options": ["Sad", "Joyful", "Angry", "Tired"], "correct": 1},
                {"q": "What is the antonym of 'big'?", "options": ["Large", "Huge", "Small", "Giant"], "correct": 2},
                {"q": "Complete: 'The cat ___ on the mat.'", "options": ["sit", "sits", "sitting", "sat"], "correct": 1},
                {"q": "Which word is a noun?", "options": ["Run", "Beautiful", "Table", "Quickly"], "correct": 2}
            ],
            "Advanced Quant": [
                {"q": "What is the probability of getting heads twice in two coin tosses?", "options": ["1/4", "1/2", "1/3", "3/4"], "correct": 0},
                {"q": "If log₂(8) = x, what is x?", "options": ["2", "3", "4", "8"], "correct": 1},
                {"q": "What is the sum of first 10 natural numbers?", "options": ["45", "50", "55", "60"], "correct": 2},
                {"q": "If sin(30°) = ?", "options": ["0", "1/2", "1", "√3/2"], "correct": 1},
                {"q": "What is 5! (5 factorial)?", "options": ["60", "100", "120", "150"], "correct": 2}
            ],
            "Advanced Logic": [
                {"q": "In a code, CAT = 24. What is DOG?", "options": ["26", "27", "28", "29"], "correct": 1},
                {"q": "If all roses are flowers and some flowers fade, then?", "options": ["All roses fade", "Some roses fade", "No roses fade", "Cannot say"], "correct": 3},
                {"q": "A is father of B, B is mother of C. A is C's?", "options": ["Grandfather", "Grandmother", "Uncle", "Father"], "correct": 0}
            ],
            "DSA": [
                {"q": "Which data structure uses LIFO?", "options": ["Queue", "Stack", "Array", "Linked List"], "correct": 1},
                {"q": "Time complexity of binary search?", "options": ["O(1)", "O(log n)", "O(n)", "O(n²)"], "correct": 1},
                {"q": "Which sorting is divide and conquer?", "options": ["Bubble", "Merge", "Insertion", "Selection"], "correct": 1},
                {"q": "What is a binary tree?", "options": ["Max 2 children", "Max 3 children", "No children", "Unlimited"], "correct": 0},
                {"q": "Which is not linear?", "options": ["Array", "Stack", "Tree", "Queue"], "correct": 2}
            ],
            "Problem Solving": [
                {"q": "Find the missing: 2, 4, 8, 16, ?", "options": ["24", "32", "36", "40"], "correct": 1},
                {"q": "A car covers 240 km in 4 hours. Distance in 7 hours?", "options": ["360", "420", "480", "520"], "correct": 1},
                {"q": "If 3x + 7 = 22, what is x?", "options": ["3", "5", "7", "9"], "correct": 1}
            ],
            "Algorithms": [
                {"q": "Time complexity of merge sort?", "options": ["O(n)", "O(n log n)", "O(n²)", "O(log n)"], "correct": 1},
                {"q": "Which algorithm finds shortest path?", "options": ["DFS", "BFS", "Dijkstra", "Binary"], "correct": 2},
                {"q": "Worst case of quick sort?", "options": ["O(n)", "O(n log n)", "O(n²)", "O(log n)"], "correct": 2}
            ],
            "DBMS": [
                {"q": "SQL command to retrieve data?", "options": ["INSERT", "UPDATE", "SELECT", "DELETE"], "correct": 2},
                {"q": "What is a primary key?", "options": ["Unique identifier", "Foreign key", "Index", "None"], "correct": 0},
                {"q": "Which is NoSQL?", "options": ["MySQL", "MongoDB", "Oracle", "PostgreSQL"], "correct": 1}
            ],
            "OOPs": [
                {"q": "OOP stands for?", "options": ["Object Oriented Programming", "Order of Operations", "Object Output Process", "None"], "correct": 0},
                {"q": "Which is not OOP principle?", "options": ["Encapsulation", "Inheritance", "Compilation", "Polymorphism"], "correct": 2},
                {"q": "What is encapsulation?", "options": ["Hiding data", "Showing data", "Deleting data", "Copying data"], "correct": 0}
            ],
            "CS Fundamentals": [
                {"q": "What is an OS?", "options": ["Software managing hardware", "Hardware", "Application", "None"], "correct": 0},
                {"q": "Which is not an OS?", "options": ["Windows", "Linux", "Oracle", "macOS"], "correct": 2},
                {"q": "What is a process?", "options": ["Running program", "File", "Folder", "None"], "correct": 0}
            ],
            "Grammar": [
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
            ]
        }
        
        questions = []
        for i in range(count):
            topic = topics[i % len(topics)] if topics else "General"
            bank = question_bank.get(topic, question_bank.get("Aptitude", []))
            
            if bank:
                q = bank[i % len(bank)]
                questions.append({
                    "id": i + 1,
                    "question": q["q"],
                    "options": q["options"],
                    "correct": q["correct"],
                    "topic": topic
                })
            else:
                questions.append({
                    "id": i + 1,
                    "question": f"{topic} practice question {i+1}",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct": i % 4,
                    "topic": topic
                })
        return questions
    
    def start_mock(self, email, company_id):
        """Start complete mock drive."""
        session_id = f"MOCK-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        company = self.get_company_sections(company_id)
        
        self.mock_sessions[session_id] = {
            "session_id": session_id,
            "email": email,
            "company": company["name"],
            "pattern": company["pattern"],
            "sections": company["sections"],
            "answers": [],
            "started_at": datetime.now().isoformat(),
            "status": "in_progress"
        }
        
        return {"status": "success", "session": self.mock_sessions[session_id]}
    
    def submit_answer(self, session_id, section_name, question_id, answer):
        """Submit answer for a question."""
        if session_id not in self.mock_sessions:
            return {"status": "error", "message": "Session not found"}
        
        self.mock_sessions[session_id]["answers"].append({
            "section": section_name,
            "question_id": question_id,
            "answer": answer,
            "submitted_at": datetime.now().isoformat()
        })
        
        return {"status": "success", "total_answers": len(self.mock_sessions[session_id]["answers"])}
    
    def complete_mock(self, session_id):
        """Complete mock drive and generate results."""
        if session_id not in self.mock_sessions:
            return {"status": "error", "message": "Session not found"}
        
        session = self.mock_sessions[session_id]
        session["status"] = "completed"
        
        total_questions = sum(s["questions_count"] for s in session["sections"])
        total_answered = len(session["answers"])
        
        # Calculate score
        score = (total_answered / total_questions * 100) if total_questions > 0 else 0
        
        results = {
            "session_id": session_id,
            "email": session["email"],
            "company": session["company"],
            "pattern": session["pattern"],
            "total_questions": total_questions,
            "answered": total_answered,
            "score": round(score, 1),
            "pass": score >= 65,
            "sections_completed": len(session["sections"]),
            "completed_at": datetime.now().isoformat()
        }
        
        self.mock_results[session_id] = results
        return {"status": "success", "results": results}
    
    def get_results(self, session_id):
        """Get mock drive results."""
        if session_id not in self.mock_results:
            return {"status": "error", "message": "Results not found"}
        return {"status": "success", "results": self.mock_results[session_id]}

company_mock = CompanyMockDrive()
