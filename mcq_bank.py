"""
Charvak MCQ Question Bank
210 Questions - 21 Topics - Market Standard
"""
import logging
import json
import os
from datetime import datetime

logger = logging.getLogger("charvakit.mcq_bank")

class MCQQuestionBank:
    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv()
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.question_bank = self._initialize_question_bank()
        logger.info(f"MCQ Question Bank ready - AI: {'ENABLED' if self.openai_api_key else 'DISABLED'}")
    
    def _initialize_question_bank(self):
        """Initialize with market-standard questions."""
        return {
            "aptitude": {
                "Quant": [
                    {"q": "What is 25% of 400?", "options": ["80", "100", "120", "150"], "correct": 1},
                    {"q": "If a shirt costs Rs. 500 after 20% discount, what was the original price?", "options": ["Rs. 600", "Rs. 625", "Rs. 650", "Rs. 700"], "correct": 1},
                    {"q": "A train travels 360 km in 6 hours. What is its speed?", "options": ["50 km/h", "55 km/h", "60 km/h", "65 km/h"], "correct": 2},
                    {"q": "What is the LCM of 12 and 18?", "options": ["24", "36", "48", "72"], "correct": 1},
                    {"q": "If 5 workers complete a job in 10 days, how many days will 10 workers take?", "options": ["3 days", "5 days", "7 days", "10 days"], "correct": 1},
                    {"q": "What is the next number: 3, 6, 12, 24, ?", "options": ["36", "48", "50", "52"], "correct": 1},
                    {"q": "If a = 5 and b = 3, what is a² + b²?", "options": ["25", "34", "36", "40"], "correct": 1},
                    {"q": "What is 15% of Rs. 2000?", "options": ["Rs. 250", "Rs. 300", "Rs. 350", "Rs. 400"], "correct": 1},
                    {"q": "A car covers 240 km in 4 hours. How far will it go in 7 hours?", "options": ["360 km", "420 km", "480 km", "520 km"], "correct": 1},
                    {"q": "What is the average of 10, 20, 30, 40, 50?", "options": ["25", "30", "35", "40"], "correct": 1}
                ],
                "Probability": [
                    {"q": "What is the probability of getting heads when flipping a fair coin?", "options": ["1/4", "1/3", "1/2", "2/3"], "correct": 2},
                    {"q": "A die is rolled. What is the probability of getting an even number?", "options": ["1/6", "1/3", "1/2", "2/3"], "correct": 2},
                    {"q": "Two coins are tossed. What is the probability of getting two heads?", "options": ["1/4", "1/3", "1/2", "3/4"], "correct": 0},
                    {"q": "A bag has 3 red and 2 blue balls. Probability of picking a red ball?", "options": ["1/5", "2/5", "3/5", "4/5"], "correct": 2},
                    {"q": "What is the probability of drawing a king from a deck of 52 cards?", "options": ["1/13", "1/26", "1/52", "4/52"], "correct": 0},
                    {"q": "A number is chosen from 1-10. Probability of getting a prime number?", "options": ["2/10", "3/10", "4/10", "5/10"], "correct": 2},
                    {"q": "Two dice are rolled. Probability of getting sum 7?", "options": ["1/6", "1/12", "1/18", "1/36"], "correct": 0},
                    {"q": "Probability of getting a red card from a deck?", "options": ["1/4", "1/3", "1/2", "3/4"], "correct": 2},
                    {"q": "A coin is tossed 3 times. Probability of exactly 2 heads?", "options": ["1/8", "3/8", "5/8", "7/8"], "correct": 1},
                    {"q": "Probability of an impossible event is?", "options": ["0", "1", "1/2", "Cannot say"], "correct": 0}
                ],
                "Data Interpretation": [
                    {"q": "If sales increased from 100 to 150 units, what is the percentage increase?", "options": ["30%", "40%", "50%", "60%"], "correct": 2},
                    {"q": "A company's revenue grew from Rs. 1L to Rs. 1.5L. Growth percentage?", "options": ["25%", "40%", "50%", "75%"], "correct": 2},
                    {"q": "If 40% of students passed, what fraction failed?", "options": ["2/5", "3/5", "4/5", "1/5"], "correct": 1},
                    {"q": "A graph shows 200 units in 2020 and 300 in 2021. Increase?", "options": ["40%", "50%", "60%", "100%"], "correct": 1},
                    {"q": "If a pie chart shows 25% for category A, what angle does it represent?", "options": ["45°", "60°", "90°", "120°"], "correct": 2},
                    {"q": "Monthly expenses: Rent 30%, Food 25%, Travel 15%, Savings 30%. What fraction is savings?", "options": ["1/5", "1/4", "3/10", "1/3"], "correct": 2},
                    {"q": "A table shows 5 values: 10, 20, 30, 40, 50. What is the median?", "options": ["20", "30", "40", "50"], "correct": 1},
                    {"q": "If a company's profit margin is 20% on sales of Rs. 5000, what is profit?", "options": ["Rs. 500", "Rs. 1000", "Rs. 1500", "Rs. 2000"], "correct": 1},
                    {"q": "A bar chart shows 100, 150, 200 for 3 months. Total?", "options": ["350", "400", "450", "500"], "correct": 2},
                    {"q": "If 60 out of 200 people prefer tea, what percentage prefer tea?", "options": ["20%", "30%", "40%", "50%"], "correct": 1}
                ],
                "Logical Reasoning": [
                    {"q": "If A > B and B > C, then?", "options": ["A > C", "A < C", "A = C", "Cannot say"], "correct": 0},
                    {"q": "All cats are animals. Some animals are pets. Therefore?", "options": ["All cats are pets", "Some cats are pets", "No cats are pets", "Cannot say"], "correct": 3},
                    {"q": "If P is brother of Q, and Q is sister of R, then P is R's?", "options": ["Brother", "Sister", "Cousin", "Cannot say"], "correct": 0},
                    {"q": "Which number comes next: 1, 4, 9, 16, ?", "options": ["20", "25", "30", "36"], "correct": 1},
                    {"q": "If all roses are flowers and some flowers fade, then?", "options": ["All roses fade", "Some roses fade", "No roses fade", "Cannot say"], "correct": 3},
                    {"q": "A is father of B, B is mother of C. A is C's?", "options": ["Grandfather", "Grandmother", "Uncle", "Father"], "correct": 0},
                    {"q": "Which is different: Apple, Banana, Carrot, Mango?", "options": ["Apple", "Banana", "Carrot", "Mango"], "correct": 2},
                    {"q": "If today is Monday, what day was 3 days ago?", "options": ["Thursday", "Friday", "Saturday", "Sunday"], "correct": 1},
                    {"q": "Complete: 2, 3, 5, 7, 11, ?", "options": ["13", "14", "15", "16"], "correct": 0},
                    {"q": "If CAT = 24, then DOG = ?", "options": ["26", "27", "28", "29"], "correct": 1}
                ],
                "Syllogisms": [
                    {"q": "All A are B. All B are C. Therefore?", "options": ["All A are C", "Some A are C", "No A are C", "Cannot say"], "correct": 0},
                    {"q": "Some X are Y. All Y are Z. Therefore?", "options": ["All X are Z", "Some X are Z", "No X are Z", "Cannot say"], "correct": 1},
                    {"q": "No P is Q. All R is P. Therefore?", "options": ["No R is Q", "Some R is Q", "All R is Q", "Cannot say"], "correct": 0},
                    {"q": "All dogs are mammals. No mammals are fish. Therefore?", "options": ["All dogs are fish", "No dogs are fish", "Some dogs are fish", "Cannot say"], "correct": 1},
                    {"q": "Some students are athletes. All athletes are fit. Therefore?", "options": ["All students are fit", "Some students are fit", "No students are fit", "Cannot say"], "correct": 1},
                    {"q": "All birds have wings. Penguins are birds. Therefore?", "options": ["Penguins have wings", "Penguins don't have wings", "Cannot say", "None"], "correct": 0},
                    {"q": "Some fruits are sweet. All sweet things are tasty. Therefore?", "options": ["All fruits are tasty", "Some fruits are tasty", "No fruits are tasty", "Cannot say"], "correct": 1},
                    {"q": "No teachers are students. Some students are children. Therefore?", "options": ["No teachers are children", "Some teachers are children", "Cannot say", "None"], "correct": 2},
                    {"q": "All cars have wheels. Some vehicles are cars. Therefore?", "options": ["All vehicles have wheels", "Some vehicles have wheels", "No vehicles have wheels", "Cannot say"], "correct": 1},
                    {"q": "If A implies B, and B is false, then?", "options": ["A is true", "A is false", "Cannot say", "None"], "correct": 1}
                ],
                "Coding-Decoding": [
                    {"q": "If CODE = 4, then DECODE = ?", "options": ["5", "6", "7", "8"], "correct": 1},
                    {"q": "If APPLE is coded as BQQMF, how is ORANGE coded?", "options": ["PSBOHF", "PSBOHE", "PSBOHG", "PSBOHD"], "correct": 0},
                    {"q": "If CAT = 3120, then DOG = ?", "options": ["4157", "4158", "4159", "4160"], "correct": 0},
                    {"q": "In a code, 'A' is 'Z', 'B' is 'Y'. How is 'HELLO' coded?", "options": ["SVOOL", "SVOLL", "SVOOL", "SVOLL"], "correct": 0},
                    {"q": "If 1 = A, 2 = B, then 8 = ?", "options": ["F", "G", "H", "I"], "correct": 2},
                    {"q": "If RAT = 39, then BAT = ?", "options": ["21", "22", "23", "24"], "correct": 1},
                    {"q": "In a code, 'M' is 'N', 'O' is 'P'. How is 'MOON' coded?", "options": ["NPPO", "NPOO", "NPPO", "NOPP"], "correct": 0},
                    {"q": "If 25 = Y, then 1 = ?", "options": ["A", "B", "C", "Z"], "correct": 0},
                    {"q": "If PEN = 35, then CAP = ?", "options": ["16", "17", "18", "19"], "correct": 1},
                    {"q": "In a code, 'BAD' = 7. What is 'GOOD'?", "options": ["41", "42", "43", "44"], "correct": 1}
                ],
                "Pattern Recognition": [
                    {"q": "What comes next: 1, 3, 6, 10, 15, ?", "options": ["18", "20", "21", "25"], "correct": 2},
                    {"q": "Complete: 2, 4, 8, 16, ?", "options": ["24", "32", "36", "40"], "correct": 1},
                    {"q": "What comes next: A, C, E, G, ?", "options": ["H", "I", "J", "K"], "correct": 1},
                    {"q": "Complete: 1, 1, 2, 3, 5, 8, ?", "options": ["10", "11", "12", "13"], "correct": 3},
                    {"q": "What comes next: Z, X, V, T, ?", "options": ["Q", "R", "S", "U"], "correct": 1},
                    {"q": "Complete: 5, 10, 20, 40, ?", "options": ["60", "80", "100", "120"], "correct": 1},
                    {"q": "What comes next: 1, 4, 9, 16, 25, ?", "options": ["30", "36", "42", "49"], "correct": 1},
                    {"q": "Complete: M, N, O, P, ?", "options": ["Q", "R", "S", "T"], "correct": 0},
                    {"q": "What comes next: 100, 90, 80, 70, ?", "options": ["50", "55", "60", "65"], "correct": 2},
                    {"q": "Complete: 2, 6, 12, 20, ?", "options": ["24", "30", "36", "42"], "correct": 1}
                ]
            },
            "technical": {
                "Data Structures": [
                    {"q": "Which data structure uses LIFO?", "options": ["Queue", "Stack", "Array", "Linked List"], "correct": 1},
                    {"q": "Which data structure uses FIFO?", "options": ["Stack", "Queue", "Tree", "Graph"], "correct": 1},
                    {"q": "Time complexity of accessing an array element by index?", "options": ["O(1)", "O(log n)", "O(n)", "O(n²)"], "correct": 0},
                    {"q": "Which is not a linear data structure?", "options": ["Array", "Stack", "Tree", "Queue"], "correct": 2},
                    {"q": "What is the maximum number of children in a binary tree?", "options": ["1", "2", "3", "Unlimited"], "correct": 1},
                    {"q": "Which data structure is best for implementing recursion?", "options": ["Queue", "Stack", "Array", "Linked List"], "correct": 1},
                    {"q": "What is a hash table used for?", "options": ["Sorting", "Fast lookup", "Recursion", "Traversal"], "correct": 1},
                    {"q": "Which traversal visits root first?", "options": ["Inorder", "Preorder", "Postorder", "Level order"], "correct": 1},
                    {"q": "What is a linked list advantage over array?", "options": ["Faster access", "Dynamic size", "Less memory", "None"], "correct": 1},
                    {"q": "Which is a self-balancing BST?", "options": ["Binary Tree", "AVL Tree", "Heap", "Trie"], "correct": 1}
                ],
                "Algorithms": [
                    {"q": "Time complexity of binary search?", "options": ["O(1)", "O(log n)", "O(n)", "O(n²)"], "correct": 1},
                    {"q": "Which sorting is most efficient for nearly sorted data?", "options": ["Bubble", "Insertion", "Merge", "Quick"], "correct": 1},
                    {"q": "Time complexity of merge sort?", "options": ["O(n)", "O(n log n)", "O(n²)", "O(log n)"], "correct": 1},
                    {"q": "Which algorithm uses divide and conquer?", "options": ["Linear search", "Merge sort", "Bubble sort", "Insertion sort"], "correct": 1},
                    {"q": "Worst case of quick sort?", "options": ["O(n)", "O(n log n)", "O(n²)", "O(log n)"], "correct": 2},
                    {"q": "Which is a greedy algorithm?", "options": ["Merge sort", "Dijkstra", "Binary search", "DFS"], "correct": 1},
                    {"q": "Time complexity of BFS?", "options": ["O(V)", "O(E)", "O(V+E)", "O(V*E)"], "correct": 2},
                    {"q": "Which algorithm finds shortest path?", "options": ["DFS", "BFS", "Dijkstra", "Binary search"], "correct": 2},
                    {"q": "Which is not a sorting algorithm?", "options": ["Quick", "Merge", "Heap", "Binary"], "correct": 3},
                    {"q": "Time complexity of linear search?", "options": ["O(1)", "O(log n)", "O(n)", "O(n²)"], "correct": 2}
                ],
                "OOPs": [
                    {"q": "What does OOP stand for?", "options": ["Object Oriented Programming", "Order of Operations", "Object Output Process", "None"], "correct": 0},
                    {"q": "Which is not an OOP principle?", "options": ["Encapsulation", "Inheritance", "Compilation", "Polymorphism"], "correct": 2},
                    {"q": "What is encapsulation?", "options": ["Hiding data", "Showing data", "Deleting data", "Copying data"], "correct": 0},
                    {"q": "What is inheritance?", "options": ["Creating new class from existing", "Deleting classes", "Merging classes", "None"], "correct": 0},
                    {"q": "What is polymorphism?", "options": ["Many forms", "Single form", "No forms", "None"], "correct": 0},
                    {"q": "Which keyword is used for inheritance in Java?", "options": ["extends", "implements", "inherits", "uses"], "correct": 0},
                    {"q": "What is abstraction?", "options": ["Hiding implementation", "Showing implementation", "Deleting implementation", "None"], "correct": 0},
                    {"q": "Can a class inherit from multiple classes in Java?", "options": ["Yes", "No", "Sometimes", "Depends"], "correct": 1},
                    {"q": "What is a constructor?", "options": ["Special method to initialize", "Regular method", "Static method", "None"], "correct": 0},
                    {"q": "What is method overloading?", "options": ["Same name, different parameters", "Same name, same parameters", "Different name", "None"], "correct": 0}
                ],
                "Operating Systems": [
                    {"q": "What is an operating system?", "options": ["Software managing hardware", "Hardware", "Application", "None"], "correct": 0},
                    {"q": "Which is not an OS?", "options": ["Windows", "Linux", "Oracle", "macOS"], "correct": 2},
                    {"q": "What is a process?", "options": ["Running program", "File", "Folder", "None"], "correct": 0},
                    {"q": "What is deadlock?", "options": ["Processes waiting for each other", "Process crash", "Memory error", "None"], "correct": 0},
                    {"q": "What is virtual memory?", "options": ["Extended memory using disk", "RAM", "Cache", "None"], "correct": 0},
                    {"q": "Which scheduling is non-preemptive?", "options": ["FCFS", "Round Robin", "SRTF", "Priority"], "correct": 0},
                    {"q": "What is a thread?", "options": ["Lightweight process", "Heavy process", "Application", "None"], "correct": 0},
                    {"q": "What is context switching?", "options": ["Switching between processes", "Turning off computer", "Opening files", "None"], "correct": 0},
                    {"q": "Which is a memory management technique?", "options": ["Paging", "Sorting", "Searching", "None"], "correct": 0},
                    {"q": "What is a semaphore?", "options": ["Synchronization tool", "File", "Process", "None"], "correct": 0}
                ],
                "DBMS/SQL": [
                    {"q": "What does SQL stand for?", "options": ["Structured Query Language", "Simple Query Language", "Standard Query Language", "None"], "correct": 0},
                    {"q": "Which SQL command retrieves data?", "options": ["INSERT", "UPDATE", "SELECT", "DELETE"], "correct": 2},
                    {"q": "What is a primary key?", "options": ["Unique identifier", "Foreign key", "Index", "None"], "correct": 0},
                    {"q": "Which is an aggregate function?", "options": ["SUM", "WHERE", "ORDER BY", "GROUP BY"], "correct": 0},
                    {"q": "What is normalization?", "options": ["Reducing redundancy", "Adding redundancy", "Deleting data", "None"], "correct": 0},
                    {"q": "Which join returns all rows from left table?", "options": ["INNER", "LEFT", "RIGHT", "FULL"], "correct": 1},
                    {"q": "What is a foreign key?", "options": ["References primary key", "Unique key", "Index", "None"], "correct": 0},
                    {"q": "Which command removes a table?", "options": ["DELETE", "DROP", "REMOVE", "TRUNCATE"], "correct": 1},
                    {"q": "What is ACID?", "options": ["Transaction properties", "Database type", "Query type", "None"], "correct": 0},
                    {"q": "Which is a NoSQL database?", "options": ["MySQL", "MongoDB", "Oracle", "PostgreSQL"], "correct": 1}
                ],
                "Computer Networks": [
                    {"q": "What does IP stand for?", "options": ["Internet Protocol", "Internal Protocol", "Internet Process", "None"], "correct": 0},
                    {"q": "Which layer handles routing?", "options": ["Network", "Transport", "Application", "Physical"], "correct": 0},
                    {"q": "What is TCP?", "options": ["Transmission Control Protocol", "Transfer Control Process", "Total Control Protocol", "None"], "correct": 0},
                    {"q": "Which protocol is connectionless?", "options": ["TCP", "UDP", "HTTP", "FTP"], "correct": 1},
                    {"q": "What is DNS used for?", "options": ["Name to IP resolution", "Data transfer", "Email", "None"], "correct": 0},
                    {"q": "Which port does HTTP use?", "options": ["21", "25", "80", "443"], "correct": 2},
                    {"q": "What is a firewall?", "options": ["Security system", "Hardware only", "Software only", "None"], "correct": 0},
                    {"q": "Which is a wireless protocol?", "options": ["Ethernet", "Wi-Fi", "Fiber", "Coaxial"], "correct": 1},
                    {"q": "What is bandwidth?", "options": ["Data transfer capacity", "Network speed only", "Latency", "None"], "correct": 0},
                    {"q": "Which protocol sends email?", "options": ["HTTP", "SMTP", "FTP", "DNS"], "correct": 1}
                ]
            },
            "pseudocode": {
                "Python": [
                    {"q": "Output of print(5 // 2)?", "options": ["2.5", "2", "3", "2.0"], "correct": 1},
                    {"q": "Which is a Python list?", "options": ["[]", "{}", "()", "<>"], "correct": 0},
                    {"q": "Output of len('Hello')?", "options": ["4", "5", "6", "7"], "correct": 1},
                    {"q": "Which keyword defines a function?", "options": ["func", "def", "function", "define"], "correct": 1},
                    {"q": "Output of print(type(5))?", "options": ["int", "float", "str", "bool"], "correct": 0},
                    {"q": "Which is a Python tuple?", "options": ["[]", "{}", "()", "<>"], "correct": 2},
                    {"q": "Output of 2 ** 3?", "options": ["6", "8", "9", "12"], "correct": 1},
                    {"q": "Which method adds element to list?", "options": ["add()", "append()", "insert()", "push()"], "correct": 1},
                    {"q": "Output of print('a' + 'b')?", "options": ["ab", "a b", "Error", "None"], "correct": 0},
                    {"q": "Which is a Python dictionary?", "options": ["[]", "{}", "()", "<>"], "correct": 1}
                ],
                "Java": [
                    {"q": "Which keyword creates an object?", "options": ["new", "create", "make", "build"], "correct": 0},
                    {"q": "What is the entry point of Java program?", "options": ["main()", "start()", "init()", "run()"], "correct": 0},
                    {"q": "Which data type is 8 bytes in Java?", "options": ["int", "long", "float", "short"], "correct": 1},
                    {"q": "Output of System.out.println(5 + 3)?", "options": ["53", "8", "Error", "None"], "correct": 1},
                    {"q": "Which is a valid variable name?", "options": ["2var", "var2", "var-2", "var 2"], "correct": 1},
                    {"q": "What does JVM stand for?", "options": ["Java Virtual Machine", "Java Visual Machine", "Java Variable Method", "None"], "correct": 0},
                    {"q": "Which loop is guaranteed to run at least once?", "options": ["for", "while", "do-while", "None"], "correct": 2},
                    {"q": "What is the default value of int?", "options": ["0", "1", "null", "undefined"], "correct": 0},
                    {"q": "Which keyword is for inheritance?", "options": ["extends", "implements", "inherits", "uses"], "correct": 0},
                    {"q": "Output of 'Java'.length()?", "options": ["3", "4", "5", "6"], "correct": 1}
                ],
                "C": [
                    {"q": "Which header file is for printf?", "options": ["stdio.h", "stdlib.h", "string.h", "math.h"], "correct": 0},
                    {"q": "What does int main() return?", "options": ["0", "1", "void", "None"], "correct": 0},
                    {"q": "Which operator is for address?", "options": ["*", "&", "%", "#"], "correct": 1},
                    {"q": "Size of int in C is?", "options": ["2 bytes", "4 bytes", "8 bytes", "Depends"], "correct": 3},
                    {"q": "Which is a valid C comment?", "options": ["//", "##", "**", "--"], "correct": 0},
                    {"q": "What does malloc do?", "options": ["Allocates memory", "Frees memory", "Copies memory", "None"], "correct": 0},
                    {"q": "Which keyword defines a structure?", "options": ["struct", "class", "object", "record"], "correct": 0},
                    {"q": "Output of printf('%d', 5+3)?", "options": ["53", "8", "Error", "None"], "correct": 1},
                    {"q": "Which is a pointer declaration?", "options": ["int *p", "int p", "int &p", "int #p"], "correct": 0},
                    {"q": "What does strlen do?", "options": ["Returns string length", "Copies string", "Compares string", "None"], "correct": 0}
                ],
                "C++": [
                    {"q": "Which header is for cout?", "options": ["iostream", "stdio.h", "stdlib.h", "None"], "correct": 0},
                    {"q": "What is cout used for?", "options": ["Output", "Input", "File handling", "None"], "correct": 0},
                    {"q": "Which keyword defines a class?", "options": ["class", "struct", "object", "type"], "correct": 0},
                    {"q": "What is inheritance in C++?", "options": ["Deriving new class", "Deleting class", "Merging", "None"], "correct": 0},
                    {"q": "Which is a C++ feature not in C?", "options": ["Classes", "Functions", "Pointers", "Arrays"], "correct": 0},
                    {"q": "Output of cout << 5 + 3?", "options": ["53", "8", "Error", "None"], "correct": 1},
                    {"q": "What does new operator do?", "options": ["Allocates memory", "Frees memory", "Copies", "None"], "correct": 0},
                    {"q": "Which is a C++ container?", "options": ["vector", "list", "map", "All"], "correct": 3},
                    {"q": "What is polymorphism in C++?", "options": ["Multiple forms", "Single form", "No form", "None"], "correct": 0},
                    {"q": "Which keyword is for namespace?", "options": ["namespace", "space", "name", "None"], "correct": 0}
                ]
            },
            "domain": {
                "Cloud": [
                    {"q": "Which is Amazon's cloud service?", "options": ["Azure", "AWS", "GCP", "Heroku"], "correct": 1},
                    {"q": "What does IaaS stand for?", "options": ["Infrastructure as a Service", "Internet as a Service", "Integration as a Service", "None"], "correct": 0},
                    {"q": "Which is a cloud deployment model?", "options": ["Public", "Private", "Hybrid", "All"], "correct": 3},
                    {"q": "What is SaaS?", "options": ["Software as a Service", "System as a Service", "Server as a Service", "None"], "correct": 0},
                    {"q": "Which is Microsoft's cloud?", "options": ["AWS", "Azure", "GCP", "Heroku"], "correct": 1},
                    {"q": "What is cloud computing?", "options": ["On-demand computing resources", "Local computing", "Desktop computing", "None"], "correct": 0},
                    {"q": "Which is Google's cloud?", "options": ["AWS", "Azure", "GCP", "Heroku"], "correct": 2},
                    {"q": "What is PaaS?", "options": ["Platform as a Service", "Process as a Service", "Product as a Service", "None"], "correct": 0},
                    {"q": "Which is a cloud storage service?", "options": ["S3", "EC2", "Lambda", "None"], "correct": 0},
                    {"q": "What is cloud scalability?", "options": ["Auto-scaling resources", "Fixed resources", "Decreasing resources", "None"], "correct": 0}
                ],
                "Web Development": [
                    {"q": "What does HTML stand for?", "options": ["HyperText Markup Language", "HighText Machine Language", "HyperText Machine Language", "None"], "correct": 0},
                    {"q": "Which is a CSS property?", "options": ["color", "if", "for", "while"], "correct": 0},
                    {"q": "What does CSS stand for?", "options": ["Cascading Style Sheets", "Computer Style Sheets", "Creative Style Sheets", "None"], "correct": 0},
                    {"q": "Which is a JavaScript framework?", "options": ["React", "Django", "Flask", "Laravel"], "correct": 0},
                    {"q": "What does HTTP stand for?", "options": ["HyperText Transfer Protocol", "HighText Transfer Protocol", "HyperText Transmission Protocol", "None"], "correct": 0},
                    {"q": "Which tag creates a hyperlink?", "options": ["<a>", "<link>", "<href>", "<url>"], "correct": 0},
                    {"q": "What is responsive design?", "options": ["Adapts to screen size", "Fixed layout", "Static design", "None"], "correct": 0},
                    {"q": "Which is a backend language?", "options": ["Python", "HTML", "CSS", "JavaScript only"], "correct": 0},
                    {"q": "What is an API?", "options": ["Application Programming Interface", "Application Process Interface", "Automated Programming Interface", "None"], "correct": 0},
                    {"q": "Which tag creates a form?", "options": ["<form>", "<input>", "<submit>", "<button>"], "correct": 0}
                ],
                "Cybersecurity": [
                    {"q": "What is phishing?", "options": ["Fraudulent emails", "Virus", "Firewall", "None"], "correct": 0},
                    {"q": "Which is a strong password?", "options": ["P@ssw0rd123!", "password", "123456", "qwerty"], "correct": 0},
                    {"q": "What is 2FA?", "options": ["Two-Factor Authentication", "Two-Factor Authorization", "Two-Factor Access", "None"], "correct": 0},
                    {"q": "What is encryption?", "options": ["Encoding data", "Deleting data", "Copying data", "None"], "correct": 0},
                    {"q": "What is a firewall?", "options": ["Security barrier", "Virus", "Antivirus", "None"], "correct": 0},
                    {"q": "What is malware?", "options": ["Malicious software", "Good software", "System software", "None"], "correct": 0},
                    {"q": "Which is a cyber attack?", "options": ["DDoS", "SQL", "HTML", "CSS"], "correct": 0},
                    {"q": "What is a VPN?", "options": ["Virtual Private Network", "Virtual Public Network", "Visual Private Network", "None"], "correct": 0},
                    {"q": "What is social engineering?", "options": ["Manipulating people", "Building software", "Network design", "None"], "correct": 0},
                    {"q": "Which is an antivirus?", "options": ["Norton", "Photoshop", "Excel", "None"], "correct": 0}
                ],
                "Agile": [
                    {"q": "What is Agile?", "options": ["Iterative development", "Waterfall", "Fixed process", "None"], "correct": 0},
                    {"q": "What is a sprint?", "options": ["Short development cycle", "Long cycle", "No cycle", "None"], "correct": 0},
                    {"q": "What is Scrum?", "options": ["Agile framework", "Programming language", "Database", "None"], "correct": 0},
                    {"q": "Who is a Scrum Master?", "options": ["Facilitator", "Developer", "Manager", "None"], "correct": 0},
                    {"q": "What is a user story?", "options": ["Requirement description", "Code", "Test", "None"], "correct": 0},
                    {"q": "What is a sprint retrospective?", "options": ["Review meeting", "Planning meeting", "Code review", "None"], "correct": 0},
                    {"q": "What is Kanban?", "options": ["Visual workflow", "Programming language", "Database", "None"], "correct": 0},
                    {"q": "What is a product backlog?", "options": ["Prioritized features", "Code repository", "Bug list", "None"], "correct": 0},
                    {"q": "What is continuous integration?", "options": ["Frequent code merging", "Rare merging", "No merging", "None"], "correct": 0},
                    {"q": "What is a daily standup?", "options": ["Daily meeting", "Weekly meeting", "Monthly meeting", "None"], "correct": 0}
                ]
            }
        }
    
    def get_topic_questions(self, category, topic, count=10):
        """Get questions for a specific topic."""
        bank = self.question_bank.get(category, {})
        questions = bank.get(topic, [])
        
        if self.openai_api_key and len(questions) < count:
            ai_questions = self._generate_ai_questions(category, topic, count - len(questions))
            questions.extend(ai_questions)
        
        return {"status": "success", "category": category, "topic": topic, "questions": questions[:count]}
    
    def _generate_ai_questions(self, category, topic, count):
        """Generate AI questions for a topic."""
        try:
            import requests
            prompt = f"Generate {count} MCQ on {topic} ({category}). 4 options each. Return JSON array with q, options, correct."
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.openai_api_key}"},
                json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}], "temperature": 0.9},
                timeout=10
            )
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            import re
            match = re.search(r'\[.*\]', content, re.DOTALL)
            if match:
                return json.loads(match.group())
        except:
            pass
        return []
    
    def get_all_topics(self):
        """Get all topics organized by category."""
        return {
            "status": "success",
            "categories": {
                "aptitude": {"name": "Aptitude", "topics": list(self.question_bank["aptitude"].keys())},
                "technical": {"name": "Technical CS", "topics": list(self.question_bank["technical"].keys())},
                "pseudocode": {"name": "Pseudocode", "topics": list(self.question_bank["pseudocode"].keys())},
                "domain": {"name": "Domain", "topics": list(self.question_bank["domain"].keys())}
            }
        }

mcq_bank = MCQQuestionBank()
