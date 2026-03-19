# Qwen LLM Integration

This module provides integration with Qwen large language models from Alibaba Cloud, supporting both cloud-based and local deployments.

## Features

- **Cloud Integration**: Connect to Qwen models via Alibaba Cloud's DashScope API
- **Local Deployment**: Run Qwen models locally using vLLM or Ollama with OpenAI-compatible API
- **Chat Completions**: Full support for chat-based interactions
- **Embeddings**: Generate text embeddings using Qwen embedding models
- **Tool/Function Calling**: Support for function calling capabilities
- **Streaming**: Real-time streaming responses
- **Multi-model Support**: Access to various Qwen model sizes and capabilities

## Supported Models

### Cloud Models (DashScope)
- `qwen-max` - Most powerful Qwen model (default)
- `qwen-plus` - Balanced performance and cost
- `qwen-turbo` - Fast and cost-effective
- `qwen-vl-max` - Vision-language multimodal model
- `text-embedding-v3` - Text embedding model

### Local Models
- `qwen2.5:7b` - 7B parameter model for resource-constrained environments
- `qwen2.5:14b` - 14B parameter model for balanced performance
- `qwen2.5:32b` - 32B parameter model for high-quality outputs
- `qwen2.5:72b` - 72B parameter model for maximum capability

## Installation

1. Install the required Python dependency:
   ```bash
   pip install openai
   ```

2. Install this module in your Odoo instance

## Configuration

### Cloud Setup (Alibaba Cloud DashScope)

1. Create an account at [Alibaba Cloud](https://www.aliyun.com/)
2. Navigate to [DashScope Console](https://dashscope.console.aliyun.com/apiKey)
3. Generate an API key
4. In Odoo, go to LLM → Providers
5. Edit "Qwen Cloud (DashScope)" provider
6. Enter your API key
7. The API base URL is pre-configured: `https://dashscope.aliyuncs.com/compatible-mode/v1`

### Local Setup (vLLM)

1. Install vLLM:
   ```bash
   pip install vllm
   ```

2. Start vLLM with a Qwen model:
   ```bash
   python -m vllm.entrypoints.openai_api_server \
       --model Qwen/Qwen2.5-7B-Instruct \
       --host 0.0.0.0 \
       --port 8000
   ```

3. In Odoo, go to LLM → Providers
4. Activate "Qwen Local" provider
5. Set API Base to: `http://localhost:8000/v1`
6. API Key can be set to: `not-needed`

### Local Setup (Ollama)

1. Install [Ollama](https://ollama.ai/)
2. Pull a Qwen model:
   ```bash
   ollama pull qwen2.5:7b
   ```

3. Start Ollama (it runs as a service by default)
4. In Odoo, go to LLM → Providers
5. Activate "Qwen Local" provider
6. Set API Base to: `http://localhost:11434/v1`

Note: When using Ollama, you can also use the dedicated `llm_ollama` module which provides native Ollama integration.

## Usage

Once configured, you can use Qwen models throughout the Odoo LLM ecosystem:

- **LLM Threads**: Create conversation threads with Qwen models
- **Knowledge Base**: Use Qwen for RAG (Retrieval-Augmented Generation)
- **Tools**: Enable function calling with Qwen models
- **Assistants**: Build AI assistants powered by Qwen

## Version Compatibility

This module is compatible with:
- Odoo 16.0
- Odoo 17.0
- Odoo 18.0

The module uses the OpenAI-compatible API format, making it forward-compatible with future Odoo versions that maintain the LLM framework.

## Troubleshooting

### Connection Issues
- Verify the API base URL is correct
- Check network connectivity to the API endpoint
- For cloud: Ensure your API key is valid and has sufficient credits
- For local: Confirm the server is running and accessible

### Model Not Found
- List available models using the "List Models" action in the provider
- For cloud: Check available models in DashScope console
- For local: Verify the model is loaded in vLLM/Ollama

### Rate Limiting
- Cloud: Check your quota in DashScope console
- Local: Adjust batch sizes or implement request throttling

## References

- [Qwen Documentation](https://help.aliyun.com/zh/dashscope/)
- [Qwen GitHub](https://github.com/QwenLM/Qwen)
- [vLLM Documentation](https://docs.vllm.ai/)
- [Ollama Documentation](https://github.com/ollama/ollama)

## License

LGPL-3

## Author

Apexive Solutions LLC
