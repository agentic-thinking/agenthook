# Changelog

All notable changes to the AgentHook specification are recorded in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Per [`GOVERNANCE.md`](./GOVERNANCE.md), breaking changes to the specification require a deprecation window of no less than nine months.

## [Unreleased]

## [0.2.0] - 2026-05-19

### Added
- Draft Runtime Attestation proposal (`AHP-004`) defining `metadata.runtime_attestation` as a non-breaking way for publishers to declare active runtime controls.
- Draft `runtime-attestation.schema.json`.
- Security guidance for the prompt-injection boundary between user-authored policy text and publisher-supplied runtime attestation.
- `STANDARDS.md` describing how AgentHook complements governance, observability, attestation, provenance, and policy-engine standards without replacing them.
- Draft Governance Context Metadata proposal (`AHP-005`) defining `metadata.governance_context` as advisory task, policy, and workflow context inside the existing envelope.
- Draft Managed Runtime Identity proposal (`AHP-006`) for runtime instance, user, device, workload, and registry binding metadata.
- Draft Approval Lifecycle Metadata proposal (`AHP-007`) for ask, approval, denial, retry, resume, and timeout flows.
- Draft Hook Fingerprint Trust proposal (`AHP-008`) for trusted, modified, untrusted, disabled, unknown, and unsupported hook states.
- Draft Runtime Contract File proposal (`AHP-009`) defining `AgentHook.md`, `agenthook.lock.json`, optional signatures, and `RuntimeContractLoaded`.
- Example `AgentHook.md` and `agenthook.lock.json` files for runtime contract discovery.

### Changed
- Up-issued the draft specification to v0.2 to reflect runtime attestation, managed identity, approval lifecycle metadata, hook fingerprint trust, and runtime contract discovery work.
- Repositioned AgentHook as an AI-agent runtime evidence specification, with portfolio governance described as a use case rather than the scope of the standard.
- Removed product-specific policy subscriber examples from steward-facing standards positioning.

## [0.1.0] - 2026-04-26

### Added
- Initial public draft of `SPEC.md` covering envelope format, ten canonical event types, standard metadata keys, hook delivery semantics, and Bronze/Silver/Gold conformance tiers.
- `CHARTER.md` with binding stewardship terms (Apache-2.0 in perpetuity, no royalty, irrevocable patent grant, right to fork, foundation transfer trigger).
- `GOVERNANCE.md` with Working Group structure, decision rules, and the AHP Proposal process.
- `MEMBERS.md` placeholder for Working Group composition.
- `CONFORMANCE/` placeholder for the conformance test harness.
- `PROPOSALS/` directory with `TEMPLATE.md` for AgentHook Proposals.
- `envelope.schema.json` machine-readable JSON Schema for the event envelope.
- `sample-event.json` example PostLLMCall event matching SPEC section 7.
- `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md`.

### Notes
- This project follows [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html). Pre-1.0 versions (`0.x.y`) signal that the public API may evolve; breaking changes during the `0.x` series are documented here with migration notes. The 1.0 release locks the wire format under the change-process defined in [`GOVERNANCE.md`](./GOVERNANCE.md).
