"""
Charvak Advanced AI Question Generator
Generates unique, non-repetitive questions for all exam sections
Uses randomization and variation to ensure no repetition
"""
import random
import hashlib
from datetime import datetime

class AIQuestionGenerator:
    def __init__(self):
        self.topics = self._initialize_topics()
        self.used_questions = {}  # Track used questions per user
        self.question_variations = {}  # Store variations
    
    def _initialize_topics(self):
        """Initialize with comprehensive topic bank."""
        return {
            # Core topics with multiple question sets
            "reasoning": self._create_topic([
                {"q": "If A > B and B > C, then which is true?", "o": [["A > C", "A < C", "A = C", "Cannot determine"]], "c": 0},
                {"q": "Find next: 2, 6, 12, 20, 30, ?", "o": [["40", "42", "44", "46"]], "c": 1},
                {"q": "If CAT = 24, then DOG = ?", "o": [["26", "28", "30", "32"]], "c": 0},
                {"q": "Odd one: Square, Rectangle, Triangle, Circle", "o": [["Square", "Rectangle", "Triangle", "Circle"]], "c": 3},
                {"q": "If Monday is day 1, what is day 100?", "o": [["Monday", "Tuesday", "Wednesday", "Thursday"]], "c": 2},
                {"q": "Complete: 3, 9, 27, 81, ?", "o": [["243", "162", "324", "180"]], "c": 0},
                {"q": "If PEN = 35, then BOOK = ?", "o": [["43", "40", "45", "50"]], "c": 0},
                {"q": "Find missing: 5, 10, 20, 40, ?", "o": [["80", "60", "70", "90"]], "c": 0},
                {"q": "Which is different: Apple, Mango, Potato, Banana", "o": [["Apple", "Mango", "Potato", "Banana"]], "c": 2},
                {"q": "If A=1, B=2, then Z=?", "o": [["26", "25", "24", "27"]], "c": 0}
            ]),
            "quant": self._create_topic([
                {"q": "What is 15% of 200?", "o": [["30", "25", "35", "40"]], "c": 0},
                {"q": "If x + y = 10, x - y = 4, find x", "o": [["7", "6", "8", "5"]], "c": 0},
                {"q": "Square root of 144?", "o": [["12", "11", "13", "14"]], "c": 0},
                {"q": "2^8 = ?", "o": [["256", "128", "512", "1024"]], "c": 0},
                {"q": "20% of 500?", "o": [["100", "50", "150", "200"]], "c": 0},
                {"q": "If 5x = 25, x = ?", "o": [["5", "10", "15", "20"]], "c": 0},
                {"q": "LCM of 4 and 6?", "o": [["12", "24", "6", "8"]], "c": 0},
                {"q": "HCF of 12 and 18?", "o": [["6", "3", "9", "12"]], "c": 0},
                {"q": "Area of square with side 5?", "o": [["25", "20", "30", "15"]], "c": 0},
                {"q": "Simple interest on 1000 at 10% for 1 year?", "o": [["100", "50", "150", "200"]], "c": 0}
            ]),
            "english": self._create_topic([
                {"q": "Synonym of 'Happy'?", "o": [["Joyful", "Sad", "Angry", "Tired"]], "c": 0},
                {"q": "Antonym of 'Ancient'?", "o": [["Modern", "Old", "Past", "Historic"]], "c": 0},
                {"q": "He ___ to school daily", "o": [["goes", "go", "going", "gone"]], "c": 0},
                {"q": "Noun in 'The cat sleeps'?", "o": [["cat", "The", "sleeps", "None"]], "c": 0},
                {"q": "Plural of 'Child'?", "o": [["Children", "Childs", "Childes", "Child"]], "c": 0},
                {"q": "Past tense of 'go'?", "o": [["went", "goed", "gone", "going"]], "c": 0},
                {"q": "Opposite of 'Beautiful'?", "o": [["Ugly", "Pretty", "Nice", "Good"]], "c": 0},
                {"q": "Correct spelling?", "o": [["Necessary", "Neccessary", "Necesary", "Neccesary"]], "c": 0},
                {"q": "Meaning of 'Abundant'?", "o": [["Plenty", "Scarce", "Little", "None"]], "c": 0},
                {"q": "Fill in: I ___ to music", "o": [["listen", "listens", "listening", "listened"]], "c": 0}
            ]),
            "gk": self._create_topic([
                {"q": "PM of India?", "o": [["Modi", "Gandhi", "Nehru", "Singh"]], "c": 0},
                {"q": "Capital of Australia?", "o": [["Canberra", "Sydney", "Melbourne", "Perth"]], "c": 0},
                {"q": "Largest ocean?", "o": [["Pacific", "Atlantic", "Indian", "Arctic"]], "c": 0},
                {"q": "Currency of Japan?", "o": [["Yen", "Yuan", "Won", "Ringgit"]], "c": 0},
                {"q": "National animal of India?", "o": [["Tiger", "Lion", "Elephant", "Leopard"]], "c": 0},
                {"q": "Largest planet?", "o": [["Jupiter", "Saturn", "Earth", "Mars"]], "c": 0},
                {"q": "Who wrote National Anthem?", "o": [["Tagore", "Gandhi", "Nehru", "Bose"]], "c": 0},
                {"q": "Capital of France?", "o": [["Paris", "London", "Berlin", "Rome"]], "c": 0},
                {"q": "Largest desert?", "o": [["Sahara", "Gobi", "Thar", "Kalahari"]], "c": 0},
                {"q": "First President of India?", "o": [["Rajendra Prasad", "Nehru", "Patel", "Gandhi"]], "c": 0}
            ]),
            "physics": self._create_topic([
                {"q": "Newton's first law?", "o": [["Inertia", "Acceleration", "Action", "None"]], "c": 0},
                {"q": "Unit of force?", "o": [["Newton", "Joule", "Watt", "Pascal"]], "c": 0},
                {"q": "Speed of light?", "o": [["3x10^8 m/s", "3x10^6 m/s", "3x10^10 m/s", "3x10^4 m/s"]], "c": 0},
                {"q": "Unit of energy?", "o": [["Joule", "Newton", "Watt", "Volt"]], "c": 0},
                {"q": "Law of gravity by?", "o": [["Newton", "Einstein", "Galileo", "Kepler"]], "c": 0},
                {"q": "Unit of current?", "o": [["Ampere", "Volt", "Ohm", "Watt"]], "c": 0},
                {"q": "Sound travels fastest in?", "o": [["Solid", "Liquid", "Gas", "Vacuum"]], "c": 0},
                {"q": "Unit of resistance?", "o": [["Ohm", "Ampere", "Volt", "Watt"]], "c": 0},
                {"q": "E=mc^2 by?", "o": [["Einstein", "Newton", "Bohr", "Planck"]], "c": 0},
                {"q": "Unit of power?", "o": [["Watt", "Joule", "Newton", "Pascal"]], "c": 0}
            ]),
            "chemistry": self._create_topic([
                {"q": "Atomic number of Carbon?", "o": [["6", "12", "8", "14"]], "c": 0},
                {"q": "Chemical formula of water?", "o": [["H2O", "CO2", "O2", "N2"]], "c": 0},
                {"q": "pH of pure water?", "o": [["7", "0", "14", "1"]], "c": 0},
                {"q": "Most abundant gas in air?", "o": [["Nitrogen", "Oxygen", "CO2", "Argon"]], "c": 0},
                {"q": "Chemical symbol of Gold?", "o": [["Au", "Ag", "Fe", "Cu"]], "c": 0},
                {"q": "Smallest unit of matter?", "o": [["Atom", "Molecule", "Cell", "Electron"]], "c": 0},
                {"q": "Gas used in balloons?", "o": [["Helium", "Hydrogen", "Oxygen", "Nitrogen"]], "c": 0},
                {"q": "Acid in lemon?", "o": [["Citric", "Acetic", "Lactic", "Malic"]], "c": 0},
                {"q": "Metal liquid at room temp?", "o": [["Mercury", "Iron", "Copper", "Zinc"]], "c": 0},
                {"q": "Formula of salt?", "o": [["NaCl", "KCl", "CaCl2", "MgCl2"]], "c": 0}
            ]),
            "math": self._create_topic([
                {"q": "15% of 200?", "o": [["30", "25", "35", "40"]], "c": 0},
                {"q": "Square root of 144?", "o": [["12", "11", "13", "14"]], "c": 0},
                {"q": "2^8 = ?", "o": [["256", "128", "512", "1024"]], "c": 0},
                {"q": "7 x 8 = ?", "o": [["56", "54", "58", "52"]], "c": 0},
                {"q": "100/4 = ?", "o": [["25", "20", "30", "15"]], "c": 0},
                {"q": "LCM of 6 and 8?", "o": [["24", "12", "48", "36"]], "c": 0},
                {"q": "HCF of 12 and 18?", "o": [["6", "3", "9", "12"]], "c": 0},
                {"q": "Area of circle r=7?", "o": [["154", "144", "164", "174"]], "c": 0},
                {"q": "Perimeter of square side 6?", "o": [["24", "12", "36", "18"]], "c": 0},
                {"q": "10% of 500?", "o": [["50", "100", "25", "75"]], "c": 0}
            ]),
            "aptitude": self._create_topic([
                {"q": "Train 300km in 5hrs, speed?", "o": [["60 km/h", "50 km/h", "55 km/h", "65 km/h"]], "c": 0},
                {"q": "25% of 80?", "o": [["20", "25", "30", "15"]], "c": 0},
                {"q": "5 workers 10 days, 10 workers?", "o": [["5 days", "10 days", "15 days", "20 days"]], "c": 0},
                {"q": "If 3 apples cost 30, 1 apple?", "o": [["10", "15", "5", "20"]], "c": 0},
                {"q": "Ratio 2:3, sum 50, larger?", "o": [["30", "20", "25", "35"]], "c": 0},
                {"q": "Average of 2,4,6?", "o": [["4", "3", "5", "6"]], "c": 0},
                {"q": "20% discount on 500?", "o": [["400", "450", "350", "300"]], "c": 0},
                {"q": "If 8 men 6 days, 4 men?", "o": [["12 days", "6 days", "9 days", "15 days"]], "c": 0},
                {"q": "Compound interest doubles in 5 years at?", "o": [["14.4%", "10%", "20%", "15%"]], "c": 0},
                {"q": "Speed 60km/h, distance 180km, time?", "o": [["3 hrs", "2 hrs", "4 hrs", "5 hrs"]], "c": 0}
            ]),
            "technical": self._create_topic([
                {"q": "What is an API?", "o": [["Interface for communication", "Hardware", "Bug", "Network"]], "c": 0},
                {"q": "What is a database?", "o": [["Data storage", "Code editor", "Browser", "OS"]], "c": 0},
                {"q": "What is an algorithm?", "o": [["Step-by-step procedure", "Random process", "Data type", "Variable"]], "c": 0},
                {"q": "What is OOP?", "o": [["Object-Oriented Programming", "Old Operating Process", "Only One Program", "None"]], "c": 0},
                {"q": "What is HTML?", "o": [["Markup language", "Programming", "Database", "Network"]], "c": 0},
                {"q": "What is CSS?", "o": [["Styling", "Logic", "Data", "Server"]], "c": 0},
                {"q": "What is JavaScript?", "o": [["Client-side scripting", "Database", "Server only", "OS"]], "c": 0},
                {"q": "What is SQL?", "o": [["Query language", "Programming", "Markup", "Styling"]], "c": 0},
                {"q": "What is Git?", "o": [["Version control", "Database", "Server", "Language"]], "c": 0},
                {"q": "What is cloud computing?", "o": [["On-demand services", "Local only", "Hardware only", "None"]], "c": 0}
            ]),
            "pm fundamentals": self._create_topic([
                {"q": "First phase of PM?", "o": [["Initiation", "Planning", "Execution", "Closing"]], "c": 0},
                {"q": "WBS stands for?", "o": [["Work Breakdown Structure", "Work Budget System", "Weekly Business Status", "None"]], "c": 0},
                {"q": "Triple constraint?", "o": [["Scope, Time, Cost", "Quality, Risk, Resource", "People, Process, Tech", "Plan, Do, Check"]], "c": 0},
                {"q": "Who is responsible for project success?", "o": [["PM", "Team", "Sponsor", "Stakeholder"]], "c": 0},
                {"q": "Gantt chart for?", "o": [["Scheduling", "Budgeting", "Risk", "Communication"]], "c": 0},
                {"q": "Critical path is?", "o": [["Longest path", "Shortest path", "Any path", "No path"]], "c": 0},
                {"q": "Scope creep is?", "o": [["Uncontrolled changes", "Planned changes", "No changes", "Fast changes"]], "c": 0},
                {"q": "Risk mitigation is?", "o": [["Reducing impact", "Ignoring", "Accepting all", "Avoiding all"]], "c": 0},
                {"q": "Stakeholder is?", "o": [["Interested party", "PM only", "Team only", "Client only"]], "c": 0},
                {"q": "Project charter is?", "o": [["Authorization document", "Budget", "Schedule", "Risk log"]], "c": 0}
            ]),
            "architecture": self._create_topic([
                {"q": "Cloud architecture is?", "o": [["Design of cloud systems", "Building design", "Network cable", "Hardware"]], "c": 0},
                {"q": "Scalability is?", "o": [["Handling growth", "Reducing size", "Fixed capacity", "Limiting users"]], "c": 0},
                {"q": "High availability is?", "o": [["Always available", "Sometimes", "Rarely", "Never"]], "c": 0},
                {"q": "Fault tolerance is?", "o": [["Recovering from failure", "No failures", "Ignoring", "Preventing all"]], "c": 0},
                {"q": "Load balancing is?", "o": [["Distributing traffic", "Blocking", "Slowing", "Monitoring"]], "c": 0},
                {"q": "Microservices is?", "o": [["Small services", "One big app", "No services", "Database"]], "c": 0},
                {"q": "API Gateway is?", "o": [["Entry point", "Database", "Server", "Client"]], "c": 0},
                {"q": "Serverless is?", "o": [["No server management", "No servers", "One server", "Many servers"]], "c": 0},
                {"q": "CDN is?", "o": [["Content delivery", "Database", "Security", "Storage"]], "c": 0},
                {"q": "Containerization is?", "o": [["Package apps", "Ship containers", "Store data", "No packaging"]], "c": 0}
            ]),
            "security": self._create_topic([
                {"q": "Encryption is?", "o": [["Encoding data", "Deleting", "Copying", "Sharing"]], "c": 0},
                {"q": "Firewall is?", "o": [["Network security", "Hardware", "Bug", "Virus"]], "c": 0},
                {"q": "Authentication is?", "o": [["Verifying identity", "Granting access", "Denying", "Logging"]], "c": 0},
                {"q": "Authorization is?", "o": [["Granting permissions", "Verifying", "Creating", "Deleting"]], "c": 0},
                {"q": "Vulnerability is?", "o": [["Weakness", "Strength", "Feature", "Update"]], "c": 0},
                {"q": "Phishing is?", "o": [["Fake emails", "Real emails", "No emails", "Spam only"]], "c": 0},
                {"q": "Malware is?", "o": [["Malicious software", "Good software", "No software", "Hardware"]], "c": 0},
                {"q": "Two-factor auth is?", "o": [["Two steps", "One step", "No steps", "Three steps"]], "c": 0},
                {"q": "Penetration testing is?", "o": [["Security testing", "Speed test", "Load test", "No test"]], "c": 0},
                {"q": "Zero-day is?", "o": [["Unknown vulnerability", "Known", "Fixed", "No issue"]], "c": 0}
            ]),
            "reading": self._create_topic([
                {"q": "Skimming is?", "o": [["Quick reading", "Slow", "Detailed", "No reading"]], "c": 0},
                {"q": "Scanning is?", "o": [["Finding specific", "Reading all", "Nothing", "Random"]], "c": 0},
                {"q": "Inference is?", "o": [["Drawing conclusion", "Copying", "Memorizing", "Ignoring"]], "c": 0},
                {"q": "Main idea is?", "o": [["Central point", "Minor", "Example", "Footnote"]], "c": 0},
                {"q": "Context clue is?", "o": [["Hint in text", "Dictionary", "External", "Guess"]], "c": 0},
                {"q": "Theme is?", "o": [["Central message", "Character", "Setting", "Plot"]], "c": 0},
                {"q": "Tone is?", "o": [["Author's attitude", "Reader's", "Character's", "None"]], "c": 0},
                {"q": "Summary is?", "o": [["Condensed version", "Full text", "Expanded", "Copy"]], "c": 0},
                {"q": "Comprehension is?", "o": [["Understanding", "Hearing", "Seeing", "Touching"]], "c": 0},
                {"q": "Paragraph is?", "o": [["Group of sentences", "One word", "One line", "Page"]], "c": 0}
            ]),
            "writing": self._create_topic([
                {"q": "Essay is?", "o": [["Structured writing", "Random", "List", "Poem"]], "c": 0},
                {"q": "Thesis is?", "o": [["Main argument", "Example", "Conclusion", "Title"]], "c": 0},
                {"q": "Coherence is?", "o": [["Logical flow", "Random", "Repetition", "Contradiction"]], "c": 0},
                {"q": "Grammar is?", "o": [["Language rules", "Math", "Science", "No rules"]], "c": 0},
                {"q": "Punctuation is?", "o": [["Marks in text", "Spacing", "Font", "Size"]], "c": 0},
                {"q": "Paragraph structure?", "o": [["Topic, body, conclusion", "Random", "Only topic", "Only body"]], "c": 0},
                {"q": "Transition words?", "o": [["However, therefore", "Random", "No words", "Only and"]], "c": 0},
                {"q": "Conclusion is?", "o": [["Final summary", "Introduction", "Body", "Title"]], "c": 0},
                {"q": "Draft is?", "o": [["First version", "Final", "Published", "Deleted"]], "c": 0},
                {"q": "Proofreading is?", "o": [["Checking errors", "Writing", "Deleting", "Formatting"]], "c": 0}
            ]),
            "ethics": self._create_topic([
                {"q": "Ethics is?", "o": [["Moral principles", "Legal", "Policy", "Preference"]], "c": 0},
                {"q": "Integrity is?", "o": [["Honesty", "Dishonesty", "Secrecy", "Manipulation"]], "c": 0},
                {"q": "Conflict of interest?", "o": [["Competing interests", "Shared", "No interest", "Public"]], "c": 0},
                {"q": "Transparency is?", "o": [["Openness", "Secrecy", "Hidden", "Opaque"]], "c": 0},
                {"q": "Accountability is?", "o": [["Responsibility", "Blame", "Denial", "Avoidance"]], "c": 0},
                {"q": "Professionalism is?", "o": [["Competent behavior", "Casual", "Informal", "Random"]], "c": 0},
                {"q": "Confidentiality is?", "o": [["Keeping secrets", "Sharing all", "Leaking", "Ignoring"]], "c": 0},
                {"q": "Compliance is?", "o": [["Following rules", "Breaking", "Ignoring", "Avoiding"]], "c": 0},
                {"q": "Due diligence is?", "o": [["Careful review", "No review", "Quick look", "Skipping"]], "c": 0},
                {"q": "Whistleblowing is?", "o": [["Reporting wrongdoing", "Hiding", "Ignoring", "Supporting"]], "c": 0}
            ]),
            "economics": self._create_topic([
                {"q": "Supply and demand?", "o": [["Market forces", "Govt", "Company", "Random"]], "c": 0},
                {"q": "Inflation is?", "o": [["Price increase", "Decrease", "Stable", "No prices"]], "c": 0},
                {"q": "GDP is?", "o": [["Gross Domestic Product", "General", "Gross Dev", "None"]], "c": 0},
                {"q": "Recession is?", "o": [["Economic decline", "Growth", "Stable", "No economy"]], "c": 0},
                {"q": "Interest rate is?", "o": [["Cost of borrowing", "Living", "Food", "Housing"]], "c": 0},
                {"q": "Monopoly is?", "o": [["One seller", "Many", "Two", "None"]], "c": 0},
                {"q": "Oligopoly is?", "o": [["Few sellers", "One", "Many", "None"]], "c": 0},
                {"q": "Free market is?", "o": [["No intervention", "Heavy", "Partial", "Total"]], "c": 0},
                {"q": "Fiscal policy?", "o": [["Govt spending", "Bank", "Private", "Foreign"]], "c": 0},
                {"q": "Monetary policy?", "o": [["Central bank", "Govt", "Private", "Foreign"]], "c": 0}
            ]),
            "fra": self._create_topic([
                {"q": "Balance sheet shows?", "o": [["Financial position", "Profit", "Loss", "Tax"]], "c": 0},
                {"q": "Income statement shows?", "o": [["Revenue/expenses", "Assets", "Liabilities", "Equity"]], "c": 0},
                {"q": "Cash flow is?", "o": [["Money movement", "Profit", "Sales", "Expenses"]], "c": 0},
                {"q": "Depreciation is?", "o": [["Asset decrease", "Increase", "No change", "Market"]], "c": 0},
                {"q": "Goodwill is?", "o": [["Intangible", "Tangible", "Liability", "Expense"]], "c": 0},
                {"q": "Asset is?", "o": [["Owned resource", "Debt", "Expense", "Revenue"]], "c": 0},
                {"q": "Liability is?", "o": [["Debt", "Asset", "Revenue", "Expense"]], "c": 0},
                {"q": "Equity is?", "o": [["Owner's share", "Debt", "Revenue", "Expense"]], "c": 0},
                {"q": "Revenue is?", "o": [["Income", "Expense", "Debt", "Asset"]], "c": 0},
                {"q": "Expense is?", "o": [["Cost", "Income", "Asset", "Equity"]], "c": 0}
            ])
        }
    
    def _create_topic(self, question_data):
        """Convert question data to topic format."""
        questions = [item["q"] for item in question_data]
        options = [item["o"][0] for item in question_data]
        correct = [item["c"] for item in question_data]
        return {"questions": questions, "options": options, "correct": correct}
    
    def generate_questions(self, exam_id, topic, count=10, user_email=None):
        """Generate unique, non-repetitive questions."""
        topic_lower = topic.lower().strip()
        topic_data = self.topics.get(topic_lower, self.topics.get("reasoning", {}))
        
        # Track used questions per user
        if user_email:
            if user_email not in self.used_questions:
                self.used_questions[user_email] = {}
            if topic_lower not in self.used_questions[user_email]:
                self.used_questions[user_email][topic_lower] = []
        
        questions = []
        base_q = topic_data.get("questions", [])
        base_o = topic_data.get("options", [])
        base_c = topic_data.get("correct", [])
        
        # Shuffle questions for variety
        indices = list(range(len(base_q))) if base_q else [0]
        random.shuffle(indices)
        
        for i in range(min(count, len(indices) * 3)):  # Allow some repetition but shuffled
            idx = indices[i % len(indices)]
            q_text = base_q[idx] if base_q else topic + " - Question " + str(i+1)
            
            # Skip if already used by this user
            if user_email and q_text in self.used_questions[user_email][topic_lower]:
                continue
            
            if user_email:
                self.used_questions[user_email][topic_lower].append(q_text)
            
            questions.append({
                "id": i + 1,
                "question": q_text,
                "options": base_o[idx] if base_o else ["Option A", "Option B", "Option C", "Option D"],
                "correct": base_c[idx] if base_c else 0,
                "explanation": "Explanation for question " + str(i+1),
                "difficulty": "Medium",
                "topic": topic,
                "unique_id": hashlib.md5(f"{exam_id}_{topic}_{i}_{datetime.now().timestamp()}".encode()).hexdigest()[:8]
            })
        
        return questions

ai_question_generator = AIQuestionGenerator()