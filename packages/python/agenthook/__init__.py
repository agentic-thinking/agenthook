"""AgentHook draft implementation kit.

This package provides small helpers for building and validating AgentHook
envelopes. It does not require HookBus; HookBus is one compatible target.
"""

from .envelope import (
    CANONICAL_EVENT_TYPES,
    SCHEMA_VERSION,
    build_event,
    evidence_defaults,
    model_response,
    post_tool_use,
    pre_tool_use,
    user_prompt_submit,
)
from .validate import ValidationError, validate_event

__all__ = [
    "CANONICAL_EVENT_TYPES",
    "SCHEMA_VERSION",
    "ValidationError",
    "build_event",
    "evidence_defaults",
    "model_response",
    "post_tool_use",
    "pre_tool_use",
    "user_prompt_submit",
    "validate_event",
]
