"""Deterministic AgentHook preflight."""

from __future__ import annotations

import time
import uuid
from typing import Any

from .collector import CollectorClient


AGENTHOOK_HOOKS = [
    "RuntimeContractLoaded",
    "SessionStart",
    "UserPromptSubmit",
    "PreLLMCall",
    "PostLLMCall",
    "ModelResponse",
    "PreToolUse",
    "ToolActivity",
    "PostToolUse",
    "HumanApprovalRequested",
    "HumanDecision",
    "AgentHandoff",
    "ErrorOccurred",
    "IncidentSignal",
    "EvidenceSeal",
    "SessionEnd",
]


def run_preflight(client: CollectorClient | None = None, session_id: str | None = None) -> dict[str, Any]:
    collector = client or CollectorClient()
    sid = session_id or f"agenthook-fixture-{uuid.uuid4()}"
    llm_corr = str(uuid.uuid4())
    tool_corr = str(uuid.uuid4())
    handoff_corr = str(uuid.uuid4())
    emitted: list[str] = []

    def emit(event_type: str, **kwargs) -> None:
        collector.emit(event_type, sid, **kwargs)
        emitted.append(event_type)

    emit(
        "RuntimeContractLoaded",
        metadata={
            "contract": {
                "id": "agenthook-fixture-preflight",
                "version": "0.1",
                "path": "./agenthook.lock.json",
                "human_readable_path": "./AGENTHOOK.md",
                "hash": "sha256:preflight-example",
                "signature_valid": True,
                "required_hooks": [
                    "SessionStart",
                    "UserPromptSubmit",
                    "PreToolUse",
                    "ToolActivity",
                    "PostToolUse",
                    "HumanDecision",
                    "EvidenceSeal",
                ],
                "conformance_mode": "gold",
            },
            "preflight": True,
        },
    )
    emit("SessionStart", metadata={"runtime": "agenthook-fixture", "preflight": True, "contract_hash": "sha256:preflight-example"})
    emit(
        "UserPromptSubmit",
        tool_input={"prompt": "AgentHook conformance fixture: exercise all standard hooks"},
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
            "response_content": "TASK COMPLETE AgentHook conformance fixture model response",
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
        "ToolActivity",
        tool_name="bash",
        tool_input={"command": "pwd"},
        metadata={
            "activity_type": "shell.process_spawn",
            "parent_event_id": "preflight-parent-tool-event",
            "target": "pwd",
            "decision": "allow",
            "preflight": True,
        },
        correlation_id=tool_corr,
    )
    emit(
        "PostToolUse",
        tool_name="bash",
        tool_input={"command": "pwd"},
        metadata={
            "duration_ms": int((time.time() - start) * 1000),
            "result_preview": "<agenthook-fixture-working-directory>",
            "preflight": True,
        },
        correlation_id=tool_corr,
    )
    emit(
        "HumanApprovalRequested",
        tool_name="approval.request",
        tool_input={"action": "continue deterministic preflight"},
        metadata={
            "approval_ref": "approval-preflight-001",
            "scope": {"session_id": sid, "action": "preflight"},
            "preflight": True,
        },
    )
    emit(
        "HumanDecision",
        tool_name="approval.decision",
        tool_input={"approval_ref": "approval-preflight-001"},
        metadata={
            "approval_ref": "approval-preflight-001",
            "approver_ref": "human-preflight-reviewer",
            "authority": "fixture",
            "decision": "allow",
            "rationale": "Deterministic preflight approval record.",
            "preflight": True,
        },
    )
    emit(
        "AgentHandoff",
        tool_name="agent.handoff",
        tool_input={"from_agent": "agenthook-fixture", "to_agent": "agenthook-preflight-reviewer"},
        metadata={
            "from_agent": "agenthook-fixture",
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
    emit(
        "IncidentSignal",
        tool_name="incident.signal",
        metadata={
            "incident_ref": "incident-preflight-001",
            "severity": "informational",
            "signal": "synthetic incident signal for subscriber coverage",
            "preflight": True,
        },
    )
    emit(
        "EvidenceSeal",
        tool_name="evidence.seal",
        metadata={
            "evidence_ref": "evidence-preflight-001",
            "hash": "sha256:preflight-evidence-example",
            "retention": {
                "class": "preflight",
                "controller": "agenthook-fixture",
                "expires_at": None,
            },
            "preflight": True,
        },
    )
    emit("SessionEnd", metadata={"status": "completed", "preflight": True})
    return {"session_id": sid, "events": emitted}
