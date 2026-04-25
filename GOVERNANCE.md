# Governance

This document defines how the AgentHook specification is stewarded, who may participate, how changes are made, and the binding commitments under which the specification is published.

## Stewardship

The AgentHook specification is published and stewarded by **Agentic Thinking Limited**, a private company limited by shares incorporated in England and Wales (company number 17152930, registered 13 April 2026, registered office in the United Kingdom).

Stewardship is provisional. The intent is to transfer stewardship to a neutral foundation (CEN/CENELEC Workshop Agreement, Linux Foundation, or a purpose-incorporated AgentHook Foundation) when adoption justifies the legal and operational cost.

Stewardship by Agentic Thinking Limited does not confer commercial rights over implementations. The specification is licensed independently of any product offered by the steward. See [`CHARTER.md`](./CHARTER.md) for the binding commitments.

## Licensing commitments

The following commitments are **binding and irrevocable** on Agentic Thinking Limited. They are written into the Charter and may not be unilaterally amended.

1. **The specification is licensed under Apache License 2.0 in perpetuity.** The license shall not be replaced, restricted, or supplemented with additional terms by the steward or any successor.
2. **No royalty fees.** No fee may be charged by the steward or any successor for the right to implement the specification, claim conformance with the specification, or use the specification's name in describing an implementation.
3. **No participation gating.** Any individual or organisation may submit Proposals (see below) and contribute to working-group discussion. Vote-eligible Working Group seats are limited to founding and elected members; this does not restrict contribution.
4. **Patent grant.** The steward grants, on behalf of itself, an irrevocable royalty-free patent license to any party implementing the specification, covering any claims the steward owns that would otherwise be infringed by a conforming implementation. This grant survives any change of stewardship.
5. **Right to fork.** The specification may be forked at any time by any party under the terms of the Apache License 2.0. The steward may not assert trademark rights against forks, provided the forks do not represent themselves as the official AgentHook specification or as conforming when they are not.
6. **Twelve-month notice on any change to these commitments.** Any proposed amendment to the Charter or to these commitments requires twelve months' public notice and the unanimous approval of the Working Group.

## Working Group

The Working Group ("WG") authors and maintains the specification.

### Composition

- **Founding Members** — invited at launch on the basis of having implemented hooks materially relevant to the specification. Founding membership is permanent; founding members may step down but cannot be removed except for breach of the Code of Conduct or written withdrawal.
- **Elected Members** — added by majority vote of existing WG members. There is no fixed cap; growth follows adoption.
- **Stewardship Seat** — Agentic Thinking Limited holds one non-voting chair seat for procedural facilitation. The chair has no casting vote on substantive matters.

The current Founding Member roster and invitation status are tracked in [`MEMBERS.md`](./MEMBERS.md).

### Meeting cadence

- One scheduled video meeting per month, public agenda, public minutes.
- Asynchronous discussion in the repository's GitHub Discussions and Issues.
- Time commitment expectation for active members: approximately one to two hours per month plus PR review.

### Decisions

- **Routine updates** (clarifications, examples, typo fixes): merge by any WG member, approved by one WG second.
- **Substantive changes** (event types, required metadata, conformance levels): require a numbered Proposal (see below) and approval by majority WG vote.
- **Breaking changes** (changes to envelope shape, removal of any required field, conformance-level redefinitions): require unanimous WG approval and a deprecation window of no less than nine months.
- **Charter amendments**: require unanimous WG approval and twelve months' public notice (binding under commitment 6).

## Proposals

Substantive specification changes are made via numbered AgentHook Proposals ("AHPs"), structured as files in [`PROPOSALS/`](./PROPOSALS/).

Each Proposal contains:
- Identifier (`AHP-NNN`), title, author, status (draft, accepted, rejected, withdrawn, superseded)
- Motivation, current behaviour, proposed change, alternatives considered
- Backwards-compatibility impact and deprecation timeline if any
- Reference implementation or implementation sketch

Proposals are merged via PR following the decision rules above.

## Conformance

The conformance test suite, scoring methodology, and certification process are defined under [`CONFORMANCE/`](./CONFORMANCE/) and operated by the steward (or a designated independent body) under the same Charter commitments.

Conformance certification carries no fee for self-test (open-source rig). The steward may charge a cost-recovery fee for hosted certification, periodic re-test, and signed reports for procurement use; such fees are subject to publication and may not be used to gate participation in the Working Group or in the specification itself.

## Code of Conduct

Participation in the Working Group is governed by the Contributor Covenant Code of Conduct, version 2.1 or later. The steward serves as initial enforcement point; the Working Group may elect an independent enforcement panel at any time.

## Changes to this document

Changes to GOVERNANCE.md follow the Charter amendment process: unanimous Working Group approval, twelve months' public notice. Editorial corrections (typo fixes, formatting, link updates) may be merged with a single WG second.
