from __future__ import annotations

import json
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from .envelope import CANONICAL_EVENT_TYPES

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SCHEMA_PATH = _REPO_ROOT / "envelope.schema.json"


class ValidationError(Exception):
    pass


def load_schema(path: str | Path | None = None) -> dict[str, Any]:
    schema_path = Path(path) if path else _SCHEMA_PATH
    if schema_path.exists():
        return json.loads(schema_path.read_text(encoding="utf-8"))
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "required": ["event_id", "event_type", "timestamp", "source"],
        "properties": {
            "schema_version": {"type": "integer"},
            "event_id": {"type": "string", "format": "uuid"},
            "event_type": {
                "type": "string",
                "anyOf": [
                    {"enum": sorted(CANONICAL_EVENT_TYPES)},
                    {"pattern": "^[A-Z][A-Za-z0-9]*$"},
                ],
            },
            "timestamp": {"type": "string", "format": "date-time"},
            "source": {"type": "string"},
            "agent_id": {"type": "string"},
            "session_id": {"type": "string"},
            "correlation_id": {"type": "string"},
            "evidence_phase": {"type": "string"},
            "tool_name": {"type": "string"},
            "tool_input": {"type": "object"},
            "action": {"type": "string"},
            "resource_kind": {"type": "string"},
            "resource": {"oneOf": [{"type": "string"}, {"type": "object"}]},
            "resource_scope": {"type": "string"},
            "operation_risk": {"type": "string"},
            "metadata": {"type": "object"},
            "annotations": {"type": "object"},
        },
        "additionalProperties": False,
    }


def _fallback_validate(event: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in ("event_id", "event_type", "timestamp", "source"):
        if field not in event:
            errors.append(f"missing required field: {field}")
    try:
        uuid.UUID(str(event.get("event_id", "")))
    except Exception:
        errors.append("event_id must be a UUID")
    if not re.match(r"^[A-Z][A-Za-z0-9]*$", str(event.get("event_type", ""))):
        errors.append(f"event_type must be canonical or PascalCase: {event.get('event_type')!r}")
    ts = str(event.get("timestamp", ""))
    try:
        datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        errors.append("timestamp must be ISO 8601 date-time")
    if not isinstance(event.get("source", ""), str) or not event.get("source", ""):
        errors.append("source must be a non-empty string")
    if "tool_input" in event and not isinstance(event["tool_input"], dict):
        errors.append("tool_input must be an object")
    if "evidence_phase" in event and event["evidence_phase"] not in {"pre_commit", "post_hoc", "observational"}:
        errors.append("evidence_phase must be pre_commit, post_hoc, or observational")
    for field in ("action", "resource_kind", "resource_scope", "operation_risk"):
        if field in event and not isinstance(event[field], str):
            errors.append(f"{field} must be a string")
    if "resource" in event and not isinstance(event["resource"], (str, dict)):
        errors.append("resource must be a string or object")
    if "metadata" in event and not isinstance(event["metadata"], dict):
        errors.append("metadata must be an object")
    if "annotations" in event and not isinstance(event["annotations"], dict):
        errors.append("annotations must be an object")
    extras = set(event) - {
        "schema_version",
        "event_id",
        "event_type",
        "timestamp",
        "source",
        "agent_id",
        "session_id",
        "correlation_id",
        "evidence_phase",
        "tool_name",
        "tool_input",
        "action",
        "resource_kind",
        "resource",
        "resource_scope",
        "operation_risk",
        "metadata",
        "annotations",
    }
    if extras:
        errors.append("unknown top-level fields: " + ", ".join(sorted(extras)))
    if not re.match(r"^[A-Za-z0-9_.:-]+$", str(event.get("source", ""))):
        errors.append("source should be a stable runtime identifier")
    return errors


def validate_event(event: dict[str, Any], schema_path: str | Path | None = None) -> list[str]:
    """Return validation errors. Empty list means valid.

    Uses jsonschema if installed, otherwise a strict fallback validator covering
    the AgentHook v0.2 required fields.
    """
    try:
        import jsonschema  # type: ignore
    except Exception:
        return _fallback_validate(event)

    schema = load_schema(schema_path)
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    return [e.message for e in sorted(validator.iter_errors(event), key=lambda e: e.path)]


def assert_valid(event: dict[str, Any], schema_path: str | Path | None = None) -> None:
    errors = validate_event(event, schema_path)
    if errors:
        raise ValidationError("; ".join(errors))
