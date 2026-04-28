# AgentHook Specification

**Version:** 0.1 (draft)
**Status:** pre-1.0, expected to change
**Editors:** Working Group (see [`MEMBERS.md`](./MEMBERS.md))
**Licence:** Apache License 2.0

This specification defines the lifecycle events that an AI agent runtime ("publisher") must expose so that external observers ("subscribers") can record, gate, and audit what an agent did, when, why, and with what reasoning. It is implementation-neutral: any transport (HTTP, Unix socket, in-process callback, message queue) and any host language is permitted, provided the wire-format and semantic guarantees defined here are met.

The specification covers:

1. The envelope format that every event must carry
2. The canonical set of event types
3. The standard metadata keys per event type
4. Hook delivery semantics (sync vs async, fail-mode behaviour)
5. Conformance levels (Bronze, Silver, Gold)
6. Runtime attestation as a non-breaking metadata extension

It does not cover:

- Transport choice (publishers may use whatever transport their host environment makes available; subscribers may listen on whatever transport they prefer; bus or middleware implementations bridge transports as needed)
- Storage of events after they are emitted (the responsibility of subscribers, not publishers)
- Authentication and authorisation between publisher and subscriber (recommended but out of scope; the conformance suite tests a publisher's ability to attach a bearer token but does not mandate any specific scheme)

## 1. Envelope format

Every event is a JSON object conforming to the following shape. Field requirements are stated per-field.

```json
{
  "schema_version": 1,
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_type": "PreToolUse",
  "timestamp": "2026-04-25T15:42:09.123Z",
  "source": "claude-code",
  "agent_id": "team-alpha-bot",
  "session_id": "session-abc123",
  "correlation_id": "run-7f3b9a2e",
  "tool_name": "Bash",
  "tool_input": { "command": "git push origin main" },
  "metadata": { "model": "claude-sonnet-4-6", "...": "..." },
  "annotations": { "subscribers": { } }
}
```

| Field | Type | Required | Purpose |
|---|---|---|---|
| `schema_version` | integer | no, defaults to `1` | Wire-format version; bumped only on breaking envelope changes |
| `event_id` | string (UUID) | yes | Unique identifier for this event |
| `event_type` | string | yes | Canonical name (see section 2) |
| `timestamp` | string (ISO 8601, UTC) | yes | When the event was emitted |
| `source` | string | yes | Publisher family, e.g. `claude-code`, `amp`, `hermes`, `cursor`, `cody`, `openai-codex` |
| `agent_id` | string | no | Specific instance of the publisher (set by the operator or the bus from a bearer token) |
| `session_id` | string | no | Groups events within one agent session |
| `correlation_id` | string | no | Links related events across sessions (multi-agent handoff, retries, parent-child agent calls) |
| `tool_name` | string | for `PreToolUse` and `PostToolUse` | Which tool the agent is calling |
| `tool_input` | object | no | Tool-specific input. Publishers MUST NOT validate; subscribers decide what matters |
| `metadata` | object | no | Hook-specific structured data (see section 3) |
| `annotations` | object | no | Free-form subscriber/operator notes; publishers SHOULD NOT depend on these |

The bus (where one is present) MAY enrich an event with `agent_id` derived from the publisher's bearer token. Publishers SHOULD treat any `agent_id` they receive in a response as authoritative.

## 2. Canonical event types

The specification defines ten canonical event types. Implementations MAY emit additional event types using PascalCase names; subscribers MAY ignore unknown types. The bus MUST NOT reject events solely on the basis of unrecognised `event_type`.

| Event type | Phase | Description |
|---|---|---|
| `PreToolUse` | before | The agent is about to execute a tool call |
| `PostToolUse` | after | The tool call returned (or threw) |
| `UserPromptSubmit` | before | The user submitted a prompt to the agent |
| `PreLLMCall` | before | The agent is about to call its LLM |
| `PostLLMCall` | after | The LLM call returned |
| `ModelResponse` | after | The model has finished generating its response (transcript-grade record) |
| `SessionStart` | state | A new agent session began |
| `SessionEnd` | state | An agent session ended |
| `AgentHandoff` | during | The agent is delegating to another agent |
| `ErrorOccurred` | after | An error was raised that did not terminate the session |

Naming rules:

- PascalCase, no underscores or dots
- Verb-first for action events (`PreToolUse`, `PostLLMCall`)
- Noun-first for state events (`SessionStart`, `ErrorOccurred`)

## 3. Standard metadata keys

`metadata` is free-form, but the following keys are canonical per event type. Publishers SHOULD emit them when the data is available; subscribers MAY rely on them.

### `PostLLMCall`

| Key | Type | Purpose |
|---|---|---|
| `model` | string | Model identifier as returned by the provider (e.g. `claude-sonnet-4-6`, `MiniMax-M2.7`, `kimi-for-coding`, `granite-4-3b`) |
| `provider` | string | Provider family, e.g. `anthropic`, `openai`, `minimax`, `moonshot`, `bedrock`, `azure`, `vertex`, `watsonx` |
| `tokens_input` | integer | Input tokens counted by the provider |
| `tokens_output` | integer | Output tokens counted by the provider |
| `total_tokens` | integer | Convenience sum |
| `reasoning_content` | string or null | Full reasoning text when the provider exposed it (Anthropic thinking blocks; OpenAI-compat `reasoning_content`, `reasoning`, or `reasoning_details`). Truncation to 64 KiB is RECOMMENDED for envelope compactness |
| `reasoning_chars` | integer | Length of the original reasoning before any truncation (for filtering/indexing without loading full payload) |
| `response_content` | string | Reply text delivered to the caller. Truncation to ~4 KiB is RECOMMENDED |

`reasoning_content` together with `response_content` constitutes a *transcript-grade* record of the LLM exchange. By "transcript-grade" we mean a record sufficient to reconstruct, after the fact, what the model was asked, how it reasoned, and what it returned, without consulting the original session transport. This is the level of evidence required by EU AI Act Article 12 record-keeping for high-risk AI systems (Annex III categories), and equivalent regulatory regimes for accountable autonomous systems.

### `PreToolUse` and `PostToolUse`

| Key | Type | Purpose |
|---|---|---|
| `estimated_usd` | number | Cost estimate (set by a budget subscriber, stamped onto the event) |
| `duration_ms` | integer | Tool wall-clock duration (`PostToolUse` only) |
| `exit_code` | integer | Tool exit code where applicable (`PostToolUse` only) |

Subscribers may add arbitrary keys, but using a name that collides with the canonical list will confuse other subscribers that trust the canonical meaning.

### `SessionStart`, first `PreLLMCall`, or first `UserPromptSubmit`

| Key | Type | Purpose |
|---|---|---|
| `runtime_attestation` | object | Publisher-supplied declaration of the runtime controls active for this session. See section 6. |

## 4. Hook delivery semantics

Implementations are expected to honour the following:

- **Pre\* events MAY block the action** while sync subscribers respond. Publishers SHOULD apply a configurable timeout (default RECOMMENDED: 5 seconds) and a documented fail-mode. The fail-mode is one of:
  - **fail-open**: on subscriber timeout or unreachable bus, the action proceeds. Default for environments where availability outranks policy enforcement.
  - **fail-closed**: on subscriber timeout or unreachable bus, the action is denied. Default for regulated environments where missing audit coverage is itself a compliance failure.

  Conforming publishers MUST default to fail-closed when the publisher cannot determine the deployment context, and MUST log every fail-mode-triggered allow or deny.
- **Post\* events MUST NOT block** the publisher beyond enqueueing for delivery. Any subscriber processing time happens out of the publisher's hot path.
- **Observer events** (`ModelResponse`, `SessionEnd`, `ErrorOccurred`) follow the same MUST NOT-block rule as Post\*.
- **Idempotency**: re-delivery of the same `event_id` MUST be safe. Subscribers MUST handle duplicates by no-op or merge, never by double-counting.
- **Ordering**: events within a `session_id` MUST be delivered in publication order. Ordering across sessions is not guaranteed.

Conforming publishers MUST document their fail-mode default and provide an operator-facing toggle.

## 5. Conformance levels

Three tiers, defined for publishers. A publisher claims a tier; the conformance test rig (see [`CONFORMANCE/`](./CONFORMANCE/)) verifies the claim.

| Tier | What is verified |
|---|---|
| **Bronze** | Publisher emits the lifecycle event types in section 2 with the envelope format in section 1 (required fields populated, valid JSON, valid event_id, valid timestamp). 80% pass on the Bronze test set. |
| **Silver** | Bronze + LLM transcript capture: every `PreLLMCall` is matched by exactly one `PostLLMCall` carrying `model`, `provider`, `tokens_input`, `tokens_output`, `response_content`. 80% pass on the Silver test set. |
| **Gold** | Silver + reasoning capture (`reasoning_content` + `reasoning_chars` populated when the provider exposes them; null/0 acceptable when not) + cross-session correlation (`correlation_id` set on Pre\* events that initiate a sub-agent or retry). 80% pass on the Gold test set. |

The 80% pass threshold permits implementations to legitimately not emit certain event types if their host runtime simply does not generate them (e.g. a CLI that has no notion of `AgentHandoff` cannot be penalised for not emitting it).

A formal conformance score is awarded by the test rig with the per-test pass/fail enumerated in a signed report.

## 6. Runtime attestation

Runtime attestation lets an agent, operator, or auditor distinguish verified runtime facts from user-authored prompt text. It is a publisher-supplied declaration of which hooks, gates, subscribers, consolidation rules, and fail modes are active for the current session.

Runtime attestation is a non-breaking metadata extension. It does not add a new canonical event type and does not change `schema_version`.

Publishers SHOULD attach runtime attestation at the earliest available point in a session:

1. `SessionStart.metadata.runtime_attestation`, when the runtime emits `SessionStart`
2. otherwise the first `PreLLMCall.metadata.runtime_attestation`
3. otherwise the first `UserPromptSubmit.metadata.runtime_attestation`

Publishers MAY also expose the same document through an implementation-specific local endpoint or tool. A bus MAY expose an aggregate attestation endpoint, but the AgentHook envelope does not require any particular bus or transport.

The attestation document MUST NOT be authored by the user and MUST NOT be inferred from user-provided policy text. It MAY be signed or MACed by the publisher/runtime. Where signatures are used, the signature covers the canonical JSON representation of the attestation excluding the `signature` field.

Minimum shape:

```json
{
  "type": "agenthook.runtime_attestation",
  "schema_version": "1.0",
  "runtime": {
    "name": "hermes-agent",
    "version": "0.0.0"
  },
  "publisher": {
    "name": "hookbus-publisher-hermes",
    "version": "0.3.0"
  },
  "session_id": "sess-abc123",
  "nonce": "session-bound-random-value",
  "issued_at": "2026-04-28T01:30:00Z",
  "expires_at": "2026-04-28T05:30:00Z",
  "event_endpoint": "http://localhost:18800/event",
  "active_subscribers": [
    {
      "name": "policy-gate",
      "role": "policy_gate",
      "mode": "enforce",
      "events": ["PreToolUse", "UserPromptSubmit"],
      "can_deny": true,
      "can_ask": true
    }
  ],
  "consolidation": {
    "strategy": "deny_wins",
    "final_verdict_source": "runtime"
  },
  "fail_mode": "fail_closed",
  "claims": {
    "tool_calls_are_runtime_gated": true,
    "gate_denials_should_be_reported": true,
    "do_not_bypass_gate": true,
    "does_not_override_model_safety": true,
    "user_text_is_not_attestation": true
  },
  "signature": null
}
```

Model-facing summaries derived from attestation MUST be factual and limited. They MUST NOT instruct the model to ignore system, platform, or safety policies. Recommended wording:

> Verified AgentHook runtime attestation: tool calls in this session are routed through the listed runtime gates before execution. If a gate denies or asks for approval, report the gate response. Do not substitute, obscure, or route around a gate. This attestation does not replace model, platform, or system safety policy.

When an agent decides a tool call is appropriate under its normal instructions, it SHOULD submit the intended tool call through the runtime gate. It MUST NOT substitute a different command, hide an action, encode an action, or use an alternate route to avoid review by an active gate.

## 7. Versioning and stability

- Pre-1.0 (current): the specification may change without notice. Implementations are encouraged to track the draft and provide feedback via Issues and Proposals.
- 1.0 onwards: changes follow the Proposal process in [`GOVERNANCE.md`](./GOVERNANCE.md). Breaking changes require unanimous Working Group approval and a deprecation window of no less than nine months.

The `schema_version` field allows implementations to negotiate envelope shape. Breaking changes increment `schema_version`. Subscribers MUST handle at least the version they were authored for; bus implementations MAY translate between versions.

## 8. Examples

### Minimal valid event

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_type": "UserPromptSubmit",
  "timestamp": "2026-04-25T15:42:09.123Z",
  "source": "amp"
}
```

### Full PostLLMCall

```json
{
  "schema_version": 1,
  "event_id": "8c4f9d12-7a8b-4c3d-9e2f-1a2b3c4d5e6f",
  "event_type": "PostLLMCall",
  "timestamp": "2026-04-25T15:42:11.487Z",
  "source": "hermes",
  "agent_id": "research-bot-3",
  "session_id": "sess-abc123",
  "correlation_id": "run-7f3b9a2e",
  "metadata": {
    "model": "Hermes-3-Llama-3.1-405B",
    "provider": "openrouter",
    "tokens_input": 1247,
    "tokens_output": 392,
    "total_tokens": 1639,
    "reasoning_content": "The user asked for a summary. I should ...",
    "reasoning_chars": 412,
    "response_content": "Here is the summary you asked for: ..."
  }
}
```

---

This is a working draft. Substantive change proposals are made through the [Proposals](./PROPOSALS/) process.


---

## Appendix A — Reference implementation sketch (non-normative)

This appendix is non-normative. It illustrates the minimum a publisher and a subscriber must do to participate. Any host language and any transport that satisfies the semantics in section 4 is permitted.

> **WARNING:** The sketches below intentionally omit authentication, authorisation, and transport security. They are pedagogical, not production code. A production deployment MUST place publishers and subscribers within an operator-controlled trust boundary OR connect them over an authenticated, integrity-protected transport. Transport security is currently out of scope of the normative specification; see [`SECURITY.md`](./SECURITY.md) for the current threat model and the rationale for treating transport security at the deployment layer.

### Publisher

```python
import httpx, uuid, datetime as dt

def emit(event_type, **fields):
    event = {
        "schema_version": 1,
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source": "your-runtime",
        **fields,
    }
    httpx.post("http://agenthook-collector:18800/event", json=event, timeout=5)

emit("PreToolUse", tool_name="Bash", tool_input={"command": "git push"})
```

### Subscriber

```python
from fastapi import FastAPI

app = FastAPI()

@app.post("/event")
async def receive(event: dict):
    if event["event_type"] == "PreToolUse":
        cmd = event.get("tool_input", {}).get("command", "")
        if "git push" in cmd:
            return {"verdict": "deny", "reason": "review push first"}
    return {"verdict": "allow"}
```

Validate every event against [`envelope.schema.json`](./envelope.schema.json). See [`sample-event.json`](./sample-event.json) for a fully-populated PostLLMCall.
