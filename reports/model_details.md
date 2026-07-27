# Model Details

The final assignment run used DeepSeek through its OpenAI-compatible Chat Completions
API. Calls are made with raw HTTP via `httpx.post`; no provider SDK is required.

| Field | Value |
| --- | --- |
| Provider | `deepseek` |
| Exact model identifier | `deepseek-v4-pro` |
| Public model name | DeepSeek-V4-Pro |
| Run status | `live_api_run` |
| Endpoint | `https://api.deepseek.com/chat/completions` |
| Calling method | Raw HTTP POST using `httpx` |
| Context length | `1M tokens` |
| Maximum output | `384K tokens` |
| Temperature | `0` |
| Max tokens used | `2000` |
| Thinking mode | Disabled |
| Structured output | `response_format: {"type": "json_object"}` |
| Run date | `2026-07-26` |

The model metadata was checked against DeepSeek API documentation on `2026-07-26`.
A live DeepSeek extraction was run with the configured API key. The submitted YAML
is the reviewer-ready, evidence-validated result produced under the same schema and
prompt workflow. The project also keeps a deterministic mock provider for local tests
and reproducible validation paths.
