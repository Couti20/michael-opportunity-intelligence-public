import re
import unicodedata


def normalizar(texto):
    texto = texto or ""
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        caractere
        for caractere in texto
        if not unicodedata.combining(caractere)
    )
    texto = texto.lower()
    return re.sub(r"\s+", " ", texto).strip()


def contem_termo(texto, termo):
    texto = normalizar(texto)
    termo = normalizar(termo)
    padrao = (
        r"(?<![a-z0-9_])"
        + re.escape(termo)
        + r"(?![a-z0-9_])"
    )
    return re.search(padrao, texto) is not None


def contem_algum(texto, termos):
    return any(contem_termo(texto, termo) for termo in termos)


SKILLS = {
    "python": ["python"],
    "javascript": ["javascript"],
    "typescript": ["typescript"],
    "java": ["java"],
    "go": [
        "golang",
        "go language",
        "go programming language",
        "go developer",
        "go engineer",
    ],
    "c#": ["c#"],
    ".net": [".net", "dotnet"],
    "php": ["php"],
    "ruby": ["ruby"],
    "rust": ["rust"],
    "fastapi": ["fastapi"],
    "django": ["django"],
    "flask": ["flask"],
    "node.js": ["node.js", "nodejs"],
    "nestjs": ["nestjs"],
    "spring boot": ["spring boot"],
    "graphql": ["graphql"],
    "rest api": ["rest api", "restful api", "api rest"],
    "react": ["react", "react.js"],
    "next.js": ["next.js", "nextjs"],
    "angular": ["angular"],
    "vue": ["vue.js", "vuejs"],
    "tailwind": ["tailwind", "tailwindcss"],
    "sql": ["sql"],
    "postgresql": ["postgresql", "postgres"],
    "mysql": ["mysql"],
    "mongodb": ["mongodb"],
    "redis": ["redis"],
    "snowflake": ["snowflake"],
    "databricks": ["databricks"],
    "spark": ["apache spark", "pyspark"],
    "airflow": ["airflow"],
    "dbt": ["dbt"],
    "kafka": ["kafka"],
    "bigquery": ["bigquery"],
    "machine learning": ["machine learning"],
    "deep learning": ["deep learning"],
    "pytorch": ["pytorch"],
    "tensorflow": ["tensorflow"],
    "scikit-learn": ["scikit-learn", "sklearn"],
    "opencv": ["opencv"],
    "computer vision": ["computer vision", "visao computacional"],
    "yolo": ["yolo"],
    "ocr": ["ocr", "tesseract"],
    "llm": [
        "llm",
        "llms",
        "large language model",
        "large language models",
    ],
    "rag": [
        "rag",
        "retrieval augmented generation",
        "retrieval-augmented generation",
    ],
    "mlflow": ["mlflow"],
    "aws": ["aws", "amazon web services"],
    "azure": ["azure"],
    "gcp": ["gcp", "google cloud", "google cloud platform"],
    "docker": ["docker"],
    "kubernetes": ["kubernetes", "k8s"],
    "terraform": ["terraform"],
    "github actions": ["github actions"],
    "ci/cd": [
        "ci/cd",
        "continuous integration",
        "continuous delivery",
    ],
    "react native": ["react native"],
    "flutter": ["flutter"],
    "android": ["android"],
    "ios": ["ios", "swiftui"],
    "swift": ["swift"],
}


TERMOS_TECH_TITULO = [
    "software engineer",
    "software developer",
    "developer",
    "desenvolvedor",
    "desenvolvedora",
    "backend",
    "frontend",
    "full stack",
    "fullstack",
    "machine learning",
    "artificial intelligence",
    "inteligencia artificial",
    "computer vision",
    "visao computacional",
    "data engineer",
    "data scientist",
    "data analyst",
    "business intelligence",
    "analytics engineer",
    "devops",
    "site reliability",
    "sre",
    "cloud engineer",
    "platform engineer",
    "mobile engineer",
    "android developer",
    "ios developer",
    "security engineer",
    "cybersecurity",
    "qa engineer",
    "automation engineer",
    "solutions engineer",
    "software architect",
    "solution architect",
    "solutions architect",
    "system architect",
    "systems architect",
    "arquiteto de software",
    "arquiteto de sistemas",
    "arquiteto de solucoes",
    "engineering manager",
    "engineering coordinator",
    "qa automation",
    "quality assurance",
    "sdet",
    "test engineer",
    "test automation",
    "application support engineer",
    "support engineer",
    "data analytics",
    "data platform",
    "data product manager",
    "database administrator",
    "database engineer",
    "mobile security",
    "application security",
    "security analyst",
    "salesforce engineer",
]


TERMOS_NAO_TECH_TITULO = [
    "credito",
    "credit analyst",
    "credit risk",
    "midia",
    "media analyst",
    "marketing",
    "growth",
    "sales",
    "vendas",
    "commercial",
    "comercial",
    "finance",
    "financeiro",
    "recruiter",
    "recrutador",
    "recrutamento",
    "talent acquisition",
    "human resources",
    "recursos humanos",
    "customer success",
    "procurement",
    "compras",
    "legal",
    "juridico",
    "account executive",
    "account manager",
    "business operations",
    "brand insights",
]


CONTEXTO_TECNICO_TITULO = [
    "engineer",
    "engenheiro",
    "developer",
    "desenvolvedor",
    "architect",
    "arquiteto",
    "administrator",
    "administrador",
    "software",
    "system",
    "sistema",
    "platform",
    "plataforma",
    "infrastructure",
    "infraestrutura",
    "security",
    "seguranca",
    "cloud",
    "qa",
    "sdet",
    "data",
    "dados",
    "analytics",
]


def vaga_no_brasil(local, descricao=""):
    local_n = normalizar(local)
    termos_brasil = [
        "brazil",
        "brasil",
        "sao paulo",
        "rio de janeiro",
        "campinas",
        "belo horizonte",
        "curitiba",
        "recife",
        "porto alegre",
        "florianopolis",
        "brasilia",
        "contagem",
        "sao carlos",
    ]

    if any(termo in local_n for termo in termos_brasil):
        return True

    locais_genericos = {
        "",
        "remote",
        "remoto",
        "latin america",
        "latam",
        "remote - latin america",
        "latin america - remote",
    }

    if local_n not in locais_genericos:
        return False

    descricao_n = normalizar(descricao)
    evidencias = [
        "based in brazil",
        "located in brazil",
        "reside in brazil",
        "resident of brazil",
        "brazil-based",
        "brazil based",
        "work authorization in brazil",
        "trabalho no brasil",
        "residir no brasil",
    ]
    return any(termo in descricao_n for termo in evidencias)


def eh_vaga_tech(titulo, descricao=""):
    titulo_n = normalizar(titulo)

    if contem_algum(titulo_n, TERMOS_TECH_TITULO):
        return True

    if contem_algum(titulo_n, TERMOS_NAO_TECH_TITULO):
        return False

    skills_titulo = extrair_skills(titulo)
    if len(skills_titulo) >= 2:
        return True

    if not contem_algum(titulo_n, CONTEXTO_TECNICO_TITULO):
        return False

    skills_descricao = extrair_skills(descricao)
    return len(skills_descricao) >= 2


def extrair_skills(texto):
    encontradas = set()
    for nome, variantes in SKILLS.items():
        if contem_algum(texto, variantes):
            encontradas.add(nome)
    return sorted(encontradas)


def classificar_senioridade(titulo, descricao=""):
    titulo = normalizar(titulo)

    if contem_algum(
        titulo,
        ["intern", "internship", "estagio", "trainee"],
    ):
        return "estagio"

    if contem_algum(
        titulo,
        [
            "junior",
            "jr",
            "entry level",
            "entry-level",
            "early career",
            "graduate",
            "associate",
        ],
    ):
        return "junior"

    if contem_algum(
        titulo,
        [
            "senior",
            "sr",
            "staff",
            "principal",
            "specialist",
            "especialista",
            "tech lead",
            "technical lead",
            "lead engineer",
        ],
    ):
        return "senior"

    if contem_algum(
        titulo,
        [
            "mid level",
            "mid-level",
            "midlevel",
            "pleno",
            "intermediate",
            "engineer ii",
            "developer ii",
        ],
    ):
        return "pleno"

    return "nao_informado"


def classificar_area(titulo, descricao=""):
    titulo_n = normalizar(titulo)
    descricao_n = normalizar(descricao)

    regras_titulo = [
        (
            "Visão Computacional",
            [
                "computer vision",
                "visao computacional",
                "image processing",
                "vision engineer",
            ],
        ),
        (
            "IA / Machine Learning",
            [
                "machine learning",
                "ml engineer",
                "ai engineer",
                "ai engineering",
                "ai scientist",
                "ai developer",
                "artificial intelligence",
                "generative ai",
                "genai",
                "deep learning",
                "llm engineer",
                "ia engineer",
                "ai trainer",
            ],
        ),
        (
            "Dados",
            [
                "data engineer",
                "data scientist",
                "data analyst",
                "analytics engineer",
                "analytics analyst",
                "data analytics",
                "data platform",
                "data product manager",
                "business intelligence",
                "bi analyst",
                "engenheiro de dados",
                "cientista de dados",
                "analista de dados",
                "especialista em dados",
                "data architect",
                "risk analytics",
            ],
        ),
        (
            "Segurança",
            [
                "security engineer",
                "security analyst",
                "cybersecurity",
                "cyber security",
                "application security",
                "mobile security",
                "cloud security",
                "information security",
                "security architect",
            ],
        ),
        (
            "QA / Testes",
            [
                "quality assurance",
                "qa engineer",
                "qa analyst",
                "qa automation",
                "test engineer",
                "test automation",
                "software tester",
                "sdet",
            ],
        ),
        (
            "Banco de Dados",
            [
                "database engineer",
                "database administrator",
                "database developer",
                "dba",
            ],
        ),
        (
            "DevOps / Cloud",
            [
                "devops",
                "site reliability",
                "sre",
                "cloud engineer",
                "cloud developer",
                "platform engineer",
                "infrastructure engineer",
                "infrastructure specialist",
            ],
        ),
        (
            "Mobile",
            [
                "mobile engineer",
                "mobile developer",
                "mobile design engineer",
                "android developer",
                "android engineer",
                "ios developer",
                "ios engineer",
                "react native",
                "flutter developer",
            ],
        ),
        ("Full Stack", ["full stack", "fullstack", "full-stack"]),
        ("Frontend", ["frontend", "front-end", "front end", "ui engineer"]),
        ("Backend", ["backend", "back-end", "back end", "server-side"]),
        (
            "Arquitetura / Soluções",
            [
                "software architect",
                "solution architect",
                "solutions architect",
                "system architect",
                "systems architect",
                "cloud architect",
                "solutions engineer",
                "solution engineer",
                "implementation engineer",
                "forward deployed engineer",
                "deployed engineer",
                "arquiteto de software",
                "arquiteto de sistemas",
                "arquiteto de solucoes",
            ],
        ),
        (
            "Suporte Técnico",
            [
                "application support engineer",
                "support engineer",
                "technical support engineer",
                "production support engineer",
                "enterprise platform specialist",
            ],
        ),
        (
            "Engenharia de Software",
            [
                "software engineer",
                "software developer",
                "developer",
                "desenvolvedor",
                "desenvolvedora",
                "engineering manager",
                "engineering coordinator",
                "software engineering manager",
                "software engineering specialist",
                "software engineering team leader",
                "desenvolvimento de software",
                "engenheiro de software",
                "coordenador de desenvolvimento de software",
                "coordenador de desenvolvimento",
                "payments engineer",
                "product engineer",
                "technical lead",
                "tech lead",
                "lead engineer",
                "integration engineer",
                "salesforce engineer",
            ],
        ),
    ]

    for area, termos in regras_titulo:
        if contem_algum(titulo_n, termos):
            return area

    skills_titulo = set(extrair_skills(titulo))

    if skills_titulo & {"react native", "flutter", "android", "ios", "swift"}:
        return "Mobile"

    if skills_titulo & {"react", "next.js", "angular", "vue", "tailwind"}:
        return "Frontend"

    if skills_titulo & {
        "airflow",
        "spark",
        "dbt",
        "databricks",
        "snowflake",
        "bigquery",
    }:
        return "Dados"

    if skills_titulo & {
        "docker",
        "kubernetes",
        "terraform",
        "github actions",
        "ci/cd",
    }:
        return "DevOps / Cloud"

    if len(skills_titulo) >= 2:
        return "Engenharia de Software"

    regras_fallback = [
        (
            "Visão Computacional",
            2,
            [
                "computer vision",
                "opencv",
                "object detection",
                "image processing",
                "image recognition",
                "video analytics",
                "yolo",
            ],
        ),
        (
            "IA / Machine Learning",
            2,
            [
                "machine learning",
                "deep learning",
                "pytorch",
                "tensorflow",
                "mlflow",
                "large language model",
                "generative ai",
                "rag",
            ],
        ),
        (
            "Dados",
            2,
            [
                "data pipeline",
                "data warehouse",
                "data lake",
                "apache spark",
                "airflow",
                "dbt",
                "databricks",
                "snowflake",
                "bigquery",
            ],
        ),
        (
            "QA / Testes",
            2,
            [
                "quality assurance",
                "automated testing",
                "test automation",
                "integration testing",
                "selenium",
                "cypress",
            ],
        ),
        (
            "Segurança",
            2,
            [
                "application security",
                "cybersecurity",
                "vulnerability",
                "penetration testing",
                "security controls",
                "threat detection",
            ],
        ),
        (
            "DevOps / Cloud",
            3,
            [
                "kubernetes",
                "docker",
                "terraform",
                "continuous integration",
                "continuous delivery",
                "aws",
                "azure",
                "google cloud",
            ],
        ),
        (
            "Banco de Dados",
            2,
            [
                "database administration",
                "database performance",
                "postgresql",
                "mysql",
                "mongodb",
                "database tuning",
            ],
        ),
    ]

    for area, minimo, termos in regras_fallback:
        sinais = sum(
            contem_termo(descricao_n, termo)
            for termo in termos
        )
        if sinais >= minimo:
            return area

    return "Tecnologia / Outros"
