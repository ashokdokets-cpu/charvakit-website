# calibrated_skills.py
# Session 105: The whitelist of skills Charvak can verifiably assess.
# Any JD containing skills outside this list gets flagged for partial
# assessment or decline (see jd_calibration.py).

CALIBRATED_SKILLS = {
    "languages": {
        "python": ["python", "py", "python3"],
        "javascript": ["javascript", "js", "ecmascript", "node", "node.js", "nodejs"],
        "typescript": ["typescript", "ts"],
        "java": ["java", "java8", "java11", "java17"],
        "cpp": ["c++", "cpp", "cplusplus"],
        "csharp": ["c#", "csharp", "dotnet-lang"],
        "go": ["go", "golang"],
        "sql": ["sql", "ansi-sql"],
        "html": ["html", "html5"],
        "css": ["css", "css3"],
    },
    "frameworks": {
        "react": ["react", "reactjs", "react.js"],
        "django": ["django"],
        "flask": ["flask"],
        "spring": ["spring", "spring-boot", "springboot"],
        "express": ["express", "expressjs"],
        "fastapi": ["fastapi"],
        "vue": ["vue", "vuejs", "vue.js"],
        "angular": ["angular", "angularjs"],
    },
    "cloud": {
        "aws-basics": ["aws", "amazon-web-services", "ec2", "s3", "lambda"],
        "azure-basics": ["azure", "microsoft-azure"],
        "gcp-basics": ["gcp", "google-cloud", "google-cloud-platform"],
        "docker": ["docker", "containers", "containerization"],
        "kubernetes-basics": ["kubernetes", "k8s"],
    },
    "data": {
        "pandas": ["pandas", "numpy"],
        "pyspark": ["pyspark", "spark", "apache-spark"],
        "sql-window": ["window-functions", "sql-window", "analytic-sql"],
        "sql-basics": ["joins", "aggregations", "group-by", "subqueries"],
        "data-structures": ["arrays", "linked-lists", "hashmaps", "trees", "graphs"],
    },
    "concepts": {
        "algorithms": ["algorithms", "sorting", "searching", "dynamic-programming", "recursion"],
        "oop": ["oop", "oops", "object-oriented", "inheritance", "polymorphism"],
        "rest-api": ["rest", "rest-api", "restful", "http-api"],
        "graphql": ["graphql"],
        "git": ["git", "version-control"],
        "testing": ["unit-testing", "integration-testing", "test-driven", "tdd"],
        "system-design-basics": ["system-design", "scalability", "caching", "load-balancing"],
        "microservices": ["microservices", "service-oriented"],
    },
    "behavioral": {
        "communication": ["communication", "written-communication", "presentation"],
        "leadership": ["leadership", "team-leadership", "mentoring", "coaching"],
        "problem-solving": ["problem-solving", "analytical-thinking", "critical-thinking"],
        "collaboration": ["teamwork", "collaboration", "cross-functional"],
        "stakeholder-management": ["stakeholder", "stakeholder-management"],
    },
}

# Flattened lookup: any alias -> canonical name
_CANONICAL = {}
for category, skills in CALIBRATED_SKILLS.items():
    for canonical, aliases in skills.items():
        for alias in aliases:
            _CANONICAL[alias.lower()] = canonical

ALL_CALIBRATED_SKILLS = set()
for category, skills in CALIBRATED_SKILLS.items():
    ALL_CALIBRATED_SKILLS.update(skills.keys())


def canonicalize(skill_name: str) -> str:
    """Return canonical skill name, or empty string if not calibrated."""
    if not skill_name:
        return ""
    return _CANONICAL.get(skill_name.strip().lower(), "")


def is_calibrated(skill_name: str) -> bool:
    """Check if a skill is in the calibrated whitelist."""
    return bool(canonicalize(skill_name))


def get_all_calibrated() -> list:
    """Return sorted list of all canonical skill names."""
    return sorted(ALL_CALIBRATED_SKILLS)