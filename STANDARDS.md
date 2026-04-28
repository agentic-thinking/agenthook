# Standards Positioning

AgentHook is an open technical specification for AI-agent runtime evidence. It is designed to complement, not replace, governance, observability, attestation, provenance, or policy-engine standards.

## What AgentHook Defines

- AI-agent lifecycle event names and envelope semantics
- Subscriber-addressable events for prompts, LLM calls, tool calls, approvals, denials, errors, handoffs, sessions, and runtime attestations
- Publisher conformance tiers for lifecycle coverage, LLM transcript capture, reasoning capture where exposed, and event correlation
- Runtime attestation metadata for declaring active controls, subscribers, fail modes, and consolidation behaviour inside the existing envelope

## Adjacent Standards and Frameworks

| Layer | Examples | What they cover | AgentHook boundary |
| --- | --- | --- | --- |
| AI governance and risk | ISO/IEC 42001, NIST AI RMF, EU AI Act obligations, state AI laws | Management systems, accountability, risk vocabulary, obligations, and oversight expectations | AgentHook supplies runtime evidence those programs can consume; it does not certify compliance. |
| Observability and event transport | OpenTelemetry, CloudEvents, W3C Trace Context | Telemetry transport, traces, spans, events, and correlation | AgentHook defines the AI-agent lifecycle semantics carried by those systems. |
| Attestation, identity, and provenance | IETF RATS, SPIFFE/SPIRE, in-toto/SLSA, Sigstore | Workload identity, supply-chain provenance, signed attestations, and verification patterns | AgentHook applies runtime attestation patterns to active agent controls and subscribers. |
| Content provenance | C2PA | Provenance metadata for digital media and generated content | AgentHook records agent runtime behaviour around content creation; it does not replace media provenance standards. |
| Policy engines and controls | Microsoft AGT, OPA, Cedar, CRE-AgentProtect, custom subscribers | Deterministic policy checks, semantic gates, allow/deny/ask decisions, redaction, and workflow routing | AgentHook carries the event and verdict grammar; policy engines decide what to do. |
| GRC and evidence systems | Existing audit, risk, and compliance platforms | Control mapping, ownership, reporting, remediation, and legal workflows | AgentHook feeds comparable runtime evidence into these systems; it is not a GRC platform. |

## Portfolio Governance Use Case

Portfolio AI governance requires consistent evidence across entities, teams, vendors, and agent runtimes. AgentHook makes that possible by giving each runtime the same evidence grammar for prompts, model calls, tool calls, approvals, denials, subscriber verdicts, and runtime attestations.

This does not mean AgentHook is a portfolio governance platform. It means AgentHook can supply the runtime evidence that a portfolio governance program, GRC platform, auditor, insurer, or legal team can evaluate.

## Reference Implementations

HookBus is the first reference runtime/bus for AgentHook events. CRE-AgentProtect is an example policy subscriber. They are useful proving grounds for the specification, but conforming implementations do not need to use either project.

The standard boundary is:

- AgentHook defines the envelope and event semantics.
- Publishers emit AgentHook-conformant events.
- Subscribers consume events and return verdicts or evidence.
- Buses and adapters route events, consolidate sync decisions, and preserve fail-mode behaviour.
- Governance systems interpret the evidence against their own obligations.
