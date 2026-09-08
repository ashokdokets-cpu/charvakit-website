with open('multi_pattern_company.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the end of patterns dict and add all remaining companies
old_end = '''            "accenture": {
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
        }'''

new_end = '''            "accenture": {
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
            },
            "capgemini": {
                "name": "Capgemini",
                "patterns": {
                    "exceller": {
                        "name": "Exceller",
                        "difficulty": "Moderate",
                        "sections": [
                            {"name": "Aptitude", "count": 20, "time": "60 min", "topics": ["Quant", "Logical"]},
                            {"name": "Technical", "count": 15, "time": "30 min", "topics": ["DSA", "DBMS"]},
                            {"name": "Coding", "count": 2, "time": "45 min", "topics": ["Basic"]}
                        ]
                    },
                    "pro": {
                        "name": "Pro",
                        "difficulty": "Hard",
                        "sections": [
                            {"name": "Advanced Aptitude", "count": 25, "time": "60 min", "topics": ["Advanced Quant", "Logical"]},
                            {"name": "Advanced Technical", "count": 15, "time": "30 min", "topics": ["DSA", "Algorithms"]},
                            {"name": "Coding", "count": 3, "time": "60 min", "topics": ["DSA", "Problem Solving"]}
                        ]
                    }
                }
            },
            "ibm": {
                "name": "IBM",
                "patterns": {
                    "associate": {
                        "name": "Associate",
                        "difficulty": "Moderate",
                        "sections": [
                            {"name": "Aptitude", "count": 20, "time": "60 min", "topics": ["Quant", "Logical"]},
                            {"name": "Technical", "count": 10, "time": "30 min", "topics": ["DSA", "OOPs"]},
                            {"name": "Coding", "count": 2, "time": "45 min", "topics": ["Basic", "DSA"]}
                        ]
                    },
                    "developer": {
                        "name": "Developer",
                        "difficulty": "Hard",
                        "sections": [
                            {"name": "Advanced Aptitude", "count": 20, "time": "60 min", "topics": ["Advanced Quant", "Logical"]},
                            {"name": "Advanced Technical", "count": 15, "time": "30 min", "topics": ["DSA", "Algorithms", "System Design"]},
                            {"name": "Coding", "count": 3, "time": "60 min", "topics": ["DSA", "Algorithms"]}
                        ]
                    }
                }
            },
            "hcl": {
                "name": "HCLTech",
                "patterns": {
                    "techbee": {
                        "name": "TechBee",
                        "difficulty": "Moderate",
                        "sections": [
                            {"name": "Aptitude", "count": 20, "time": "60 min", "topics": ["Quant", "Verbal"]},
                            {"name": "Technical", "count": 15, "time": "30 min", "topics": ["CS Fundamentals"]},
                            {"name": "Coding", "count": 2, "time": "30 min", "topics": ["Basic"]}
                        ]
                    },
                    "tss": {
                        "name": "TSS",
                        "difficulty": "Hard",
                        "sections": [
                            {"name": "Advanced Aptitude", "count": 20, "time": "60 min", "topics": ["Advanced Quant", "Logical"]},
                            {"name": "Advanced Technical", "count": 15, "time": "30 min", "topics": ["DSA", "DBMS"]},
                            {"name": "Coding", "count": 2, "time": "45 min", "topics": ["DSA"]}
                        ]
                    }
                }
            },
            "tech_mahindra": {
                "name": "Tech Mahindra",
                "patterns": {
                    "talent": {
                        "name": "Talent Acquisition",
                        "difficulty": "Moderate",
                        "sections": [
                            {"name": "Aptitude", "count": 20, "time": "60 min", "topics": ["Quant", "Logical"]},
                            {"name": "Technical", "count": 10, "time": "30 min", "topics": ["DSA"]},
                            {"name": "Coding", "count": 2, "time": "45 min", "topics": ["Basic"]}
                        ]
                    },
                    "digital": {
                        "name": "Digital",
                        "difficulty": "Hard",
                        "sections": [
                            {"name": "Advanced Aptitude", "count": 20, "time": "60 min", "topics": ["Advanced Quant", "Logical"]},
                            {"name": "Advanced Technical", "count": 15, "time": "30 min", "topics": ["DSA", "Algorithms"]},
                            {"name": "Coding", "count": 3, "time": "60 min", "topics": ["DSA"]}
                        ]
                    }
                }
            },
            "lti": {
                "name": "LTI",
                "patterns": {
                    "get": {
                        "name": "Graduate Engineer Trainee",
                        "difficulty": "Moderate",
                        "sections": [
                            {"name": "Aptitude", "count": 20, "time": "60 min", "topics": ["Quant", "Logical"]},
                            {"name": "Technical", "count": 10, "time": "30 min", "topics": ["DSA"]},
                            {"name": "Coding", "count": 2, "time": "45 min", "topics": ["Basic"]}
                        ]
                    },
                    "digital": {
                        "name": "Digital",
                        "difficulty": "Hard",
                        "sections": [
                            {"name": "Advanced Aptitude", "count": 20, "time": "60 min", "topics": ["Advanced Quant", "Logical"]},
                            {"name": "Advanced Technical", "count": 15, "time": "30 min", "topics": ["DSA", "Algorithms"]},
                            {"name": "Coding", "count": 2, "time": "60 min", "topics": ["DSA"]}
                        ]
                    }
                }
            },
            "mindtree": {
                "name": "Mindtree",
                "patterns": {
                    "graduate": {
                        "name": "Graduate Engineer",
                        "difficulty": "Moderate",
                        "sections": [
                            {"name": "Aptitude", "count": 20, "time": "60 min", "topics": ["Quant", "Logical"]},
                            {"name": "Technical", "count": 10, "time": "30 min", "topics": ["DSA"]},
                            {"name": "Coding", "count": 2, "time": "45 min", "topics": ["Basic"]}
                        ]
                    },
                    "specialist": {
                        "name": "Specialist",
                        "difficulty": "Hard",
                        "sections": [
                            {"name": "Advanced Aptitude", "count": 20, "time": "60 min", "topics": ["Advanced Quant", "Logical"]},
                            {"name": "Advanced Technical", "count": 15, "time": "30 min", "topics": ["DSA", "Algorithms"]},
                            {"name": "Coding", "count": 3, "time": "60 min", "topics": ["DSA"]}
                        ]
                    }
                }
            },
            "deloitte": {
                "name": "Deloitte",
                "patterns": {
                    "analyst": {
                        "name": "Analyst",
                        "difficulty": "Moderate",
                        "sections": [
                            {"name": "Aptitude", "count": 25, "time": "60 min", "topics": ["Quant", "Logical", "Verbal"]},
                            {"name": "Technical", "count": 10, "time": "30 min", "topics": ["CS Fundamentals"]},
                            {"name": "Communication", "count": 5, "time": "15 min", "topics": ["Grammar"]}
                        ]
                    },
                    "consultant": {
                        "name": "Consultant",
                        "difficulty": "Hard",
                        "sections": [
                            {"name": "Advanced Aptitude", "count": 25, "time": "60 min", "topics": ["Advanced Quant", "Critical Reasoning"]},
                            {"name": "Technical", "count": 15, "time": "30 min", "topics": ["DSA", "DBMS"]},
                            {"name": "Case Study", "count": 5, "time": "30 min", "topics": ["Problem Solving"]}
                        ]
                    }
                }
            },
            "kpmg": {
                "name": "KPMG",
                "patterns": {
                    "analyst": {
                        "name": "Analyst",
                        "difficulty": "Moderate",
                        "sections": [
                            {"name": "Aptitude", "count": 25, "time": "60 min", "topics": ["Quant", "Logical", "Verbal"]},
                            {"name": "Technical", "count": 10, "time": "30 min", "topics": ["CS Fundamentals"]},
                            {"name": "Communication", "count": 5, "time": "15 min", "topics": ["Grammar"]}
                        ]
                    },
                    "advisory": {
                        "name": "Advisory",
                        "difficulty": "Hard",
                        "sections": [
                            {"name": "Advanced Aptitude", "count": 25, "time": "60 min", "topics": ["Advanced Quant", "Critical Reasoning"]},
                            {"name": "Technical", "count": 15, "time": "30 min", "topics": ["DSA", "DBMS"]}
                        ]
                    }
                }
            },
            "ey": {
                "name": "EY",
                "patterns": {
                    "associate": {
                        "name": "Associate",
                        "difficulty": "Moderate",
                        "sections": [
                            {"name": "Aptitude", "count": 25, "time": "60 min", "topics": ["Quant", "Logical", "Verbal"]},
                            {"name": "Technical", "count": 10, "time": "30 min", "topics": ["CS Fundamentals"]},
                            {"name": "Communication", "count": 5, "time": "15 min", "topics": ["Grammar"]}
                        ]
                    },
                    "analyst": {
                        "name": "Analyst",
                        "difficulty": "Hard",
                        "sections": [
                            {"name": "Advanced Aptitude", "count": 25, "time": "60 min", "topics": ["Advanced Quant", "Critical Reasoning"]},
                            {"name": "Technical", "count": 15, "time": "30 min", "topics": ["DSA", "DBMS"]}
                        ]
                    }
                }
            },
            "pwc": {
                "name": "PwC",
                "patterns": {
                    "associate": {
                        "name": "Associate",
                        "difficulty": "Moderate",
                        "sections": [
                            {"name": "Aptitude", "count": 25, "time": "60 min", "topics": ["Quant", "Logical", "Verbal"]},
                            {"name": "Technical", "count": 10, "time": "30 min", "topics": ["CS Fundamentals"]},
                            {"name": "Communication", "count": 5, "time": "15 min", "topics": ["Grammar"]}
                        ]
                    },
                    "advisory": {
                        "name": "Advisory",
                        "difficulty": "Hard",
                        "sections": [
                            {"name": "Advanced Aptitude", "count": 25, "time": "60 min", "topics": ["Advanced Quant", "Critical Reasoning"]},
                            {"name": "Technical", "count": 15, "time": "30 min", "topics": ["DSA", "DBMS"]}
                        ]
                    }
                }
            },
            "amazon": {
                "name": "Amazon",
                "patterns": {
                    "sde": {
                        "name": "SDE",
                        "difficulty": "Hard",
                        "sections": [
                            {"name": "Aptitude", "count": 20, "time": "60 min", "topics": ["Quant", "Logical"]},
                            {"name": "Technical", "count": 15, "time": "30 min", "topics": ["DSA", "Algorithms"]},
                            {"name": "Coding", "count": 2, "time": "60 min", "topics": ["DSA", "Problem Solving"]}
                        ]
                    },
                    "sde_2": {
                        "name": "SDE II",
                        "difficulty": "Very Hard",
                        "sections": [
                            {"name": "System Design", "count": 5, "time": "45 min", "topics": ["System Design", "Architecture"]},
                            {"name": "Advanced Coding", "count": 3, "time": "90 min", "topics": ["DSA", "Algorithms", "Dynamic Programming"]}
                        ]
                    }
                }
            },
            "google": {
                "name": "Google",
                "patterns": {
                    "swe": {
                        "name": "SWE",
                        "difficulty": "Very Hard",
                        "sections": [
                            {"name": "Aptitude", "count": 20, "time": "60 min", "topics": ["Quant", "Logical"]},
                            {"name": "Technical", "count": 15, "time": "30 min", "topics": ["DSA", "Algorithms"]},
                            {"name": "Coding", "count": 2, "time": "60 min", "topics": ["DSA", "Problem Solving"]}
                        ]
                    },
                    "swe_2": {
                        "name": "SWE II",
                        "difficulty": "Very Hard",
                        "sections": [
                            {"name": "System Design", "count": 5, "time": "45 min", "topics": ["System Design", "Architecture"]},
                            {"name": "Advanced Coding", "count": 3, "time": "90 min", "topics": ["DSA", "Algorithms"]}
                        ]
                    }
                }
            },
            "microsoft": {
                "name": "Microsoft",
                "patterns": {
                    "swe": {
                        "name": "SWE",
                        "difficulty": "Hard",
                        "sections": [
                            {"name": "Aptitude", "count": 20, "time": "60 min", "topics": ["Quant", "Logical"]},
                            {"name": "Technical", "count": 15, "time": "30 min", "topics": ["DSA", "Algorithms"]},
                            {"name": "Coding", "count": 2, "time": "60 min", "topics": ["DSA", "Problem Solving"]}
                        ]
                    },
                    "swe_2": {
                        "name": "SWE II",
                        "difficulty": "Very Hard",
                        "sections": [
                            {"name": "System Design", "count": 5, "time": "45 min", "topics": ["System Design", "Architecture"]},
                            {"name": "Advanced Coding", "count": 3, "time": "90 min", "topics": ["DSA", "Algorithms"]}
                        ]
                    }
                }
            }
        }'''

if old_end in content:
    content = content.replace(old_end, new_end)
    with open('multi_pattern_company.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ ALL 18 companies now have multi-pattern support!')
else:
    print('Pattern not found')
