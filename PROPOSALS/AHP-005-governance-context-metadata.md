# AHP-005: Governance Context Metadata

| Field | Value |
|---|---|
| Identifier | AHP-005 |
| Title | Governance Context Metadata |
| Author | Agentic Thinking Limited |
| Status | Draft |
| Created | 2026-04-28 |
| Updated | 2026-04-28 |
| Supersedes | N/A |
| Superseded by | N/A |

## Motivation

AgentHook events can record what an agent was asked, what it attempted, which subscriber decisions were returned, and what the runtime produced. Policy, audit, workflow, and observability subscribers also need compact context about the current task frame: what the runtime believes the user or workflow is trying to achieve, where that context came from, and how fresh or reliable it is.

Without a shared metadata convention, publishers and subscribers invent incompatible task-context fields. That makes task-alignment checks harder to implement, and weakens audit trails when reviewers need to reconstruct why an action was considered in scope.

This Proposal defines optional governance context metadata that can be carried inside the existing AgentHook envelope.

## Current behaviour

The AgentHook envelope permits arbitrary `metadata` fields. The specification does not currently define a standard shape for current task context, policy references, workflow context, or source/confidence labels.

## Proposed change

Define `metadata.governance_context` as an optional metadata object. It is advisory runtime context. It is not an authorisation decision.

Example:

```json
{
  "metadata": {
    "governance_context": {
      "task_summary": "Check whether semantic alignment is working in the test environment.",
      "task_source": "user",
      "task_confidence": "explicit",
      "scope": "session",
      "context_id": "ctx-123",
      "policy_ref": "policy://example/semantic-intent-alignment",
      "created_at": "2026-04-28T09:30:00Z"
    }
  }
}
```

### Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `task_summary` | string | no | Human-readable current task frame. Publishers SHOULD keep this compact and SHOULD NOT include secrets. |
| `task_source` | enum | no | `user`, `workflow`, `publisher`, or `agent`. Describes where the task context came from. |
| `task_confidence` | enum | no | `explicit`, `derived`, `carried_forward`, or `suggested`. Describes how directly the context maps to a user or workflow instruction. |
| `scope` | enum | no | `turn`, `session`, or `workflow_step`. Describes the intended lifetime of the context. |
| `context_id` | string | no | Publisher-defined identifier for correlating related events under the same context. |
| `policy_ref` | string | no | Optional reference to a policy, ruleset, or control context known to the deployment. |
| `created_at` | string | no | ISO 8601 timestamp for when the context was created. |

### Source semantics

- `user`: context originated from direct user input.
- `workflow`: context originated from a workflow, approval system, or orchestration layer.
- `publisher`: context was derived or carried forward by the publisher/runtime adapter.
- `agent`: context was suggested by an agent or model. This is useful for observability, but MUST NOT be treated as enforcement-grade evidence by itself.

### Confidence semantics

- `explicit`: direct statement from the source.
- `derived`: inferred or summarised by publisher or workflow logic.
- `carried_forward`: retained from a previous turn or workflow step.
- `suggested`: proposed by an agent or model.

## Trust constraints

`metadata.governance_context` is advisory context only.

Subscribers MUST NOT treat `metadata.governance_context` as an authorisation decision by itself.

Subscribers MUST perform their own policy evaluation before allowing, denying, escalating, redacting, or otherwise acting on an event.

Publishers MUST NOT mark agent-generated task summaries as `task_source: "user"` or `task_source: "workflow"`.

Publishers SHOULD preserve the raw user prompt or workflow event separately where available, so subscribers and auditors can compare the original input with any derived task summary.

`policy_ref` is a reference only. This Proposal does not define policy retrieval, policy integrity, or policy evaluation semantics.

This Proposal intentionally does not define `authorized_tools`, `forbidden_tools`, or command-level permissions. Those belong to policy subscribers, workflow systems, or deployment-specific policy references.

## Backwards-compatibility impact

- Does this change the wire format? No. It defines an optional metadata convention inside the existing envelope.
- Does this require a `schema_version` bump? No.
- Does this affect existing publishers? No. Publishers may ignore the convention.
- Does this affect existing subscribers? No. Subscribers may ignore unknown metadata.

## Deprecation plan

No existing field is removed or renamed. No deprecation is required.

## Reference implementation

Reference implementation work is expected to cover:

- a publisher adapter helper that can attach `metadata.governance_context`;
- a policy subscriber that consumes the context as one input among others;
- an audit subscriber that records the context alongside prompts, tool calls, model calls, decisions, and results.

The reference implementation MUST demonstrate that `governance_context` is not treated as authorisation by itself.

## Security considerations

This Proposal introduces a standard place for runtime task context, which can improve auditability but can also create false confidence if overtrusted.

Key risks:

- A compromised or poorly implemented publisher may mislabel inferred context as direct user intent.
- An agent may suggest an over-broad task summary.
- A subscriber may incorrectly treat `policy_ref` or `task_summary` as sufficient permission to act.
- Stale `carried_forward` context may outlive the task it described.

Required mitigations:

- Subscribers MUST treat `governance_context` as advisory.
- Subscribers MUST perform independent policy evaluation.
- Agent-suggested context MUST be labelled with `task_source: "agent"` and/or `task_confidence: "suggested"`.
- Publishers SHOULD rotate or clear governance context when task scope changes.
- Publishers SHOULD include raw prompt/workflow evidence where available.

## Alternatives considered

### Task attestation metadata

A stricter `metadata.task_attestation` object was considered. It was rejected for this draft because the term "attestation" implies a stronger trust and integrity model than this Proposal defines.

### Standard authorised-tool fields

Fields such as `authorized_tools` and `forbidden_tools` were considered. They were rejected for this draft because they can be misused as permissions. Command-level and tool-level authorisation is deployment-specific and belongs in policy subscribers or referenced policy systems.

### New canonical event type

A new `TaskUpdate` or `TaskAttestation` event type was considered. It was rejected for this draft because the existing metadata channel is sufficient and backwards compatible.

## Unresolved questions

- Should future versions define stronger integrity binding between governance context and the original user or workflow event?
- Should `scope` semantics be tightened with testable definitions for each runtime class?
- Should `context_id` be mandatory for conformance tiers above Bronze?
- Should a future Proposal define a separate, cryptographically verifiable task attestation object?

## Status history

| Date | Status | Note |
|---|---|---|
| 2026-04-28 | Draft | Initial submission |
