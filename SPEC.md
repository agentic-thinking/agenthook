# AgentHook Specification

**Version:** 0.1 (draft)
**Status:** pre-1.0, expected to change
**Editors:** Working Group (see [`MEMBERS.md`](./MEMBERS.md))
**Licence:** Apache License 2.0

This specification defines the lifecycle events that an AI agent runtime ("publisher") must expose so that external observers ("subscribers") can record, gate, and audit what an agent did, when, why, and with what reasoning where that reasoning is exposed by the runtime or provider. It is implementation-neutral: any transport (HTTP, Unix socket, in-process callback, message queue) and any host language is permitted, provided the wire-format and semantic guarantees defined here are met.

The specification covers:

1. The envelope format that every event must carry
2. The canonical set of event types
3. The standard metadata keys per event type
4. Hook delivery semantics (sync vs async, fail-mode behaviour)
5. Conformance levels (Bronze, Silver, Gold)
6. Runtime attestation as a non-breaking metadata extension
7. Publisher manifests as an interim local-first identity, coverage, and verification layer
8. Managed runtime identity and approval metadata for enterprise deployments

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
  "evidence_phase": "pre_commit",
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
| `evidence_phase` | string enum | no | Evidence class for this event: `pre_commit`, `post_hoc`, or `observational` |
| `tool_name` | string | for `PreToolUse` and `PostToolUse` | Which tool the agent is calling |
| `tool_input` | object | no | Tool-specific input. Publishers MUST NOT validate; subscribers decide what matters |
| `metadata` | object | no | Hook-specific structured data (see section 3) |
| `annotations` | object | no | Free-form subscriber/operator notes; publishers SHOULD NOT depend on these |

The bus (where one is present) MAY enrich an event with `agent_id` derived from the publisher's bearer token. Publishers SHOULD treat any `agent_id` they receive in a response as authoritative.

`evidence_phase` distinguishes the audit meaning of an event from its event name:

- `pre_commit`: the event was emitted before the action committed and, where applicable, the publisher waited for the configured admission decision or fail-mode.
- `post_hoc`: the event was emitted after the action committed.
- `observational`: the event records runtime state or model output and is not represented as an authorisation receipt.

Publishers MUST NOT represent `post_hoc` or `observational` events as equivalent to `pre_commit` authorisation evidence.

### Identity metadata

For shared or central collectors, publishers SHOULD include stable, non-secret identity metadata where available. These keys are advisory evidence unless verified or stamped by the collector.

AgentHook deployments MAY be single-publisher local installs, multi-publisher team buses, or centrally shared collectors across organisational boundaries. Identity metadata supports the shared cases without requiring any deployment to use a central collector.

| Metadata key | Type | Purpose |
|---|---|---|
| `publisher_id` | string | Stable publisher package/type identifier, usually matching the publisher manifest; not an individual installation |
| `user_id` | string | Human user or pseudonymous user reference for the session |
| `account_id` | string | Runtime/provider account reference where distinct from `user_id` |
| `instance_id` | string | Local publisher/runtime installation instance |
| `host_id` | string | Machine, container, or workload identity, preferably pseudonymous |

Publishers MUST NOT place secrets, bearer tokens, private credentials, or raw personal data in identity metadata. Central buses SHOULD derive authoritative identity from authentication where possible and MAY overwrite `agent_id` or add verified identity annotations before routing to subscribers.

Pseudonymous identifiers are still attributable operational metadata. Implementers SHOULD treat `user_id`, `account_id`, `instance_id`, and `host_id` as subject to retention, access-control, audit, and cross-border transfer policies. Pseudonymous does not mean anonymous.

### Managed runtime identity and device registry

Enterprise deployments often need to distinguish an approved user from an approved runtime instance and an approved device or workload. A user may be authorised to use a runtime family or API key, but a specific session is still unmanaged if the publisher is missing, the instance is unknown, or the event cannot be tied to an approved device, host, container, or workload.

Publishers MAY include managed runtime identity metadata inside `metadata.managed_runtime`. This object describes the stable publisher installation that emitted the event, plus optional registry context for the device or workload that ran it. It is not a permission grant by itself.

AgentHook does not claim to discover every AI tool, model client, API call, or browser session on an enterprise network. Managed runtime identity applies to participating publishers and to integrated enterprise controls that emit comparable AgentHook evidence. Activity outside the managed runtime registry remains the responsibility of the implementing organisation's MDM, EDR, proxy, SASE, CASB, SIEM, identity governance, procurement, and acceptable-use enforcement.

Minimum shape:

```json
{
  "metadata": {
    "managed_runtime": {
      "publisher_id": "org.example.publisher.codex-cli",
      "runtime_id": "codex-cli",
      "instance_id": "pubinst_7f91c2",
      "session_id": "sess_abc123",
      "user_ref": "user_8a21",
      "device_ref": "device_042",
      "approval_ref": "approval_12345",
      "registry_ref": "registry_entry_9c12",
      "registration_status": "registered",
      "approval_status": "approved",
      "verification_strength": "registered",
      "device_registry": {
        "registry_id": "org.example.mdm",
        "registry_type": "mdm",
        "entry_ref": "mdm_device_042",
        "binding": "device",
        "posture": "compliant",
        "last_verified_at": "2026-04-29T09:25:00Z"
      }
    }
  }
}
```

| Field | Type | Purpose |
|---|---|---|
| `publisher_id` | string | Stable publisher package/type identifier |
| `runtime_id` | string | Runtime family or product identifier |
| `instance_id` | string | Stable local publisher/runtime installation identity. This SHOULD persist across sessions until explicitly rotated or revoked |
| `session_id` | string | Current runtime session. This SHOULD change per session and SHOULD match the envelope `session_id` where possible |
| `user_ref` | string | Pseudonymous user, account, or principal reference |
| `device_ref` | string | Pseudonymous device, host, container, or workload reference |
| `approval_ref` | string | Optional reference to an enterprise approval, change ticket, registry entry, or workflow item |
| `registry_ref` | string | Optional reference to the enterprise registry entry for this publisher/runtime instance |
| `registration_status` | enum | `unregistered`, `registered`, `revoked`, or `unknown` |
| `approval_status` | enum | `approved`, `pending`, `denied`, `expired`, or `unknown` |
| `verification_strength` | enum | `self_declared`, `registered`, `signed`, or `device_attested` |
| `device_registry` | object | Optional advisory device, workload, or host registry binding |

`device_registry` is intentionally generic. It MAY represent MDM, CMDB, EDR, IAM, SPIFFE/SPIRE, Kubernetes workload identity, TPM-backed attestation, VDI inventory, a cloud instance registry, or a manual enterprise register.

| Device registry field | Type | Purpose |
|---|---|---|
| `registry_id` | string | Stable identifier for the registry or control plane |
| `registry_type` | enum | `mdm`, `cmdb`, `edr`, `iam`, `spiffe`, `kubernetes`, `cloud`, `tpm`, `vdi`, `manual`, or `other` |
| `entry_ref` | string | Pseudonymous registry entry reference |
| `binding` | enum | `device`, `host`, `container`, `workload`, `user_device`, or `service_account` |
| `posture` | enum | `compliant`, `non_compliant`, `unknown`, `not_checked`, or `not_applicable` |
| `last_verified_at` | string | ISO 8601 timestamp for the last registry/posture verification |
| `expires_at` | string | Optional expiry for the registry binding or posture check |

`instance_id` is the stable identity that lets an enterprise recognise "this installed publisher on this device or workload" across multiple sessions. `device_ref` links that runtime instance to the host, device, container, or workload where it ran. `session_id` remains per-session. `event_id` remains per-event.

Verification strength semantics:

- `self_declared`: the publisher supplied the fields, but no external registry or signature has verified them.
- `registered`: a collector, gateway, or policy subscriber matched the instance against an enterprise registry.
- `signed`: the event or attestation is signed or MACed by a key bound to the registered instance.
- `device_attested`: the instance is also bound to a verified device, workload identity, MDM record, SPIFFE identity, TPM-backed attestation, or equivalent enterprise control.

Consumers MUST treat `managed_runtime` as evidence, not authority. A publisher claiming `approval_status: "approved"` MUST NOT be sufficient for an allow decision unless a subscriber, collector, gateway, or enterprise registry independently verifies the claim. Gateways and policy subscribers SHOULD be able to block, ask, quarantine, or route activity from participating publishers or integrated enterprise controls when `managed_runtime` is absent, unknown, revoked, expired, below the required `verification_strength`, or not bound to an approved device/workload registry entry. Implementations MUST NOT claim complete network-wide discovery unless integrated with enterprise controls that provide that visibility.

Where a bus verifies identity from authentication, it SHOULD keep publisher-supplied claims separate from verified identity, for example:

```json
{
  "agent_id": "runtime-instance-01",
  "metadata": {
    "publisher_id": "uk.example.publisher.runtime",
    "instance_id": "runtime-instance-01",
    "managed_runtime": {
      "publisher_id": "uk.example.publisher.runtime",
      "runtime_id": "example-runtime",
      "instance_id": "runtime-instance-01",
      "device_ref": "device_042",
      "registry_ref": "registry_entry_9c12",
      "registration_status": "registered",
      "approval_status": "approved",
      "verification_strength": "registered",
      "device_registry": {
        "registry_id": "org.example.mdm",
        "registry_type": "mdm",
        "entry_ref": "mdm_device_042",
        "binding": "device",
        "posture": "compliant"
      }
    }
  },
  "annotations": {
    "bus": {
      "verified_identity": {
        "method": "bearer_token",
        "agent_id": "runtime-instance-01",
        "managed_runtime_verified": true,
        "registry_verified": true,
        "verification_strength": "device_attested",
        "verified_registry": {
          "registry_id": "org.example.mdm",
          "registry_type": "mdm",
          "entry_ref": "mdm_device_042",
          "posture": "compliant",
          "verified_at": "2026-04-29T09:30:00Z"
        }
      }
    }
  }
}
```

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

`reasoning_content` together with `response_content` constitutes a *transcript-grade* record of the LLM exchange when the runtime or provider exposes reasoning. By "transcript-grade" we mean a record sufficient to reconstruct, after the fact, what the model was asked, what reasoning was available to the runtime, and what it returned, without consulting the original session transport. This can support record-keeping obligations such as EU AI Act Article 12 for high-risk AI systems, but AgentHook does not itself certify legal compliance.

### `PreToolUse` and `PostToolUse`

| Key | Type | Purpose |
|---|---|---|
| `tool_call_id` | string (UUID) | Stable identifier linking a `PreToolUse` event to the corresponding `PostToolUse`, denial, or error event |
| `admission_verdict` | object | Consolidated verdict for admission-bound `PreToolUse`: `verdict`, `reason`, optional `subscriber`, and optional `claim_reference` |
| `estimated_usd` | number | Cost estimate (set by a budget subscriber, stamped onto the event) |
| `tool_input_executed` | object | Tool input actually executed (`PostToolUse` only). SHOULD match the admitted `PreToolUse.tool_input` unless the publisher records an explicit mutation reason |
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

  Conforming publishers MUST default to fail-closed when the publisher cannot determine the deployment context. A fail-mode trigger MUST be emitted as an AgentHook event, normally `ErrorOccurred` with `metadata.error_type: "admission_fail_mode"`, `metadata.fail_mode_triggered: true`, and `metadata.outcome: "allow"` or `"deny"`.
- **Observational Pre\* telemetry**: a publisher MAY emit a `Pre*` event for visibility without blocking. Such events MUST set `evidence_phase` to `observational` or omit `evidence_phase`, and MUST NOT be represented as runtime authorisation evidence.
- **Admission-bound Pre\* evidence**: a publisher that claims an action was authorised, denied, or escalated by runtime controls MUST emit the relevant `Pre*` event before the action commits, set `evidence_phase` to `pre_commit`, block until a subscriber verdict or documented fail-mode is reached, and record the consolidated result in `metadata.admission_verdict`. If the action has already committed and the event is emitted afterwards, the event is `post_hoc` or `observational` telemetry and MUST NOT be represented as equivalent to pre-commit authorisation evidence.
- **Tool-call pairing**: admission-bound `PreToolUse` events SHOULD carry `metadata.tool_call_id`. The corresponding `PostToolUse`, denial, or fail-mode `ErrorOccurred` event SHOULD carry the same `tool_call_id`. `PostToolUse.metadata.tool_input_executed` SHOULD record the input actually executed so subscribers can detect time-of-check/time-of-use drift.
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

### Admission-bound profile

The Bronze, Silver, and Gold tiers describe event coverage and transcript quality. They do not by themselves prove that a publisher's gates are in the action admission path. A publisher MAY additionally claim the `admission-bound` profile when:

- enforcement-capable `Pre*` events use `evidence_phase: "pre_commit"`
- the publisher blocks until a subscriber verdict or documented fail-mode before the action commits
- `metadata.admission_verdict` records the consolidated decision
- fail-mode allows or denies are emitted as AgentHook events
- tool calls use stable `metadata.tool_call_id` pairing between pre, post, denial, and fail-mode events where the host runtime exposes a tool-call boundary

The conformance rig SHOULD test the `admission-bound` profile separately from Bronze, Silver, and Gold so a publisher cannot satisfy an authorisation claim with post-hoc logging alone.

## 6. Runtime attestation

Runtime attestation lets an agent, operator, or auditor distinguish verified runtime facts from user-authored prompt text. It is a publisher-supplied declaration of which hooks, gates, subscribers, consolidation rules, and fail modes are active for the current session.

Runtime attestation is a non-breaking metadata extension. It does not add a new canonical event type and does not change `schema_version`.

Attestation is only as strong as the runtime path that produced it. For enforcement-capable controls, attestation SHOULD describe controls that participate in the pre-commit admission path for the relevant action. A receipt produced after an action commits can be useful for observability, incident review, or audit chronology, but it is not equivalent to evidence that the action was admitted by a runtime gate before execution.

Publishers SHOULD attach runtime attestation at the earliest available point in a session:

1. `SessionStart.metadata.runtime_attestation`, when the runtime emits `SessionStart`
2. otherwise the first `PreLLMCall.metadata.runtime_attestation`
3. otherwise the first `UserPromptSubmit.metadata.runtime_attestation`

Publishers MAY also expose the same document through an implementation-specific local endpoint or tool. A bus MAY expose an aggregate attestation endpoint, but the AgentHook envelope does not require any particular bus or transport.

The attestation document MUST NOT be authored by the user and MUST NOT be inferred from user-provided policy text. It MAY be signed or MACed by the publisher/runtime. Where signatures are used, the signature covers the canonical JSON representation of the attestation excluding the `signature` field. Publishers SHOULD set `authenticity` to `unsigned`, `signed`, or `bus_attested`.

If `claims.tool_calls_are_runtime_gated` is `true`, the publisher MUST implement admission-bound `PreToolUse` semantics from section 4 for tool execution. If the publisher cannot block before tool execution, the claim MUST be `false` or omitted. If `claims.do_not_bypass_gate` is `true`, the runtime MUST NOT provide an alternate tool execution path that skips an active admission-bound gate. These claims are testable runtime claims, not model instructions.

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
  "authenticity": "unsigned",
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

> AgentHook runtime attestation (`authenticity`: signed|unsigned|bus_attested): tool calls in this session are routed through the listed runtime gates before execution when `tool_calls_are_runtime_gated` is true. If a gate denies or asks for approval, report the gate response. Do not substitute, obscure, or route around a gate. This attestation does not replace model, platform, or system safety policy.

When an agent decides a tool call is appropriate under its normal instructions, it SHOULD submit the intended tool call through the runtime gate. It MUST NOT substitute a different command, hide an action, encode an action, or use an alternate route to avoid review by an active gate.

## 7. Publisher manifests

Until agent runtimes emit AgentHook natively, an AgentHook publisher SHOULD ship a repository-root `agenthook.publisher.json` file conforming to [`publisher-manifest.schema.json`](./publisher-manifest.schema.json).

The manifest is an interim local-first, machine-readable declaration of:

- the stable `publisher_id`
- the runtime and versions tested
- the AgentHook source label used in envelopes
- supported, partial, planned, and unavailable lifecycle events
- installer and command entry points
- runtime configuration files touched by the publisher
- known limitations
- self-attested verification commands and current conformance status

The manifest is not an enforcement document. It MUST NOT contain secrets, bearer tokens, private endpoints, policy rules, or executable install logic. Subscribers MUST treat manifest claims as evidence about publisher coverage, not as authority to allow or deny an action.

Publishers SHOULD use reverse-DNS identifiers, for example `uk.agenticthinking.publisher.anthropic.claude-code`. A public registry MAY later index manifests by `publisher_id`, but conformance does not require central registration in v0.1.

Collectors and buses MAY use publisher manifests to display onboarding state, supported hook coverage, limitations, and verification status. They MUST still verify live runtime events before reporting a publisher as active. Native AgentHook runtimes may expose equivalent manifest metadata through their own standard implementation once the draft reaches stable standard status.

## 8. Versioning and stability

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
