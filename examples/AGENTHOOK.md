# AgentHook Example Runtime Contract

This example contract is intentionally minimal. It demonstrates the
human-readable counterpart to `agenthook.lock.json`.

## Required Events

- `RuntimeContractLoaded`
- `SessionStart`
- `UserPromptSubmit`
- `PreToolUse`
- `ToolActivity`
- `PostToolUse`
- `HumanDecision`
- `EvidenceSeal`
- `SessionEnd`

## Runtime Expectations

The runtime loads `agenthook.lock.json` before the session starts, emits
`RuntimeContractLoaded`, and records the loaded contract digest in session
metadata where available.

Prompt text may reference this contract, but prompt text is not the contract.
