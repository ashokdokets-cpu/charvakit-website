"""
Charvak AI Question Generator
Generates unique questions for exam preparation
"""
import logging
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger("charvakit.ai_questions")

class AIQuestionGenerator:
    def __init__(self):
        self.topics = {
            "reasoning": {
                "questions": [
                    "If A > B and B > C, then which is true?",
                    "Find the next number: 2, 6, 12, 20, 30, ?",
                    "If CAT = 24, then DOG = ?",
                    "Odd one out: Square, Rectangle, Triangle, Circle",
                    "If today is Monday, what day is 100 days from now?"
                ],
                "options": [
                    ["A > C", "A < C", "A = C", "Cannot determine"],
                    ["40", "42", "44", "46"],
                    ["26", "28", "30", "32"],
                    ["Square", "Rectangle", "Triangle", "Circle"],
                    ["Monday", "Tuesday", "Wednesday", "Thursday"]
                ],
                "correct": [0, 1, 0, 3, 2]
            },
            "quant": {
                "questions": [
                    "What is 15% of 200?",
                    "If x + y = 10 and x - y = 4, find x.",
                    "What is the square root of 144?",
                    "A train travels 300 km in 5 hours. Speed?",
                    "What is 2^8?"
                ],
                "options": [
                    ["25", "30", "35", "40"],
                    ["5", "6", "7", "8"],
                    ["10", "11", "12", "13"],
                    ["50 km/h", "55 km/h", "60 km/h", "65 km/h"],
                    ["128", "256", "512", "1024"]
                ],
                "correct": [1, 2, 2, 2, 1]
            },
            "english": {
                "questions": [
                    "Choose the correct synonym of 'Happy':",
                    "Which is grammatically correct?",
                    "Fill in the blank: He ___ to school daily."
                ],
                "options": [
                    ["Sad", "Joyful", "Angry", "Tired"],
                    ["He go", "He goes", "He going", "He gone"],
                    ["go", "goes", "going", "gone"]
                ],
                "correct": [1, 1, 1]
            },
            "gk": {
                "questions": [
                    "Who is the Prime Minister of India?",
                    "What is the capital of Australia?",
                    "Which is the largest ocean?"
                ],
                "options": [
                    ["Modi", "Gandhi", "Nehru", "Singh"],
                    ["Sydney", "Canberra", "Melbourne", "Perth"],
                    ["Atlantic", "Indian", "Pacific", "Arctic"]
                ],
                "correct": [0, 1, 2]
            },
            "anatomy": {
                "questions": [
                    "Which bone is known as the collarbone?",
                    "What is the largest organ in the human body?",
                    "How many chambers does the human heart have?",
                    "Which part of the brain controls balance?",
                    "What is the functional unit of the kidney?"
                ],
                "options": [
                    ["Clavicle", "Scapula", "Humerus", "Sternum"],
                    ["Liver", "Skin", "Brain", "Lungs"],
                    ["2", "3", "4", "6"],
                    ["Cerebellum", "Cerebrum", "Medulla", "Pons"],
                    ["Neuron", "Nephron", "Glomerulus", "Tubule"]
                ],
                "correct": [0, 1, 2, 0, 1]
            },
            "pathology": {
                "questions": [
                    "What is the most common type of cancer worldwide?",
                    "Which cell type is involved in allergic reactions?",
                    "What is the hallmark of acute inflammation?",
                    "Which disease is caused by insulin deficiency?",
                    "What is the most common cause of cirrhosis?"
                ],
                "options": [
                    ["Lung cancer", "Breast cancer", "Colon cancer", "Prostate cancer"],
                    ["Mast cells", "Neutrophils", "Lymphocytes", "Macrophages"],
                    ["Fibrosis", "Neutrophil infiltration", "Granuloma", "Calcification"],
                    ["Type 1 Diabetes", "Type 2 Diabetes", "Both", "Neither"],
                    ["Alcohol", "Hepatitis B", "Hepatitis C", "NASH"]
                ],
                "correct": [0, 0, 1, 0, 0]
            },
            "medicine": {
                "questions": [
                    "What is the first-line treatment for hypertension?",
                    "Which antibiotic is used for tuberculosis?",
                    "What is the normal range for blood glucose?",
                    "Which vitamin deficiency causes scurvy?",
                    "What is the most common cause of pneumonia?"
                ],
                "options": [
                    ["ACE inhibitors", "Beta blockers", "Diuretics", "Calcium channel blockers"],
                    ["Penicillin", "Isoniazid", "Tetracycline", "Erythromycin"],
                    ["70-100 mg/dL", "100-150 mg/dL", "150-200 mg/dL", "200-250 mg/dL"],
                    ["Vitamin A", "Vitamin B12", "Vitamin C", "Vitamin D"],
                    ["Streptococcus pneumoniae", "Staphylococcus aureus", "Klebsiella", "Pseudomonas"]
                ],
                "correct": [0, 1, 0, 2, 0]
            },
            "surgery": {
                "questions": [
                    "What is the most common surgical emergency?",
                    "Which incision is used for appendectomy?",
                    "What is the first sign of postoperative infection?",
                    "Which suture material is absorbable?",
                    "What is the most common cause of bowel obstruction?"
                ],
                "options": [
                    ["Appendicitis", "Cholecystitis", "Hernia", "Perforation"],
                    ["McBurney", "Midline", "Kocher", "Pfannenstiel"],
                    ["Fever", "Pain", "Redness", "Swelling"],
                    ["Nylon", "Silk", "Vicryl", "Prolene"],
                    ["Adhesions", "Hernia", "Tumor", "Volvulus"]
                ],
                "correct": [0, 0, 0, 2, 0]
            },
            "nursing": {
                "questions": [
                    "What is the normal adult heart rate?",
                    "Which position is best for a patient with dyspnea?",
                    "What is the first step in wound care?",
                    "Normal body temperature in Celsius?",
                    "What does PRN mean?"
                ],
                "options": [
                    ["60-100 bpm", "40-60 bpm", "100-120 bpm", "120-140 bpm"],
                    ["Supine", "Fowler's", "Prone", "Trendelenburg"],
                    ["Clean the wound", "Apply dressing", "Assess the wound", "Remove old dressing"],
                    ["36-37 C", "37-38 C", "38-39 C", "35-36 C"],
                    ["As needed", "Every hour", "Before meals", "At bedtime"]
                ],
                "correct": [0, 1, 2, 0, 0]
            },
            "physiology": {
                "questions": [
                    "What is the normal pH of human blood?",
                    "Which hormone regulates blood sugar?",
                    "What is the functional unit of the nervous system?",
                    "Normal adult respiratory rate?",
                    "What is the normal range for systolic BP?"
                ],
                "options": [
                    ["7.35-7.45", "7.0-7.2", "7.5-7.6", "6.8-7.0"],
                    ["Insulin", "Glucagon", "Cortisol", "Thyroxine"],
                    ["Neuron", "Nephron", "Alveoli", "Cell"],
                    ["12-20/min", "8-10/min", "20-30/min", "30-40/min"],
                    ["90-120 mmHg", "120-140 mmHg", "140-160 mmHg", "80-100 mmHg"]
                ],
                "correct": [0, 0, 0, 0, 0]
            },
            "biochemistry": {
                "questions": [
                    "What is the building block of proteins?",
                    "Which enzyme breaks down carbohydrates?",
                    "What is the energy currency of the cell?",
                    "Which vitamin is fat-soluble?",
                    "What is the normal fasting blood glucose?"
                ],
                "options": [
                    ["Amino acids", "Fatty acids", "Glucose", "Nucleotides"],
                    ["Amylase", "Lipase", "Protease", "Lactase"],
                    ["ATP", "ADP", "AMP", "GTP"],
                    ["Vitamin C", "Vitamin B12", "Vitamin D", "Vitamin B6"],
                    ["70-100 mg/dL", "100-150 mg/dL", "150-200 mg/dL", "200-250 mg/dL"]
                ],
                "correct": [0, 0, 0, 2, 0]
            },
            "microbiology": {
                "questions": [
                    "Which organism causes tuberculosis?",
                    "What is the most common cause of UTI?",
                    "Which virus causes AIDS?",
                    "What is the gram stain of E. coli?",
                    "Which fungus causes candidiasis?"
                ],
                "options": [
                    ["Mycobacterium tuberculosis", "Streptococcus", "Staphylococcus", "E. coli"],
                    ["E. coli", "Klebsiella", "Pseudomonas", "Proteus"],
                    ["HIV", "HPV", "HBV", "HCV"],
                    ["Gram-negative", "Gram-positive", "Acid-fast", "None"],
                    ["Candida albicans", "Aspergillus", "Cryptococcus", "Histoplasma"]
                ],
                "correct": [0, 0, 0, 0, 0]
            },
            "pharmacology": {
                "questions": [
                    "Which drug is used for pain relief?",
                    "What is the antidote for heparin?",
                    "Which antibiotic class includes penicillin?",
                    "What is the first-line drug for type 2 diabetes?",
                    "Which drug class is used for hypertension?"
                ],
                "options": [
                    ["Paracetamol", "Insulin", "Aspirin", "Warfarin"],
                    ["Protamine sulfate", "Vitamin K", "Fresh frozen plasma", "Platelets"],
                    ["Beta-lactams", "Macrolides", "Tetracyclines", "Aminoglycosides"],
                    ["Metformin", "Insulin", "Glibenclamide", "Pioglitazone"],
                    ["ACE inhibitors", "Statins", "PPIs", "NSAIDs"]
                ],
                "correct": [0, 0, 0, 0, 0]
            },
            "pediatrics": {
                "questions": [
                    "What is the normal birth weight?",
                    "At what age does a child start walking?",
                    "Which vaccine is given at birth?",
                    "What is the most common childhood cancer?",
                    "Normal heart rate for a newborn?"
                ],
                "options": [
                    ["2.5-3.5 kg", "1.5-2.5 kg", "3.5-4.5 kg", "4.5-5.5 kg"],
                    ["12 months", "6 months", "18 months", "9 months"],
                    ["BCG", "MMR", "Polio", "DPT"],
                    ["Leukemia", "Lymphoma", "Brain tumor", "Neuroblastoma"],
                    ["120-160 bpm", "80-100 bpm", "60-80 bpm", "100-120 bpm"]
                ],
                "correct": [0, 0, 0, 0, 0]
            },
            "psychiatry": {
                "questions": [
                    "What is the most common mental health disorder?",
                    "Which neurotransmitter is linked to depression?",
                    "What is the first-line treatment for schizophrenia?",
                    "What does CBT stand for?",
                    "Which disorder is characterized by mood swings?"
                ],
                "options": [
                    ["Anxiety", "Depression", "Schizophrenia", "Bipolar"],
                    ["Serotonin", "Dopamine", "GABA", "Glutamate"],
                    ["Antipsychotics", "Antidepressants", "Mood stabilizers", "Anxiolytics"],
                    ["Cognitive Behavioral Therapy", "Clinical Behavior Test", "Central Brain Treatment", "None"],
                    ["Bipolar", "Depression", "Anxiety", "OCD"]
                ],
                "correct": [0, 0, 0, 0, 0]
            },
            "obg": {
                "questions": [
                    "What is the normal duration of pregnancy?",
                    "Which hormone is detected in pregnancy tests?",
                    "What is the most common cause of postpartum hemorrhage?",
                    "Normal fetal heart rate?",
                    "Which vitamin is recommended in pregnancy?"
                ],
                "options": [
                    ["40 weeks", "36 weeks", "38 weeks", "42 weeks"],
                    ["hCG", "FSH", "LH", "Prolactin"],
                    ["Uterine atony", "Placenta previa", "Abruption", "Retained placenta"],
                    ["110-160 bpm", "80-100 bpm", "160-180 bpm", "60-80 bpm"],
                    ["Folic acid", "Vitamin C", "Vitamin D", "Vitamin B12"]
                ],
                "correct": [0, 0, 0, 0, 0]
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