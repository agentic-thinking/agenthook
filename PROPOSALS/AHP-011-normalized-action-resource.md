# AHP-011: Normalized Action and Resource Fields

**Status:** Draft  
**Created:** 2026-05-20  
**Target:** AgentHook v0.2 draft amendment  
**Type:** Non-breaking envelope extension

## Summary

Add publisher-agnostic action and resource fields to `PreToolUse` and `PostToolUse` events:

- `action`
- `resource_kind`
- `resource`
- `resource_scope`
- `operation_risk`

The fields describe the semantic operation being attempted while preserving the runtime's native `tool_name` and `tool_input`.

## Motivation

Agent runtimes expose different native tools for the same operation. A file read may appear as:

- `tool_name: "Bash"`, `tool_input.command: "cat /workspace/customer-risk.md"`
- `tool_name: "read"`, `tool_input.path: "/workspace/customer-risk.md"`
- an MCP file resource
- a browser/download operation

Policy subscribers should not need brittle per-publisher parsing or fake tool aliases to answer the same governance question: "is this agent trying to read a sensitive file?"

## Proposal

Publishers SHOULD keep native runtime fields unchanged:

```json
{
  "tool_name": "read",
  "tool_input": {
    "path": "/workspace/customer-risk.md"
  }
}
```

When the operation can be identified safely, publishers SHOULD add normalized fields:

```json
{
  "action": "read",
  "resource_kind": "file",
  "resource": "/workspace/customer-risk.md",
  "resource_scope": "workspace",
  "operation_risk": "sensitive_read"
}
```

Subscribers SHOULD prefer normalized fields for portable policy and MAY fall back to native fields when normalized fields are absent.

Publishers SHOULD NOT alias or rewrite `tool_name` solely to satisfy a legacy subscriber rule shape. If compatibility data is needed, it SHOULD be carried in `metadata` without hiding the native tool.

## Compatibility

This is non-breaking:

- Existing v0.2 events remain valid.
- Publishers may omit the new fields.
- Subscribers that do not understand the fields can ignore them.
- Buses can enrich the fields where appropriate, but should annotate derived enrichment.

## Recommended Vocabulary

Recommended actions:

- `read`
- `write`
- `edit`
- `delete`
- `execute`
- `query`
- `search`
- `open`
- `send`
- `publish`
- `approve`
- `handoff`

Recommended resource kinds:

- `file`
- `directory`
- `shell`
- `process`
- `database`
- `table`
- `url`
- `email`
- `message`
- `repository`
- `package`
- `container`
- `kubernetes`
- `cloud`
- `model`
- `agent`
- `approval`
- `ticket`
- `secret`
- `unknown`

## Conformance Impact

For v0.2, this is an advisory draft amendment. Future Gold or Platinum profiles may require normalized action/resource fields for publishers that expose tool calls capable of reading, writing, executing, querying, sending, opening, or publishing resources.
