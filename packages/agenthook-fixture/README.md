# AgentHook Conformance Fixture

Minimal AgentHook conformance fixture for AgentHook-compatible HTTP collectors,
event buses, and governance test environments.

This is not a production SDK and not an autonomous agent. It exists to prove
that a runtime can emit the full AgentHook lifecycle surface. HookBus is the
default local collector example, not a requirement of the standard.

## Commands

```bash
agenthook-fixture preflight
agenthook-fixture --preflight
agenthook-fixture reasoning-smoke "Reply exactly: TASK COMPLETE"
```

`preflight` emits the core AgentHook lifecycle hooks:

- `SessionStart`
- `UserPromptSubmit`
- `PreLLMCall`
- `PostLLMCall`
- `ModelResponse`
- `PreToolUse`
- `PostToolUse`
- `AgentHandoff`
- `ErrorOccurred`
- `SessionEnd`

## Environment

Set `AGENTHOOK_COLLECTOR_URL` to an AgentHook-compatible collector endpoint and
set `AGENTHOOK_COLLECTOR_TOKEN` if that collector requires a bearer token.

For local HookBus testing, the fixture also accepts `HOOKBUS_URL`,
`HOOKBUS_TOKEN`, and `HOOKBUS_SOURCE` as compatibility aliases.

Optional OpenAI-compatible reasoning smoke:

Set `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL`, `LLM_PROVIDER`, and
`LLM_REASONING_MODE` in your shell or private environment file.
