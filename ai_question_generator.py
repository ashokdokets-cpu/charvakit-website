"""
Charvak AI-Powered Question Generator
Smart Variation System - Cost-optimized with high engagement
"""
import os
import json
import logging
import random
import hashlib
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger("charvakit.ai_questions")

class AIQuestionGenerator:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.used_questions = {}
        self.topic_fallback = self._initialize_fallback_topics()
        self.question_cache = {}
        self.cache_ttl = timedelta(days=30)  # Keep questions for 30 days
        self.daily_ai_usage = {}
        self.max_daily_ai = 100
        self.variation_prefixes = [
            "Identify: ",
            "Choose the best answer: ",
            "Select the correct option: ",
            "Which of the following is correct? ",
            "Determine: ",
            "Analyze and answer: ",
            "Pick the right option: ",
            "Find the correct answer: "
        ]
        logger.info(f"Smart Variation System ready - OpenAI: {'ENABLED' if self.openai_api_key else 'DISABLED'}")
    
    def _initialize_fallback_topics(self):
        """Fallback topics - FREE."""
        return {
            "reasoning": {"questions": ["If A > B and B > C, which is true?", "Find next: 2, 6, 12, 20, ?", "Odd one: Square, Circle, Triangle", "If CAT = 24, DOG = ?", "Complete: 3, 9, 27, 81, ?"], "options": [["A > C", "A < C", "A = C"], ["42", "40", "44"], ["Square", "Circle", "All"], ["26", "28", "30"], ["243", "162", "324"]], "correct": [0, 0, 2, 0, 0]},
            "quant": {"questions": ["15% of 200?", "Square root of 144?", "2^8?", "20% of 500?", "LCM of 4 and 6?"], "options": [["30", "25", "35"], ["12", "11", "13"], ["256", "128", "512"], ["100", "50", "150"], ["12", "24", "6"]], "correct": [0, 0, 0, 0, 0]},
            "english": {"questions": ["Synonym of Happy?", "Antonym of Ancient?", "He ___ to school", "Plural of Child?", "Past tense of go?"], "options": [["Joyful", "Sad", "Angry"], ["Modern", "Old", "Past"], ["goes", "go", "going"], ["Children", "Childs", "Child"], ["went", "goed", "gone"]], "correct": [0, 0, 0, 0, 0]},
            "gk": {"questions": ["PM of India?", "Capital of Australia?", "Largest ocean?", "Currency of Japan?", "National animal?"], "options": [["Modi", "Gandhi", "Nehru"], ["Canberra", "Sydney", "Perth"], ["Pacific", "Atlantic", "Indian"], ["Yen", "Yuan", "Won"], ["Tiger", "Lion", "Elephant"]], "correct": [0, 0, 0, 0, 0]},
            "anatomy": {"questions": ["Collarbone bone?", "Largest organ?", "Heart chambers?", "Balance control?", "Kidney functional unit?"], "options": [["Clavicle", "Scapula", "Sternum"], ["Skin", "Liver", "Brain"], ["4", "2", "6"], ["Cerebellum", "Cerebrum", "Medulla"], ["Nephron", "Neuron", "Glomerulus"]], "correct": [0, 0, 0, 0, 0]},
            "pathology": {"questions": ["Most common cancer?", "Allergic reaction cells?", "Acute inflammation?", "Insulin deficiency?", "Cirrhosis cause?"], "options": [["Lung", "Breast", "Colon"], ["Mast cells", "Neutrophils", "Macrophages"], ["Neutrophils", "Fibrosis", "Granuloma"], ["Type 1", "Type 2", "Both"], ["Alcohol", "Hepatitis B", "Hepatitis C"]], "correct": [0, 0, 0, 0, 0]},
            "medicine": {"questions": ["First-line HTN?", "TB antibiotic?", "Normal glucose?", "Scurvy vitamin?", "Pneumonia cause?"], "options": [["ACE inhibitors", "Beta blockers", "CCB"], ["Isoniazid", "Penicillin", "Tetracycline"], ["70-100", "100-150", "150-200"], ["Vitamin C", "Vitamin D", "Vitamin B12"], ["Streptococcus", "Staph", "Klebsiella"]], "correct": [0, 0, 0, 0, 0]},
            "surgery": {"questions": ["Surgical emergency?", "Appendectomy incision?", "Post-op infection?", "Absorbable suture?", "Bowel obstruction?"], "options": [["Appendicitis", "Hernia", "Cholecystitis"], ["McBurney", "Midline", "Kocher"], ["Fever", "Pain", "Redness"], ["Vicryl", "Nylon", "Silk"], ["Adhesions", "Hernia", "Tumor"]], "correct": [0, 0, 0, 0, 0]},
            "nursing": {"questions": ["Normal heart rate?", "Dyspnea position?", "Wound care first?", "Normal temperature?", "PRN meaning?"], "options": [["60-100", "40-60", "100-120"], ["Fowler's", "Supine", "Prone"], ["Assess", "Clean", "Dress"], ["36-37C", "37-38C", "38-39C"], ["As needed", "Every hour", "Before meals"]], "correct": [0, 0, 0, 0, 0]},
            "physiology": {"questions": ["Blood pH?", "Blood sugar hormone?", "Nervous system unit?", "Respiratory rate?", "Systolic BP?"], "options": [["7.35-7.45", "7.0-7.2", "7.5-7.6"], ["Insulin", "Glucagon", "Cortisol"], ["Neuron", "Nephron", "Alveoli"], ["12-20", "8-10", "20-30"], ["90-120", "120-140", "140-160"]], "correct": [0, 0, 0, 0, 0]},
            "biochemistry": {"questions": ["Protein building block?", "Carb enzyme?", "Energy currency?", "Fat-soluble vitamin?", "Fasting glucose?"], "options": [["Amino acids", "Fatty acids", "Glucose"], ["Amylase", "Lipase", "Protease"], ["ATP", "ADP", "AMP"], ["Vitamin D", "Vitamin C", "Vitamin B12"], ["70-100", "100-150", "150-200"]], "correct": [0, 0, 0, 0, 0]},
            "microbiology": {"questions": ["TB organism?", "UTI cause?", "AIDS virus?", "E. coli gram?", "Candidiasis fungus?"], "options": [["Mycobacterium", "Streptococcus", "Staph"], ["E. coli", "Klebsiella", "Pseudomonas"], ["HIV", "HPV", "HBV"], ["Gram-negative", "Gram-positive", "Acid-fast"], ["Candida", "Aspergillus", "Cryptococcus"]], "correct": [0, 0, 0, 0, 0]},
            "pharmacology": {"questions": ["Pain relief drug?", "Heparin antidote?", "Penicillin class?", "Type 2 diabetes?", "HTN drug class?"], "options": [["Paracetamol", "Insulin", "Warfarin"], ["Protamine", "Vitamin K", "FFP"], ["Beta-lactams", "Macrolides", "Tetracyclines"], ["Metformin", "Insulin", "Glibenclamide"], ["ACE inhibitors", "Statins", "PPIs"]], "correct": [0, 0, 0, 0, 0]},
            "pediatrics": {"questions": ["Birth weight?", "Walking age?", "Birth vaccine?", "Childhood cancer?", "Newborn heart rate?"], "options": [["2.5-3.5 kg", "1.5-2.5 kg", "3.5-4.5 kg"], ["12 months", "6 months", "18 months"], ["BCG", "MMR", "Polio"], ["Leukemia", "Lymphoma", "Brain tumor"], ["120-160", "80-100", "60-80"]], "correct": [0, 0, 0, 0, 0]},
            "psychiatry": {"questions": ["Common mental disorder?", "Depression neurotransmitter?", "Schizophrenia treatment?", "CBT stands for?", "Mood swing disorder?"], "options": [["Anxiety", "Depression", "Bipolar"], ["Serotonin", "Dopamine", "GABA"], ["Antipsychotics", "Antidepressants", "Mood stabilizers"], ["Cognitive Behavioral", "Clinical", "Central"], ["Bipolar", "Depression", "Anxiety"]], "correct": [0, 0, 0, 0, 0]},
            "obg": {"questions": ["Pregnancy duration?", "Pregnancy hormone?", "PPH cause?", "Fetal heart rate?", "Pregnancy vitamin?"], "options": [["40 weeks", "36 weeks", "38 weeks"], ["hCG", "FSH", "LH"], ["Uterine atony", "Previa", "Abruption"], ["110-160", "80-100", "160-180"], ["Folic acid", "Vitamin C", "Vitamin D"]], "correct": [0, 0, 0, 0, 0]},
            "dental": {"questions": ["Wisdom tooth?", "Hardest substance?", "Adult teeth?", "Tooth decay?", "Lower teeth nerve?"], "options": [["Third molar", "First molar", "Premolar"], ["Enamel", "Dentin", "Bone"], ["32", "28", "30"], ["Caries", "Gingivitis", "Sensitivity"], ["Inferior alveolar", "Facial", "Trigeminal"]], "correct": [0, 0, 0, 0, 0]},
            "clinical": {"questions": ["Normal BP?", "Diabetes test?", "Fever cause?", "Respiratory rate?", "Shock sign?"], "options": [["120/80", "140/90", "100/60"], ["Fasting glucose", "Lipid", "CBC"], ["Infection", "Dehydration", "Stress"], ["12-20", "8-10", "20-30"], ["Hypotension", "Tachycardia", "Fever"]], "correct": [0, 0, 0, 0, 0]},
            "pm fundamentals": {"questions": ["First PM phase?", "WBS?", "Triple constraint?", "Project success?", "Gantt chart?"], "options": [["Initiation", "Planning", "Execution"], ["Work Breakdown", "Work Budget", "Weekly"], ["Scope Time Cost", "Quality", "People"], ["PM", "Team", "Sponsor"], ["Scheduling", "Budgeting", "Risk"]], "correct": [0, 0, 0, 0, 0]},
            "agile": {"questions": ["Agile is?", "Sprint duration?", "Scrum master?", "Agile manifesto?", "User story?"], "options": [["Iterative", "Waterfall", "Random"], ["2-4 weeks", "6 months", "1 year"], ["Facilitator", "Manager", "Boss"], ["4 values", "10 values", "2 values"], ["Requirement", "Bug", "Test"]], "correct": [0, 0, 0, 0, 0]},
            "scrum": {"questions": ["Team size?", "Daily standup?", "Product backlog?", "Sprint review?", "Scrum roles?"], "options": [["5-9", "20-30", "50+"], ["15 min", "1 hour", "2 hours"], ["Ordered list", "Random", "No list"], ["Inspect", "Ignore", "Skip"], ["3 roles", "5 roles", "1 role"]], "correct": [0, 0, 0, 0, 0]},
            "architecture": {"questions": ["Cloud architecture?", "Scalability?", "High availability?", "Fault tolerance?", "Load balancing?"], "options": [["Design", "Building", "Hardware"], ["Growth", "Reduction", "Fixed"], ["Always on", "Sometimes", "Never"], ["Recovery", "No failures", "Ignoring"], ["Distributing", "Blocking", "Slowing"]], "correct": [0, 0, 0, 0, 0]},
            "security": {"questions": ["Encryption?", "Firewall?", "Authentication?", "Authorization?", "Vulnerability?"], "options": [["Encoding", "Deleting", "Sharing"], ["Security", "Hardware", "Bug"], ["Identity", "Access", "Denial"], ["Permissions", "Verifying", "Creating"], ["Weakness", "Strength", "Feature"]], "correct": [0, 0, 0, 0, 0]},
            "development": {"questions": ["SDLC?", "Agile dev?", "CI/CD?", "Git?", "API?"], "options": [["Lifecycle", "Random", "No process"], ["Iterative", "Waterfall", "No method"], ["Continuous", "One-time", "Manual"], ["Version control", "Database", "Server"], ["Interface", "Hardware", "Bug"]], "correct": [0, 0, 0, 0, 0]},
            "cloud": {"questions": ["Cloud computing?", "IaaS?", "SaaS?", "PaaS?", "Serverless?"], "options": [["On-demand", "Local only", "Hardware"], ["Infrastructure", "Platform", "Software"], ["Software", "Infrastructure", "Platform"], ["Platform", "Infrastructure", "Software"], ["No server mgmt", "One server", "Many servers"]], "correct": [0, 0, 0, 0, 0]},
            "k8s": {"questions": ["Kubernetes?", "Pod?", "Node?", "Deployment?", "Service?"], "options": [["Orchestration", "Database", "Language"], ["Smallest unit", "Largest", "None"], ["Machine", "Container", "App"], ["Release", "Coding", "Testing"], ["Network", "Storage", "Compute"]], "correct": [0, 0, 0, 0, 0]},
            "networking": {"questions": ["TCP/IP?", "DNS?", "HTTP?", "HTTPS?", "FTP?"], "options": [["Protocol", "Hardware", "Language"], ["Name resolution", "Storage", "Compute"], ["Web", "Database", "Security"], ["Secure web", "Database", "Storage"], ["File transfer", "Email", "Web"]], "correct": [0, 0, 0, 0, 0]},
            "linux": {"questions": ["Linux?", "Shell?", "chmod?", "ls?", "grep?"], "options": [["OS", "Hardware", "App"], ["Command interface", "GUI", "Database"], ["Permissions", "Delete", "Copy"], ["List files", "Delete", "Copy"], ["Search text", "Delete", "Copy"]], "correct": [0, 0, 0, 0, 0]},
            "testing": {"questions": ["Unit testing?", "Integration?", "Regression?", "Black box?", "White box?"], "options": [["Individual", "System", "None"], ["Combined", "Single", "Random"], ["Re-test", "Skip", "New only"], ["No internal", "Internal", "None"], ["Internal", "No internal", "None"]], "correct": [0, 0, 0, 0, 0]},
            "crm": {"questions": ["CRM?", "Salesforce?", "Lead?", "Pipeline?", "Contact?"], "options": [["Customer mgmt", "Database", "OS"], ["CRM platform", "OS", "Language"], ["Potential", "Customer only", "None"], ["Stages", "Random", "None"], ["Person", "Company only", "None"]], "correct": [0, 0, 0, 0, 0]},
            "automation": {"questions": ["Automation?", "RPA?", "CI/CD?", "Script?", "Workflow?"], "options": [["Reduce manual", "Increase", "No change"], ["Robotic", "Manual", "None"], ["Automated", "Manual", "Random"], ["Code", "Hardware", "None"], ["Process", "Random", "None"]], "correct": [0, 0, 0, 0, 0]},
            "ethics": {"questions": ["Ethics?", "Integrity?", "Transparency?", "Accountability?", "Compliance?"], "options": [["Moral", "Legal", "Policy"], ["Honesty", "Dishonesty", "Secrecy"], ["Openness", "Secrecy", "Hidden"], ["Responsibility", "Blame", "Denial"], ["Following", "Breaking", "Ignoring"]], "correct": [0, 0, 0, 0, 0]},
            "economics": {"questions": ["Supply/demand?", "Inflation?", "GDP?", "Recession?", "Interest rate?"], "options": [["Market", "Govt", "Random"], ["Price up", "Down", "Stable"], ["Gross Domestic", "General", "None"], ["Decline", "Growth", "Stable"], ["Borrowing", "Living", "Food"]], "correct": [0, 0, 0, 0, 0]},
            "fra": {"questions": ["Balance sheet?", "Income statement?", "Cash flow?", "Depreciation?", "Goodwill?"], "options": [["Position", "Profit", "Tax"], ["Revenue", "Assets", "Equity"], ["Movement", "Profit", "Sales"], ["Decrease", "Increase", "No change"], ["Intangible", "Tangible", "Liability"]], "correct": [0, 0, 0, 0, 0]},
            "audit": {"questions": ["Audit?", "Internal audit?", "External audit?", "Audit report?", "Audit evidence?"], "options": [["Review", "Ignore", "Skip"], ["Internal", "External only", "None"], ["Independent", "Internal", "None"], ["Findings", "Random", "None"], ["Proof", "Random", "None"]], "correct": [0, 0, 0, 0, 0]},
            "tax": {"questions": ["Tax?", "Income tax?", "GST?", "Tax deduction?", "Tax credit?"], "options": [["Levy", "Gift", "Loan"], ["Earnings", "Sales", "Property"], ["Goods/services", "Income", "Property"], ["Reduce income", "Reduce tax", "None"], ["Reduce tax", "Reduce income", "None"]], "correct": [0, 0, 0, 0, 0]},
            "governance": {"questions": ["Governance?", "Compliance?", "Board role?", "Risk oversight?", "Ethics program?"], "options": [["Framework", "Random", "None"], ["Following", "Breaking", "Ignoring"], ["Oversight", "Operations", "Marketing"], ["Monitor", "Ignore", "Skip"], ["Guidelines", "Random", "None"]], "correct": [0, 0, 0, 0, 0]},
            "finance": {"questions": ["Finance?", "ROI?", "Budgeting?", "Forecasting?", "Cash management?"], "options": [["Money mgmt", "Random", "None"], ["Return", "Cost", "Tax"], ["Planning", "Random", "No plan"], ["Prediction", "Random", "None"], ["Liquidity", "Random", "None"]], "correct": [0, 0, 0, 0, 0]},
            "strategy": {"questions": ["Strategy?", "SWOT?", "Porter's five?", "Vision?", "Mission?"], "options": [["Plan", "Random", "None"], ["Strengths", "Weaknesses", "None"], ["Competitive", "Random", "None"], ["Future", "Past", "None"], ["Purpose", "Random", "None"]], "correct": [0, 0, 0, 0, 0]},
            "reading": {"questions": ["Skimming?", "Scanning?", "Inference?", "Main idea?", "Context clue?"], "options": [["Quick", "Slow", "None"], ["Specific", "All", "None"], ["Conclusion", "Copy", "Ignore"], ["Central", "Minor", "None"], ["Hint", "Dictionary", "Guess"]], "correct": [0, 0, 0, 0, 0]},
            "writing": {"questions": ["Essay?", "Thesis?", "Coherence?", "Grammar?", "Punctuation?"], "options": [["Structured", "Random", "List"], ["Argument", "Example", "Title"], ["Flow", "Random", "Repetition"], ["Rules", "Math", "Science"], ["Marks", "Spacing", "Font"]], "correct": [0, 0, 0, 0, 0]},
            "listening": {"questions": ["Active listening?", "Paraphrasing?", "Note-taking?", "Comprehension?", "Lecture?"], "options": [["Focused", "Passive", "Ignoring"], ["Restating", "Copying", "Translating"], ["Key points", "All", "None"], ["Understanding", "Hearing", "Seeing"], ["Talk", "Conversation", "Argument"]], "correct": [0, 0, 0, 0, 0]},
            "speaking": {"questions": ["Pronunciation?", "Fluency?", "Intonation?", "Articulation?", "Presentation?"], "options": [["Sound", "Spelling", "Writing"], ["Smooth", "Fast", "Slow"], ["Pitch", "Volume", "Speed"], ["Clear", "Mumbling", "Whispering"], ["Formal", "Casual", "Argument"]], "correct": [0, 0, 0, 0, 0]},
            "varc": {"questions": ["Reading comp?", "Para jumble?", "Summary?", "Vocabulary?", "Tone?"], "options": [["Understanding", "Fast", "Skip"], ["Arrange", "Write", "Delete"], ["Condense", "Expand", "Repeat"], ["Words", "Grammar", "Spelling"], ["Attitude", "Reader's", "Character's"]], "correct": [0, 0, 0, 0, 0]},
            "dilr": {"questions": ["Data interpretation?", "Logical reasoning?", "Pie chart?", "Bar graph?", "Table?"], "options": [["Analyze", "Collect", "Delete"], ["Conclude", "Memorize", "Guess"], ["Circular", "Linear", "Square"], ["Bars", "Lines", "Dots"], ["Grid", "Story", "Poem"]], "correct": [0, 0, 0, 0, 0]},
            "teaching": {"questions": ["Teaching aptitude?", "Pedagogy?", "Assessment?", "Lesson plan?", "Classroom mgmt?"], "options": [["Skill", "Random", "None"], ["Method", "Random", "None"], ["Evaluation", "Random", "None"], ["Plan", "Random", "None"], ["Control", "Random", "None"]], "correct": [0, 0, 0, 0, 0]},
            "research": {"questions": ["Research?", "Hypothesis?", "Methodology?", "Data analysis?", "Conclusion?"], "options": [["Investigation", "Random", "None"], ["Prediction", "Random", "None"], ["Method", "Random", "None"], ["Analyze", "Random", "None"], ["Finding", "Random", "None"]], "correct": [0, 0, 0, 0, 0]},
            "science": {"questions": ["Scientific method?", "Experiment?", "Theory?", "Observation?", "Data?"], "options": [["Systematic", "Random", "None"], ["Test", "Random", "None"], ["Explanation", "Random", "None"], ["Watch", "Random", "None"], ["Facts", "Random", "None"]], "correct": [0, 0, 0, 0, 0]},
            "numerical": {"questions": ["15% of 200?", "Square root of 144?", "2^8?", "7 x 8?", "100/4?"], "options": [["30", "25", "35"], ["12", "11", "13"], ["256", "128", "512"], ["56", "54", "58"], ["25", "20", "30"]], "correct": [0, 0, 0, 0, 0]},
            "verbal": {"questions": ["Verbal reasoning?", "Analogy?", "Antonym?", "Synonym?", "Sentence completion?"], "options": [["Logic", "Random", "None"], ["Similar", "Different", "None"], ["Opposite", "Same", "None"], ["Same", "Opposite", "None"], ["Complete", "Random", "None"]], "correct": [0, 0, 0, 0, 0]},
            "physics": {"questions": ["Newton's law?", "Unit of force?", "Speed of light?", "Energy unit?", "Current unit?"], "options": [["Inertia", "Acceleration", "Action"], ["Newton", "Joule", "Watt"], ["3x10^8", "3x10^6", "3x10^10"], ["Joule", "Newton", "Watt"], ["Ampere", "Volt", "Ohm"]], "correct": [0, 0, 0, 0, 0]},
            "chemistry": {"questions": ["Carbon atomic #?", "Water formula?", "pH of water?", "Abundant gas?", "Gold symbol?"], "options": [["6", "12", "8"], ["H2O", "CO2", "O2"], ["7", "0", "14"], ["Nitrogen", "Oxygen", "CO2"], ["Au", "Ag", "Fe"]], "correct": [0, 0, 0, 0, 0]},
            "math": {"questions": ["15% of 200?", "Square root of 144?", "2^8?", "7 x 8?", "100/4?"], "options": [["30", "25", "35"], ["12", "11", "13"], ["256", "128", "512"], ["56", "54", "58"], ["25", "20", "30"]], "correct": [0, 0, 0, 0, 0]},
            "aptitude": {"questions": ["Train speed?", "25% of 80?", "Workers time?", "Ratio?", "Average?"], "options": [["60 km/h", "50", "55"], ["20", "25", "30"], ["5 days", "10", "15"], ["30", "20", "25"], ["4", "3", "5"]], "correct": [0, 0, 0, 0, 0]},
            "technical": {"questions": ["API?", "Database?", "Algorithm?", "OOP?", "HTML?"], "options": [["Interface", "Hardware", "Bug"], ["Data storage", "Editor", "Browser"], ["Step-by-step", "Random", "Data type"], ["Object", "Old", "Only"], ["Markup", "Programming", "Database"]], "correct": [0, 0, 0, 0, 0]}
        }
    
    def generate_questions(self, exam_id, topic, count=10, user_email=None):
        """Smart generation with variation."""
        topic_lower = topic.lower().strip()
        cache_key = f"{exam_id}_{topic_lower}"
        
        # Check cache with variation
        if cache_key in self.question_cache:
            cache_data = self.question_cache[cache_key]
            cached = cache_data["questions"]
            if len(cached) >= count * 3:
                # We have enough questions - sample with variation
                sampled = random.sample(cached, min(count * 3, len(cached)))
                return self._apply_variation(sampled)[:count]
        
        # Check daily AI limit
        can_use_ai = True
        if user_email:
            today = datetime.now().strftime("%Y-%m-%d")
            if user_email not in self.daily_ai_usage:
                self.daily_ai_usage[user_email] = {}
            if today not in self.daily_ai_usage[user_email]:
                self.daily_ai_usage[user_email][today] = 0
            can_use_ai = self.daily_ai_usage[user_email][today] + count <= self.max_daily_ai
        
        # Use OpenAI for small batches
        if self.openai_api_key and count <= 20 and can_use_ai:
            try:
                questions = self.generate_with_openai(exam_id, topic, count * 3)
                if questions:
                    if user_email:
                        self.daily_ai_usage[user_email][today] += count
                    if cache_key not in self.question_cache:
                        self.question_cache[cache_key] = {"questions": [], "timestamp": datetime.now()}
                    self.question_cache[cache_key]["questions"].extend(questions)
                    sampled = random.sample(questions, min(count, len(questions)))
                    return self._apply_variation(sampled)
        
        # Fallback with variation
        return self._generate_fallback_with_variation(exam_id, topic, count)
    
    def _generate_fallback_with_variation(self, exam_id, topic, count=10):
        """Generate fallback with variation."""
        topic_lower = topic.lower().strip()
        topic_data = self.topic_fallback.get(topic_lower, self.topic_fallback.get("reasoning", {}))
        
        questions = []
        base_q = topic_data.get("questions", [])
        base_o = topic_data.get("options", [])
        base_c = topic_data.get("correct", [])
        
        indices = list(range(len(base_q))) if base_q else [0]
        random.shuffle(indices)
        
        for i in range(min(count, 20)):
            idx = indices[i % len(indices)]
            questions.append({
                "id": i + 1,
                "question": base_q[idx] if base_q else topic + " - Question " + str(i+1),
                "options": base_o[idx] if base_o else ["Option A", "Option B", "Option C", "Option D"],
                "correct": base_c[idx] if base_c else 0,
                "explanation": "Explanation for question " + str(i+1),
                "difficulty": "Medium",
                "topic": topic,
                "ai_generated": False
            })
        
        return self._apply_variation(questions)
    
    def _apply_variation(self, questions):
        """Apply variations - shuffle options, add prefix."""
        varied = []
        for i, q in enumerate(questions):
            # Shuffle options
            options = list(q["options"])
            correct_idx = q["correct"]
            if correct_idx < len(options):
                correct_option = options[correct_idx]
                random.shuffle(options)
                new_correct = options.index(correct_option)
            else:
                new_correct = 0
            
            # Add random prefix
            prefix = random.choice(self.variation_prefixes)
            question_text = q["question"]
            if random.random() > 0.5:
                question_text = prefix + question_text
            
            varied.append({
                "id": i + 1,
                "question": question_text,
                "options": options,
                "correct": new_correct,
                "explanation": q.get("explanation", ""),
                "difficulty": q.get("difficulty", "Medium"),
                "topic": q.get("topic", ""),
                "ai_generated": q.get("ai_generated", False),
                "variation_id": random.randint(1, 99999)
            })
        
        # Shuffle question order
        random.shuffle(varied)
        
        # Reassign IDs
        for i, q in enumerate(varied):
            q["id"] = i + 1
        
        return varied
    
    def generate_with_openai(self, exam_id, topic, count=10):
        """Generate questions using OpenAI."""
        try:
            import requests
            prompt = f"Generate {count} unique multiple-choice questions for '{topic}' topic in '{exam_id}' exam. Return as JSON array with fields: question, options (array of 4), correct (index 0-3), explanation."
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.openai_api_key}", "Content-Type": "application/json"},
                json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}], "temperature": 0.8, "max_tokens": 2000},
                timeout=30
            )
            
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                questions = json.loads(json_match.group())
                formatted = []
                for i, q in enumerate(questions):
                    formatted.append({
                        "id": i + 1,
                        "question": q.get("question", ""),
                        "options": q.get("options", ["A", "B", "C", "D"]),
                        "correct": q.get("correct", 0),
                        "explanation": q.get("explanation", ""),
                        "difficulty": "Medium",
                        "topic": topic,
                        "ai_generated": True
                    })
                return formatted
            return []
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            return []

ai_question_generator = AIQuestionGenerator()
