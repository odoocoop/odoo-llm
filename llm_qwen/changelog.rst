========================
Qwen LLM Integration
========================

This module provides integration with Qwen large language models from Alibaba Cloud.

16.0.1.0.0 (2024-01-01)
~~~~~~~~~~~~~~~~~~~~~~~

**Features:**
- Initial release
- Support for Qwen cloud models via DashScope API
- Support for local Qwen models via OpenAI-compatible API (vLLM, Ollama)
- Chat completions with streaming support
- Embeddings generation
- Tool/function calling support
- Pre-configured providers for both cloud and local deployments
- Multiple model configurations (qwen-max, qwen-plus, qwen-turbo, qwen-vl-max)
- Local model configurations (qwen2.5:7b, 14b, 32b, 72b)

**Compatibility:**
- Odoo 16.0+
- Odoo 17.0+
- Odoo 18.0+

**Dependencies:**
- llm
- llm_tool
- openai (Python package)

**Configuration:**
- Cloud: Requires Alibaba Cloud DashScope API key
- Local: Requires vLLM or Ollama with OpenAI-compatible endpoint

