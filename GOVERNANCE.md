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
3. **No participation gating.** Any individual or organisation may submit Proposals (see below) and contribute to working-group discussion. Vote-eligible Working Group seats are limited to Inaugural and Elected Working Group Members; this does not restrict contribution.
4. **Patent grant.** The steward grants, on behalf of itself, an irrevocable royalty-free patent license to any party implementing the specification, covering any claims the steward owns that would otherwise be infringed by a conforming implementation. This grant survives any change of stewardship.
5. **Right to fork.** The specification may be forked at any time by any party under the terms of the Apache License 2.0. The steward may not assert trademark rights against forks, provided the forks do not represent themselves as the official AgentHook specification or as conforming when they are not.
6. **Twelve-month notice on any change to these commitments.** Any proposed amendment to the Charter or to these commitments requires twelve months' public notice and the unanimous approval of the Working Group.

## Working Group

The Working Group ("WG") authors and maintains the specification.

### Composition

The Working Group has the following tiers:

- **Inaugural Working Group Members** - invited at v1.0 launch on the basis
  of having implemented hooks, subscribers, collectors, or other materially
  relevant infrastructure for the specification before public draft.
  Inaugural status is a launch-cohort designation. Inaugural Members hold
  full voting rights equivalent to Elected Working Group Members.

- **Elected Working Group Members** - admitted by majority vote of existing
  Working Group Members. Candidates must normally have served as Maintainer
  for no less than twelve months and their organisation must have shipped at
  least one AgentHook-conformant implementation at Silver or Gold tier.
  Elected Working Group Members hold full voting rights equivalent to
  Inaugural Working Group Members.

- **Maintainers** - appointed by majority Working Group Member vote on
  nomination by an existing Maintainer or Working Group Member. Maintainers
  have PR review rights over their recorded area of ownership, may merge
  routine updates within that area with one Working Group Member or Maintainer
  second, may author AHPs, and attend Working Group meetings as participants.
  Maintainers do not vote on substantive changes, breaking changes, Charter
  amendments, Working Group membership, or stewardship-transfer decisions.
  Maintainer status is reviewed annually and lapses after twelve months of
  inactivity.

- **Implementer Track Participants** - organisations that have shipped or
  are actively shipping an AgentHook-conformant publisher, subscriber, or
  collector. Self-nomination is by PR or membership issue, ratified by one
  Working Group Member second. Implementer Track Participants attend Working
  Group meetings as observers, may comment on AHPs, and may author AHPs as
  submitters. They do not vote. Implementer Track participation is the
  standard path to Maintainer and subsequently Elected Working Group Member
  status. Participation lapses after twelve months of inactivity in the
  implementation work that qualified the organisation.

- **Stewardship Seat** - Agentic Thinking Limited holds one non-voting chair
  seat for procedural facilitation. The chair has no casting vote on
  substantive matters.

The current roster for each tier is tracked in [`MEMBERS.md`](./MEMBERS.md).

### Inactivity

A voting Working Group Member who has no recorded participation for twelve
months may be moved to inactive status by majority vote of the other active
Working Group Members. Recorded participation includes PR review, AHP
authorship or review, conformance work, implementation updates, issue triage,
meeting attendance, or other Working Group activity recorded in public minutes
or repository history.

Inactive members remain listed for historical traceability, but do not count
toward quorum or votes. They may be reinstated by majority vote of active
Working Group Members.

### Meeting cadence

- One scheduled video meeting per month, public agenda, public minutes.
- Asynchronous discussion in the repository's GitHub Discussions and Issues.
- Time commitment expectation for active members: approximately one to two hours per month plus PR review.

### Decisions

- **Routine updates** (clarifications, examples, typo fixes): merge by any
  Working Group Member, or by a Maintainer within their recorded area of
  ownership, approved by one Working Group Member or Maintainer second.
- **Substantive changes** (event types, required metadata, conformance
  levels): require a numbered Proposal (see below) and approval by majority
  active Working Group Member vote. Maintainers and Implementer Track
  Participants may author or comment on AHPs, but do not vote on them.
- **Breaking changes** (changes to envelope shape, removal of any required
  field, conformance-level redefinitions): require unanimous active Working
  Group Member approval and a deprecation window of no less than nine months.
- **Maintainer appointments**: require majority active Working Group Member
  vote once the Working Group is seated.
- **Implementer Track ratifications**: require one Working Group Member second
  once the Working Group is seated.
- **Charter amendments**: require unanimous active Working Group Member
  approval and twelve months' public notice (binding under commitment 6).

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

Until the first Working Group is seated and the Charter is countersigned by
the Inaugural Working Group Members, Agentic Thinking Limited may make
pre-ratification governance clarifications, provided they do not weaken the
binding commitments in the Charter.

During the same pre-ratification period, Agentic Thinking Limited may accept
Implementer Track entries provisionally. Provisional entries should be reviewed
at the first seated Working Group meeting.

After ratification, substantive changes to GOVERNANCE.md follow the Charter
amendment process: unanimous active Working Group Member approval and twelve
months' public notice. Editorial corrections (typo fixes, formatting, link
updates) may be merged with a single Working Group Member second.
