"""Tiny AgentHook collector publisher used by the Lily flight test."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass
from typing import Any, Callable


Transport = Callable[[str, dict[str, str], bytes], dict[str, Any]]


@dataclass
class CollectorDecision:
    decision: str = "allow"
    reason: str = ""

    @property
    def denied(self) -> bool:
        return self.decision == "deny"


@dataclass
class CollectorConfig:
    url: str = os.getenv("AGENTHOOK_COLLECTOR_URL") or os.getenv("HOOKBUS_URL", "http://127.0.0.1:18800/event")
    token: str = os.getenv("AGENTHOOK_COLLECTOR_TOKEN") or os.getenv("HOOKBUS_TOKEN", "")
    source: str = os.getenv("AGENTHOOK_SOURCE") or os.getenv("HOOKBUS_SOURCE", "lily-flight")
    agent_id: str = os.getenv("AGENTHOOK_AGENT_ID", "lily-flight")


class CollectorClient:
    def __init__(self, config: CollectorConfig | None = None, transport: Transport | None = None):
        self.config = config or CollectorConfig()
        self.transport = transport or self._post_json

    def envelope(
        self,
        event_type: str,
        session_id: str,
        *,
        tool_name: str = "",
        tool_input: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        correlation_id: str = "",
    ) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "source": self.config.source,
            "agent_id": self.config.agent_id,
            "session_id": session_id,
            "correlation_id": correlation_id,
            "tool_name": tool_name,
            "tool_input": tool_input or {},
            "metadata": {
                "publisher": "lily-flight",
                "agenthook_standard": "https://agenthook.org",
                **(metadata or {}),
            },
        }

    def emit(
        self,
        event_type: str,
        session_id: str,
        *,
        tool_name: str = "",
        tool_input: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        correlation_id: str = "",
    ) -> CollectorDecision:
        envelope = self.envelope(
            event_type,
            session_id,
            tool_name=tool_name,
            tool_input=tool_input,
            metadata=metadata,
            correlation_id=correlation_id,
        )
        headers = {"Content-Type": "application/json"}
        if self.config.token:
            headers["Authorization"] = f"Bearer {self.config.token}"
        result = self.transport(self.config.url, headers, json.dumps(envelope).encode())
        return CollectorDecision(
            decision=str(result.get("decision", "allow")).lower(),
            reason=str(result.get("reason", "")),
        )

    @staticmethod
    def _post_json(url: str, headers: dict[str, str], body: bytes) -> dict[str, Any]:
        opener = urllib.request.build_opener(NoRedirectHandler)
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with opener.open(req, timeout=15) as response:
                raw = response.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            if 300 <= exc.code < 400:
                raise RuntimeError("Collector request redirected; refusing to forward authorization headers") from exc
            raise RuntimeError(f"Collector returned HTTP {exc.code}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Collector request failed: {exc.reason}") from exc
        try:
            return json.loads(raw) if raw else {"decision": "allow"}
        except json.JSONDecodeError as exc:
            raise RuntimeError("Collector returned invalid JSON") from exc


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None
