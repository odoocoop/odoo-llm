import json
import logging
import uuid

from openai import OpenAI

from odoo import api, models

_logger = logging.getLogger(__name__)


class LLMProvider(models.Model):
    _inherit = "llm.provider"

    @api.model
    def _get_available_services(self):
        services = super()._get_available_services()
        return services + [("qwen", "Qwen")]

    def qwen_get_client(self):
        """Get Qwen client instance using OpenAI-compatible API
        
        For local Qwen models: Use api_base like http://localhost:8000/v1 (vLLM) or http://localhost:11434/v1 (Ollama)
        For cloud Qwen models: Use api_base https://dashscope.aliyuncs.com/compatible-mode/v1 with API key
        """
        api_base = self.api_base or "https://dashscope.aliyuncs.com/compatible-mode/v1"
        api_key = self.api_key or "not-needed"  # Local models don't need API key
        
        return OpenAI(api_key=api_key, base_url=api_base)

    # Qwen specific implementation
    def qwen_format_tools(self, tools):
        """Format tools for Qwen (OpenAI-compatible format)"""
        return [self._qwen_format_tool(tool) for tool in tools]

    def _qwen_format_tool(self, tool):
        """Convert a tool to Qwen format (OpenAI-compatible)

        Args:
            tool: llm.tool record to convert

        Returns:
            Dictionary in Qwen tool format
        """
        try:
            if tool.input_schema:
                try:
                    schema = json.loads(tool.input_schema)
                    return self._create_qwen_tool_from_schema(schema, tool)
                except json.JSONDecodeError:
                    _logger.error(f"Invalid JSON schema for tool {tool.name}")

            schema = tool.get_input_schema()
            if schema:
                return self._create_qwen_tool_from_schema(schema, tool)

            _logger.warning(
                f"Could not get schema for tool {tool.name}, using fallback"
            )
            schema = {"type": "object", "properties": {}, "required": []}
            return self._create_qwen_tool_from_schema(schema, tool)

        except Exception as e:
            _logger.error(f"Error formatting tool {tool.name}: {str(e)}")
            schema = {
                "title": tool.name,
                "description": tool.description,
                "properties": {},
                "required": [],
            }
            return self._create_qwen_tool_from_schema(schema, tool)

    def _recursively_patch_schema_items(self, schema_node):
        """Recursively ensure 'items' dictionaries have a 'type' defined."""
        if not isinstance(schema_node, dict):
            return

        if "items" in schema_node and isinstance(schema_node["items"], dict):
            items_dict = schema_node["items"]
            if "type" not in items_dict:
                items_dict["type"] = "string"
            self._recursively_patch_schema_items(items_dict)

        if "properties" in schema_node and isinstance(schema_node["properties"], dict):
            for prop_schema in schema_node["properties"].values():
                self._recursively_patch_schema_items(prop_schema)

        for combiner in ["anyOf", "allOf", "oneOf"]:
            if combiner in schema_node and isinstance(schema_node[combiner], list):
                for sub_schema in schema_node[combiner]:
                    self._recursively_patch_schema_items(sub_schema)

    def _create_qwen_tool_from_schema(self, schema, tool):
        """Convert a JSON schema dictionary to Qwen tool format

        Args:
            schema: JSON schema dictionary
            tool: llm.tool record

        Returns:
            Dictionary in Qwen tool format
        """
        if not schema:
            _logger.warning(
                f"Could not generate schema for tool {tool.name}, skipping."
            )
            return None

        # Ensure all nested 'items' have a 'type' for broader compatibility
        parameters_schema = schema
        self._recursively_patch_schema_items(parameters_schema)

        # Format according to OpenAI/Qwen requirements
        formatted_tool = {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": parameters_schema.get("properties", {}),
                    "required": parameters_schema.get("required", []),
                },
            },
        }

        return formatted_tool

    def qwen_chat(
        self,
        messages,
        model=None,
        stream=False,
        tools=None,
        tool_choice="auto",
        prepend_messages=None,
    ):
        """Send chat messages using Qwen with tools support"""
        model = self.get_model(model, "chat")

        # Prepare request parameters
        params = self._prepare_chat_params(
            model,
            messages,
            stream,
            tools=tools,
            prepend_messages=prepend_messages,
            tool_choice=tool_choice,
        )

        # Make the API call
        response = self.client.chat.completions.create(**params)

        # Process the response based on streaming mode
        if not stream:
            return self._qwen_process_non_streaming_response(response)
        else:
            return self._qwen_process_streaming_response(response)

    def _qwen_process_non_streaming_response(self, response):
        """Processes Qwen non-streamed response and returns ONE standardized dict."""
        _logger.info("Processing non-streaming Qwen response.")
        try:
            choice = response.choices[0]
            message = choice.message
            result = {}

            if message.content:
                result["content"] = message.content

            if message.tool_calls:
                result["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in message.tool_calls
                ]

            if "content" in result or "tool_calls" in result:
                return result
            else:
                _logger.warning(
                    "Qwen non-streaming response had no content or tool calls."
                )
                return {}

        except (AttributeError, IndexError, Exception) as e:
            _logger.exception("Error processing Qwen non-streaming response")
            return {"error": f"Error processing response: {e}"}

    def _qwen_process_streaming_response(self, response_stream):
        """
        Processes Qwen stream and yields standardized dicts.
        Yields: {'content': str} OR {'tool_calls': list} OR {'error': str}
        """
        assembled_tool_calls = {}
        final_tool_calls_list = []
        stream_has_tools = False
        finish_reason = None

        try:
            for chunk in response_stream:
                choice = chunk.choices[0] if chunk.choices else None
                delta = choice.delta if choice else None
                chunk_finish_reason = choice.finish_reason if choice else None
                if chunk_finish_reason:
                    finish_reason = chunk_finish_reason

                if not delta:
                    continue

                if delta.content:
                    yield {"content": delta.content}

                if delta.tool_calls:
                    stream_has_tools = True
                    call_counter = 0
                    for tool_call_chunk in delta.tool_calls:
                        index = tool_call_chunk.index or call_counter
                        assembled_tool_calls = self._update_qwen_tool_call_chunk(
                            assembled_tool_calls, tool_call_chunk, index
                        )
                        call_counter += 1
            
            if stream_has_tools:
                if finish_reason == "tool_calls" or (
                    finish_reason != "error" and assembled_tool_calls
                ):
                    for index, call_data in sorted(assembled_tool_calls.items()):
                        if call_data.get("_complete"):
                            tool_call_id = call_data.get("id").strip() or str(
                                uuid.uuid4()
                            )
                            final_tool_calls_list.append(
                                {
                                    "id": tool_call_id,
                                    "type": call_data.get("type", "function"),
                                    "function": {
                                        "name": call_data["function"]["name"],
                                        "arguments": call_data["function"]["arguments"],
                                    },
                                }
                            )
                        else:
                            yield {
                                "error": f"Received incomplete tool call data from provider for tool index {index}."
                            }

                    if final_tool_calls_list:
                        yield {"tool_calls": final_tool_calls_list}
                    elif assembled_tool_calls:
                        _logger.warning(
                            "Stream indicated tool calls, but none were successfully assembled."
                        )

                elif finish_reason != "error":
                    _logger.warning(
                        f"Qwen stream had tool chunks but finished with reason '{finish_reason}'. Not yielding tool calls."
                    )

        except Exception as e:
            yield {"error": f"Internal error processing stream: {e}"}

    def _update_qwen_tool_call_chunk(self, tool_call_chunks, tool_call_chunk, index):
        """
        Helper to assemble fragmented tool calls from Qwen stream chunks.
        """
        if index not in tool_call_chunks:
            tool_call_chunks[index] = {
                "id": tool_call_chunk.id,
                "type": tool_call_chunk.type,
                "function": {"name": "", "arguments": ""},
                "_complete": False,
            }

        current_call = tool_call_chunks[index]

        if tool_call_chunk.id:
            current_call["id"] = tool_call_chunk.id
        if tool_call_chunk.type:
            current_call["type"] = tool_call_chunk.type

        func_chunk = tool_call_chunk.function
        if func_chunk:
            if func_chunk.name:
                current_call["function"]["name"] = func_chunk.name
            if func_chunk.arguments:
                current_call["function"]["arguments"] += func_chunk.arguments

        # Use the common helper to determine completeness
        current_call["_complete"] = self._is_tool_call_complete(
            current_call["function"], expected_endings=("]", "}")
        )

        return tool_call_chunks

    def qwen_embedding(self, texts, model=None):
        """Generate embeddings using Qwen"""
        model = self.get_model(model, "embedding")

        # Ensure texts is a list
        if isinstance(texts, str):
            texts = [texts]

        response = self.client.embeddings.create(model=model.name, input=texts)
        return [r.embedding for r in response.data]

    def qwen_models(self, model_id=None):
        """List available Qwen models"""
        if model_id:
            try:
                model = self.client.models.retrieve(model_id)
                yield self._qwen_parse_model(model)
            except Exception as e:
                _logger.error(f"Error retrieving model {model_id}: {e}")
        else:
            try:
                models = self.client.models.list()
                for model in models.data:
                    yield self._qwen_parse_model(model)
            except Exception as e:
                _logger.error(f"Error listing models: {e}")

    def _qwen_parse_model(self, model):
        capabilities = ["chat"]  # default
        if "embedding" in model.id.lower():
            capabilities = ["embedding"]
        elif "vision" in model.id.lower() or "vl" in model.id.lower():
            capabilities = ["chat", "multimodal"]

        return {
            "name": model.id,
            "details": {
                "id": model.id,
                "capabilities": capabilities,
                "created": getattr(model, 'created', None),
                "owned_by": getattr(model, 'owned_by', None),
            },
        }

    def qwen_format_messages(self, messages, system_prompt=None):
        """Format messages for Qwen API (OpenAI-compatible)

        Args:
            messages: mail.message recordset to format
            system_prompt: Optional system prompt (deprecated, use prepend_messages)

        Returns:
            List of formatted messages in Qwen-compatible format
        """
        formatted_messages = []

        # Add system prompt if provided (for backward compatibility)
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})

        # Format the rest of the messages
        for message in messages:
            formatted_message = self._dispatch("format_message", record=message)
            if formatted_message:
                formatted_messages.append(formatted_message)

        return formatted_messages
