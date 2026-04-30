"""Deterministic 10-hook AgentHook preflight."""

from __future__ import annotations

import time
import uuid
from typing import Any

from .collector import CollectorClient


AGENTHOOK_HOOKS = [
    "SessionStart",
    "UserPromptSubmit",
    "PreLLMCall",
    "PostLLMCall",
    "ModelResponse",
    "PreToolUse",
    "PostToolUse",
    "AgentHandoff",
    "ErrorOccurred",
    "SessionEnd",
]


def run_preflight(client: CollectorClient | None = None, session_id: str | None = None) -> dict[str, Any]:
    collector = client or CollectorClient()
    sid = session_id or f"lily-flight-{uuid.uuid4()}"
    llm_corr = str(uuid.uuid4())
    tool_corr = str(uuid.uuid4())
    handoff_corr = str(uuid.uuid4())
    emitted: list[str] = []

    def emit(event_type: str, **kwargs) -> None:
        collector.emit(event_type, sid, **kwargs)
        emitted.append(event_type)

    emit("SessionStart", metadata={"runtime": "lily-flight", "preflight": True})
    emit(
        "UserPromptSubmit",
        tool_input={"prompt": "AgentHook flight test: exercise all standard hooks"},
        metadata={"blocking": True, "preflight": True},
    )
    emit(
        "PreLLMCall",
        tool_name="llm.chat",
        tool_input={"message_count": 1, "tools": ["bash"]},
        metadata={"provider": "preflight", "model": "preflight-model", "blocking": True},
        correlation_id=llm_corr,
    )
    emit(
        "PostLLMCall",
        tool_name="llm.chat",
        metadata={
            "provider": "preflight",
            "model": "preflight-model",
            "duration_ms": 1,
            "finish_reason": "stop",
            "tokens_input": 4,
            "tokens_output": 6,
            "total_tokens": 10,
        },
        correlation_id=llm_corr,
    )
    emit(
        "ModelResponse",
        tool_name="model.response",
        metadata={
            "provider": "preflight",
            "model": "preflight-model",
            "response_content": "TASK COMPLETE AgentHook flight-test model response",
            "response_chars": 50,
            "reasoning_available": True,
            "reasoning_content": "Preflight reasoning trace: verify subscriber handling without external model calls.",
            "reasoning_chars": 76,
            "reasoning_truncated": False,
        },
        correlation_id=llm_corr,
    )
    emit(
        "PreToolUse",
        tool_name="bash",
        tool_input={"command": "pwd"},
        metadata={"blocking": True, "preflight": True},
        correlation_id=tool_corr,
    )
    start = time.time()
    emit(
        "PostToolUse",
        tool_name="bash",
        tool_input={"command": "pwd"},
        metadata={
            "duration_ms": int((time.time() - start) * 1000),
            "result_preview": "<lily-flight-working-directory>",
            "preflight": True,
        },
        correlation_id=tool_corr,
    )
    emit(
        "AgentHandoff",
        tool_name="agent.handoff",
        tool_input={"from_agent": "lily-flight", "to_agent": "agenthook-preflight-reviewer"},
        metadata={
            "from_agent": "lily-flight",
            "to_agent": "agenthook-preflight-reviewer",
            "handoff_reason": "verify AgentHook handoff event availability",
            "preflight": True,
        },
        correlation_id=handoff_corr,
    )
    emit(
        "ErrorOccurred",
        tool_name="preflight.error",
        metadata={
            "phase": "preflight",
            "error": "intentional preflight error event",
            "handled": True,
            "preflight": True,
        },
    )
    emit("SessionEnd", metadata={"status": "completed", "preflight": True})
    return {"session_id": sid, "events": emitted}
