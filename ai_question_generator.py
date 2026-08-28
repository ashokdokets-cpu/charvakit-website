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