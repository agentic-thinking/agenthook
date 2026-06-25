# AHP-007: Approval Lifecycle Metadata

| Field | Value |
|---|---|
| Identifier | AHP-007 |
| Title | Approval Lifecycle Metadata |
| Author | Agentic Thinking maintainers |
| Status | Draft |
| Created | 2026-05-08 |
| Updated | 2026-05-08 |
| Supersedes | N/A |
| Superseded by | N/A |

## Motivation

Autonomous agents can attempt actions that should not execute until a human or workflow owner approves them: production SSH, deployment, data export, destructive operations, financial workflows, regulated decisions, or other sensitive tool calls.

AgentHook already allows synchronous subscribers to return `allow`, `deny`, or `ask`. The missing piece is a standard way to describe the approval lifecycle behind `ask`: which workflow is pending, how a publisher should pause, how it should resume, and what evidence links the final execution to the approval decision.

Without this convention, every runtime and bus invents a different approval shape. That makes autonomous-agent pause/resume behaviour brittle and weakens audit evidence.

## Current behaviour

`SPEC.md` section 2 defines ten canonical event types. `SPEC.md` section 4 states that Pre* events may block while synchronous subscribers respond. The Python conformance helper already accepts subscriber responses with `decision` values of `allow`, `deny`, or `ask`.

The current spec does not define:

- standard metadata for pending approval workflows;
- how an agent should resume after approval;
- how to represent approval granted, denied, expired, or cancelled states;
- whether the agent retries the same event, retries with a workflow id, or waits inside the publisher wrapper.

## Proposed change

Define `metadata.approval` as an optional metadata object on subscriber responses and related AgentHook events.

Minimum shape:

```json
{
  "approval": {
    "required": true,
    "status": "pending",
    "workflow_id": "wf_123",
    "action_id": "act_456",
    "department": "management",
    "reviewer_ref": "group:management",
    "requested_at": "2026-05-08T03:42:00Z",
    "expires_at": "2026-05-08T03:57:00Z",
    "resume_policy": "retry_same_event"
  }
}
```

Standard fields:

| Field | Type | Required | Purpose |
|---|---|---|---|
| `required` | boolean | yes | Whether approval is required before execution |
| `status` | enum | yes | `pending`, `approved`, `denied`, `expired`, or `cancelled` |
| `workflow_id` | string | yes when available | Approval workflow identifier |
| `action_id` | string | yes when available | Action identifier within the workflow |
| `department` | string | no | Routing department, role, or queue |
| `reviewer_ref` | string | no | Pseudonymous reviewer, group, or queue reference |
| `requested_at` | string | no | ISO 8601 timestamp when approval was requested |
| `decided_at` | string | no | ISO 8601 timestamp when approval was granted or denied |
| `expires_at` | string | no | ISO 8601 approval timeout |
| `resume_policy` | enum | no | `retry_same_event`, `retry_with_workflow_id`, `publisher_waits`, or `manual_retry` |
| `decision_ref` | string | no | Reference to the approval decision record |
| `approval_url` | string | no | Operator-facing approval link |

Recommended response semantics:

- If a subscriber returns `decision: "ask"` with `metadata.approval.status: "pending"`, the publisher or hook wrapper MUST NOT execute the original action.
- If the action is later approved, the publisher MAY retry the same event or retry with the workflow id, depending on `resume_policy`.
- A subscriber, bus, gateway, or approval system MUST verify the approval state before returning `allow`.
- Publisher-supplied approval metadata is evidence only. It is not sufficient authority to execute by itself.

Optional additional event types:

| Event type | Phase | Description |
|---|---|---|
| `ApprovalRequested` | during | A human or workflow approval was requested for a pending action |
| `ApprovalGranted` | during | The pending action was approved |
| `ApprovalDenied` | during | The pending action was rejected |
| `ToolUseResumed` | after | A paused tool call resumed after approval |
| `ToolUseBlocked` | after | A paused tool call was denied, expired, cancelled, or timed out |

These event types remain non-canonical while this Proposal is in Draft. They do not change the v0.2 core ten-event conformance set.

## Backwards-compatibility impact

- Does this change the wire format? No. It uses the existing `metadata` object and optional additional PascalCase event types already permitted by `SPEC.md` section 2.
- Does this require a `schema_version` bump? No.
- Does this affect existing publishers? No. Existing publishers may ignore `metadata.approval`.
- Does this affect existing subscribers? No. Subscribers that do not understand approval metadata can ignore it.

The repository schema should allow additional PascalCase event types, because `SPEC.md` already permits them. This Proposal includes a schema clarification rather than a breaking change.

## Deprecation plan

No deprecation is required.

## Reference implementation

HookBus + AgentProtect CRE + approval-workflow lab validation on 2026-05-08:

1. A `PreToolUse` event attempted a sensitive remote administration action.
2. AgentProtect CRE returned `decision: "ask"`.
3. The approval workflow created a workflow record.
4. The notification layer sent an approval request to the configured reviewer.
5. Human approval was recorded.
6. The same event was retried.
7. AgentProtect CRE returned `decision: "allow"` with the approved workflow id.
8. The tool call resumed and produced disk output.

Implementation sketch:

```python
response = gate(pre_tool_use_event)
if response["decision"] == "ask":
    approval = response.get("metadata", {}).get("approval", {})
    if approval.get("resume_policy") == "publisher_waits":
        wait_until_terminal(approval["workflow_id"])
    else:
        return blocked_until_retry(response)

response = gate(pre_tool_use_event)
if response["decision"] == "allow":
    execute_tool_call()
```

## Security considerations

Approval metadata introduces a risk of forged approvals if publishers, agents, or model-generated text are treated as authoritative.

Consumers MUST treat `metadata.approval` as evidence, not authority. An `approved` status supplied by the publisher or model MUST NOT allow execution unless a trusted subscriber, bus, gateway, or approval system verifies the workflow and action. Approval links SHOULD be operator-facing and SHOULD NOT be exposed to the model unless explicitly configured. Approval records SHOULD be audit logged with actor, timestamp, decision, reason, and workflow/action ids.

Secrets and credentials MUST NOT be stored in approval metadata. If an approval request references sensitive tool input, the approval system SHOULD redact or tokenise secrets before notification.

## Alternatives considered

### Add five new canonical events immediately

Rejected for this draft. The ten-event conformance set should not churn before v1.0 unless the Working Group accepts a formal event-set change.

### Treat approval as annotations

Rejected. `annotations` are subscriber/operator notes. Approval state affects execution, retry, and audit semantics, so it needs a standard metadata convention.

### Model approval as managed runtime identity

Rejected. `metadata.managed_runtime` describes an approved runtime installation. It does not describe approval for a specific action.

## Unresolved questions

- Should `ToolUseResumed` and `ToolUseBlocked` become canonical v1.0 events?
- Should `publisher_waits` be required for Gold conformance in regulated deployments?
- Should `approval_url` be allowed in model-facing summaries, or only in operator dashboards and notifications?
- Should approval decisions require a signed decision record in enterprise conformance tests?

## Status history

| Date | Status | Note |
|---|---|---|
| 2026-05-08 | Draft | Initial submission |
