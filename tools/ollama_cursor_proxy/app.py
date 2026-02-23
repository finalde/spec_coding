#!/usr/bin/env python3
"""
OpenAI-compatible proxy that forwards Cursor requests to Ollama.
Cursor only allows certain model names (e.g. gpt-4o-mini). This proxy accepts
that name and forwards to Ollama with your real model (e.g. qwen3-coder:latest).
"""

import os
import requests
from flask import Flask, request, Response, jsonify

app = Flask(__name__)

OLLAMA_BASE = os.environ.get("OLLAMA_BASE", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen3-coder:latest")
# Model name to advertise to Cursor (must be one Cursor's allowlist accepts)
CURSOR_MODEL = os.environ.get("CURSOR_MODEL", "gpt-4o-mini")


@app.route("/v1/models", methods=["GET"])
def list_models():
    """Return a single model Cursor accepts; we map it to Ollama under the hood."""
    return jsonify({
        "object": "list",
        "data": [
            {
                "id": CURSOR_MODEL,
                "object": "model",
                "created": 0,
                "owned_by": "ollama-proxy",
            }
        ],
    })


# OpenAI params that Ollama's /v1/chat/completions accepts; drop the rest to avoid 400s
OLLAMA_CHAT_KEYS = {"model", "messages", "stream", "max_tokens", "temperature", "top_p", "stop", "frequency_penalty", "presence_penalty"}


@app.route("/v1/chat/completions", methods=["POST"])
def chat_completions():
    """Forward chat completions to Ollama, rewriting model to OLLAMA_MODEL."""
    try:
        body = request.get_json(force=True, silent=True) or {}
    except Exception:
        body = {}
    # Force the model Ollama should use
    body["model"] = OLLAMA_MODEL
    # Strip params Ollama may reject (e.g. tools, response_format) to avoid 400
    body = {k: v for k, v in body.items() if k in OLLAMA_CHAT_KEYS}
    url = f"{OLLAMA_BASE.rstrip('/')}/v1/chat/completions"
    resp = requests.post(
        url,
        json=body,
        timeout=300,
        stream=body.get("stream", False),
    )
    if body.get("stream"):
        return Response(
            resp.iter_content(chunk_size=1024),
            status=resp.status_code,
            mimetype="text/event-stream",
            headers={k: v for k, v in resp.headers.items() if k.lower() != "transfer-encoding"},
        )
    return Response(resp.content, status=resp.status_code, mimetype="application/json")


@app.route("/v1/completions", methods=["POST"])
def completions():
    """Forward legacy completions to Ollama with model rewrite."""
    try:
        body = request.get_json(force=True, silent=True) or {}
    except Exception:
        body = {}
    body["model"] = OLLAMA_MODEL
    url = f"{OLLAMA_BASE.rstrip('/')}/v1/completions"
    resp = requests.post(url, json=body, timeout=300)
    return Response(resp.content, status=resp.status_code, mimetype="application/json")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Ollama proxy: Cursor model '{CURSOR_MODEL}' -> Ollama '{OLLAMA_MODEL}' at {OLLAMA_BASE}")
    print(f"OpenAI-compatible base URL: http://127.0.0.1:{port}/v1")
    app.run(host="0.0.0.0", port=port, threaded=True)
