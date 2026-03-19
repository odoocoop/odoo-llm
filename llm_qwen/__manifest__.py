{
    "name": "Qwen LLM Integration",
    "summary": "Qwen provider integration for LLM module (Local & Cloud)",
    "description": """
        Implements Qwen provider service for the LLM integration module.
        Supports both local Qwen models (via Ollama or vLLM) and cloud Qwen models (via DashScope/Alibaba Cloud).
        
        Features:
        - Local Qwen models deployment
        - Cloud Qwen models via Alibaba Cloud API
        - Chat completions support
        - Embeddings support
        - Tool/function calling support
    """,
    "author": "Apexive Solutions LLC",
    "website": "https://github.com/apexive/odoo-llm",
    "category": "Technical",
    "version": "16.0.1.0.0",
    "depends": ["llm", "llm_tool"],
    "external_dependencies": {
        "python": ["openai"],
    },
    "data": [
        "data/llm_publisher.xml",
        "data/llm_provider.xml",
        "data/llm_model.xml",
    ],
    "images": [
        "static/description/banner.jpeg",
    ],
    "license": "LGPL-3",
    "installable": True,
    "auto_install": False,
}
