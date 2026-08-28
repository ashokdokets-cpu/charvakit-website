"""
Charvak AI-Powered Question Generator
Optimized with caching and hybrid approach for cost efficiency
"""
import os
import json
import logging
import random
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger("charvakit.ai_questions")

class AIQuestionGenerator:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.used_questions = {}
        self.topic_fallback = self._initialize_fallback_topics()
        self.question_cache = {}  # Cache: {cache_key: {"questions": [], "timestamp": datetime}}
        self.cache_ttl = timedelta(hours=24)  # Cache valid for 24 hours
        self.daily_ai_usage = {}  # Track daily AI usage per user
        self.max_daily_ai = 100  # Max AI questions per user per day
        logger.info(f"AI Question Generator ready - OpenAI: {'ENABLED' if self.openai_api_key else 'DISABLED'}")
    
    def _initialize_fallback_topics(self):
        """Fallback topics - FREE, no API cost."""
        return {
            "reasoning": {"questions": ["If A > B and B > C, which is true?", "Find next: 2, 6, 12, 20, ?", "Odd one: Square, Circle, Triangle"], "options": [["A > C", "A < C", "A = C"], ["42", "40", "44"], ["Square", "Circle", "All"]], "correct": [0, 0, 2]},
            "quant": {"questions": ["15% of 200?", "Square root of 144?", "2^8?"], "options": [["30", "25", "35"], ["12", "11", "13"], ["256", "128", "512"]], "correct": [0, 0, 0]},
            "english": {"questions": ["Synonym of Happy?", "Antonym of Ancient?", "He ___ to school"], "options": [["Joyful", "Sad", "Angry"], ["Modern", "Old", "Past"], ["goes", "go", "going"]], "correct": [0, 0, 0]},
            "gk": {"questions": ["PM of India?", "Capital of Australia?", "Largest ocean?"], "options": [["Modi", "Gandhi", "Nehru"], ["Canberra", "Sydney", "Perth"], ["Pacific", "Atlantic", "Indian"]], "correct": [0, 0, 0]},
            "anatomy": {"questions": ["Collarbone bone?", "Largest organ?", "Heart chambers?"], "options": [["Clavicle", "Scapula", "Sternum"], ["Skin", "Liver", "Brain"], ["4", "2", "6"]], "correct": [0, 0, 0]},
            "pathology": {"questions": ["Most common cancer?", "Allergic reaction cells?", "Acute inflammation hallmark?"], "options": [["Lung", "Breast", "Colon"], ["Mast cells", "Neutrophils", "Macrophages"], ["Neutrophils", "Fibrosis", "Granuloma"]], "correct": [0, 0, 0]},
            "medicine": {"questions": ["First-line HTN?", "TB antibiotic?", "Normal glucose?"], "options": [["ACE inhibitors", "Beta blockers", "CCB"], ["Isoniazid", "Penicillin", "Tetracycline"], ["70-100", "100-150", "150-200"]], "correct": [0, 0, 0]},
            "surgery": {"questions": ["Common surgical emergency?", "Appendectomy incision?", "Post-op infection sign?"], "options": [["Appendicitis", "Hernia", "Cholecystitis"], ["McBurney", "Midline", "Kocher"], ["Fever", "Pain", "Redness"]], "correct": [0, 0, 0]},
            "nursing": {"questions": ["Normal heart rate?", "Dyspnea position?", "Wound care first?"], "options": [["60-100", "40-60", "100-120"], ["Fowler's", "Supine", "Prone"], ["Assess", "Clean", "Dress"]], "correct": [0, 0, 0]},
            "physiology": {"questions": ["Blood pH?", "Blood sugar hormone?", "Nervous system unit?"], "options": [["7.35-7.45", "7.0-7.2", "7.5-7.6"], ["Insulin", "Glucagon", "Cortisol"], ["Neuron", "Nephron", "Alveoli"]], "correct": [0, 0, 0]},
            "biochemistry": {"questions": ["Protein building block?", "Carb enzyme?", "Energy currency?"], "options": [["Amino acids", "Fatty acids", "Glucose"], ["Amylase", "Lipase", "Protease"], ["ATP", "ADP", "AMP"]], "correct": [0, 0, 0]},
            "microbiology": {"questions": ["TB organism?", "UTI common cause?", "AIDS virus?"], "options": [["Mycobacterium", "Streptococcus", "Staph"], ["E. coli", "Klebsiella", "Pseudomonas"], ["HIV", "HPV", "HBV"]], "correct": [0, 0, 0]},
            "pharmacology": {"questions": ["Pain relief drug?", "Heparin antidote?", "Penicillin class?"], "options": [["Paracetamol", "Insulin", "Warfarin"], ["Protamine", "Vitamin K", "FFP"], ["Beta-lactams", "Macrolides", "Tetracyclines"]], "correct": [0, 0, 0]},
            "pediatrics": {"questions": ["Normal birth weight?", "Walking age?", "Birth vaccine?"], "options": [["2.5-3.5 kg", "1.5-2.5 kg", "3.5-4.5 kg"], ["12 months", "6 months", "18 months"], ["BCG", "MMR", "Polio"]], "correct": [0, 0, 0]},
            "psychiatry": {"questions": ["Common mental disorder?", "Depression neurotransmitter?", "CBT stands for?"], "options": [["Anxiety", "Depression", "Bipolar"], ["Serotonin", "Dopamine", "GABA"], ["Cognitive Behavioral", "Clinical", "Central"]], "correct": [0, 0, 0]},
            "obg": {"questions": ["Pregnancy duration?", "Pregnancy test hormone?", "PPH common cause?"], "options": [["40 weeks", "36 weeks", "38 weeks"], ["hCG", "FSH", "LH"], ["Uterine atony", "Previa", "Abruption"]], "correct": [0, 0, 0]},
            "dental": {"questions": ["Wisdom tooth?", "Hardest substance?", "Adult teeth count?"], "options": [["Third molar", "First molar", "Premolar"], ["Enamel", "Dentin", "Bone"], ["32", "28", "30"]], "correct": [0, 0, 0]},
            "clinical": {"questions": ["Normal BP?", "Diabetes test?", "Fever common cause?"], "options": [["120/80", "140/90", "100/60"], ["Fasting glucose", "Lipid", "CBC"], ["Infection", "Dehydration", "Stress"]], "correct": [0, 0, 0]},
            "pm fundamentals": {"questions": ["First PM phase?", "WBS?", "Triple constraint?"], "options": [["Initiation", "Planning", "Execution"], ["Work Breakdown", "Work Budget", "Weekly"], ["Scope Time Cost", "Quality", "People"]], "correct": [0, 0, 0]},
            "agile": {"questions": ["Agile is?", "Sprint duration?", "Scrum master role?"], "options": [["Iterative", "Waterfall", "Random"], ["2-4 weeks", "6 months", "1 year"], ["Facilitator", "Manager", "Boss"]], "correct": [0, 0, 0]},
            "scrum": {"questions": ["Scrum team size?", "Daily standup?", "Product backlog?"], "options": [["5-9", "20-30", "50+"], ["15 min", "1 hour", "2 hours"], ["Ordered list", "Random", "No list"]], "correct": [0, 0, 0]},
            "architecture": {"questions": ["Cloud architecture?", "Scalability?", "High availability?"], "options": [["Design", "Building", "Hardware"], ["Growth", "Reduction", "Fixed"], ["Always on", "Sometimes", "Never"]], "correct": [0, 0, 0]},
            "security": {"questions": ["Encryption?", "Firewall?", "Authentication?"], "options": [["Encoding", "Deleting", "Sharing"], ["Security", "Hardware", "Bug"], ["Identity", "Access", "Denial"]], "correct": [0, 0, 0]},
            "development": {"questions": ["SDLC?", "Agile dev?", "CI/CD?"], "options": [["Lifecycle", "Random", "No process"], ["Iterative", "Waterfall", "No method"], ["Continuous", "One-time", "Manual"]], "correct": [0, 0, 0]},
            "cloud": {"questions": ["Cloud computing?", "IaaS?", "SaaS?"], "options": [["On-demand", "Local only", "Hardware"], ["Infrastructure", "Platform", "Software"], ["Software", "Infrastructure", "Platform"]], "correct": [0, 0, 0]},
            "k8s": {"questions": ["Kubernetes?", "Pod?", "Node?"], "options": [["Orchestration", "Database", "Language"], ["Smallest unit", "Largest", "None"], ["Machine", "Container", "App"]], "correct": [0, 0, 0]},
            "networking": {"questions": ["TCP/IP?", "DNS?", "HTTP?"], "options": [["Protocol", "Hardware", "Language"], ["Name resolution", "Storage", "Compute"], ["Web protocol", "Database", "Security"]], "correct": [0, 0, 0]},
            "linux": {"questions": ["Linux?", "Shell?", "chmod?"], "options": [["OS", "Hardware", "App"], ["Command interface", "GUI", "Database"], ["Permissions", "Delete", "Copy"]], "correct": [0, 0, 0]},
            "testing": {"questions": ["Unit testing?", "Integration testing?", "Regression?"], "options": [["Individual", "System", "None"], ["Combined", "Single", "Random"], ["Re-test", "Skip", "New only"]], "correct": [0, 0, 0]},
            "crm": {"questions": ["CRM?", "Salesforce?", "Lead management?"], "options": [["Customer management", "Database", "OS"], ["CRM platform", "OS", "Language"], ["Track leads", "Ignore", "Delete"]], "correct": [0, 0, 0]},
            "automation": {"questions": ["Automation?", "RPA?", "CI/CD pipeline?"], "options": [["Reduce manual", "Increase", "No change"], ["Robotic", "Manual", "None"], ["Automated", "Manual", "Random"]], "correct": [0, 0, 0]},
            "ethics": {"questions": ["Ethics?", "Integrity?", "Transparency?"], "options": [["Moral", "Legal", "Policy"], ["Honesty", "Dishonesty", "Secrecy"], ["Openness", "Secrecy", "Hidden"]], "correct": [0, 0, 0]},
            "economics": {"questions": ["Supply/demand?", "Inflation?", "GDP?"], "options": [["Market", "Govt", "Random"], ["Price up", "Down", "Stable"], ["Gross Domestic", "General", "None"]], "correct": [0, 0, 0]},
            "fra": {"questions": ["Balance sheet?", "Income statement?", "Cash flow?"], "options": [["Position", "Profit", "Tax"], ["Revenue", "Assets", "Equity"], ["Movement", "Profit", "Sales"]], "correct": [0, 0, 0]},
            "audit": {"questions": ["Audit?", "Internal audit?", "External audit?"], "options": [["Review", "Ignore", "Skip"], ["Internal", "External only", "None"], ["Independent", "Internal", "None"]], "correct": [0, 0, 0]},
            "tax": {"questions": ["Tax?", "Income tax?", "GST?"], "options": [["Levy", "Gift", "Loan"], ["Earnings", "Sales", "Property"], ["Goods/services", "Income", "Property"]], "correct": [0, 0, 0]},
            "governance": {"questions": ["Governance?", "Compliance?", "Board role?"], "options": [["Framework", "Random", "None"], ["Following", "Breaking", "Ignoring"], ["Oversight", "Operations", "Marketing"]], "correct": [0, 0, 0]},
            "finance": {"questions": ["Finance?", "ROI?", "Budgeting?"], "options": [["Money management", "Random", "None"], ["Return", "Cost", "Tax"], ["Planning", "Random", "No plan"]], "correct": [0, 0, 0]},
            "strategy": {"questions": ["Strategy?", "SWOT?", "Porter's five?"], "options": [["Plan", "Random", "None"], ["Strengths", "Weaknesses only", "None"], ["Competitive", "Random", "None"]], "correct": [0, 0, 0]},
            "reading": {"questions": ["Skimming?", "Scanning?", "Inference?"], "options": [["Quick", "Slow", "None"], ["Specific", "All", "None"], ["Conclusion", "Copy", "Ignore"]], "correct": [0, 0, 0]},
            "writing": {"questions": ["Essay?", "Thesis?", "Coherence?"], "options": [["Structured", "Random", "List"], ["Argument", "Example", "Title"], ["Flow", "Random", "Repetition"]], "correct": [0, 0, 0]},
            "listening": {"questions": ["Active listening?", "Paraphrasing?", "Note-taking?"], "options": [["Focused", "Passive", "Ignoring"], ["Restating", "Copying", "Translating"], ["Key points", "All", "None"]], "correct": [0, 0, 0]},
            "speaking": {"questions": ["Pronunciation?", "Fluency?", "Intonation?"], "options": [["Sound", "Spelling", "Writing"], ["Smooth", "Fast", "Slow"], ["Pitch", "Volume", "Speed"]], "correct": [0, 0, 0]},
            "varc": {"questions": ["Reading comp?", "Para jumble?", "Summary?"], "options": [["Understanding", "Fast", "Skip"], ["Arrange", "Write", "Delete"], ["Condense", "Expand", "Repeat"]], "correct": [0, 0, 0]},
            "dilr": {"questions": ["Data interpretation?", "Logical reasoning?", "Pie chart?"], "options": [["Analyze", "Collect", "Delete"], ["Conclude", "Memorize", "Guess"], ["Circular", "Linear", "Square"]], "correct": [0, 0, 0]},
            "teaching": {"questions": ["Teaching aptitude?", "Pedagogy?", "Assessment?"], "options": [["Skill", "Random", "None"], ["Method", "Random", "None"], ["Evaluation", "Random", "None"]], "correct": [0, 0, 0]},
            "research": {"questions": ["Research?", "Hypothesis?", "Methodology?"], "options": [["Investigation", "Random", "None"], ["Prediction", "Random", "None"], ["Method", "Random", "None"]], "correct": [0, 0, 0]},
            "science": {"questions": ["Scientific method?", "Experiment?", "Theory?"], "options": [["Systematic", "Random", "None"], ["Test", "Random", "None"], ["Explanation", "Random", "None"]], "correct": [0, 0, 0]},
            "numerical": {"questions": ["15% of 200?", "Square root of 144?", "2^8?"], "options": [["30", "25", "35"], ["12", "11", "13"], ["256", "128", "512"]], "correct": [0, 0, 0]},
            "verbal": {"questions": ["Verbal reasoning?", "Analogy?", "Antonym?"], "options": [["Logic", "Random", "None"], ["Similar", "Different", "None"], ["Opposite", "Same", "None"]], "correct": [0, 0, 0]},
            "physics": {"questions": ["Newton's first law?", "Unit of force?", "Speed of light?"], "options": [["Inertia", "Acceleration", "Action"], ["Newton", "Joule", "Watt"], ["3x10^8", "3x10^6", "3x10^10"]], "correct": [0, 0, 0]},
            "chemistry": {"questions": ["Carbon atomic number?", "Water formula?", "pH of water?"], "options": [["6", "12", "8"], ["H2O", "CO2", "O2"], ["7", "0", "14"]], "correct": [0, 0, 0]},
            "math": {"questions": ["15% of 200?", "Square root of 144?", "2^8?"], "options": [["30", "25", "35"], ["12", "11", "13"], ["256", "128", "512"]], "correct": [0, 0, 0]},
            "aptitude": {"questions": ["Train 300km 5hrs speed?", "25% of 80?", "5 workers 10 days?"], "options": [["60 km/h", "50", "55"], ["20", "25", "30"], ["5 days", "10", "15"]], "correct": [0, 0, 0]},
            "technical": {"questions": ["API?", "Database?", "Algorithm?"], "options": [["Interface", "Hardware", "Bug"], ["Data storage", "Editor", "Browser"], ["Step-by-step", "Random", "Data type"]], "correct": [0, 0, 0]}
        }
    
    def generate_questions(self, exam_id, topic, count=10, user_email=None):
        """Smart generation with caching and hybrid approach."""
        topic_lower = topic.lower().strip()
        cache_key = f"{exam_id}_{topic_lower}"
        
        # Check cache first (FREE)
        if cache_key in self.question_cache:
            cache_data = self.question_cache[cache_key]
            if datetime.now() - cache_data["timestamp"] < self.cache_ttl:
                cached_questions = cache_data["questions"]
                if len(cached_questions) >= count:
                    return random.sample(cached_questions, count)
        
        # Check daily AI usage limit
        if user_email:
            today = datetime.now().strftime("%Y-%m-%d")
            if user_email not in self.daily_ai_usage:
                self.daily_ai_usage[user_email] = {}
            if today not in self.daily_ai_usage[user_email]:
                self.daily_ai_usage[user_email][today] = 0
            
            ai_used = self.daily_ai_usage[user_email][today]
            can_use_ai = ai_used + count <= self.max_daily_ai
        else:
            can_use_ai = True
        
        # Use OpenAI for small batches (≤20) if within limit
        if self.openai_api_key and count <= 20 and can_use_ai:
            try:
                questions = self.generate_with_openai(exam_id, topic, count)
                if questions:
                    # Update usage
                    if user_email:
                        self.daily_ai_usage[user_email][today] += count
                    # Cache the questions
                    if cache_key not in self.question_cache:
                        self.question_cache[cache_key] = {"questions": [], "timestamp": datetime.now()}
                    self.question_cache[cache_key]["questions"].extend(questions)
                    return questions
            except Exception as e:
                logger.error(f"OpenAI failed, using fallback: {e}")
        
        # Fallback to predefined topics (FREE)
        return self._generate_fallback(exam_id, topic, count)
    
    def _generate_fallback(self, exam_id, topic, count=10):
        """Generate from fallback topics - FREE."""
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
        
        return questions
    
    def generate_with_openai(self, exam_id, topic, count=10):
        """Generate questions using OpenAI API."""
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
            
            import re
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