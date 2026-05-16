# AHP-008: Hook Fingerprint Trust

| Field | Value |
|---|---|
| Identifier | AHP-008 |
| Title | Hook Fingerprint Trust |
| Author | Agentic Thinking maintainers |
| Status | Draft |
| Created | 2026-05-16 |
| Updated | 2026-05-16 |
| Supersedes | N/A |
| Superseded by | N/A |

## Motivation

Agent runtimes increasingly need to distinguish an installed hook from a trusted hook. A hook file, command, plugin, or runtime adapter can be present on disk and still be unsafe to execute if it has changed since review, was installed by an untrusted actor, or no longer matches the approved governance path.

OpenAI Codex `0.130.0` introduced a hook trust and review model where installed hooks can exist and pass basic configuration checks, but real session hooks do not execute until their fingerprint is trusted. That pattern is useful beyond Codex. AgentHook should define a vendor-neutral convention for hook identity, fingerprinting, and trust state so enterprise operators can detect modified or unreviewed runtime hooks before an agent acts.

Without a shared convention:

- publishers invent incompatible hook identity fields;
- preflight checks can pass while runtime hooks are suppressed by the host;
- changed adapter commands can silently drift away from the reviewed governance path;
- operators cannot easily tell whether the active hook surface is trusted, modified, untrusted, disabled, or unknown.

## Current behaviour

`SPEC.md` already defines runtime attestation, publisher manifests, managed runtime identity, and admission-bound pre-action evidence. These cover what a runtime claims is active and whether tool calls are in the admission path.

The current specification does not define:

- a stable hook or adapter fingerprint;
- how a runtime reports whether a hook was reviewed or trusted;
- how a publisher manifest declares expected hook fingerprints;
- how preflight or conformance tools should treat modified or untrusted hooks.

## Proposed change

Define hook fingerprint trust metadata that may appear in:

- `metadata.runtime_attestation.hooks`;
- `metadata.managed_runtime.hooks`;
- `agenthook.publisher.json`;
- conformance and preflight reports.

Minimum shape:

```json
{
  "hook_trust": {
    "hook_id": "uk.agenticthinking.publisher.openai.codex-cli.pretooluse",
    "runtime": "codex-cli",
    "hook_event": "PreToolUse",
    "command": "env HOOKBUS_URL=... codex-gate",
    "fingerprint": "sha256:6c8a...",
    "fingerprint_alg": "sha256",
    "trust_status": "trusted",
    "reviewed_at": "2026-05-16T13:42:00Z",
    "reviewed_by": "operator:local-admin",
    "source": "local_config",
    "config_path": "~/.codex/hooks.json"
  }
}
```

Standard fields:

| Field | Type | Required | Purpose |
|---|---|---|---|
| `hook_id` | string | yes | Stable identifier for this logical hook or adapter entry |
| `runtime` | string | yes | Runtime family or product identifier |
| `hook_event` | string | yes | AgentHook event or host hook event the entry maps to |
| `command` | string | no | Human-readable command or plugin reference. Secrets SHOULD be redacted |
| `fingerprint` | string | yes when available | Cryptographic digest of the hook command, file, plugin, or canonical hook config |
| `fingerprint_alg` | string | yes when `fingerprint` is present | Digest algorithm, initially `sha256` |
| `trust_status` | enum | yes | `trusted`, `modified`, `untrusted`, `disabled`, `unknown`, or `not_supported` |
| `reviewed_at` | string | no | ISO 8601 timestamp when the current fingerprint was approved |
| `reviewed_by` | string | no | Pseudonymous reviewer, group, device, or registry reference |
| `source` | enum | no | `runtime`, `publisher`, `bus`, `local_config`, `registry`, or `operator` |
| `config_path` | string | no | Local or logical config path where the hook was declared |
| `expected_fingerprint` | string | no | Fingerprint expected by a manifest, registry, or policy |
| `observed_fingerprint` | string | no | Fingerprint observed during preflight or attestation |

Recommended status semantics:

- `trusted`: the observed fingerprint matches a reviewed hook entry.
- `modified`: the hook exists, but the observed fingerprint differs from the trusted fingerprint.
- `untrusted`: the hook exists, but no trusted fingerprint has been recorded.
- `disabled`: the hook was expected but is not active.
- `unknown`: the runtime or publisher could not determine trust state.
- `not_supported`: the runtime does not expose hook fingerprint or trust data.

Admission-bound publishers SHOULD include hook trust state in runtime attestation before the first governed action. If a publisher claims `claims.tool_calls_are_runtime_gated: true`, its active blockable hook entries SHOULD have `trust_status: "trusted"` or an equivalent bus/registry verified state.

Preflight and conformance tools SHOULD fail or warn prominently when a required admission-bound hook is `modified`, `untrusted`, `disabled`, or `unknown`, depending on the configured fail mode.

Publisher manifests MAY declare expected hook entries:

```json
{
  "hook_trust": [
    {
      "hook_id": "uk.agenticthinking.publisher.openai.codex-cli.pretooluse",
      "runtime": "codex-cli",
      "hook_event": "PreToolUse",
      "config_path": "~/.codex/hooks.json",
      "fingerprint_alg": "sha256",
      "expected_fingerprint": "sha256:6c8a..."
    }
  ]
}
```

## Backwards-compatibility impact

- Does this change the wire format? No. It uses existing `metadata` and manifest extension points.
- Does this require a `schema_version` bump? No.
- Does this affect existing publishers? No. Existing publishers may omit hook trust metadata.
- Does this affect existing subscribers? No. Subscribers that do not understand hook trust metadata can ignore it.

This Proposal defines an optional metadata convention. It does not require runtimes to implement Codex-style hook review flows.

## Security considerations

Hook trust metadata is evidence, not authority. A publisher claiming `trust_status: "trusted"` MUST NOT be sufficient for an allow decision unless the responsible runtime, bus, gateway, registry, or policy subscriber verifies the claim.

Fingerprints SHOULD be computed over canonicalised hook material. For command hooks, this may include the command string after environment expansion rules are applied, the target executable path, and the digest of the executable or script where practical. For plugin hooks, this may include the plugin file digest, manifest digest, and runtime configuration entry.

Fingerprints MUST NOT include raw bearer tokens, API keys, passwords, or other secrets. Commands and config paths SHOULD redact secret values before being stored in evidence or displayed to operators.

If a required admission-bound hook is modified or untrusted, regulated or high-assurance deployments SHOULD fail closed until reviewed.

## Reference implementation

OpenAI Codex `0.130.0` introduced hook fingerprint trust behaviour. On the Agentic Thinking demo server, the Codex HookBus preflight was updated on 2026-05-16 to:

1. enable the current Codex hook feature flag;
2. normalise the installed HookBus hook config;
3. compute trusted hashes for the HookBus Codex hooks;
4. write those trusted fingerprints into Codex local config;
5. run doctor checks before the Codex session starts;
6. verify real session events reached HookBus.

This restored live `SessionStart`, `UserPromptSubmit`, and `Stop` HookBus events after Codex began requiring hook trust.

## Alternatives considered

### Leave hook trust to each runtime

Rejected. Runtime-specific trust models are useful, but AgentHook needs a portable way to report and test whether the active hook path is trusted.

### Put trust only in publisher manifests

Rejected. Manifests describe expected state. Runtime attestation and preflight need to report observed state.

### Treat hook trust as managed runtime identity only

Rejected. Managed runtime identity says which runtime instance emitted an event. Hook fingerprint trust says whether a specific hook or adapter entry has changed since review.

## Unresolved questions

- Should `trusted` require a local human review, a signed manifest, a registry entry, or any of those?
- Should admission-bound conformance require trusted fingerprints for all blockable hooks?
- Should `fingerprint` cover only hook configuration, or also the executable/script referenced by the hook?
- Should hook trust become part of runtime attestation minimum shape in v1.0?

## Status history

| Date | Status | Note |
|---|---|---|
| 2026-05-16 | Draft | Initial proposal after Codex hook trust behaviour was observed in production testing |
