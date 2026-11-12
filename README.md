# langchain-animeapi

[AnimeAPI](https://animeapi.ai) tool for [LangChain](https://github.com/langchain-ai/langchain) and LangGraph agents: anime image generation at **$0.003 per image**, one of the cheapest anime image APIs. Prepaid balance from $5 that never expires, no subscription; new accounts get 3 free images without a card.

```bash
pip install langchain-animeapi
```

Create a key (it starts with `ank_`) at <https://animeapi.ai/dashboard/api-keys> and set it as `ANIMEAPI_API_KEY`.

## Quick start

```python
from langchain_animeapi import AnimeAPIGenerateImage

tool = AnimeAPIGenerateImage()  # reads ANIMEAPI_API_KEY

print(tool.invoke({"prompt": "a shrine maiden sweeping autumn leaves", "orientation": "landscape"}))
# Image generated: https://animeapi.ai/i/….webp
# Model anime, landscape, $0.003. Balance left: $4.997.
# The link is not permanent storage; download the image to keep it.
```

## With an agent

```python
from langchain.agents import create_agent
from langchain_animeapi import AnimeAPIGenerateImage

agent = create_agent(model, tools=[AnimeAPIGenerateImage()])  # model: your chat model
result = agent.invoke({"messages": [{"role": "user", "content": "Draw a chibi cat barista, square."}]})
```

Any chat model that supports tool calling works: `model.bind_tools([AnimeAPIGenerateImage()])`. The model writes the prompt and picks the shape. When it calls the tool, the `ToolMessage` carries a short text for the model and the details as `artifact`:

```python
msg = tool.invoke({
    "type": "tool_call", "id": "call_1", "name": "animeapi_generate_image",
    "args": {"prompt": "a chibi cat barista holding a latte", "orientation": "square"},
})
msg.artifact["image_url"]        # https://animeapi.ai/i/….webp
msg.artifact["enhanced_prompt"]  # the tags the model received
msg.artifact["price_usd"]        # 0.003
msg.artifact["balance_usd"]      # balance after this image
```

`ainvoke` works the same way for async agents.

## Options

| Option | Default | What it does |
| --- | --- | --- |
| `api_key` | `ANIMEAPI_API_KEY` | Your key. Stored as a secret, so it does not show up in `repr()` or traces. |
| `model` | `"anime"` | `"anime"` $0.003, `"ultra"` $0.01, `"ultra-max"` $0.02 per image. Set by you, not by the language model, so an agent cannot pick a more expensive one. |
| `enhance` | `True` | Rewrites plain words into tags for the anime model. |
| `timeout` | `120` | Seconds to wait for one request. |
| `max_retries` | `2` | Retries for failures the API marks as retryable. |

What the language model can set per call: `prompt` (up to 1000 characters) and `orientation` (`portrait`, `square` or `landscape`; same price).

AnimeAPI does not generate adult content. Explicit prompts are refused and not charged.

## Errors

A failed call does not raise inside your agent: the tool answers with an error `ToolMessage` carrying AnimeAPI's own message, so the model can tell the user what happened (prompt refused, wrong key, empty balance). Set `handle_tool_error=False` to get a `ToolException` instead.

## Keeping the image

Image URLs are not permanent storage. Download what you want to keep, for example with the SDK this package is built on:

```python
from animeapi import AnimeAPI

AnimeAPI().download(msg.artifact["image_url"]).save("cat.webp")
```

## Prices

| Model | Price per image | Use it for |
| --- | --- | --- |
| `anime` | **$0.003** | Characters, portraits, avatars, scenes. About 4 seconds. |
| `ultra` | $0.01 | Long, detailed prompts; legible text in the image. |
| `ultra-max` | $0.02 | Highest detail. |

## Tested

Run against the live API with `langchain-core` 1.8.0 on 2026-11-12: a direct call, a tool call (returns a `ToolMessage` with the artifact), an async tool call, a refused prompt and a wrong key (both come back as error messages, uncharged).

## Links

- AnimeAPI: <https://animeapi.ai> · [Docs](https://animeapi.ai/docs) · [API reference](https://animeapi.ai/docs/api-reference)
- Python SDK: [animeapi-sdk](https://github.com/animeapi-ai/animeapi-python) · MCP server for agents: <https://animeapi.ai/mcp>
- Licence: [MIT](LICENSE)
