# AgentHook

An open specification for the lifecycle hooks every AI agent runtime should expose so that operators, auditors, and regulators can record what an agent did, when, why, and with what reasoning.

The specification is **Apache-2.0**. Stewardship sits with **Agentic Thinking Limited (UK)** under the commitments set out in [`GOVERNANCE.md`](./GOVERNANCE.md). Adopters benefit from a perpetual no-relicence pledge and a working-group governance model.

The first reference implementation is [HookBus](https://github.com/agentic-thinking/hookbus). Other compliant implementations are explicitly invited and will be tested against the same conformance suite.

## Why it exists

EU AI Act Article 12 (record-keeping obligations) becomes enforceable on **2 August 2026** for high-risk AI systems falling under Annex III categories. Every enterprise deploying agentic AI must demonstrate auditable, transcript-grade records of every action an agent takes. By "transcript-grade" we mean a record sufficient to reconstruct, after the fact, what the model was asked, how it reasoned, and what it returned.

Agent runtimes today expose hooks inconsistently. Coverage varies between vendors and over time. There is no shared definition of what a complete hook surface looks like, what events must be emitted, or what metadata each event must carry. Without a standard, every enterprise rebuilds the same compliance plumbing per vendor, and every regulator has to evaluate every implementation from scratch.

AgentHook defines that standard.

## Documents

- [`SPEC.md`](./SPEC.md): the wire-format specification (envelope, event types, metadata keys)
- [`GOVERNANCE.md`](./GOVERNANCE.md): how the working group operates, perpetual licensing commitments
- [`CHARTER.md`](./CHARTER.md): formal stewardship terms, signed
- [`MEMBERS.md`](./MEMBERS.md): founding members and invitee status
- [`CONFORMANCE/`](./CONFORMANCE/): test rig (forthcoming)
- [`PROPOSALS/`](./PROPOSALS/): change process (AHP, "AgentHook Proposal")

## Status

Pre-v1.0 public draft. Working group composition in progress. Substantive change proposals are made through the Proposals process.
