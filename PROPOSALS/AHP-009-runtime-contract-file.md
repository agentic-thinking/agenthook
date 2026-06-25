# AHP-009: AgentHook Runtime Contract File

| Field | Value |
|---|---|
| Identifier | AHP-009 |
| Title | AgentHook Runtime Contract File |
| Author | Agentic Thinking maintainers |
| Status | Draft |
| Created | 2026-05-17 |
| Updated | 2026-05-17 |
| Supersedes | N/A |
| Superseded by | N/A |

## Motivation

AgentHook is intended to be the vendor-facing compatibility contract for agent runtimes, CLIs, SDKs, wrappers, and buses. The wire envelope defines what evidence is emitted, but conforming agents also need a predictable local contract that explains how governance context, approval decisions, sensitive operational details, and runtime boundaries must be handled before the agent acts.

Vendor-specific instruction files such as `CLAUDE.md` are useful for one runtime, but they do not create a portable standard. Without a shared AgentHook runtime contract file, each publisher has to re-express the same behavioural requirements in runtime-specific formats. That creates drift and makes enterprise governance depend on prompt wording instead of a reviewed runtime contract.

A standard `AgentHook.md` file gives vendors and operators one human-readable contract that can be discovered, loaded, hashed, attested, and referenced by runtime events.

## Current behaviour

The current draft specification defines envelopes, event types, publisher manifests, runtime attestation, approval lifecycle metadata, managed runtime identity, and hook fingerprint trust. It does not yet define a standard agent-facing contract file.

The current ecosystem therefore relies on a mix of:

- runtime-specific instruction files;
- publisher README guidance;
- ad hoc environment variables;
- policy subscriber responses;
- local demo instructions;
- human operator convention.

Those mechanisms can work locally, but they are not enough for a vendor-neutral standard.

## Proposed change

Define `AgentHook.md` as the preferred human-readable runtime contract file for AgentHook-aware publishers and runtimes.

A publisher or runtime MAY also recognise `AGENTHOOK.md` as a case-stable compatibility alias, but new documentation SHOULD use `AgentHook.md`.

A conforming runtime contract set MAY include:

| File | Purpose |
|---|---|
| `AgentHook.md` | Human-readable runtime contract for agents, operators, and reviewers |
| `agenthook.lock.json` | Machine-readable contract digest, version, required hooks, and policy expectations |
| `agenthook.signature` | Optional detached signature or registry proof for high-assurance deployments |

The runtime contract SHOULD cover:

- how to treat labelled AgentHook, AgentKnowledge, AgentFlow, policy, and approval context;
- how to honour `allow`, `deny`, and `ask` decisions;
- how to stop after an approval request instead of trying alternate tools;
- how to preserve `event_id`, `session_id`, `action_id`, `tool_call_id`, and approval references;
- how to handle sensitive operational details without printing them in visible prose;
- how to report blocked, denied, approved, resumed, and failed actions to the user;
- which hooks are required for the runtime to claim admission-bound governance;
- which fail mode applies when the bus or subscribers are unavailable;
- which publisher manifest and runtime attestation fields bind the contract to the running instance.

## RuntimeContractLoaded event

Publishers MAY emit an additional PascalCase event named `RuntimeContractLoaded` before the first governed action in a session. This event is not part of the v0.2 core ten-event conformance set while this Proposal remains Draft.

Minimum metadata shape:

```json
{
  "event_type": "RuntimeContractLoaded",
  "evidence_phase": "pre_commit",
  "metadata": {
    "runtime_contract": {
      "human_readable_path": "./AgentHook.md",
      "lock_path": "./agenthook.lock.json",
      "contract_version": "0.2-draft",
      "contract_hash": "sha256:...",
      "signature_status": "unsigned",
      "required_hooks": ["UserPromptSubmit", "PreToolUse", "PostToolUse", "Stop"],
      "fail_mode": "fail_closed"
    }
  }
}
```

Recommended fields:

| Field | Type | Purpose |
|---|---|---|
| `human_readable_path` | string | Path to `AgentHook.md` or a recognised alias |
| `lock_path` | string | Path to `agenthook.lock.json` when present |
| `contract_version` | string | Version of the local runtime contract |
| `contract_hash` | string | Digest of the loaded contract material |
| `signature_status` | enum | `signed`, `unsigned`, `invalid`, `unknown`, or `not_supported` |
| `signature_ref` | string | Optional signature, registry, or transparency-log reference |
| `required_hooks` | array | AgentHook events required for the claimed governance mode |
| `fail_mode` | enum | `fail_open` or `fail_closed` |

## Conformance guidance

Bronze publishers MAY discover `AgentHook.md` and record its digest in runtime attestation.

Bronze, Silver, and Gold v0.2 conformance remains hook and evidence based. This draft does not make `AgentHook.md`, `agenthook.lock.json`, signatures, or `RuntimeContractLoaded` mandatory for Silver.

High-assurance publishers SHOULD load `AgentHook.md`, load `agenthook.lock.json` when present, and emit `RuntimeContractLoaded` before the first governed action. Publishers claiming a Platinum or equivalent high-assurance profile SHOULD verify signatures when supplied and MUST NOT enter that high-assurance mode if required runtime contract material is missing, modified, or invalid.

If high-assurance mode is requested and the required runtime contract is missing, modified, unsigned, or invalid, the publisher SHOULD fail closed or downgrade its conformance claim.

The contract file is not a substitute for enforcement. It is the reviewed, discoverable declaration of expected runtime behaviour. Enforcement still belongs to the runtime, publisher, bus, gateway, and policy subscribers.

## Backwards-compatibility impact

- Does this change the wire format? No. It uses an optional additional event type and existing metadata extension points.
- Does this require a `schema_version` bump? No.
- Does this affect existing publishers? No. Existing publishers may omit runtime contract metadata.
- Does this affect existing subscribers? No. Subscribers that do not understand `RuntimeContractLoaded` can ignore it.

## Security considerations

`AgentHook.md` is governance context, not arbitrary user prompt text. Runtimes SHOULD distinguish a reviewed runtime contract from user-authored session content. A malicious user prompt MUST NOT be able to override the active runtime contract.

Contract hashes MUST NOT include raw secrets. Contract files SHOULD describe sensitive-data handling rules, but SHOULD NOT contain passwords, bearer tokens, private keys, or customer secrets.

If a runtime surfaces any part of the contract to the model, it SHOULD do so as trusted runtime context or system-level context, not as user-authored text. Where the host runtime cannot make that distinction, the publisher SHOULD clearly mark the context source and SHOULD rely on pre-tool enforcement rather than prompt compliance alone.

## Reference implementation sketch

A local publisher can implement the draft convention by:

1. searching the working directory and parent directories for `AgentHook.md`, then `AGENTHOOK.md`;
2. loading `agenthook.lock.json` if present;
3. computing a SHA-256 digest over the loaded contract material;
4. verifying a detached signature or registry entry where configured;
5. emitting `RuntimeContractLoaded` before the first governed action;
6. including the runtime contract digest in runtime attestation;
7. treating `ask` decisions as non-bypassable pauses until the linked approval is resolved.

## Alternatives considered

1. Keep using vendor-specific files only. Rejected because it makes AgentHook depend on runtime-specific instruction names.
2. Put all behaviour in `agenthook.publisher.json`. Rejected because publisher manifests describe package capability, not local operational policy.
3. Put all behaviour in subscriber responses. Rejected because agents need stable pre-session behaviour before the first subscriber response arrives.

## Unresolved questions

- Whether `RuntimeContractLoaded` should become a canonical event in v1.0 or remain an optional extension.
- Whether `agenthook.lock.json` needs a formal JSON schema in the next proposal.
- Whether case-sensitive filesystems should require `AgentHook.md` only or continue recognising `AGENTHOOK.md` as an alias.
