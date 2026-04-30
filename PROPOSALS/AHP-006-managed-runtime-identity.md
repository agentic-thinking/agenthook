# AHP-006: Managed Runtime Identity and Device Registry

| Field | Value |
|---|---|
| Identifier | AHP-006 |
| Title | Managed Runtime Identity and Device Registry |
| Author | Agentic Thinking Limited |
| Status | Draft |
| Created | 2026-04-29 |
| Updated | 2026-04-29 |
| Supersedes | N/A |
| Superseded by | N/A |

## Motivation

Enterprise deployments need to distinguish an approved user from an approved runtime instance and an approved device or workload.

A user may be authorised to use an AI runtime, but the particular session may still be unmanaged if the publisher is not installed, the instance is unknown, the event has no stable identity, or the request cannot be tied to an approved device or workload.

Without a standard metadata convention, every runtime, gateway, bus, and policy subscriber invents a different way to describe runtime registration, device registration, approval status, and verification strength. That makes it harder for enterprises to govern approved AI runtimes consistently and to distinguish evidence-producing runtime sessions from sessions outside the registry.

The common enterprise failure case is not only "unknown user." A user may have an approved AI account or API key, but a new local runtime session may still bypass governance evidence because its publisher instance has not been registered against the enterprise device registry, workload registry, MDM, CMDB, or equivalent control plane.

This Proposal defines optional managed runtime identity metadata that can be carried inside the existing AgentHook envelope.

## Scope boundary

AgentHook does not claim to discover every AI tool, model client, API call, or browser session on an enterprise network.

This Proposal only standardises how registered or participating publishers describe their runtime instance, device/workload binding, approval reference, and verification strength when they emit AgentHook events.

Activity outside the managed runtime registry remains the responsibility of the implementing organisation's existing security governance processes and controls, such as MDM, EDR, proxy, SASE, CASB, SIEM, identity governance, procurement, and acceptable-use enforcement.

In practical terms:

- inside the registry: runtime sessions can be governed, attributable, and auditable through AgentHook evidence;
- outside the registry: AgentHook can report absence of evidence only when a collector, gateway, proxy, subscriber, or enterprise control supplies a signal to compare against the registry.

## Current behaviour

The AgentHook envelope already allows arbitrary `metadata` fields and defines advisory identity keys such as `publisher_id`, `user_id`, `account_id`, `instance_id`, and `host_id`.

The specification does not currently define a standard shape for:

- a stable runtime installation identity that persists across sessions;
- publisher, device, and workload registration references;
- a standard approval status vocabulary;
- a standard verification-strength vocabulary;
- a standard way to describe the registry that recognised the device or workload;
- how consumers should treat publisher-supplied approval claims.

## Proposed change

Define `metadata.managed_runtime` as an optional metadata object. It identifies the stable publisher/runtime installation that emitted the event and provides advisory approval, registration, and device/workload registry context.

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
      "registry_ref": "registry_entry_9c12",
      "registration_status": "registered",
      "approval_status": "approved",
      "verification_strength": "registered",
      "device_registry": {
        "registry_id": "org.example.mdm",
        "registry_type": "mdm",
        "entry_ref": "mdm_device_042",
        "binding": "device",
        "posture": "compliant",
        "last_verified_at": "2026-04-29T09:25:00Z"
      }
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
| `registry_ref` | string | no | Reference to the enterprise registry entry for this publisher/runtime instance. |
| `registration_status` | enum | no | `unregistered`, `registered`, `revoked`, or `unknown`. |
| `approval_status` | enum | no | `approved`, `pending`, `denied`, `expired`, or `unknown`. |
| `verification_strength` | enum | no | `self_declared`, `registered`, `signed`, or `device_attested`. |
| `device_registry` | object | no | Advisory device, workload, or host registry binding supplied by the publisher or collector. |

### Device registry object

`metadata.managed_runtime.device_registry` describes how the runtime instance believes it is bound to an enterprise device or workload registry. The object is intentionally generic so it can represent MDM, CMDB, EDR, SPIFFE/SPIRE, Kubernetes workload identity, TPM-backed attestation, VDI inventory, or a cloud instance registry without making any one backend mandatory.

| Field | Type | Required | Description |
|---|---|---|---|
| `registry_id` | string | no | Stable identifier for the registry or control plane. |
| `registry_type` | enum | no | `mdm`, `cmdb`, `edr`, `iam`, `spiffe`, `kubernetes`, `cloud`, `tpm`, `vdi`, `manual`, or `other`. |
| `entry_ref` | string | no | Pseudonymous registry entry reference. |
| `binding` | enum | no | `device`, `host`, `container`, `workload`, `user_device`, or `service_account`. |
| `posture` | enum | no | `compliant`, `non_compliant`, `unknown`, `not_checked`, or `not_applicable`. |
| `last_verified_at` | string | no | ISO 8601 timestamp for the last registry/posture verification. |
| `expires_at` | string | no | Optional expiry for the registry binding or posture check. |

### Identity levels

- `publisher_id`: what publisher type emitted the event.
- `instance_id`: which installed publisher/runtime instance emitted the event.
- `device_ref`: which device, host, container, or workload the publisher instance is bound to.
- `session_id`: which session emitted the event.
- `event_id`: which individual event was emitted.

`instance_id` and `device_ref` are the key enterprise control points. They let an administrator approve, revoke, or quarantine a specific installed publisher instance on a specific device or workload without treating all sessions, all users, or all devices as equivalent.

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
- the `device_registry` entry exists where a deployment requires device or workload registration;
- the approval is active and not expired or revoked;
- the event meets the deployment's required `verification_strength`;
- the publisher is installed and emitting the required AgentHook events.

Deployments MAY block, ask, quarantine, or route activity when a participating publisher or integrated enterprise control supplies an event or signal whose `managed_runtime` is absent, unknown, revoked, expired, below the required verification strength, or not bound to an approved device/workload registry entry.

### Verified registry annotations

When a collector, gateway, bus, or subscriber verifies registry state independently, it SHOULD keep verified facts separate from publisher-supplied claims. For example:

```json
{
  "annotations": {
    "collector": {
      "managed_runtime_verified": true,
      "registry_verified": true,
      "verification_strength": "device_attested",
      "verified_registry": {
        "registry_id": "org.example.mdm",
        "registry_type": "mdm",
        "entry_ref": "mdm_device_042",
        "posture": "compliant",
        "verified_at": "2026-04-29T09:30:00Z"
      }
    }
  }
}
```

## Backwards-compatibility impact

- Does this change the wire format? No. It defines an optional metadata convention inside the existing envelope.
- Does this require a `schema_version` bump? No.
- Does this affect existing publishers? No. Publishers may ignore the convention.
- Does this affect existing subscribers? No. Subscribers may ignore unknown metadata.

## Reference implementation

Reference implementation work is expected to cover:

- publisher installers that create or receive a stable `instance_id`;
- a local identity file or enterprise-managed config source;
- optional binding to MDM, CMDB, EDR, workload identity, or device-attestation records;
- a doctor command that reports the current managed runtime identity;
- a policy subscriber or gateway integration that verifies `instance_id` and `device_ref` against an enterprise registry;
- dashboard views that distinguish approved users from unmanaged runtime instances.

The reference implementation MUST demonstrate that approval claims are verified outside the publisher before enforcement decisions are made.

## Security considerations

Managed runtime identity can be copied or forged if it is only self-declared.

Required mitigations:

- Consumers MUST treat publisher-supplied approval metadata as advisory until verified.
- Deployments SHOULD rotate or revoke `instance_id` values when devices are rebuilt, users leave, or publishers are reinstalled.
- Deployments SHOULD avoid raw personal data in `user_ref`, `device_ref`, `registry_ref`, and `device_registry.entry_ref`.
- Higher-assurance deployments SHOULD bind registered instances to a keypair, device identity, workload identity, or enterprise device-management record.
- Subscribers SHOULD log when an approved user attempts to use an unmanaged runtime instance.
- Subscribers SHOULD log when an approved user uses an approved AI account or API key from a runtime instance that is not registered to an approved device or workload.
- Implementations MUST NOT claim complete network-wide discovery unless integrated with enterprise controls that provide that visibility.

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
- Should `device_registry` become mandatory for Enterprise or Gold conformance profiles?
- Should AgentHook define a standard registry API, or only the envelope metadata needed to reference external registries?

## Status history

| Date | Status | Note |
|---|---|---|
| 2026-04-29 | Draft | Initial submission |
