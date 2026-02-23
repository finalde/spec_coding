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

## Troubleshooting: "We're having trouble connecting to the model provider"

- **Use localhost first**  
  If Cursor runs on the same machine as the proxy (e.g. Cursor on Windows, proxy in WSL), set **Override Base URL** to `http://localhost:8000/v1` and leave ngrok off. No browser warning and fewer moving parts.

- **ngrok free tier**  
  Free ngrok can show an HTML "Visit Site" page instead of the API. Cursor can’t add headers, so that response breaks the connection. Options: (1) Use **localhost:8000** as above, or (2) use another tunnel (e.g. `cloudflared tunnel --url http://localhost:8000`), or (3) upgrade ngrok so the interstitial is disabled.

- **Checklist**  
  1. Ollama: `ollama serve` and `ollama pull <model>`.  
  2. Proxy: `make run-ollama-proxy` (or `make run-ollama-proxy-deepseek`) — must be on port 8000.  
  3. If using ngrok: `ngrok http 8000` (tunnel to the **proxy**, not 11434).  
  4. In Cursor: Base URL ends with `/v1`, model is `gpt-4o-mini`.
