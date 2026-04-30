"""Optional OpenAI-compatible reasoning smoke for ModelResponse."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
import uuid
from typing import Any

from .collector import CollectorClient


def _post_json(url: str, payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            raw = response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:300]
        raise RuntimeError(f"Provider returned HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Provider request failed: {exc.reason}") from exc
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Provider returned invalid JSON") from exc


def run_reasoning_smoke(prompt: str, client: CollectorClient | None = None) -> dict[str, Any]:
    api_key = os.getenv("LLM_API_KEY")
    if not api_key:
        raise SystemExit("LLM_API_KEY is required")

    collector = client or CollectorClient()
    sid = f"lily-flight-reasoning-{uuid.uuid4()}"
    corr = str(uuid.uuid4())
    provider = os.getenv("LLM_PROVIDER", "openai-compatible")
    model = os.getenv("LLM_MODEL", "reasoning-model")
    base_url = os.getenv("LLM_BASE_URL", "http://127.0.0.1:8000/v1").rstrip("/")
    thinking = os.getenv("LLM_REASONING_MODE", "enabled").strip().lower()

    collector.emit("SessionStart", sid, metadata={"runtime": "lily-flight", "reasoning_smoke": True})
    collector.emit(
        "UserPromptSubmit",
        sid,
        tool_input={"prompt": prompt},
        metadata={"blocking": True, "reasoning_smoke": True},
    )
    collector.emit(
        "PreLLMCall",
        sid,
        tool_name="llm.chat",
        tool_input={"message_count": 1, "tools": []},
        metadata={"provider": provider, "model": model, "blocking": True},
        correlation_id=corr,
    )

    payload: dict[str, Any] = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": float(os.getenv("LLM_TEMPERATURE", "0.6")),
    }
    if thinking not in {"", "none", "off", "false", "0"}:
        payload["thinking"] = {"type": thinking}

    start = time.time()
    data = _post_json(
        f"{base_url}/chat/completions",
        payload,
        {
            "Authorization": f"Bearer {api_key}",
            "User-Agent": os.getenv("LLM_USER_AGENT", "agenthook-lily-flight/0.1"),
        },
    )
    duration_ms = int((time.time() - start) * 1000)
    usage = data.get("usage") or {}
    choice = (data.get("choices") or [{}])[0]
    message = choice.get("message") or {}
    content = message.get("content") or ""
    reasoning = message.get("reasoning_content") or message.get("reasoning") or ""

    collector.emit(
        "PostLLMCall",
        sid,
        tool_name="llm.chat",
        metadata={
            "provider": provider,
            "model": model,
            "duration_ms": duration_ms,
            "finish_reason": choice.get("finish_reason") or "stop",
            "tokens_input": usage.get("prompt_tokens", 0),
            "tokens_output": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
        },
        correlation_id=corr,
    )
    collector.emit(
        "ModelResponse",
        sid,
        tool_name="model.response",
        metadata={
            "provider": provider,
            "model": model,
            "response_content": content[:8000],
            "response_chars": len(content),
            "reasoning_available": bool(reasoning),
            "reasoning_content": reasoning[:16000] if reasoning else "",
            "reasoning_chars": len(reasoning),
            "reasoning_truncated": len(reasoning) > 16000,
            "provider_message_keys": sorted(message.keys()),
        },
        correlation_id=corr,
    )
    collector.emit("SessionEnd", sid, metadata={"status": "completed", "reasoning_smoke": True})
    return {
        "session_id": sid,
        "response_content": content,
        "reasoning_available": bool(reasoning),
        "reasoning_chars": len(reasoning),
    }
