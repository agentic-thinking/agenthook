# AHP-013: Action Governance Evidence Profile

| Field | Value |
|---|---|
| Identifier | AHP-013 |
| Title | Action Governance Evidence Profile |
| Author | Agentic Thinking editor team |
| Status | Draft |
| Created | 2026-06-06 |
| Updated | 2026-06-06 |
| Supersedes |  |
| Superseded by |  |

## Summary

Define an optional `action-governance` profile for publishers that emit comparable governance evidence around agent actions and tool calls.

The profile does not replace OpenAI tools, Anthropic `tool_use`, Gemini `functionDeclarations`, MCP `tools/call`, framework-native tools, browser actions, shell commands, or local runtime tools. It standardizes the evidence envelope around those actions: what was requested, how it maps to a canonical action, what risk and policy state applied, whether the call was validated, redacted, approved, denied, retried, executed, and what actually ran.

## Motivation

Model-facing and harness-facing tool systems are already fragmented and useful in their own domains:

- provider APIs expose their own model-facing call formats;
- MCP standardizes tool discovery and invocation between clients and servers;
- frameworks expose native tool abstractions;
- OpenTelemetry can record tool execution spans and GenAI telemetry.

None of those layers fully answers the governance evidence question for an enterprise or auditor: was this action in the pre-commit admission path, what policy decision applied, what risk class was assigned, whether an approval workflow paused execution, whether arguments were redacted or validated, whether retries were equivalent to a pending approval, and whether the executed action matched the requested action.

AgentHook is the right layer for this because it already defines runtime evidence envelopes, normalized action/resource fields, admission-bound semantics, approval lifecycle metadata, and web evidence. AHP-013 connects those pieces into a named profile.

## Current behaviour

AgentHook v0.2 already defines:

- `PreToolUse` and `PostToolUse` events;
- normalized top-level `action`, `resource_kind`, `resource`, `resource_scope`, and `operation_risk` fields in AHP-011;
- `metadata.tool_call_id`, `metadata.admission_verdict`, and `metadata.tool_input_executed`;
- approval lifecycle metadata in AHP-007;
- Web Evidence events in AHP-012;
- the `admission-bound` profile.

The missing piece is a standard metadata shape for tool identity, provider translation, risk, validation, redaction, retry, and execution evidence across provider and framework surfaces.

## Proposed change

Add an optional `action-governance` profile. A publisher MAY claim this profile when it emits the following evidence for governed `PreToolUse` and `PostToolUse` events where the runtime exposes the data.

### Profile evidence requirements

For governed `PreToolUse` events, publishers claiming this profile MUST emit the following minimum evidence unless the host runtime cannot expose the boundary, in which case the limitation MUST be documented in the publisher manifest:

- stable `metadata.tool_call_id`;
- normalized top-level `action`, `resource_kind`, `resource`, `resource_scope`, and `operation_risk` when safely identifiable;
- `metadata.tool_identity`;
- `metadata.risk`.

For governed admission-bound `PreToolUse` events, publishers MUST also emit:

- `evidence_phase: "pre_commit"`;
- `metadata.admission_verdict` once a policy subscriber, bus, gateway, or runtime decision is reached.

For governed `PostToolUse` events, publishers claiming this profile MUST emit:

- the same `metadata.tool_call_id` as the admitted `PreToolUse`, or an explicit `metadata.retry.previous_tool_call_id`;
- `metadata.tool_input_executed`;
- `metadata.execution`.

Publishers SHOULD also emit `metadata.provider_translation` when the call originated from a provider, protocol, framework, browser, shell, or native runtime surface that can be identified; `metadata.validation` when argument validation ran; `metadata.redaction` when arguments, outputs, or evidence were redacted; and `metadata.retry` when the event is part of a retry/resume sequence.

### Tool identity

`metadata.tool_identity` describes the tool independently of the provider-specific model-facing name.

```json
{
  "tool_identity": {
    "canonical_name": "email.send",
    "provider_name": "send_email",
    "source": "openai_tools",
    "schema_hash": "sha256:1111111111111111111111111111111111111111111111111111111111111111"
  }
}
```

Fields:

| Field | Type | Purpose |
|---|---|---|
| `canonical_name` | string | Stable action/tool identifier such as `web.search`, `email.send`, `shell.exec`, `browser.navigate`, `memory.write`, or `crm.update_record` |
| `provider_name` | string | Native tool, function, command, or method name as exposed by the provider/runtime/framework |
| `source` | string | Native surface, such as `openai_tools`, `anthropic_tool_use`, `gemini_function_declarations`, `mcp_tools_call`, `browser_action`, `shell_command`, or `native_runtime_tool` |
| `schema_hash` | string | Optional digest of the tool/function/input schema, preferably `sha256:<hex>` |

### Provider translation

`metadata.provider_translation` records how the native call surface maps to AgentHook evidence.

```json
{
  "provider_translation": {
    "model_facing_tool": "send_email",
    "provider": "openai",
    "provider_surface": "openai_tools",
    "adapter_version": "openai-tools-v1",
    "schema_hash": "sha256:1111111111111111111111111111111111111111111111111111111111111111"
  }
}
```

Recommended `provider_surface` values include:

- `openai_tools`
- `anthropic_tool_use`
- `gemini_function_declarations`
- `mcp_tools_call`
- `langchain_tool`
- `llamaindex_tool`
- `semantic_kernel_function`
- `vercel_ai_sdk_tool`
- `openai_agents_sdk_tool`
- `browser_action`
- `shell_command`
- `native_runtime_tool`
- `other`

### Risk metadata

`metadata.risk` records the profile-specific risk assessment.

```json
{
  "risk": {
    "risk_class": "external_side_effect",
    "requires_human_approval": true,
    "data_exfiltration_risk": "moderate",
    "writes_external_system": true,
    "idempotent": false,
    "contains_secret": false
  }
}
```

Recommended fields:

| Field | Type | Purpose |
|---|---|---|
| `risk_class` | string | Classification such as `read_only`, `sensitive_read`, `external_side_effect`, `destructive_write`, `credential_access`, `publication`, or `runtime_change` |
| `requires_human_approval` | boolean | Whether policy requires a human or workflow approval before execution |
| `data_exfiltration_risk` | string | `none`, `low`, `moderate`, `high`, or `unknown` |
| `writes_external_system` | boolean | Whether the action can mutate a system outside the local runtime/workspace |
| `idempotent` | boolean | Whether repeated execution is expected to be safe |
| `contains_secret` | boolean | Whether the request or result is known to contain a secret after redaction checks |

### Validation, redaction, retry, and execution metadata

`metadata.validation` records argument/schema validation:

```json
{
  "validation": {
    "status": "passed",
    "validator": "publisher",
    "schema_hash": "sha256:1111111111111111111111111111111111111111111111111111111111111111"
  }
}
```

`metadata.redaction` records redaction state without embedding sensitive values:

```json
{
  "redaction": {
    "applied": true,
    "fields": ["tool_input.body"],
    "policy_id": "redact-message-body-v1"
  }
}
```

`metadata.retry` records retry/resume relationships:

```json
{
  "retry": {
    "attempt": 2,
    "previous_tool_call_id": "call_001",
    "reason": "approval_resumed"
  }
}
```

`metadata.execution` records post-execution evidence:

```json
{
  "execution": {
    "started_at": "2026-06-06T12:00:01Z",
    "completed_at": "2026-06-06T12:00:02Z",
    "outcome": "succeeded",
    "duration_ms": 431,
    "result_ref": "evidence://tool-results/call-001",
    "result_hash": "sha256:2222222222222222222222222222222222222222222222222222222222222222"
  }
}
```

Publishers SHOULD use references and hashes for sensitive or bulky tool inputs/results rather than embedding unbounded content in the envelope.

### Admission semantics

For publishers claiming both `admission-bound` and `action-governance`:

- if `metadata.admission_verdict.verdict` is `deny`, the action MUST NOT execute;
- if the verdict is `ask`, equivalent retries MUST stop while approval is pending;
- if the action executes after approval, `PostToolUse` MUST reference the same `metadata.tool_call_id` or an explicit `metadata.retry.previous_tool_call_id`, and MUST include `metadata.approval.workflow_id` and `metadata.approval.decision_ref` when available;
- if the executed tool input differs from the admitted input, `PostToolUse.metadata.tool_input_executed` MUST record the executed input and the publisher SHOULD explain the mutation in `metadata.execution.mutation_reason` or equivalent metadata.

### Optional extension events

Implementations MAY emit the following PascalCase events where the runtime exposes distinct lifecycle boundaries:

| Event type | Phase | Description |
|---|---|---|
| `ToolCallValidated` | before | Tool arguments or provider schema were validated before execution |
| `ToolCallRedacted` | during | Tool input, result, or evidence was redacted before routing, storage, or model exposure |
| `ToolCallRetried` | during | A tool call was retried, resumed, or linked to a prior pending call |

These events are optional in v0.2 and do not affect Bronze, Silver, or Gold scoring while this Proposal remains Draft.

### Profile schema

The generic envelope schema intentionally allows arbitrary `metadata` so extension drafts do not break existing publishers. Implementations that claim `action-governance` SHOULD additionally validate governed examples and publisher output against [`action-governance-profile.schema.json`](../action-governance-profile.schema.json), which constrains the profile-specific `metadata.tool_identity`, `metadata.provider_translation`, `metadata.risk`, `metadata.validation`, `metadata.redaction`, `metadata.retry`, `metadata.execution`, and AHP-007-compatible `metadata.approval` fields.

## Backwards-compatibility impact

- Wire format change: no. This uses optional metadata and optional PascalCase extension events.
- `schema_version` bump: no.
- Existing publishers: unaffected unless they claim `action-governance`.
- Existing subscribers: can ignore unknown metadata and optional events.

## Relationship to MCP, provider tool calling, and OpenTelemetry

AgentHook does not replace MCP or provider tool-calling APIs. MCP standardizes tool discovery and invocation. Provider APIs define model-facing call formats. Frameworks define native tool abstractions. OpenTelemetry records observability spans and metrics.

AgentHook standardizes governance semantics: pre-commit evidence, admission verdicts, approval state, normalized action/resource identity, risk metadata, trusted schema/tool identity, redaction, retry/resume, and requested-versus-executed comparison.

AgentHook events MAY be exported as OpenTelemetry spans, logs, or events, and SHOULD preserve trace context where available. OpenTelemetry records observability. AgentHook records governance evidence.

## Security considerations

Tool arguments and results can contain personal data, confidential data, credentials, session state, proprietary business data, or regulated content. Publishers MUST NOT place secrets, bearer tokens, raw credentials, session cookies, or unnecessary personal data in `metadata.tool_identity`, `metadata.provider_translation`, `metadata.risk`, `metadata.validation`, `metadata.redaction`, `metadata.retry`, or `metadata.execution`.

`metadata.tool_call_id` is an opaque stable string, not necessarily a UUID. Publishers SHOULD use non-secret provider or runtime call IDs where available, or generate a stable local identifier when the provider does not expose one. Use stable identifiers, hashes, and evidence references where possible. Treat `contains_secret: false` as an evidence claim that may require independent verification by a subscriber, scanner, gateway, or policy engine.

## Open questions

- Whether `action-governance` should become part of Gold or a future Platinum profile.
- Whether `metadata.risk.risk_class` should become a controlled vocabulary in v1.0.
- Whether schema trust should be unified with AHP-008 hook fingerprint trust in a future proposal.
