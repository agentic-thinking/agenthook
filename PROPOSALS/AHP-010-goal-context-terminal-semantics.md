# AHP-010: Goal Context and Terminal Semantics

| Field | Value |
|---|---|
| Identifier | AHP-010 |
| Title | Goal Context and Terminal Semantics |
| Author | Agentic Thinking maintainers |
| Status | Draft |
| Created | 2026-05-20 |
| Updated | 2026-05-20 |
| Supersedes | N/A |
| Superseded by | N/A |

## Motivation

Agent runtimes increasingly execute work against an explicit goal, task, or terminal session rather than a single isolated prompt. Governance and audit systems need a portable way to understand which goal an event belongs to, whether a tool call is inside the intended terminal scope, and how child sessions or delegated agents relate to the original request.

Without goal context, subscribers can still evaluate individual tool calls, but they have less evidence for questions such as:

- whether the action still matches the user's active goal;
- whether the agent has drifted into a different task;
- whether a child session inherited the correct constraints;
- whether approval applied to the current goal, asset, and session lineage;
- whether the terminal or workspace boundary is still the expected one.

## Proposed change

Define optional goal lifecycle metadata and event semantics that publishers MAY emit when the runtime exposes goal state.

This draft does not move goal ownership into AgentHook. The runtime, CLI, or agent framework remains responsible for managing its own goal state. AgentHook makes that state auditable and subscriber-addressable.

## Event types

Publishers MAY emit the following draft extension events:

| Event | Phase | Purpose |
|---|---|---|
| `GoalSet` | state | Records that a goal, task, or objective became active for a session. |
| `GoalStatus` | state | Records progress, pause, completion, cancellation, denial, or failure for the active goal. |

These events are outside the v0.2 core ten-event conformance set while this Proposal remains Draft.

## Metadata fields

Goal-aware publishers SHOULD include the following fields when available:

| Field | Type | Purpose |
|---|---|---|
| `goal_id` | string | Stable identifier for the current goal. |
| `goal_source` | string | Source of the goal, such as user prompt, CLI command, workflow, API, or parent agent. |
| `goal_status` | string | Current state, such as active, paused, completed, failed, denied, or cancelled. |
| `root_session_id` | string | Session id where the goal originated. |
| `parent_session_id` | string | Parent session id when the current session is delegated or nested. |
| `lineage_session_ids` | array | Ordered session lineage from root to current session. |
| `terminal_scope` | object | Optional terminal, workspace, repository, or execution boundary known to the runtime. |
| `constraints` | array | Optional constraints inherited from the user, workflow, policy, or runtime. |

## Conformance guidance

Bronze, Silver, and Gold v0.2 conformance does not require goal lifecycle events. Goal context is a draft extension that subscribers MAY use for stronger policy evaluation, audit reconstruction, and workflow continuity.

High-assurance publishers SHOULD preserve goal identifiers, session lineage, and terminal scope across pre-action and post-action events where the runtime exposes those details.

## Backwards-compatibility impact

- Does this change the wire format? No. It uses optional additional event types and metadata fields.
- Does this require a `schema_version` bump? No.
- Does this affect existing publishers? No. Existing publishers may omit goal context.
- Does this affect existing subscribers? No. Subscribers that do not understand goal events can ignore them.

## Security considerations

Goal context is evidence, not authorisation. A subscriber MUST NOT treat user-authored goal text as proof that a policy, approval, or runtime contract exists. Goal metadata should be considered alongside runtime attestation, approval lifecycle metadata, and policy subscriber decisions.

Publishers SHOULD avoid placing secrets, credentials, raw personal data, or unnecessary business-sensitive content in goal metadata. Use stable identifiers and references where possible.

## Open questions

- Whether `GoalSet` and `GoalStatus` should become core events in v1.0.
- Whether terminal scope should have a required schema or remain implementation-defined.
- Whether approval lifecycle metadata should reference `goal_id` directly when an approval is goal-scoped.
