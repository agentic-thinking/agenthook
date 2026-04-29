# AHP-006: Managed Runtime Identity

| Field | Value |
|---|---|
| Identifier | AHP-006 |
| Title | Managed Runtime Identity |
| Author | Agentic Thinking Limited |
| Status | Draft |
| Created | 2026-04-29 |
| Updated | 2026-04-29 |
| Supersedes | N/A |
| Superseded by | N/A |

## Motivation

Enterprise deployments need to distinguish an approved user from an approved runtime instance.

A user may be authorised to use an AI runtime, but the particular session may still be unmanaged if the publisher is not installed, the instance is unknown, the event has no stable identity, or the request cannot be tied to an approved device or workload.

Without a standard metadata convention, every runtime, gateway, bus, and policy subscriber invents a different way to describe runtime registration, approval status, and verification strength. That makes it harder for enterprises to block unmanaged AI activity while allowing sanctioned runtime use.

This Proposal defines optional managed runtime identity metadata that can be carried inside the existing AgentHook envelope.

## Current behaviour

The AgentHook envelope already allows arbitrary `metadata` fields and defines advisory identity keys such as `publisher_id`, `user_id`, `account_id`, `instance_id`, and `host_id`.

The specification does not currently define a standard shape for:

- a stable runtime installation identity that persists across sessions;
- registration and approval references;
- a standard approval status vocabulary;
- a standard verification-strength vocabulary;
- how consumers should treat publisher-supplied approval claims.

## Proposed change

Define `metadata.managed_runtime` as an optional metadata object. It identifies the stable publisher/runtime installation that emitted the event and provides advisory approval and registration context.

Example:

```json
{
  "metadata": {
    "managed_runtime": {
      "publisher_id": "org.example.publisher.codex-cli",
      "runtime_id": "codex-cli",
      "instance_id": "pubinst_7f91c2",
      "session_id": "sess_abc123",
      "user_ref": "user_8a21",
      "device_ref": "device_042",
      "approval_ref": "approval_12345",
      "registration_status": "registered",
      "approval_status": "approved",
      "verification_strength": "registered"
    }
  }
}
```

### Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `publisher_id` | string | no | Stable publisher package/type identifier. |
| `runtime_id` | string | no | Runtime family or product identifier. |
| `instance_id` | string | no | Stable local publisher/runtime installation identity. SHOULD persist across sessions until explicitly rotated or revoked. |
| `session_id` | string | no | Current runtime session. SHOULD change per session and SHOULD match the envelope `session_id` where possible. |
| `user_ref` | string | no | Pseudonymous user, account, or principal reference. |
| `device_ref` | string | no | Pseudonymous device, host, container, or workload reference. |
| `approval_ref` | string | no | Reference to an enterprise approval, change ticket, registry entry, or workflow item. |
| `registration_status` | enum | no | `unregistered`, `registered`, `revoked`, or `unknown`. |
| `approval_status` | enum | no | `approved`, `pending`, `denied`, `expired`, or `unknown`. |
| `verification_strength` | enum | no | `self_declared`, `registered`, `signed`, or `device_attested`. |

### Identity levels

- `publisher_id`: what publisher type emitted the event.
- `instance_id`: which installed publisher/runtime instance emitted the event.
- `session_id`: which session emitted the event.
- `event_id`: which individual event was emitted.

`instance_id` is the key enterprise control point. It lets an administrator approve, revoke, or quarantine a specific installed publisher instance without treating all sessions or all users as equivalent.

### Verification strength

- `self_declared`: the publisher supplied the fields, but no external registry or signature has verified them.
- `registered`: a collector, gateway, or policy subscriber matched the instance against an enterprise registry.
- `signed`: the event or attestation is signed or MACed by a key bound to the registered instance.
- `device_attested`: the instance is also bound to a verified device, workload identity, MDM record, SPIFFE identity, TPM-backed attestation, or equivalent enterprise control.

## Trust constraints

`metadata.managed_runtime` is evidence, not authority.

Consumers MUST NOT treat `approval_status: "approved"` as sufficient permission by itself.

Gateways, collectors, policy subscribers, or enterprise registries SHOULD independently verify:

- the `instance_id` exists;
- the instance is assigned to the expected user, account, device, or workload;
- the approval is active and not expired or revoked;
- the event meets the deployment's required `verification_strength`;
- the publisher is installed and emitting the required AgentHook events.

Deployments MAY block, ask, quarantine, or route unmanaged AI activity when `managed_runtime` is absent, unknown, revoked, expired, or below the required verification strength.

## Backwards-compatibility impact

- Does this change the wire format? No. It defines an optional metadata convention inside the existing envelope.
- Does this require a `schema_version` bump? No.
- Does this affect existing publishers? No. Publishers may ignore the convention.
- Does this affect existing subscribers? No. Subscribers may ignore unknown metadata.

## Reference implementation

Reference implementation work is expected to cover:

- publisher installers that create or receive a stable `instance_id`;
- a local identity file or enterprise-managed config source;
- a doctor command that reports the current managed runtime identity;
- a policy subscriber or gateway integration that verifies `instance_id` against a registry;
- dashboard views that distinguish approved users from unmanaged runtime instances.

The reference implementation MUST demonstrate that approval claims are verified outside the publisher before enforcement decisions are made.

## Security considerations

Managed runtime identity can be copied or forged if it is only self-declared.

Required mitigations:

- Consumers MUST treat publisher-supplied approval metadata as advisory until verified.
- Deployments SHOULD rotate or revoke `instance_id` values when devices are rebuilt, users leave, or publishers are reinstalled.
- Deployments SHOULD avoid raw personal data in `user_ref` and `device_ref`.
- Higher-assurance deployments SHOULD bind registered instances to a keypair, device identity, workload identity, or enterprise device-management record.
- Subscribers SHOULD log when an approved user attempts to use an unmanaged runtime instance.

## Alternatives considered

### Put approval directly in runtime attestation

Rejected for this draft. Runtime attestation describes session controls. Managed runtime identity describes instance registration and enterprise approval. They are related but not the same trust object.

### Make approval a new canonical event type

Rejected for this draft. Approval records often live in enterprise workflow systems, registries, or identity systems. AgentHook should carry references and evidence without mandating the approval workflow.

### Require signatures at Bronze

Rejected for this draft. Signatures are valuable, but mandatory signing would make early adoption harder. The `verification_strength` field leaves a path from self-declared metadata to signed or device-attested deployments.

## Unresolved questions

- Should `instance_id` become mandatory for Silver or Gold conformance?
- Should AgentHook define a standard local identity file path?
- Should future versions define a canonical challenge-response flow for registering publisher instances?
- Should `approval_ref` support a URI format with integrity binding?

## Status history

| Date | Status | Note |
|---|---|---|
| 2026-04-29 | Draft | Initial submission |
