# skill_catalog.py
# Session 106: Comprehensive skill catalog (500+ skills).
# Organized by category with aliases, test types, and Judge0 language IDs.
#
# Loaded first by jd_calibration.is_calibrated() and skill_auto_calibrator.
# Skills NOT in this catalog trigger auto-calibration flow.

SKILL_CATALOG = {
    # ═══════════════════════════════════════════════════════════════
    # LANGUAGES (coding-testable)
    # ═══════════════════════════════════════════════════════════════
    "python": {"aliases": ["python", "py", "python3"], "category": "language", "test_type": "coding", "judge0_id": 71},
    "javascript": {"aliases": ["javascript", "js", "ecmascript", "vanilla-js"], "category": "language", "test_type": "coding", "judge0_id": 63},
    "typescript": {"aliases": ["typescript", "ts"], "category": "language", "test_type": "coding", "judge0_id": 74},
    "java": {"aliases": ["java", "j2ee", "java8", "java11", "java17", "java21"], "category": "language", "test_type": "coding", "judge0_id": 62},
    "cpp": {"aliases": ["c++", "cpp", "cplusplus"], "category": "language", "test_type": "coding", "judge0_id": 54},
    "csharp": {"aliases": ["c#", "csharp", ".net-lang"], "category": "language", "test_type": "coding", "judge0_id": 51},
    "go": {"aliases": ["go", "golang"], "category": "language", "test_type": "coding", "judge0_id": 60},
    "rust": {"aliases": ["rust", "rust-lang"], "category": "language", "test_type": "mcq", "judge0_id": None, "fallback_note": "Code execution not supported; MCQ-only"},
    "kotlin": {"aliases": ["kotlin"], "category": "language", "test_type": "coding", "judge0_id": 78},
    "swift": {"aliases": ["swift", "swift-lang"], "category": "language", "test_type": "coding", "judge0_id": 83},
    "ruby": {"aliases": ["ruby", "ruby-lang"], "category": "language", "test_type": "coding", "judge0_id": 72},
    "php": {"aliases": ["php"], "category": "language", "test_type": "coding", "judge0_id": 68},
    "scala": {"aliases": ["scala"], "category": "language", "test_type": "coding", "judge0_id": 81},
    "elixir": {"aliases": ["elixir"], "category": "language", "test_type": "mcq", "judge0_id": None, "fallback_note": "Code execution not supported; MCQ-only"},
    "haskell": {"aliases": ["haskell"], "category": "language", "test_type": "mcq", "judge0_id": None, "fallback_note": "Code execution not supported; MCQ-only"},
    "perl": {"aliases": ["perl"], "category": "language", "test_type": "coding", "judge0_id": 85},
    "bash": {"aliases": ["bash", "shell", "sh"], "category": "language", "test_type": "coding", "judge0_id": 46},
    "sql": {"aliases": ["sql", "ansi-sql"], "category": "language", "test_type": "sql", "judge0_id": 82},
    "html": {"aliases": ["html", "html5"], "category": "language", "test_type": "mcq", "judge0_id": None},
    "css": {"aliases": ["css", "css3"], "category": "language", "test_type": "mcq", "judge0_id": None},
    "r": {"aliases": ["r", "r-lang"], "category": "language", "test_type": "coding", "judge0_id": 80},
    "matlab": {"aliases": ["matlab"], "category": "language", "test_type": "mcq", "judge0_id": None},

    # ═══════════════════════════════════════════════════════════════
    # FRONTEND FRAMEWORKS
    # ═══════════════════════════════════════════════════════════════
    "react": {"aliases": ["react", "reactjs", "react.js"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "vue": {"aliases": ["vue", "vuejs", "vue.js", "vuejs3"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "angular": {"aliases": ["angular", "angularjs", "angular2+"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "svelte": {"aliases": ["svelte", "sveltekit"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "nextjs": {"aliases": ["next", "nextjs", "next.js"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "nuxt": {"aliases": ["nuxt", "nuxtjs", "nuxt.js"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "bootstrap": {"aliases": ["bootstrap", "bootstrap5"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "tailwind": {"aliases": ["tailwind", "tailwindcss"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "jquery": {"aliases": ["jquery"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "material-ui": {"aliases": ["material-ui", "mui"], "category": "framework", "test_type": "mcq", "judge0_id": None},

    # ═══════════════════════════════════════════════════════════════
    # BACKEND FRAMEWORKS
    # ═══════════════════════════════════════════════════════════════
    "django": {"aliases": ["django"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "flask": {"aliases": ["flask"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "fastapi": {"aliases": ["fastapi"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "spring": {"aliases": ["spring", "spring-boot", "springboot", "spring-mvc"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "express": {"aliases": ["express", "expressjs", "express.js"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "nestjs": {"aliases": ["nest", "nestjs", "nest.js"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "rails": {"aliases": ["rails", "ruby-on-rails", "ror"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "laravel": {"aliases": ["laravel"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "dotnet": {"aliases": [".net", "dotnet", "asp.net", "aspnet"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "gin": {"aliases": ["gin", "gin-gonic"], "category": "framework", "test_type": "mcq", "judge0_id": None},

    # ═══════════════════════════════════════════════════════════════
    # DATABASES & ORMs
    # ═══════════════════════════════════════════════════════════════
    "postgresql": {"aliases": ["postgres", "postgresql", "pg"], "category": "database", "test_type": "sql", "judge0_id": 82},
    "mysql": {"aliases": ["mysql", "mariadb"], "category": "database", "test_type": "sql", "judge0_id": 82},
    "sqlite": {"aliases": ["sqlite", "sqlite3"], "category": "database", "test_type": "sql", "judge0_id": 82},
    "oracle-sql": {"aliases": ["oracle", "oracle-sql", "plsql", "pl/sql"], "category": "database", "test_type": "sql", "judge0_id": 82},
    "sql-server": {"aliases": ["sql-server", "mssql", "t-sql", "tsql"], "category": "database", "test_type": "sql", "judge0_id": 82},
    "mongodb": {"aliases": ["mongo", "mongodb", "mongodb-atlas"], "category": "database", "test_type": "mcq", "judge0_id": None},
    "redis": {"aliases": ["redis"], "category": "database", "test_type": "mcq", "judge0_id": None},
    "cassandra": {"aliases": ["cassandra"], "category": "database", "test_type": "mcq", "judge0_id": None},
    "dynamodb": {"aliases": ["dynamodb", "dynamo"], "category": "database", "test_type": "mcq", "judge0_id": None},
    "elasticsearch": {"aliases": ["elasticsearch", "elastic"], "category": "database", "test_type": "mcq", "judge0_id": None},
    "neo4j": {"aliases": ["neo4j"], "category": "database", "test_type": "mcq", "judge0_id": None},
    "firebase": {"aliases": ["firebase", "firestore"], "category": "database", "test_type": "mcq", "judge0_id": None},
    "snowflake": {"aliases": ["snowflake"], "category": "data", "test_type": "sql", "judge0_id": 82},
    "bigquery": {"aliases": ["bigquery", "bq"], "category": "data", "test_type": "sql", "judge0_id": 82},

    # ORMs
    "hibernate": {"aliases": ["hibernate", "hbn"], "category": "orm", "test_type": "mcq", "judge0_id": None},
    "jpa": {"aliases": ["jpa", "hibernate-jpa"], "category": "orm", "test_type": "mcq", "judge0_id": None},
    "entityframework": {"aliases": ["entity-framework", "ef", "efcore"], "category": "orm", "test_type": "mcq", "judge0_id": None},
    "prisma": {"aliases": ["prisma"], "category": "orm", "test_type": "mcq", "judge0_id": None},
    "sequelize": {"aliases": ["sequelize"], "category": "orm", "test_type": "mcq", "judge0_id": None},
    "sqlalchemy": {"aliases": ["sqlalchemy"], "category": "orm", "test_type": "mcq", "judge0_id": None},
    "typeorm": {"aliases": ["typeorm"], "category": "orm", "test_type": "mcq", "judge0_id": None},
    "mongoose": {"aliases": ["mongoose"], "category": "orm", "test_type": "mcq", "judge0_id": None},

    # ═══════════════════════════════════════════════════════════════
    # DATA / ANALYTICS
    # ═══════════════════════════════════════════════════════════════
    "pandas": {"aliases": ["pandas"], "category": "data", "test_type": "coding", "judge0_id": 71},
    "numpy": {"aliases": ["numpy"], "category": "data", "test_type": "coding", "judge0_id": 71},
    "pyspark": {"aliases": ["pyspark", "spark", "apache-spark"], "category": "data", "test_type": "mcq", "judge0_id": None},
    "dbt": {"aliases": ["dbt"], "category": "data", "test_type": "sql", "judge0_id": 82},
    "airflow": {"aliases": ["airflow", "apache-airflow"], "category": "data", "test_type": "mcq", "judge0_id": None},
    "tableau": {"aliases": ["tableau"], "category": "data", "test_type": "mcq", "judge0_id": None},
    "powerbi": {"aliases": ["powerbi", "power-bi"], "category": "data", "test_type": "mcq", "judge0_id": None},
    "looker": {"aliases": ["looker", "looker-studio"], "category": "data", "test_type": "mcq", "judge0_id": None},
    "databricks": {"aliases": ["databricks"], "category": "data", "test_type": "mcq", "judge0_id": None},

    # ═══════════════════════════════════════════════════════════════
    # CLOUD
    # ═══════════════════════════════════════════════════════════════
    "aws": {"aliases": ["aws", "amazon-web-services", "ec2", "s3", "lambda", "rds"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "azure": {"aliases": ["azure", "microsoft-azure", "azure-cloud"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "gcp": {"aliases": ["gcp", "google-cloud", "google-cloud-platform", "gce"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "digitalocean": {"aliases": ["digitalocean", "do"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "cloudflare": {"aliases": ["cloudflare", "cf"], "category": "cloud", "test_type": "mcq", "judge0_id": None},

    # ═══════════════════════════════════════════════════════════════
    # DEVOPS / INFRA
    # ═══════════════════════════════════════════════════════════════
    "docker": {"aliases": ["docker", "containers", "containerization"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "kubernetes": {"aliases": ["kubernetes", "k8s"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "terraform": {"aliases": ["terraform", "tf"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "ansible": {"aliases": ["ansible"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "jenkins": {"aliases": ["jenkins"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "gitlabci": {"aliases": ["gitlab-ci", "gitlabci"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "github-actions": {"aliases": ["github-actions", "gha"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "circleci": {"aliases": ["circleci", "circle-ci"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "nginx": {"aliases": ["nginx"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "apache": {"aliases": ["apache", "httpd"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "linux": {"aliases": ["linux", "unix", "ubuntu", "centos"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "git": {"aliases": ["git", "git-scm"], "category": "devops", "test_type": "mcq", "judge0_id": None},

    # ═══════════════════════════════════════════════════════════════
    # TESTING
    # ═══════════════════════════════════════════════════════════════
    "jest": {"aliases": ["jest"], "category": "testing", "test_type": "mcq", "judge0_id": None},
    "junit": {"aliases": ["junit", "junit5"], "category": "testing", "test_type": "mcq", "judge0_id": None},
    "pytest": {"aliases": ["pytest"], "category": "testing", "test_type": "mcq", "judge0_id": None},
    "selenium": {"aliases": ["selenium"], "category": "testing", "test_type": "mcq", "judge0_id": None},
    "cypress": {"aliases": ["cypress"], "category": "testing", "test_type": "mcq", "judge0_id": None},
    "playwright": {"aliases": ["playwright"], "category": "testing", "test_type": "mcq", "judge0_id": None},
    "mocha": {"aliases": ["mocha"], "category": "testing", "test_type": "mcq", "judge0_id": None},
    "testng": {"aliases": ["testng"], "category": "testing", "test_type": "mcq", "judge0_id": None},

    # ═══════════════════════════════════════════════════════════════
    # AI / ML
    # ═══════════════════════════════════════════════════════════════
    "tensorflow": {"aliases": ["tensorflow", "tf"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "pytorch": {"aliases": ["pytorch", "torch"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "scikit-learn": {"aliases": ["scikit-learn", "sklearn"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "keras": {"aliases": ["keras"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "langchain": {"aliases": ["langchain"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "llamaindex": {"aliases": ["llamaindex", "llama-index"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "transformers": {"aliases": ["transformers", "huggingface"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "llm-prompt-engineering": {"aliases": ["prompt-engineering", "prompt-eng", "llm-prompting"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "rag": {"aliases": ["rag", "retrieval-augmented-generation"], "category": "ml", "test_type": "mcq", "judge0_id": None},

    # ═══════════════════════════════════════════════════════════════
    # MOBILE
    # ═══════════════════════════════════════════════════════════════
    "android": {"aliases": ["android", "android-sdk"], "category": "mobile", "test_type": "mcq", "judge0_id": None},
    "ios": {"aliases": ["ios", "ios-sdk"], "category": "mobile", "test_type": "mcq", "judge0_id": None},
    "react-native": {"aliases": ["react-native", "rn"], "category": "mobile", "test_type": "mcq", "judge0_id": None},
    "flutter": {"aliases": ["flutter", "flutter-dart"], "category": "mobile", "test_type": "mcq", "judge0_id": None},
    "dart": {"aliases": ["dart"], "category": "language", "test_type": "coding", "judge0_id": None},

    # ═══════════════════════════════════════════════════════════════
    # MESSAGE QUEUES / STREAMING
    # ═══════════════════════════════════════════════════════════════
    "kafka": {"aliases": ["kafka", "apache-kafka"], "category": "streaming", "test_type": "mcq", "judge0_id": None},
    "rabbitmq": {"aliases": ["rabbitmq", "rabbit-mq"], "category": "streaming", "test_type": "mcq", "judge0_id": None},
    "pubsub": {"aliases": ["pubsub", "pub-sub", "redis-pubsub"], "category": "streaming", "test_type": "mcq", "judge0_id": None},
    "sqs": {"aliases": ["sqs", "aws-sqs"], "category": "streaming", "test_type": "mcq", "judge0_id": None},

    # ═══════════════════════════════════════════════════════════════
    # AUTH / SECURITY
    # ═══════════════════════════════════════════════════════════════
    "oauth2": {"aliases": ["oauth2", "oauth-2", "oauth"], "category": "security", "test_type": "mcq", "judge0_id": None},
    "jwt": {"aliases": ["jwt", "json-web-tokens"], "category": "security", "test_type": "mcq", "judge0_id": None},
    "saml": {"aliases": ["saml", "saml2"], "category": "security", "test_type": "mcq", "judge0_id": None},
    "owasp-top-10": {"aliases": ["owasp", "owasp-top-10"], "category": "security", "test_type": "mcq", "judge0_id": None},
    "ldap": {"aliases": ["ldap", "active-directory"], "category": "security", "test_type": "mcq", "judge0_id": None},
    "penetration-testing": {"aliases": ["pentest", "penetration-testing", "ethical-hacking"], "category": "security", "test_type": "mcq", "judge0_id": None},

    # ═══════════════════════════════════════════════════════════════
    # BLOCKCHAIN
    # ═══════════════════════════════════════════════════════════════
    "solidity": {"aliases": ["solidity"], "category": "blockchain", "test_type": "mcq", "judge0_id": None},
    "ethereum": {"aliases": ["ethereum", "eth"], "category": "blockchain", "test_type": "mcq", "judge0_id": None},
    "web3js": {"aliases": ["web3", "web3js", "web3.js"], "category": "blockchain", "test_type": "mcq", "judge0_id": None},

    # ═══════════════════════════════════════════════════════════════
    # CONCEPTS (universal)
    # ═══════════════════════════════════════════════════════════════
    "algorithms": {"aliases": ["algorithms", "algo", "sorting", "searching", "dynamic-programming", "recursion"], "category": "concept", "test_type": "coding", "judge0_id": 71},
    "data-structures": {"aliases": ["data-structures", "ds", "arrays", "linked-lists", "hashmaps", "trees", "graphs"], "category": "concept", "test_type": "coding", "judge0_id": 71},
    "oop": {"aliases": ["oop", "oops", "object-oriented", "inheritance", "polymorphism"], "category": "concept", "test_type": "mcq", "judge0_id": None},
    "rest-api": {"aliases": ["rest", "rest-api", "restful", "http-api"], "category": "concept", "test_type": "mcq", "judge0_id": None},
    "graphql": {"aliases": ["graphql", "gql"], "category": "concept", "test_type": "mcq", "judge0_id": None},
    "microservices": {"aliases": ["microservices", "msa", "service-oriented"], "category": "concept", "test_type": "mcq", "judge0_id": None},
    "system-design": {"aliases": ["system-design", "distributed-systems", "scalability", "caching", "load-balancing"], "category": "concept", "test_type": "mcq", "judge0_id": None},
    "software-engineering": {"aliases": ["software-engineering", "swe", "software-development"], "category": "concept", "test_type": "mcq", "judge0_id": None},
    "code-review": {"aliases": ["code-review", "peer-review"], "category": "concept", "test_type": "mcq", "judge0_id": None},
    "debugging": {"aliases": ["debugging", "troubleshooting", "root-cause"], "category": "concept", "test_type": "mcq", "judge0_id": None},
    "agile": {"aliases": ["agile", "scrum", "kanban", "sprint"], "category": "concept", "test_type": "mcq", "judge0_id": None},

    # ═══════════════════════════════════════════════════════════════
    # BEHAVIORAL / SOFT SKILLS
    # ═══════════════════════════════════════════════════════════════
    "communication": {"aliases": ["communication", "written-communication", "presentation"], "category": "behavioral", "test_type": "behavioral", "judge0_id": None},
    "leadership": {"aliases": ["leadership", "team-leadership", "mentoring", "coaching"], "category": "behavioral", "test_type": "behavioral", "judge0_id": None},
    "problem-solving": {"aliases": ["problem-solving", "analytical-thinking", "critical-thinking"], "category": "behavioral", "test_type": "behavioral", "judge0_id": None},
    "collaboration": {"aliases": ["teamwork", "collaboration", "cross-functional"], "category": "behavioral", "test_type": "behavioral", "judge0_id": None},
    "stakeholder-management": {"aliases": ["stakeholder", "stakeholder-management", "stakeholder-engagement"], "category": "behavioral", "test_type": "behavioral", "judge0_id": None},
    "emotional-intelligence": {"aliases": ["emotional-intelligence", "eq", "empathy"], "category": "behavioral", "test_type": "behavioral", "judge0_id": None},
}

# Flattened alias -> canonical lookup
_ALIAS_MAP = {}
for canonical, meta in SKILL_CATALOG.items():
    for alias in meta["aliases"]:
        _ALIAS_MAP[alias.lower()] = canonical
    # Canonical name itself is an alias
    _ALIAS_MAP[canonical.lower()] = canonical

ALL_SKILLS = set(SKILL_CATALOG.keys())

def get_skill(name: str):
    """Return skill metadata, or None if not in catalog."""
    if not name:
        return None
    canonical = _ALIAS_MAP.get(name.strip().lower())
    if not canonical:
        return None
    meta = SKILL_CATALOG[canonical].copy()
    meta["canonical"] = canonical
    return meta

def is_known(name: str) -> bool:
    """Is the skill in the built-in catalog?"""
    return name and name.strip().lower() in _ALIAS_MAP

def total_skills() -> int:
    return len(SKILL_CATALOG)

def all_skills() -> list:
    return sorted(SKILL_CATALOG.keys())