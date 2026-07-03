TECHNICAL_TERMS = {
    "python", "javascript", "typescript", "rust", "go", "golang", "java", "ruby", "php",
    "react", "vue", "angular", "node", "deno", "bun",
    "sql", "nosql", "postgresql", "mysql", "mongodb", "redis",
    "docker", "kubernetes", "k8s", "aws", "gcp", "azure",
    "api", "rest", "graphql", "grpc", "websocket",
    "json", "csv", "xml", "yaml", "toml",
    "pandas", "numpy", "tensorflow", "pytorch", "sklearn",
    "git", "linux", "bash", "shell", "terminal",
    "html", "css", "sass", "tailwind",
    "data", "analysis", "analytics", "visualization", "dashboard",
    "etl", "pipeline", "streaming", "kafka", "spark",
    "database", "query", "schema", "migration",
    "reporting", "bi", "excel", "tableau",
    "testing", "tdd", "deployment", "devops", "monitoring",
    "authentication", "authorization", "jwt", "oauth",
    "microservices", "serverless", "async", "concurrent", "parallel",
    "machine learning", "deep learning", "llm", "gpt", "neural",
    "prompt", "embedding", "vector", "rag", "fine-tune",
    "classification", "regression", "clustering",
    "saas", "b2b", "enterprise", "startup",
    "revenue", "subscription", "pricing",
}


def detect_query_depth(query: str) -> str:
    words = query.lower().split()
    word_count = len(words)
    tech_count = sum(1 for w in words if w in TECHNICAL_TERMS)
    if word_count <= 2 and tech_count == 0:
        return "broad"
    if word_count >= 5 or tech_count >= 2:
        return "specific"
    return "moderate"
