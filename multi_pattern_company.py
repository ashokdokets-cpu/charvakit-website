"""
Charvak Multi-Pattern Company System
Supports multiple patterns per company (TCS NQT, Digital, Innovator)
"""
import logging
import json
import os
from datetime import datetime

logger = logging.getLogger("charvakit.multi_pattern")

class MultiPatternCompany:
    def __init__(self):
        self.patterns = self._initialize_patterns()
        logger.info("Multi-Pattern Company System ready")
    
    def _initialize_patterns(self):
        """Initialize all company patterns."""
        return {
            "tcs": {
                "name": "TCS",
                "patterns": {
                    "nqt": {
                        "name": "NQT",
                        "difficulty": "Moderate",
                        "description": "National Qualifier Test - Standard fresher hiring",
                        "sections": [
                            {"name": "Foundation", "count": 25, "time": "75 min", "topics": ["Aptitude", "Logical", "Verbal"]},
                            {"name": "Advanced", "count": 10, "time": "25 min", "topics": ["Advanced Quant", "Advanced Logic"]},
                            {"name": "Coding", "count": 2, "time": "55 min", "topics": ["DSA", "Problem Solving"]}
                        ]
                    },
                    "digital": {
                        "name": "Digital",
                        "difficulty": "Hard",
                        "description": "TCS Digital - Higher package, advanced difficulty",
                        "sections": [
                            {"name": "Advanced Aptitude", "count": 20, "time": "60 min", "topics": ["Advanced Quant", "Logical", "Verbal"]},
                            {"name": "Advanced Coding", "count": 2, "time": "60 min", "topics": ["DSA", "Algorithms", "Dynamic Programming"]},
                            {"name": "Technical Interview", "count": 10, "time": "30 min", "topics": ["DSA", "DBMS", "OOPs", "Networks"]}
                        ]
                    },
                    "innovator": {
                        "name": "Innovator",
                        "difficulty": "Very Hard",
                        "description": "TCS Innovator - Premium package, toughest difficulty",
                        "sections": [
                            {"name": "Research Aptitude", "count": 20, "time": "60 min", "topics": ["Advanced Quant", "Critical Reasoning"]},
                            {"name": "Advanced Coding", "count": 3, "time": "90 min", "topics": ["DSA", "Algorithms", "System Design"]},
                            {"name": "Innovation Challenge", "count": 5, "time": "45 min", "topics": ["Problem Solving", "Design Thinking"]}
                        ]
                    }
                }
            },
            "infosys": {
                "name": "Infosys",
                "patterns": {
                    "inftyq": {
                        "name": "InfyTQ",
                        "difficulty": "Moderate",
                        "sections": [
                            {"name": "Aptitude", "count": 20, "time": "60 min", "topics": ["Quant", "Logical"]},
                            {"name": "Technical", "count": 15, "time": "30 min", "topics": ["DSA", "DBMS", "OOPs"]},
                            {"name": "Coding", "count": 3, "time": "90 min", "topics": ["DSA", "Algorithms"]}
                        ]
                    },
                    "hackwithinfy": {
                        "name": "HackWithInfy",
                        "difficulty": "Hard",
                        "sections": [
                            {"name": "Competitive Coding", "count": 3, "time": "180 min", "topics": ["DSA", "Algorithms", "Dynamic Programming"]}
                        ]
                    }
                }
            },
            "cognizant": {
                "name": "Cognizant",
                "patterns": {
                    "genc": {
                        "name": "GenC",
                        "difficulty": "Moderate",
                        "sections": [
                            {"name": "Aptitude", "count": 20, "time": "60 min", "topics": ["Quantitative", "Analytical", "Verbal"]},
                            {"name": "Communication", "count": 10, "time": "20 min", "topics": ["Speaking", "Grammar"]},
                            {"name": "Programming", "count": 5, "time": "45 min", "topics": ["SQL", "Debugging"]}
                        ]
                    },
                    "genc_elevate": {
                        "name": "GenC Elevate",
                        "difficulty": "Hard",
                        "sections": [
                            {"name": "Advanced Aptitude", "count": 25, "time": "60 min", "topics": ["Advanced Quant", "Logical"]},
                            {"name": "Advanced Programming", "count": 5, "time": "60 min", "topics": ["SQL", "DSA"]},
                            {"name": "Coding", "count": 2, "time": "60 min", "topics": ["DSA", "Algorithms"]}
                        ]
                    },
                    "genc_pro": {
                        "name": "GenC Pro",
                        "difficulty": "Very Hard",
                        "sections": [
                            {"name": "Expert Aptitude", "count": 20, "time": "60 min", "topics": ["Advanced Quant", "Critical Reasoning"]},
                            {"name": "System Design", "count": 5, "time": "45 min", "topics": ["System Design", "Architecture"]},
                            {"name": "Advanced Coding", "count": 3, "time": "90 min", "topics": ["DSA", "Algorithms"]}
                        ]
                    }
                }
            },
            "wipro": {
                "name": "Wipro",
                "patterns": {
                    "elite_nth": {
                        "name": "Elite NTH",
                        "difficulty": "Moderate",
                        "sections": [
                            {"name": "Aptitude", "count": 20, "time": "48 min", "topics": ["Logical", "Quant"]},
                            {"name": "Communication", "count": 2, "time": "20 min", "topics": ["Essay", "Email"]},
                            {"name": "Coding", "count": 2, "time": "45 min", "topics": ["Basic", "Intermediate"]}
                        ]
                    },
                    "turbo": {
                        "name": "Turbo",
                        "difficulty": "Hard",
                        "sections": [
                            {"name": "Advanced Aptitude", "count": 25, "time": "60 min", "topics": ["Advanced Quant", "Logical"]},
                            {"name": "Advanced Coding", "count": 3, "time": "90 min", "topics": ["DSA", "Algorithms"]}
                        ]
                    }
                }
            },
            "accenture": {
                "name": "Accenture",
                "patterns": {
                    "ase": {
                        "name": "ASE",
                        "difficulty": "Moderate",
                        "sections": [
                            {"name": "Cognitive", "count": 25, "time": "60 min", "topics": ["Aptitude", "Logical"]},
                            {"name": "Technical", "count": 15, "time": "30 min", "topics": ["CS Fundamentals"]},
                            {"name": "Communication", "count": 10, "time": "20 min", "topics": ["Grammar"]}
                        ]
                    },
                    "advanced_ase": {
                        "name": "Advanced ASE",
                        "difficulty": "Hard",
                        "sections": [
                            {"name": "Advanced Cognitive", "count": 25, "time": "60 min", "topics": ["Advanced Quant", "Logical"]},
                            {"name": "Advanced Technical", "count": 20, "time": "30 min", "topics": ["DSA", "DBMS"]},
                            {"name": "Coding", "count": 2, "time": "45 min", "topics": ["DSA"]}
                        ]
                    }
                }
            }
        }
    
    def get_company_patterns(self, company_id):
        """Get all patterns for a company."""
        company = self.patterns.get(company_id)
        if not company:
            return {"status": "error", "message": "Company not found"}
        
        patterns = []
        for pattern_id, pattern in company["patterns"].items():
            patterns.append({
                "id": pattern_id,
                "name": pattern["name"],
                "difficulty": pattern["difficulty"],
                "description": pattern.get("description", ""),
                "total_questions": sum(s["count"] for s in pattern["sections"])
            })
        
        return {"status": "success", "company": company["name"], "patterns": patterns}
    
    def start_pattern_mock(self, email, company_id, pattern_id):
        """Start mock drive for a specific pattern."""
        company = self.patterns.get(company_id)
        if not company:
            return {"status": "error", "message": "Company not found"}
        
        pattern = company["patterns"].get(pattern_id)
        if not pattern:
            return {"status": "error", "message": "Pattern not found"}
        
        session_id = f"MOCK-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return {
            "status": "success",
            "session_id": session_id,
            "company": company["name"],
            "pattern": pattern["name"],
            "difficulty": pattern["difficulty"],
            "description": pattern.get("description", ""),
            "sections": pattern["sections"],
            "total_questions": sum(s["count"] for s in pattern["sections"])
        }

multi_pattern = MultiPatternCompany()
