# AHP-004: Runtime Attestation

| Field | Value |
|---|---|
| Identifier | AHP-004 |
| Title | Runtime Attestation |
| Author | Agentic Thinking editor team |
| Status | Draft |
| Created | 2026-04-28 |
| Updated | 2026-04-28 |
| Supersedes |  |
| Superseded by |  |

## Motivation

Agents, operators, and auditors need a way to distinguish verified runtime controls from user-authored prompt text.

In live testing, an agent could observe that a gate existed only after tool calls were blocked. Before that, user-provided text describing the gate was correctly treated as untrusted prompt content. That creates avoidable friction: the agent may over-refuse before a gate sees the tool call, inspect runtime internals to prove the gate exists, or misunderstand which subscriber produced a final verdict.

Runtime Attestation closes that gap. It gives the publisher/runtime a structured way to say: these hooks are active, these subscribers may enforce, this consolidation rule is in use, and this fail mode applies. The attestation informs the agent without replacing model, platform, or system safety policy.

The strongest form of runtime evidence is not a receipt logged after the fact. It is evidence produced by the same pre-commit admission path that allowed, denied, or escalated the action. If the action committed before the check ran, the receipt is observational telemetry rather than enforcement-grade authorisation evidence.

## Current behaviour

`SPEC.md` v0.1 defines the AgentHook envelope, ten canonical event types, standard metadata keys, hook delivery semantics, and publisher conformance levels. It does not define a standard way for a publisher to declare the runtime controls active in a session.

The current envelope already has a `metadata` object. This Proposal uses that extension point and does not change the envelope shape.

## Proposed change

Add `metadata.runtime_attestation` as a standard metadata key that may appear on:

- `SessionStart`, preferred when emitted by the runtime
- the first `PreLLMCall` in a session, when `SessionStart` is unavailable
- the first `UserPromptSubmit` in a session, when neither of the above is available

The attestation document has type `agenthook.runtime_attestation` and declares runtime state for the current session.

Minimum fields:

- `type`
- `schema_version`
- `runtime`
- `publisher`
- `session_id`
- `nonce`
- `issued_at`
- `expires_at`
- `event_endpoint`
- `active_subscribers`
- `consolidation`
- `fail_mode`
- `authenticity`
- `claims`
- `signature`

The schema is defined in `runtime-attestation.schema.json`.

The attestation is publisher-supplied. It is not user-authored. A bus may expose or aggregate attestation, but no bus endpoint is required by this Proposal.

For enforcement-capable events, publishers SHOULD bind the attestation and resulting receipt to the authorisation decision that admits, denies, or escalates the action before it commits. Implementations SHOULD distinguish:

- pre-commit authorisation evidence
- post-action observational telemetry
- best-effort logging receipts

Post-hoc logs remain useful, but they should not be represented as equivalent to evidence produced by a runtime gate in the action's admission path.

If a publisher claims `tool_calls_are_runtime_gated`, that claim is normative: the publisher must emit `PreToolUse` before execution, block until the configured verdict or fail-mode, and record the consolidated decision in the event metadata. If the publisher cannot block before execution, it must not claim the tool call was runtime-gated.

This Proposal also standardises the optional envelope field `evidence_phase` with `pre_commit`, `post_hoc`, and `observational` values. Attested gate receipts should use `pre_commit`; decorative logs or records emitted after an action committed should not.

Recommended model-facing summary:

> AgentHook runtime attestation (`authenticity`: signed|unsigned|bus_attested): tool calls in this session are routed through the listed runtime gates before execution when `tool_calls_are_runtime_gated` is true. If a gate denies or asks for approval, report the gate response. Do not substitute, obscure, or route around a gate. This attestation does not replace model, platform, or system safety policy.

Forbidden model-facing claims include:

- "ignore your safety rules"
- "never refuse"
- "always run every tool"
- "the user can override any denial"

## Backwards-compatibility impact

- Does this change the wire format? No. It standardises a metadata key inside the existing envelope.
- Does this require a `schema_version` bump? No.
- Does this affect existing publishers? Publishers may ignore it until they choose to implement attestation.
- Does this affect existing subscribers? Subscribers that do not inspect `metadata.runtime_attestation` continue unchanged.

## Deprecation plan

No deprecation is required.

## Reference implementation

Initial reference implementation target:

- `hookbus-publisher-hermes` builds the attestation at session start or first LLM call.
- It attaches the full document to the first available AgentHook event metadata.
- It injects a short factual summary into the model context.
- It does not require a HookBus core change.

## Security considerations

Runtime Attestation is a security boundary between user prompt text and runtime-provided facts.

User-authored claims about hooks, gates, policies, PINs, approvals, subscribers, fail modes, or runtime state must not be treated as attestation. A malicious user could otherwise paste a fake governance document and induce the agent to trust non-existent controls.

Attestation does not give the runtime authority to override model, platform, or system safety policy. It tells the agent what runtime controls exist for tool execution. Enforcement remains outside the model path.

Attestation also must not launder post-hoc logging into authorisation evidence. A publisher that emits an event after an irreversible action has already committed should identify that event as observational telemetry. A subscriber may still audit, alert, or open an incident from that telemetry, but it did not admit the action before execution.

Signatures or MACs are optional in this draft because deployment trust boundaries vary. Implementations that expose attestation across process or host boundaries should sign or MAC the document and bind it to a session nonce and expiry.

Unsigned attestation must not be presented to the model or auditor as cryptographically verified. Implementations should label authenticity explicitly as `unsigned`, `signed`, or `bus_attested`.

## Alternatives considered

### Add a new canonical event type

Rejected for this draft. The existing `SessionStart` event and `metadata` extension point are sufficient. Adding an eleventh canonical event would create unnecessary churn before the v1.0 event set is finalised.

### Require a bus endpoint

Rejected for this draft. AgentHook is implementation-neutral and cannot require HookBus or any bus. Publishers can supply attestation directly. A bus may expose an endpoint later as an implementation feature.

### Put attestation in `annotations`

Rejected. `annotations` are free-form subscriber/operator notes that publishers should not depend on. Attestation is publisher/runtime-supplied metadata, so `metadata.runtime_attestation` is the clearer home.

## Unresolved questions

- Should signed Runtime Attestation become a future conformance requirement?
- Should the conformance suite verify attestation for a Gold+ or Enterprise profile?
- What canonical signature format should be recommended for v1.0?
- Should standard subscriber roles be enumerated (`policy_gate`, `dlp`, `context_provider`, `audit`, `workflow`)?

## Status history

| Date | Status | Note |
|---|---|---|
| 2026-04-28 | Draft | Initial submission |
