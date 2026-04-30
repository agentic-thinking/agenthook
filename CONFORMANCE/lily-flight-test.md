# Lily Flight Test

Lily Flight Test is a minimal AgentHook conformance fixture. It exists to
exercise the complete AgentHook lifecycle surface through a collector or bus.
It is not a production SDK and not an autonomous agent runtime.
HookBus is one reference collector that can receive these events; it is not
required by AgentHook or by this fixture.

The fixture lives in [`packages/lily-flight-test`](../packages/lily-flight-test).

## What it emits

`lily-flight --preflight` emits one deterministic session containing all ten
canonical AgentHook event types, in order:

1. `SessionStart`
2. `UserPromptSubmit`
3. `PreLLMCall`
4. `PostLLMCall`
5. `ModelResponse`
6. `PreToolUse`
7. `PostToolUse`
8. `AgentHandoff`
9. `ErrorOccurred`
10. `SessionEnd`

The preflight `ModelResponse` carries synthetic reasoning metadata so that
collectors, dashboards, and subscribers can verify reasoning-field handling
without making an external model call.

## Commands

```bash
cd packages/lily-flight-test
python3 -m pip install -e .
python3 -m pytest -q

export AGENTHOOK_COLLECTOR_URL=http://127.0.0.1:18800/event
export AGENTHOOK_COLLECTOR_TOKEN=...
lily-flight --preflight
```

For a real provider reasoning smoke test, set `LLM_API_KEY`, `LLM_BASE_URL`,
and `LLM_MODEL` outside the repository and run:

```bash
lily-flight reasoning-smoke "Reply exactly: TASK COMPLETE"
```

## Conformance status

This fixture is self-attested as **Gold** for the AgentHook v0.1 draft because
it emits all ten canonical events, includes matched LLM and tool pairs, carries
reasoning metadata when available or synthetic reasoning in deterministic
preflight mode, and uses correlation IDs across the LLM, tool, and handoff
segments.

This is a technical interoperability signal only. It is not a legal compliance
certification and it does not replace the formal conformance harness planned for
specification v1.0.
