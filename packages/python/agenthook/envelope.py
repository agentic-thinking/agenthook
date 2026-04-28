from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

SCHEMA_VERSION = 1

CANONICAL_EVENT_TYPES = {
    "PreToolUse",
    "PostToolUse",
    "UserPromptSubmit",
    "PreLLMCall",
    "PostLLMCall",
    "ModelResponse",
    "SessionStart",
    "SessionEnd",
    "AgentHandoff",
    "ErrorOccurred",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def evidence_defaults(**overrides: Any) -> dict[str, Any]:
    """Return canonical evidence-availability metadata.

    Publishers should emit explicit availability state instead of omitting
    fields silently. Values may be overridden when the runtime exposes data.
    """
    data: dict[str, Any] = {
        "response_available": False,
        "response_text": None,
        "response_chars": 0,
        "reasoning_available": False,
        "reasoning_content": None,
        "reasoning_chars": 0,
        "reasoning_redacted": False,
        "reasoning_signature_present": False,
        "reasoning_unavailable_reason": "not_exposed_by_runtime",
        "transcript_available": False,
        "transcript_path": None,
        "evidence_origin": "adapter",
        "control_point": "observational",
        "enforcement_capable": False,
        "agenthook_standard": "https://agenthook.org",
    }
    data.update(overrides)
    return data


def build_event(
    event_type: str,
    source: str,
    session_id: str = "",
    *,
    tool_name: str = "",
    tool_input: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
    agent_id: str = "",
    correlation_id: str = "",
    event_id: str | None = None,
    timestamp: str | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "event_id": event_id or str(uuid.uuid4()),
        "event_type": event_type,
        "timestamp": timestamp or utc_now(),
        "source": source,
        "agent_id": agent_id,
        "session_id": session_id,
        "correlation_id": correlation_id,
        "tool_name": tool_name,
        "tool_input": tool_input or {},
        "metadata": metadata or {},
        "annotations": {},
    }


def pre_tool_use(source: str, session_id: str, tool_name: str, tool_input: dict[str, Any]) -> dict[str, Any]:
    return build_event(
        "PreToolUse",
        source,
        session_id,
        tool_name=tool_name,
        tool_input=tool_input,
        metadata=evidence_defaults(control_point="pre_action", enforcement_capable=True),
    )


def post_tool_use(
    source: str,
    session_id: str,
    tool_name: str,
    tool_input: dict[str, Any],
    *,
    exit_code: int | None = None,
    duration_ms: int | None = None,
) -> dict[str, Any]:
    metadata = evidence_defaults(control_point="post_action")
    if exit_code is not None:
        metadata["exit_code"] = exit_code
    if duration_ms is not None:
        metadata["duration_ms"] = duration_ms
    return build_event("PostToolUse", source, session_id, tool_name=tool_name, tool_input=tool_input, metadata=metadata)


def user_prompt_submit(source: str, session_id: str, prompt: str) -> dict[str, Any]:
    return build_event(
        "UserPromptSubmit",
        source,
        session_id,
        tool_input={"prompt": prompt},
        metadata=evidence_defaults(control_point="pre_action"),
    )


def model_response(
    source: str,
    session_id: str,
    *,
    response_text: str | None = None,
    reasoning_content: str | None = None,
    provider: str = "",
    model: str = "",
    transcript_path: str | None = None,
) -> dict[str, Any]:
    metadata = evidence_defaults(provider=provider, model=model)
    if response_text:
        metadata.update(response_available=True, response_text=response_text, response_chars=len(response_text))
    if reasoning_content:
        metadata.update(
            reasoning_available=True,
            reasoning_content=reasoning_content,
            reasoning_chars=len(reasoning_content),
            reasoning_unavailable_reason="",
        )
    if transcript_path:
        metadata.update(transcript_available=True, transcript_path=transcript_path)
    return build_event("ModelResponse", source, session_id, tool_name="llm.response", metadata=metadata)
