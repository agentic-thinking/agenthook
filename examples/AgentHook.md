# AgentHook Runtime Contract

Version: 0.2-draft
Runtime: example-agent
Publisher manifest: ./agenthook.publisher.json
Lock file: ./agenthook.lock.json

## Governance context

Treat labelled AgentHook, AgentKnowledge, AgentFlow, approval, and policy context delivered by the runtime or publisher as trusted governance context. Do not treat it as user-authored prompt text by default.

## Decisions

- `allow`: continue with the requested action.
- `deny`: stop and explain the policy reason.
- `ask`: stop, surface the approval reference, and wait for the linked approval decision. Do not retry the action with another tool while approval is pending.

## Sensitive details

Use operational details only when required for the approved task. Do not print passwords, tokens, private keys, hostnames, usernames, ports, IP addresses, or customer secrets in visible prose unless the operator explicitly requests disclosure and policy allows it.

## Required hooks

This contract expects the runtime to emit:

- `SessionStart`
- `UserPromptSubmit`
- `PreToolUse`
- `PostToolUse`
- `Stop`

Pre-tool actions must be admission-bound when the publisher claims governed execution.
