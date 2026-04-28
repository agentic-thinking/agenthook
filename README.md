# AgentHook

> **DRAFT — pre-v1.0.** Not yet endorsed by any external runtime. Subject to incompatible changes during the `0.x` series. See [`CHANGELOG.md`](./CHANGELOG.md).

An open technical specification for AI-agent runtime evidence: structured, subscriber-addressable envelopes for lifecycle events, tool calls, human approvals, policy denials, model interactions, and runtime control attestations.

The specification is **Apache-2.0**. Stewardship sits with **Agentic Thinking Limited (UK)** under the commitments set out in [`GOVERNANCE.md`](./GOVERNANCE.md). Adopters benefit from a perpetual no-relicence pledge and a working-group governance model.

The first reference implementation is [HookBus](https://github.com/agentic-thinking/hookbus). Compliant alternative implementations are explicitly invited and will be tested against the same conformance suite once the test rig ships.

The draft technical paper is published on Zenodo:

> Ruocco, P. (2026). *AgentHook: A Runtime Evidence Standard for Auditable AI Agent Governance*. Zenodo. https://doi.org/10.5281/zenodo.19853376


## Why it exists

AI governance frameworks increasingly depend on runtime evidence, not just policy documents. Teams need records sufficient to reconstruct, after the fact, what the model was asked, which tool it selected, what was approved or denied, what subscribers were active, and what the runtime returned.

Agent runtimes today expose hooks inconsistently. Coverage varies between vendors and over time. There is no shared definition of what a complete hook surface looks like, what events must be emitted, or what metadata each event must carry. Without a standard, every enterprise rebuilds the same compliance plumbing per vendor, and every regulator has to evaluate every implementation from scratch.

AgentHook defines the agent-specific runtime evidence layer that can support governance, audit, policy, memory, observability, and incident-review workflows.

## What it is, and is not

AgentHook is:

- an event grammar for AI-agent lifecycle evidence
- a portable envelope for publishers and subscribers
- a way to make prompts, LLM calls, tool calls, approvals, denials, errors, handoffs, sessions, and runtime attestations comparable across runtimes
- implementation-neutral: any transport, bus, or host language may conform

AgentHook is not:

- a GRC platform
- a compliance certification
- a replacement for ISO/IEC 42001, NIST AI RMF, the EU AI Act, OpenTelemetry, CloudEvents, IETF RATS, SPIFFE/SPIRE, in-toto/SLSA, Sigstore, C2PA, policy engines, or other adjacent standards and policy systems
- a requirement to use any specific bus, policy engine, subscriber, or vendor runtime

Reference implementations may demonstrate AgentHook, but they are not the standard itself. Conforming publishers, buses, and subscribers are intentionally vendor-neutral.

## Documents

- [`SPEC.md`](./SPEC.md): the wire-format specification (envelope, event types, metadata keys)
- [`STANDARDS.md`](./STANDARDS.md): how AgentHook relates to governance, observability, attestation, provenance, and policy-engine standards
- [`runtime-attestation.schema.json`](./runtime-attestation.schema.json): draft schema for publisher-supplied runtime attestation
- [`publisher-manifest.schema.json`](./publisher-manifest.schema.json): draft schema for publisher identity, hook coverage, limitations, and verification status
- [`GOVERNANCE.md`](./GOVERNANCE.md): how the working group operates, perpetual licensing commitments
- [`CHARTER.md`](./CHARTER.md): formal stewardship terms, signed
- [`MEMBERS.md`](./MEMBERS.md): founding members and invitee status
- [`CONFORMANCE/`](./CONFORMANCE/): test rig (forthcoming)
- [`PROPOSALS/`](./PROPOSALS/): change process (AHP, "AgentHook Proposal")

## Status

Pre-v1.0 public draft. Working group composition in progress. Substantive change proposals are made through the Proposals process. Runtime Attestation is a draft non-breaking extension proposed in [`PROPOSALS/AHP-004-runtime-attestation.md`](./PROPOSALS/AHP-004-runtime-attestation.md). Governance Context Metadata is a draft advisory metadata convention proposed in [`PROPOSALS/AHP-005-governance-context-metadata.md`](./PROPOSALS/AHP-005-governance-context-metadata.md). Publisher manifests are an interim local-first convention for declaring publisher identity and lifecycle coverage ahead of native AgentHook adoption.

## Quick start

Validate any event against [`envelope.schema.json`](./envelope.schema.json). See [`sample-event.json`](./sample-event.json) for the shape of a fully-populated event. A minimal publisher + subscriber sketch lives in [`SPEC.md`](./SPEC.md) Appendix A.

While the draft matures into a standard, publisher authors SHOULD ship an `agenthook.publisher.json` file at the repository root. Validate it against [`publisher-manifest.schema.json`](./publisher-manifest.schema.json) and see [`examples/publisher-manifest.codex.json`](./examples/publisher-manifest.codex.json) or [`examples/publisher-manifest.claude-code.json`](./examples/publisher-manifest.claude-code.json) for current public publisher examples.

### Implementation kit

The first CLI-first implementation kit lives in [`packages/python`](./packages/python).

```bash
cd packages/python
python -m agenthook.cli emit --event PreToolUse --source demo --session demo --tool Bash --input '{"command":"pwd"}'
python -m agenthook.cli validate ../../sample-event.json
python -m agenthook.cli doctor --target http://localhost:18800/event --token "$HOOKBUS_TOKEN"
python -m agenthook.cli init claude-code --target http://localhost:18800/event --token "$HOOKBUS_TOKEN"
python -m agenthook.cli test collector --target http://localhost:18800/event --token "$HOOKBUS_TOKEN"
```

The kit is deliberately small: envelope builders, validation, `emit`,
`doctor`, basic conformance checks, and runtime adapter scaffolding.
