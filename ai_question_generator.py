"""
Charvak AI Question Generator
Generates unique questions for exam preparation
"""

class AIQuestionGenerator:
    def __init__(self):
        self.topics = {
            "reasoning": {
                "questions": ["If A > B and B > C, then which is true?", "Find the next number: 2, 6, 12, 20, 30, ?", "If CAT = 24, then DOG = ?"],
                "options": [["A > C", "A < C", "A = C", "Cannot determine"], ["40", "42", "44", "46"], ["26", "28", "30", "32"]],
                "correct": [0, 1, 0]
            },
            "quant": {
                "questions": ["What is 15% of 200?", "If x + y = 10 and x - y = 4, find x.", "What is the square root of 144?"],
                "options": [["25", "30", "35", "40"], ["5", "6", "7", "8"], ["10", "11", "12", "13"]],
                "correct": [1, 2, 2]
            },
            "english": {
                "questions": ["Choose the correct synonym of 'Happy':", "Which is grammatically correct?", "Fill in the blank: He ___ to school daily."],
                "options": [["Sad", "Joyful", "Angry", "Tired"], ["He go", "He goes", "He going", "He gone"], ["go", "goes", "going", "gone"]],
                "correct": [1, 1, 1]
            },
            "gk": {
                "questions": ["Who is the Prime Minister of India?", "What is the capital of Australia?", "Which is the largest ocean?"],
                "options": [["Modi", "Gandhi", "Nehru", "Singh"], ["Sydney", "Canberra", "Melbourne", "Perth"], ["Atlantic", "Indian", "Pacific", "Arctic"]],
                "correct": [0, 1, 2]
            },
            "anatomy": {
                "questions": ["Which bone is known as the collarbone?", "What is the largest organ in the human body?", "How many chambers does the human heart have?"],
                "options": [["Clavicle", "Scapula", "Humerus", "Sternum"], ["Liver", "Skin", "Brain", "Lungs"], ["2", "3", "4", "6"]],
                "correct": [0, 1, 2]
            },
            "pathology": {
                "questions": ["What is the most common type of cancer worldwide?", "Which cell type is involved in allergic reactions?", "What is the hallmark of acute inflammation?"],
                "options": [["Lung cancer", "Breast cancer", "Colon cancer", "Prostate cancer"], ["Mast cells", "Neutrophils", "Lymphocytes", "Macrophages"], ["Fibrosis", "Neutrophil infiltration", "Granuloma", "Calcification"]],
                "correct": [0, 0, 1]
            },
            "medicine": {
                "questions": ["What is the first-line treatment for hypertension?", "Which antibiotic is used for tuberculosis?", "What is the normal range for blood glucose?"],
                "options": [["ACE inhibitors", "Beta blockers", "Diuretics", "CCB"], ["Penicillin", "Isoniazid", "Tetracycline", "Erythromycin"], ["70-100 mg/dL", "100-150 mg/dL", "150-200 mg/dL", "200-250 mg/dL"]],
                "correct": [0, 1, 0]
            },
            "surgery": {
                "questions": ["What is the most common surgical emergency?", "Which incision is used for appendectomy?", "What is the first sign of postoperative infection?"],
                "options": [["Appendicitis", "Cholecystitis", "Hernia", "Perforation"], ["McBurney", "Midline", "Kocher", "Pfannenstiel"], ["Fever", "Pain", "Redness", "Swelling"]],
                "correct": [0, 0, 0]
            },
            "nursing": {
                "questions": ["What is the normal adult heart rate?", "Which position is best for a patient with dyspnea?", "What is the first step in wound care?"],
                "options": [["60-100 bpm", "40-60 bpm", "100-120 bpm", "120-140 bpm"], ["Supine", "Fowler's", "Prone", "Trendelenburg"], ["Clean wound", "Apply dressing", "Assess wound", "Remove dressing"]],
                "correct": [0, 1, 2]
            },
            "physiology": {
                "questions": ["What is the normal pH of human blood?", "Which hormone regulates blood sugar?", "What is the functional unit of the nervous system?"],
                "options": [["7.35-7.45", "7.0-7.2", "7.5-7.6", "6.8-7.0"], ["Insulin", "Glucagon", "Cortisol", "Thyroxine"], ["Neuron", "Nephron", "Alveoli", "Cell"]],
                "correct": [0, 0, 0]
            },
            "biochemistry": {
                "questions": ["What is the building block of proteins?", "Which enzyme breaks down carbohydrates?", "What is the energy currency of the cell?"],
                "options": [["Amino acids", "Fatty acids", "Glucose", "Nucleotides"], ["Amylase", "Lipase", "Protease", "Lactase"], ["ATP", "ADP", "AMP", "GTP"]],
                "correct": [0, 0, 0]
            },
            "microbiology": {
                "questions": ["Which organism causes tuberculosis?", "What is the most common cause of UTI?", "Which virus causes AIDS?"],
                "options": [["Mycobacterium TB", "Streptococcus", "Staphylococcus", "E. coli"], ["E. coli", "Klebsiella", "Pseudomonas", "Proteus"], ["HIV", "HPV", "HBV", "HCV"]],
                "correct": [0, 0, 0]
            },
            "pharmacology": {
                "questions": ["Which drug is used for pain relief?", "What is the antidote for heparin?", "Which antibiotic class includes penicillin?"],
                "options": [["Paracetamol", "Insulin", "Aspirin", "Warfarin"], ["Protamine sulfate", "Vitamin K", "FFP", "Platelets"], ["Beta-lactams", "Macrolides", "Tetracyclines", "Aminoglycosides"]],
                "correct": [0, 0, 0]
            },
            "pediatrics": {
                "questions": ["What is the normal birth weight?", "At what age does a child start walking?", "Which vaccine is given at birth?"],
                "options": [["2.5-3.5 kg", "1.5-2.5 kg", "3.5-4.5 kg", "4.5-5.5 kg"], ["12 months", "6 months", "18 months", "9 months"], ["BCG", "MMR", "Polio", "DPT"]],
                "correct": [0, 0, 0]
            },
            "psychiatry": {
                "questions": ["What is the most common mental health disorder?", "Which neurotransmitter is linked to depression?", "What does CBT stand for?"],
                "options": [["Anxiety", "Depression", "Schizophrenia", "Bipolar"], ["Serotonin", "Dopamine", "GABA", "Glutamate"], ["Cognitive Behavioral Therapy", "Clinical Behavior Test", "Central Brain Treatment", "None"]],
                "correct": [0, 0, 0]
            },
            "obg": {
                "questions": ["What is the normal duration of pregnancy?", "Which hormone is detected in pregnancy tests?", "What is the most common cause of postpartum hemorrhage?"],
                "options": [["40 weeks", "36 weeks", "38 weeks", "42 weeks"], ["hCG", "FSH", "LH", "Prolactin"], ["Uterine atony", "Placenta previa", "Abruption", "Retained placenta"]],
                "correct": [0, 0, 0]
            },
            "dental": {
                "questions": ["Which tooth is the wisdom tooth?", "What is the hardest substance in body?", "How many permanent teeth does an adult have?"],
                "options": [["Third molar", "First molar", "Second molar", "Premolar"], ["Enamel", "Dentin", "Bone", "Cementum"], ["28", "30", "32", "34"]],
                "correct": [0, 0, 2]
            },
            "clinical": {
                "questions": ["What is the normal range for blood pressure?", "Which test is used to diagnose diabetes?", "What is the most common cause of fever?"],
                "options": [["120/80 mmHg", "140/90 mmHg", "100/60 mmHg", "160/100 mmHg"], ["Fasting glucose", "Lipid profile", "CBC", "LFT"], ["Infection", "Dehydration", "Stress", "Medication"]],
                "correct": [0, 0, 0]
            },
            "pm fundamentals": {
                "questions": ["What is the first phase of project management?", "What does WBS stand for?", "What is the triple constraint?"],
                "options": [["Initiation", "Planning", "Execution", "Closing"], ["Work Breakdown Structure", "Work Budget System", "Weekly Business Status", "None"], ["Scope, Time, Cost", "Quality, Risk, Resource", "People, Process, Tech", "Plan, Do, Check"]],
                "correct": [0, 0, 0]
            },
            "people": {
                "questions": ["What is the key to team motivation?", "What is emotional intelligence?", "What is conflict resolution?"],
                "options": [["Recognition", "Money", "Fear", "Pressure"], ["Understanding emotions", "IQ", "Technical skills", "Memory"], ["Finding solutions", "Avoiding", "Winning arguments", "Ignoring"]],
                "correct": [0, 0, 0]
            },
            "process": {
                "questions": ["What is process improvement?", "What is Lean methodology?", "What is Six Sigma?"],
                "options": [["Continuous enhancement", "One-time change", "Random change", "No change"], ["Eliminating waste", "Adding steps", "More resources", "More time"], ["Reducing defects", "Increasing defects", "Ignoring quality", "Faster only"]],
                "correct": [0, 0, 0]
            },
            "business": {
                "questions": ["What is ROI?", "What is a business case?", "What is NPV?"],
                "options": [["Return on Investment", "Rate of Interest", "Return on Income", "None"], ["Justification document", "Legal document", "HR document", "Marketing plan"], ["Net Present Value", "New Project Value", "Net Profit Value", "None"]],
                "correct": [0, 0, 0]
            },
            "architecture": {
                "questions": ["What is cloud architecture?", "What is scalability?", "What is high availability?"],
                "options": [["Design of cloud systems", "Building design", "Network cable", "Hardware"], ["Handling growth", "Reducing size", "Fixed capacity", "Limiting users"], ["Always available", "Sometimes available", "Rarely available", "Never available"]],
                "correct": [0, 0, 0]
            },
            "security": {
                "questions": ["What is encryption?", "What is a firewall?", "What is authentication?"],
                "options": [["Encoding data", "Deleting data", "Copying data", "Sharing data"], ["Network security", "Hardware", "Software bug", "Virus"], ["Verifying identity", "Granting access", "Denying access", "Logging in"]],
                "correct": [0, 0, 0]
            },
            "reading": {
                "questions": ["What is skimming?", "What is scanning?", "What is inference?"],
                "options": [["Quick reading", "Slow reading", "Detailed reading", "No reading"], ["Finding specific info", "Reading everything", "Reading nothing", "Random"], ["Drawing conclusion", "Copying text", "Memorizing", "Ignoring"]],
                "correct": [0, 0, 0]
            },
            "listening": {
                "questions": ["What is active listening?", "What is paraphrasing?", "What is note-taking?"],
                "options": [["Focused listening", "Passive hearing", "Ignoring", "Interrupting"], ["Restating", "Copying", "Translating", "Shortening"], ["Recording key points", "Writing everything", "Not writing", "Typing only"]],
                "correct": [0, 0, 0]
            },
            "speaking": {
                "questions": ["What is pronunciation?", "What is fluency?", "What is intonation?"],
                "options": [["Sound of words", "Spelling", "Writing", "Reading"], ["Smooth speech", "Fast speech", "Slow speech", "No speech"], ["Voice pitch", "Volume only", "Speed only", "Words only"]],
                "correct": [0, 0, 0]
            },
            "writing": {
                "questions": ["What is an essay?", "What is a thesis statement?", "What is coherence?"],
                "options": [["Structured writing", "Random notes", "List", "Poem"], ["Main argument", "Example", "Conclusion", "Title"], ["Logical flow", "Random order", "Repetition", "Contradiction"]],
                "correct": [0, 0, 0]
            },
            "ethics": {
                "questions": ["What is ethics?", "What is integrity?", "What is conflict of interest?"],
                "options": [["Moral principles", "Legal rules", "Company policy", "Personal preference"], ["Honesty", "Dishonesty", "Secrecy", "Manipulation"], ["Competing interests", "Shared interest", "No interest", "Public interest"]],
                "correct": [0, 0, 0]
            },
            "economics": {
                "questions": ["What is supply and demand?", "What is inflation?", "What is GDP?"],
                "options": [["Market forces", "Government rules", "Company policy", "Random"], ["Price increase", "Price decrease", "Price stability", "No prices"], ["Gross Domestic Product", "General Development Plan", "Gross Development Product", "None"]],
                "correct": [0, 0, 0]
            },
            "fra": {
                "questions": ["What is balance sheet?", "What is income statement?", "What is cash flow?"],
                "options": [["Financial position", "Profit only", "Loss only", "Tax only"], ["Revenue and expenses", "Assets only", "Liabilities only", "Equity only"], ["Money movement", "Profit only", "Sales only", "Expenses only"]],
                "correct": [0, 0, 0]
            },
            "varc": {
                "questions": ["What is reading comprehension?", "What is para jumble?", "What is summary writing?"],
                "options": [["Understanding text", "Reading fast", "Reading slow", "Skipping"], ["Arranging sentences", "Writing sentences", "Deleting sentences", "Copying"], ["Condensing text", "Expanding text", "Repeating text", "Ignoring"]],
                "correct": [0, 0, 0]
            },
            "dilr": {
                "questions": ["What is data interpretation?", "What is logical reasoning?", "What is a pie chart?"],
                "options": [["Analyzing data", "Collecting data", "Deleting data", "Ignoring"], ["Drawing conclusions", "Memorizing facts", "Copying text", "Guessing"], ["Circular chart", "Linear chart", "Square chart", "No chart"]],
                "correct": [0, 0, 0]
            },
            "physics": {
                "questions": ["What is Newton's first law?", "What is velocity?", "What is energy?"],
                "options": [["Inertia", "Acceleration", "Action-reaction", "None"], ["Speed with direction", "Speed only", "Direction only", "Distance"], ["Capacity to work", "Force", "Power", "Pressure"]],
                "correct": [0, 0, 0]
            },
            "chemistry": {
                "questions": ["What is the atomic number?", "What is a molecule?", "What is pH?"],
                "options": [["Number of protons", "Number of electrons", "Number of neutrons", "Atomic mass"], ["Group of atoms", "Single atom", "Element", "Compound only"], ["Acidity measure", "Temperature", "Pressure", "Volume"]],
                "correct": [0, 0, 0]
            },
            "math": {
                "questions": ["What is 15% of 200?", "What is square root of 144?", "What is 2^8?"],
                "options": [["30", "25", "35", "40"], ["12", "11", "13", "14"], ["256", "128", "512", "1024"]],
                "correct": [0, 0, 0]
            },
            "aptitude": {
                "questions": ["If a train travels 300 km in 5 hours, what is its speed?", "What is 25% of 80?", "If 5 workers build a wall in 10 days, how long for 10 workers?"],
                "options": [["60 km/h", "50 km/h", "55 km/h", "65 km/h"], ["20", "25", "30", "15"], ["5 days", "10 days", "15 days", "20 days"]],
                "correct": [0, 0, 0]
            },
            "technical": {
                "questions": ["What is an API?", "What is a database?", "What is an algorithm?"],
                "options": [["Interface for communication", "Hardware", "Software bug", "Network"], ["Data storage", "Code editor", "Browser", "OS"], ["Step-by-step procedure", "Random process", "Data type", "Variable"]],
                "correct": [0, 0, 0]
            }
        }
    
    def generate_questions(self, exam_id, topic, count=10):
        topic_lower = topic.lower().strip()
        topic_data = self.topics.get(topic_lower, self.topics.get("reasoning", {}))
        questions = []
        base_q = topic_data.get("questions", [])
        base_o = topic_data.get("options", [])
        base_c = topic_data.get("correct", [])
        for i in range(count):
            idx = i % len(base_q) if base_q else 0
            questions.append({
                "id": i + 1,
                "question": base_q[idx] if base_q else topic + " - Question " + str(i+1),
                "options": base_o[idx] if base_o else ["Option A", "Option B", "Option C", "Option D"],
                "correct": base_c[idx] if base_c else 0,
                "explanation": "Explanation for question " + str(i+1),
                "difficulty": "Medium",
                "topic": topic
            })
        return questions

ai_question_generator = AIQuestionGenerator()