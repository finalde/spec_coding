# Ollama–Cursor proxy

Cursor only allows certain model names (e.g. `gpt-4o-mini`). This proxy accepts those names and forwards requests to your local Ollama with the model you choose (e.g. `qwen3-coder:latest`).

## 1. Run Ollama

```bash
ollama serve
# optional: ollama pull qwen3-coder:latest
```

## 2. Run the proxy

From repo root:

```bash
make venv   # once
make run-ollama-proxy
```

Or with custom model/port:

```bash
OLLAMA_MODEL=qwen3-coder:latest PORT=8000 .venv/bin/python tools/ollama_cursor_proxy/app.py
```

Default: listens on **8000**, maps Cursor model **gpt-4o-mini** → Ollama **qwen3-coder:latest**.

Env vars:

- `OLLAMA_BASE` – Ollama URL (default `http://localhost:11434`)
- `OLLAMA_MODEL` – Ollama model name (default `qwen3-coder:latest`)
- `CURSOR_MODEL` – model name to advertise to Cursor (default `gpt-4o-mini`; must be one Cursor accepts)
- `PORT` – proxy port (default `8000`)

## 3. Expose with ngrok (so Cursor can use it)

In another terminal:

```bash
ngrok http 8000
```

Copy the **https** URL (e.g. `https://abc123.ngrok-free.app`).

## 4. Configure Cursor

- **Override Base URL:** `https://YOUR-NGROK-URL.ngrok-free.app/v1`
- **Model:** `gpt-4o-mini` (or whatever you set for `CURSOR_MODEL`)

Cursor will send requests to the proxy; the proxy forwards them to Ollama with `qwen3-coder:latest` (or your `OLLAMA_MODEL`).
