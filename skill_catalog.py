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

    # ═══════════════════════════════════════════════════════════════
    # EXPANSION BATCH 1: Cloud + Kubernetes (Session 106 Part 7a)
    # ═══════════════════════════════════════════════════════════════

    # ─── AWS SERVICES (30) ───
    "aws-ec2": {"aliases": ["aws-ec2", "ec2", "aws-ec2-instances"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "aws-s3": {"aliases": ["aws-s3", "s3", "s3-bucket"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "aws-lambda": {"aliases": ["aws-lambda", "lambda", "lambda-function"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "aws-rds": {"aliases": ["aws-rds", "rds", "aurora"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "aws-dynamodb": {"aliases": ["aws-dynamodb", "dynamodb"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "aws-cloudfront": {"aliases": ["cloudfront", "aws-cloudfront"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "aws-route53": {"aliases": ["route53", "route-53"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "aws-eks": {"aliases": ["aws-eks", "eks", "elastic-kubernetes-service"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "aws-ecs": {"aliases": ["aws-ecs", "ecs", "elastic-container-service"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "aws-fargate": {"aliases": ["fargate", "aws-fargate"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "aws-iam": {"aliases": ["aws-iam", "iam", "iam-roles"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "aws-vpc": {"aliases": ["aws-vpc", "vpc"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "aws-cloudwatch": {"aliases": ["cloudwatch", "aws-cloudwatch"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "aws-sns": {"aliases": ["aws-sns", "sns", "simple-notification-service"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "aws-sqs": {"aliases": ["aws-sqs", "sqs", "simple-queue-service"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "aws-api-gateway": {"aliases": ["api-gateway", "aws-api-gateway"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "aws-kinesis": {"aliases": ["kinesis", "aws-kinesis"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "aws-glue": {"aliases": ["aws-glue", "glue"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "aws-athena": {"aliases": ["athena", "aws-athena"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "aws-redshift": {"aliases": ["redshift", "aws-redshift"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "aws-sagemaker": {"aliases": ["sagemaker", "aws-sagemaker"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "aws-rekognition": {"aliases": ["rekognition", "aws-rekognition"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "aws-comprehend": {"aliases": ["comprehend", "aws-comprehend"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "aws-transcribe": {"aliases": ["transcribe", "aws-transcribe"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "aws-step-functions": {"aliases": ["step-functions", "aws-step-functions"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "aws-batch": {"aliases": ["aws-batch"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "aws-secrets-manager": {"aliases": ["secrets-manager", "aws-secrets-manager"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "aws-kms": {"aliases": ["aws-kms", "kms"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "aws-cognito": {"aliases": ["cognito", "aws-cognito"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "aws-amplify": {"aliases": ["amplify", "aws-amplify"], "category": "cloud", "test_type": "mcq", "judge0_id": None},

    # ─── AZURE SERVICES (15) ───
    "azure-app-service": {"aliases": ["azure-app-service", "app-service"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "azure-functions": {"aliases": ["azure-functions"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "azure-aks": {"aliases": ["azure-aks", "aks"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "azure-cosmos-db": {"aliases": ["cosmos-db", "azure-cosmos", "cosmosdb"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "azure-storage": {"aliases": ["azure-storage", "blob-storage"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "azure-service-bus": {"aliases": ["service-bus", "azure-service-bus"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "azure-event-hub": {"aliases": ["event-hub", "event-hubs", "azure-event-hub"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "azure-logic-apps": {"aliases": ["logic-apps", "azure-logic-apps"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "azure-devops": {"aliases": ["azure-devops", "ado"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "azure-monitor": {"aliases": ["azure-monitor"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "azure-ad": {"aliases": ["azure-ad", "entra-id", "azure-active-directory"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "azure-key-vault": {"aliases": ["key-vault", "azure-key-vault"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "azure-cognitive": {"aliases": ["azure-cognitive", "cognitive-services"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "azure-synapse": {"aliases": ["synapse", "azure-synapse"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "azure-data-factory": {"aliases": ["data-factory", "adf", "azure-data-factory"], "category": "cloud", "test_type": "mcq", "judge0_id": None},

    # ─── GCP SERVICES (15) ───
    "gcp-compute-engine": {"aliases": ["compute-engine", "gce"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "gcp-cloud-functions": {"aliases": ["cloud-functions", "gcp-cloud-functions"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "gcp-cloud-run": {"aliases": ["cloud-run", "gcp-cloud-run"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "gcp-gke": {"aliases": ["gke", "google-kubernetes-engine"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "gcp-bigtable": {"aliases": ["bigtable", "gcp-bigtable"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "gcp-spanner": {"aliases": ["spanner", "cloud-spanner"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "gcp-firestore": {"aliases": ["firestore", "gcp-firestore"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "gcp-pubsub": {"aliases": ["gcp-pubsub", "google-pubsub"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "gcp-cloud-storage": {"aliases": ["cloud-storage", "gcs", "gcp-cloud-storage"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "gcp-bigquery-ml": {"aliases": ["bigquery-ml", "bqml"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "gcp-vertex-ai": {"aliases": ["vertex-ai", "vertex", "gcp-vertex"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "gcp-dataflow": {"aliases": ["dataflow", "gcp-dataflow"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "gcp-dataproc": {"aliases": ["dataproc", "gcp-dataproc"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "gcp-cloud-sql": {"aliases": ["cloud-sql", "gcp-cloud-sql"], "category": "cloud", "test_type": "mcq", "judge0_id": None},
    "gcp-cloud-cdn": {"aliases": ["gcp-cloud-cdn"], "category": "cloud", "test_type": "mcq", "judge0_id": None},

    # ─── KUBERNETES ECOSYSTEM (35) ───
    "helm": {"aliases": ["helm", "helm-charts"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "istio": {"aliases": ["istio", "istio-service-mesh"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "linkerd": {"aliases": ["linkerd"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "argocd": {"aliases": ["argocd", "argo-cd", "argo"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "flux": {"aliases": ["flux", "fluxcd", "flux-cd"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "prometheus": {"aliases": ["prometheus", "prometheus-monitoring"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "grafana": {"aliases": ["grafana"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "fluentd": {"aliases": ["fluentd"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "fluent-bit": {"aliases": ["fluent-bit", "fluentbit"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "loki": {"aliases": ["loki", "grafana-loki"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "jaeger": {"aliases": ["jaeger", "jaeger-tracing"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "tempo": {"aliases": ["tempo", "grafana-tempo"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "kiali": {"aliases": ["kiali"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "kubescape": {"aliases": ["kubescape"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "opa": {"aliases": ["opa", "open-policy-agent"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "vault": {"aliases": ["vault", "hashicorp-vault"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "consul": {"aliases": ["consul", "hashicorp-consul"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "nomad": {"aliases": ["nomad", "hashicorp-nomad"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "rancher": {"aliases": ["rancher", "rancher-k8s"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "openshift": {"aliases": ["openshift", "ocp", "red-hat-openshift"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "knative": {"aliases": ["knative", "knative-serving"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "tekton": {"aliases": ["tekton", "tekton-pipelines"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "crossplane": {"aliases": ["crossplane"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "kubevirt": {"aliases": ["kubevirt"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "longhorn": {"aliases": ["longhorn"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "cilium": {"aliases": ["cilium"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "calico": {"aliases": ["calico", "calico-networking"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "traefik": {"aliases": ["traefik"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "haproxy": {"aliases": ["haproxy"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "envoy": {"aliases": ["envoy", "envoy-proxy"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "kong": {"aliases": ["kong", "kong-gateway"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "ambassador": {"aliases": ["ambassador", "emissary", "ambassador-edge-stack"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "nginx-ingress": {"aliases": ["nginx-ingress"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "kube-state-metrics": {"aliases": ["kube-state-metrics"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "keda": {"aliases": ["keda", "keda-autoscaler"], "category": "devops", "test_type": "mcq", "judge0_id": None},

    # ═══════════════════════════════════════════════════════════════
    # EXPANSION BATCH 2: AI/ML + Data + Models (Session 106 Part 7b)
    # ═══════════════════════════════════════════════════════════════

    # ─── AI MODELS / APIS (20) ───
    "gpt-4": {"aliases": ["gpt-4", "gpt4"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "gpt-4o": {"aliases": ["gpt-4o", "gpt4o"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "gpt-4o-mini": {"aliases": ["gpt-4o-mini"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "gpt-5": {"aliases": ["gpt-5", "gpt5"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "claude": {"aliases": ["claude", "anthropic-claude"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "claude-3": {"aliases": ["claude-3", "claude-3.5", "claude-3.5-sonnet", "claude-sonnet"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "gemini": {"aliases": ["gemini", "google-gemini", "gemini-pro"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "llama": {"aliases": ["llama", "llama3", "llama-3", "llama2"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "mistral": {"aliases": ["mistral", "mistral-ai", "mixtral"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "whisper": {"aliases": ["whisper", "openai-whisper"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "elevenlabs": {"aliases": ["elevenlabs", "eleven-labs"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "stability-ai": {"aliases": ["stability-ai", "stable-diffusion", "sdxl"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "midjourney": {"aliases": ["midjourney"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "dall-e": {"aliases": ["dall-e", "dalle", "dall-e-3"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "cohere": {"aliases": ["cohere", "cohere-ai"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "hugging-face": {"aliases": ["hugging-face", "huggingface", "hf"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "transformers": {"aliases": ["transformers", "hf-transformers"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "diffusers": {"aliases": ["diffusers", "hf-diffusers"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "vllm": {"aliases": ["vllm"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "tgi": {"aliases": ["tgi", "text-generation-inference"], "category": "ml", "test_type": "mcq", "judge0_id": None},

    # ─── LLM FRAMEWORKS / AGENTS (30) ───
    "langchain": {"aliases": ["langchain"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "langgraph": {"aliases": ["langgraph"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "langsmith": {"aliases": ["langsmith"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "llamaindex": {"aliases": ["llamaindex", "llama-index"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "crewai": {"aliases": ["crewai", "crew-ai"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "autogen": {"aliases": ["autogen", "autogen-ai"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "autogpt": {"aliases": ["autogpt"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "babyagi": {"aliases": ["babyagi"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "metagpt": {"aliases": ["metagpt"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "superagent": {"aliases": ["superagent"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "agno": {"aliases": ["agno", "agno-ai"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "pydantic-ai": {"aliases": ["pydantic-ai"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "instructor": {"aliases": ["instructor", "instructor-ai"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "dspy": {"aliases": ["dspy"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "semantic-kernel": {"aliases": ["semantic-kernel"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "haystack": {"aliases": ["haystack"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "litellm": {"aliases": ["litellm"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "openrouter": {"aliases": ["openrouter"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "portkey": {"aliases": ["portkey"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "helicone": {"aliases": ["helicone"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "langfuse": {"aliases": ["langfuse"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "rag": {"aliases": ["rag", "retrieval-augmented-generation"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "ragas": {"aliases": ["ragas"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "function-calling": {"aliases": ["function-calling", "tool-calling"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "prompt-engineering": {"aliases": ["prompt-engineering", "prompt-eng"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "fine-tuning": {"aliases": ["fine-tuning", "finetuning"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "lora": {"aliases": ["lora"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "qlora": {"aliases": ["qlora"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "peft": {"aliases": ["peft"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "rlhf": {"aliases": ["rlhf"], "category": "ml", "test_type": "mcq", "judge0_id": None},

    # ─── VECTOR DATABASES / EMBEDDINGS (15) ───
    "chroma": {"aliases": ["chroma", "chromadb"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "pinecone": {"aliases": ["pinecone"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "weaviate": {"aliases": ["weaviate"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "milvus": {"aliases": ["milvus"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "qdrant": {"aliases": ["qdrant"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "faiss": {"aliases": ["faiss"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "pgvector": {"aliases": ["pgvector"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "embeddings": {"aliases": ["embeddings", "vector-embeddings"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "vector-databases": {"aliases": ["vector-databases", "vector-db"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "openai-embeddings": {"aliases": ["openai-embeddings", "text-embedding-3"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "mlflow": {"aliases": ["mlflow"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "wandb": {"aliases": ["wandb", "weights-and-biases"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "kubeflow": {"aliases": ["kubeflow"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "dvc": {"aliases": ["dvc", "data-version-control"], "category": "ml", "test_type": "mcq", "judge0_id": None},
    "ray": {"aliases": ["ray", "ray-io", "ray-serve"], "category": "ml", "test_type": "mcq", "judge0_id": None},

    # ─── DATA ENGINEERING TOOLS (30) ───
    "apache-beam": {"aliases": ["apache-beam", "beam"], "category": "data", "test_type": "mcq", "judge0_id": None},
    "apache-flink": {"aliases": ["flink", "apache-flink"], "category": "data", "test_type": "mcq", "judge0_id": None},
    "apache-storm": {"aliases": ["storm", "apache-storm"], "category": "data", "test_type": "mcq", "judge0_id": None},
    "spark-streaming": {"aliases": ["spark-streaming"], "category": "data", "test_type": "mcq", "judge0_id": None},
    "kafka-streams": {"aliases": ["kafka-streams"], "category": "data", "test_type": "mcq", "judge0_id": None},
    "debezium": {"aliases": ["debezium"], "category": "data", "test_type": "mcq", "judge0_id": None},
    "nifi": {"aliases": ["nifi", "apache-nifi"], "category": "data", "test_type": "mcq", "judge0_id": None},
    "talend": {"aliases": ["talend"], "category": "data", "test_type": "mcq", "judge0_id": None},
    "informatica": {"aliases": ["informatica"], "category": "data", "test_type": "mcq", "judge0_id": None},
    "airbyte": {"aliases": ["airbyte"], "category": "data", "test_type": "mcq", "judge0_id": None},
    "fivetran": {"aliases": ["fivetran"], "category": "data", "test_type": "mcq", "judge0_id": None},
    "matillion": {"aliases": ["matillion"], "category": "data", "test_type": "mcq", "judge0_id": None},
    "stitch": {"aliases": ["stitch", "stitch-data"], "category": "data", "test_type": "mcq", "judge0_id": None},
    "segment": {"aliases": ["segment", "segment-io"], "category": "data", "test_type": "mcq", "judge0_id": None},
    "hightouch": {"aliases": ["hightouch"], "category": "data", "test_type": "mcq", "judge0_id": None},
    "cube": {"aliases": ["cube", "cube-js"], "category": "data", "test_type": "mcq", "judge0_id": None},
    "metabase": {"aliases": ["metabase"], "category": "data", "test_type": "mcq", "judge0_id": None},
    "superset": {"aliases": ["superset", "apache-superset"], "category": "data", "test_type": "mcq", "judge0_id": None},
    "redash": {"aliases": ["redash"], "category": "data", "test_type": "mcq", "judge0_id": None},
    "mode-analytics": {"aliases": ["mode", "mode-analytics"], "category": "data", "test_type": "mcq", "judge0_id": None},
    "preset": {"aliases": ["preset"], "category": "data", "test_type": "mcq", "judge0_id": None},
    "hex": {"aliases": ["hex", "hex-data"], "category": "data", "test_type": "mcq", "judge0_id": None},
    "observable": {"aliases": ["observable", "observable-hq"], "category": "data", "test_type": "mcq", "judge0_id": None},
    "streamlit": {"aliases": ["streamlit"], "category": "data", "test_type": "mcq", "judge0_id": None},
    "gradio": {"aliases": ["gradio"], "category": "data", "test_type": "mcq", "judge0_id": None},
    "dash": {"aliases": ["dash", "plotly-dash"], "category": "data", "test_type": "mcq", "judge0_id": None},
    "shiny": {"aliases": ["shiny", "r-shiny"], "category": "data", "test_type": "mcq", "judge0_id": None},
    "jupyter": {"aliases": ["jupyter", "jupyter-notebook"], "category": "data", "test_type": "mcq", "judge0_id": None},
    "jupyterlab": {"aliases": ["jupyterlab"], "category": "data", "test_type": "mcq", "judge0_id": None},
    "zeppelin": {"aliases": ["zeppelin", "apache-zeppelin"], "category": "data", "test_type": "mcq", "judge0_id": None},

    # ═══════════════════════════════════════════════════════════════
    # EXPANSION BATCH 3: Frontend + Backend + Testing + Streaming (Session 106 Part 7c)
    # ═══════════════════════════════════════════════════════════════

    # ─── MODERN FRONTEND FRAMEWORKS (30) ───
    "remix": {"aliases": ["remix", "remix-run"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "astro": {"aliases": ["astro", "astro-build"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "solidjs": {"aliases": ["solid", "solidjs", "solid-js"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "qwik": {"aliases": ["qwik", "qwik-city"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "alpinejs": {"aliases": ["alpine", "alpinejs", "alpine.js"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "htmx": {"aliases": ["htmx"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "lit": {"aliases": ["lit", "lit-element", "lit-html"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "stencil": {"aliases": ["stencil", "stenciljs"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "ember": {"aliases": ["ember", "emberjs", "ember.js"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "backbone": {"aliases": ["backbone", "backbonejs"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "preact": {"aliases": ["preact"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "mithril": {"aliases": ["mithril", "mithril.js"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "inferno": {"aliases": ["inferno", "infernojs"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "dojo": {"aliases": ["dojo", "dojo-toolkit"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "aurelia": {"aliases": ["aurelia"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "redux-toolkit": {"aliases": ["redux", "redux-toolkit", "rtk"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "zustand": {"aliases": ["zustand"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "recoil": {"aliases": ["recoil"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "jotai": {"aliases": ["jotai"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "mobx": {"aliases": ["mobx"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "xstate": {"aliases": ["xstate"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "tanstack-query": {"aliases": ["tanstack-query", "react-query"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "tanstack-router": {"aliases": ["tanstack-router"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "tanstack-table": {"aliases": ["tanstack-table"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "chakra-ui": {"aliases": ["chakra-ui", "chakra"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "ant-design": {"aliases": ["ant-design", "antd"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "shadcn-ui": {"aliases": ["shadcn", "shadcn-ui"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "radix-ui": {"aliases": ["radix-ui", "radix"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "headless-ui": {"aliases": ["headless-ui"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "primevue": {"aliases": ["primevue"], "category": "framework", "test_type": "mcq", "judge0_id": None},

    # ─── MODERN BACKEND FRAMEWORKS (25) ───
    "hapi": {"aliases": ["hapi", "hapi.js"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "koa": {"aliases": ["koa", "koa.js"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "restify": {"aliases": ["restify"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "feathers": {"aliases": ["feathers", "feathersjs"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "adonis": {"aliases": ["adonis", "adonisjs"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "strapi": {"aliases": ["strapi"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "hono": {"aliases": ["hono"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "actix": {"aliases": ["actix", "actix-web"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "axum": {"aliases": ["axum"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "rocket": {"aliases": ["rocket", "rocket-rs"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "fiber": {"aliases": ["fiber", "fiber-go"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "echo": {"aliases": ["echo", "echo-go"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "chi": {"aliases": ["chi", "chi-go"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "buffalo": {"aliases": ["buffalo", "buffalo-go"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "phoenix": {"aliases": ["phoenix", "phoenix-framework"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "liveview": {"aliases": ["liveview", "phoenix-liveview"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "vapor": {"aliases": ["vapor", "vapor-swift"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "ktor": {"aliases": ["ktor"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "micronaut": {"aliases": ["micronaut"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "quarkus": {"aliases": ["quarkus"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "vertx": {"aliases": ["vertx", "vert.x"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "helidon": {"aliases": ["helidon"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "loopback": {"aliases": ["loopback", "loopback4"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "sails": {"aliases": ["sails", "sailsjs"], "category": "framework", "test_type": "mcq", "judge0_id": None},
    "kuzzle": {"aliases": ["kuzzle"], "category": "framework", "test_type": "mcq", "judge0_id": None},

    # ─── TESTING TOOLS (25) ───
    "vitest": {"aliases": ["vitest"], "category": "testing", "test_type": "mcq", "judge0_id": None},
    "karma": {"aliases": ["karma", "karma-js"], "category": "testing", "test_type": "mcq", "judge0_id": None},
    "jasmine": {"aliases": ["jasmine"], "category": "testing", "test_type": "mcq", "judge0_id": None},
    "protractor": {"aliases": ["protractor"], "category": "testing", "test_type": "mcq", "judge0_id": None},
    "appium": {"aliases": ["appium"], "category": "testing", "test_type": "mcq", "judge0_id": None},
    "detox": {"aliases": ["detox"], "category": "testing", "test_type": "mcq", "judge0_id": None},
    "xctest": {"aliases": ["xctest"], "category": "testing", "test_type": "mcq", "judge0_id": None},
    "espresso": {"aliases": ["espresso", "espresso-android"], "category": "testing", "test_type": "mcq", "judge0_id": None},
    "robot-framework": {"aliases": ["robot-framework"], "category": "testing", "test_type": "mcq", "judge0_id": None},
    "testcafe": {"aliases": ["testcafe"], "category": "testing", "test_type": "mcq", "judge0_id": None},
    "puppeteer": {"aliases": ["puppeteer"], "category": "testing", "test_type": "mcq", "judge0_id": None},
    "webdriverio": {"aliases": ["webdriverio", "wdio"], "category": "testing", "test_type": "mcq", "judge0_id": None},
    "nightwatch": {"aliases": ["nightwatch"], "category": "testing", "test_type": "mcq", "judge0_id": None},
    "cucumber": {"aliases": ["cucumber"], "category": "testing", "test_type": "mcq", "judge0_id": None},
    "gherkin": {"aliases": ["gherkin"], "category": "testing", "test_type": "mcq", "judge0_id": None},
    "behave": {"aliases": ["behave"], "category": "testing", "test_type": "mcq", "judge0_id": None},
    "rspec": {"aliases": ["rspec"], "category": "testing", "test_type": "mcq", "judge0_id": None},
    "minitest": {"aliases": ["minitest"], "category": "testing", "test_type": "mcq", "judge0_id": None},
    "testify": {"aliases": ["testify", "testify-go"], "category": "testing", "test_type": "mcq", "judge0_id": None},
    "ginkgo": {"aliases": ["ginkgo", "ginkgo-go"], "category": "testing", "test_type": "mcq", "judge0_id": None},
    "catch2": {"aliases": ["catch2", "catch"], "category": "testing", "test_type": "mcq", "judge0_id": None},
    "gtest": {"aliases": ["gtest", "google-test"], "category": "testing", "test_type": "mcq", "judge0_id": None},
    "mockito": {"aliases": ["mockito"], "category": "testing", "test_type": "mcq", "judge0_id": None},
    "testcontainers": {"aliases": ["testcontainers"], "category": "testing", "test_type": "mcq", "judge0_id": None},
    "wiremock": {"aliases": ["wiremock"], "category": "testing", "test_type": "mcq", "judge0_id": None},

    # ─── MESSAGE QUEUES / STREAMING (15) ───
    "activemq": {"aliases": ["activemq", "active-mq"], "category": "streaming", "test_type": "mcq", "judge0_id": None},
    "zeromq": {"aliases": ["zeromq", "zmq"], "category": "streaming", "test_type": "mcq", "judge0_id": None},
    "nats": {"aliases": ["nats"], "category": "streaming", "test_type": "mcq", "judge0_id": None},
    "pulsar": {"aliases": ["pulsar", "apache-pulsar"], "category": "streaming", "test_type": "mcq", "judge0_id": None},
    "redpanda": {"aliases": ["redpanda"], "category": "streaming", "test_type": "mcq", "judge0_id": None},
    "mqtt": {"aliases": ["mqtt"], "category": "streaming", "test_type": "mcq", "judge0_id": None},
    "redis-streams": {"aliases": ["redis-streams"], "category": "streaming", "test_type": "mcq", "judge0_id": None},
    "celery": {"aliases": ["celery"], "category": "streaming", "test_type": "mcq", "judge0_id": None},
    "sidekiq": {"aliases": ["sidekiq"], "category": "streaming", "test_type": "mcq", "judge0_id": None},
    "resque": {"aliases": ["resque"], "category": "streaming", "test_type": "mcq", "judge0_id": None},
    "bullmq": {"aliases": ["bullmq", "bull"], "category": "streaming", "test_type": "mcq", "judge0_id": None},
    "temporal": {"aliases": ["temporal", "temporal-io"], "category": "streaming", "test_type": "mcq", "judge0_id": None},
    "cadence": {"aliases": ["cadence", "uber-cadence"], "category": "streaming", "test_type": "mcq", "judge0_id": None},
    "sqs-streaming": {"aliases": ["sqs-queue"], "category": "streaming", "test_type": "mcq", "judge0_id": None},
    "event-hubs-streaming": {"aliases": ["eventhubs"], "category": "streaming", "test_type": "mcq", "judge0_id": None},

    # ═══════════════════════════════════════════════════════════════
    # EXPANSION BATCH 4: Databases + Observability + Security + Domain (Session 106 Part 7d)
    # ═══════════════════════════════════════════════════════════════

    # ─── EXTENDED DATABASES (25) ───
    "supabase": {"aliases": ["supabase"], "category": "database", "test_type": "mcq", "judge0_id": None},
    "fauna": {"aliases": ["fauna", "faunadb"], "category": "database", "test_type": "mcq", "judge0_id": None},
    "clickhouse": {"aliases": ["clickhouse"], "category": "database", "test_type": "sql", "judge0_id": 82},
    "timescaledb": {"aliases": ["timescaledb", "timescale"], "category": "database", "test_type": "sql", "judge0_id": 82},
    "couchdb": {"aliases": ["couchdb", "couch-db"], "category": "database", "test_type": "mcq", "judge0_id": None},
    "influxdb": {"aliases": ["influxdb", "influx"], "category": "database", "test_type": "mcq", "judge0_id": None},
    "victoriametrics": {"aliases": ["victoriametrics", "vm"], "category": "database", "test_type": "mcq", "judge0_id": None},
    "memgraph": {"aliases": ["memgraph"], "category": "database", "test_type": "mcq", "judge0_id": None},
    "arangodb": {"aliases": ["arangodb", "arango"], "category": "database", "test_type": "mcq", "judge0_id": None},
    "orientdb": {"aliases": ["orientdb"], "category": "database", "test_type": "mcq", "judge0_id": None},
    "couchbase": {"aliases": ["couchbase"], "category": "database", "test_type": "mcq", "judge0_id": None},
    "ravendb": {"aliases": ["ravendb"], "category": "database", "test_type": "mcq", "judge0_id": None},
    "hbase": {"aliases": ["hbase", "apache-hbase"], "category": "database", "test_type": "mcq", "judge0_id": None},
    "aerospike": {"aliases": ["aerospike"], "category": "database", "test_type": "mcq", "judge0_id": None},
    "rocksdb": {"aliases": ["rocksdb"], "category": "database", "test_type": "mcq", "judge0_id": None},
    "leveldb": {"aliases": ["leveldb"], "category": "database", "test_type": "mcq", "judge0_id": None},
    "lmdb": {"aliases": ["lmdb"], "category": "database", "test_type": "mcq", "judge0_id": None},
    "duckdb": {"aliases": ["duckdb"], "category": "database", "test_type": "sql", "judge0_id": 82},
    "mariadb": {"aliases": ["mariadb"], "category": "database", "test_type": "sql", "judge0_id": 82},
    "percona": {"aliases": ["percona"], "category": "database", "test_type": "sql", "judge0_id": 82},
    "yugabytedb": {"aliases": ["yugabytedb", "yugabyte"], "category": "database", "test_type": "mcq", "judge0_id": None},
    "cockroachdb": {"aliases": ["cockroachdb", "cockroach"], "category": "database", "test_type": "sql", "judge0_id": 82},
    "tidb": {"aliases": ["tidb"], "category": "database", "test_type": "sql", "judge0_id": 82},
    "vitess": {"aliases": ["vitess"], "category": "database", "test_type": "mcq", "judge0_id": None},
    "pocketbase": {"aliases": ["pocketbase"], "category": "database", "test_type": "mcq", "judge0_id": None},

    # ─── OBSERVABILITY (20) ───
    "datadog": {"aliases": ["datadog", "dd"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "newrelic": {"aliases": ["newrelic", "new-relic"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "dynatrace": {"aliases": ["dynatrace"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "appdynamics": {"aliases": ["appdynamics"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "sentry": {"aliases": ["sentry", "sentry-io"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "rollbar": {"aliases": ["rollbar"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "bugsnag": {"aliases": ["bugsnag"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "honeycomb": {"aliases": ["honeycomb", "honeycomb-io"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "lightstep": {"aliases": ["lightstep"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "zipkin": {"aliases": ["zipkin"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "opentelemetry": {"aliases": ["opentelemetry", "otel"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "elastic-apm": {"aliases": ["elastic-apm"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "splunk": {"aliases": ["splunk"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "sumologic": {"aliases": ["sumologic", "sumo-logic"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "loggly": {"aliases": ["loggly"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "papertrail": {"aliases": ["papertrail"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "wazuh": {"aliases": ["wazuh"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "falco": {"aliases": ["falco"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "fluentd-logging": {"aliases": ["fluentd-logging"], "category": "devops", "test_type": "mcq", "judge0_id": None},
    "vector-logging": {"aliases": ["vector", "vector-dev"], "category": "devops", "test_type": "mcq", "judge0_id": None},

    # ─── SECURITY TOOLS (20) ───
    "burp-suite": {"aliases": ["burp", "burp-suite"], "category": "security", "test_type": "mcq", "judge0_id": None},
    "owasp-zap": {"aliases": ["zap", "owasp-zap"], "category": "security", "test_type": "mcq", "judge0_id": None},
    "nmap": {"aliases": ["nmap"], "category": "security", "test_type": "mcq", "judge0_id": None},
    "metasploit": {"aliases": ["metasploit", "msf"], "category": "security", "test_type": "mcq", "judge0_id": None},
    "wireshark": {"aliases": ["wireshark"], "category": "security", "test_type": "mcq", "judge0_id": None},
    "kali": {"aliases": ["kali", "kali-linux"], "category": "security", "test_type": "mcq", "judge0_id": None},
    "nessus": {"aliases": ["nessus"], "category": "security", "test_type": "mcq", "judge0_id": None},
    "qualys": {"aliases": ["qualys"], "category": "security", "test_type": "mcq", "judge0_id": None},
    "aqua-security": {"aliases": ["aqua", "aqua-security"], "category": "security", "test_type": "mcq", "judge0_id": None},
    "twistlock": {"aliases": ["twistlock", "prisma-cloud"], "category": "security", "test_type": "mcq", "judge0_id": None},
    "snyk": {"aliases": ["snyk"], "category": "security", "test_type": "mcq", "judge0_id": None},
    "veracode": {"aliases": ["veracode"], "category": "security", "test_type": "mcq", "judge0_id": None},
    "checkmarx": {"aliases": ["checkmarx"], "category": "security", "test_type": "mcq", "judge0_id": None},
    "fortify": {"aliases": ["fortify", "micro-focus-fortify"], "category": "security", "test_type": "mcq", "judge0_id": None},
    "sonarqube": {"aliases": ["sonarqube", "sonar"], "category": "security", "test_type": "mcq", "judge0_id": None},
    "trivy": {"aliases": ["trivy"], "category": "security", "test_type": "mcq", "judge0_id": None},
    "grype": {"aliases": ["grype"], "category": "security", "test_type": "mcq", "judge0_id": None},
    "semgrep": {"aliases": ["semgrep"], "category": "security", "test_type": "mcq", "judge0_id": None},
    "bandit": {"aliases": ["bandit", "bandit-py"], "category": "security", "test_type": "mcq", "judge0_id": None},
    "snyk-code": {"aliases": ["snyk-code"], "category": "security", "test_type": "mcq", "judge0_id": None},

    # ─── DOMAIN-SPECIFIC (30) ───
    "pharma-qa": {"aliases": ["pharma-qa", "pharmaceutical-qa"], "category": "domain", "test_type": "mcq", "judge0_id": None},
    "clinical-research": {"aliases": ["clinical-research", "clinical-trials"], "category": "domain", "test_type": "mcq", "judge0_id": None},
    "regulatory-affairs": {"aliases": ["regulatory-affairs", "regulatory"], "category": "domain", "test_type": "mcq", "judge0_id": None},
    "gmp": {"aliases": ["gmp", "good-manufacturing-practice"], "category": "domain", "test_type": "mcq", "judge0_id": None},
    "glp": {"aliases": ["glp", "good-laboratory-practice"], "category": "domain", "test_type": "mcq", "judge0_id": None},
    "gcp-pharma": {"aliases": ["gcp-pharma", "good-clinical-practice"], "category": "domain", "test_type": "mcq", "judge0_id": None},
    "pharmacovigilance": {"aliases": ["pharmacovigilance", "pv"], "category": "domain", "test_type": "mcq", "judge0_id": None},
    "medical-coding": {"aliases": ["medical-coding", "icd-10"], "category": "domain", "test_type": "mcq", "judge0_id": None},
    "hipaa": {"aliases": ["hipaa"], "category": "domain", "test_type": "mcq", "judge0_id": None},
    "fda-compliance": {"aliases": ["fda-compliance", "fda"], "category": "domain", "test_type": "mcq", "judge0_id": None},
    "sox": {"aliases": ["sox", "sarbanes-oxley"], "category": "domain", "test_type": "mcq", "judge0_id": None},
    "gdpr": {"aliases": ["gdpr"], "category": "domain", "test_type": "mcq", "judge0_id": None},
    "pci-dss": {"aliases": ["pci-dss", "pci"], "category": "domain", "test_type": "mcq", "judge0_id": None},
    "iso-27001": {"aliases": ["iso-27001"], "category": "domain", "test_type": "mcq", "judge0_id": None},
    "iso-9001": {"aliases": ["iso-9001"], "category": "domain", "test_type": "mcq", "judge0_id": None},
    "six-sigma": {"aliases": ["six-sigma", "6-sigma"], "category": "domain", "test_type": "mcq", "judge0_id": None},
    "lean": {"aliases": ["lean", "lean-methodology"], "category": "domain", "test_type": "mcq", "judge0_id": None},
    "kaizen": {"aliases": ["kaizen"], "category": "domain", "test_type": "mcq", "judge0_id": None},
    "tqm": {"aliases": ["tqm", "total-quality-management"], "category": "domain", "test_type": "mcq", "judge0_id": None},
    "supply-chain": {"aliases": ["supply-chain", "supply-chain-management"], "category": "domain", "test_type": "mcq", "judge0_id": None},
    "logistics": {"aliases": ["logistics"], "category": "domain", "test_type": "mcq", "judge0_id": None},
    "procurement": {"aliases": ["procurement"], "category": "domain", "test_type": "mcq", "judge0_id": None},
    "inventory-management": {"aliases": ["inventory-management", "inventory"], "category": "domain", "test_type": "mcq", "judge0_id": None},
    "financial-modeling": {"aliases": ["financial-modeling"], "category": "domain", "test_type": "mcq", "judge0_id": None},
    "financial-analysis": {"aliases": ["financial-analysis"], "category": "domain", "test_type": "mcq", "judge0_id": None},
    "investment-banking": {"aliases": ["investment-banking", "ib"], "category": "domain", "test_type": "mcq", "judge0_id": None},
    "accounting": {"aliases": ["accounting"], "category": "domain", "test_type": "mcq", "judge0_id": None},
    "ifrs": {"aliases": ["ifrs"], "category": "domain", "test_type": "mcq", "judge0_id": None},
    "gaap": {"aliases": ["gaap", "us-gaap"], "category": "domain", "test_type": "mcq", "judge0_id": None},
    "tax-compliance": {"aliases": ["tax-compliance", "taxation"], "category": "domain", "test_type": "mcq", "judge0_id": None},
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