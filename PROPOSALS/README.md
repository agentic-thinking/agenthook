# AgentHook Proposals (AHPs)

Substantive changes to the AgentHook specification are made through numbered AgentHook Proposals, modelled after the Python PEP and Rust RFC processes.

## When a Proposal is required

A Proposal is required for:

- Adding, removing, or renaming a canonical event type
- Adding, removing, or renaming a required envelope field
- Changing the standard metadata keys for an event type
- Changing conformance level definitions or thresholds
- Changing the schema_version contract
- Any change with backward-compatibility impact

A Proposal is not required for:

- Typographical fixes, formatting, link updates, examples, illustrative wording
- Clarifications that do not change observable behaviour
- New examples or non-normative appendices

These can be merged via a regular pull request with one Working Group second.

## Process

1. **Draft.** Open a PR adding a file `PROPOSALS/AHP-NNN-short-title.md`. Use the template in `TEMPLATE.md` (forthcoming). Set `Status: Draft`.
2. **Discussion.** Working Group reviews on the PR and in the next monthly meeting. Discussion may run for one or more cycles.
3. **Status changes.** As discussion converges, the author updates the Proposal status:
   - `Draft` — under active discussion
   - `Accepted` — Working Group has approved per the rules in [`GOVERNANCE.md`](../GOVERNANCE.md) section "Decisions"
   - `Rejected` — Working Group has declined; reason recorded in the Proposal
   - `Withdrawn` — author has withdrawn; reason recorded
   - `Superseded` — replaced by a later Proposal; pointer added
4. **Merge.** Accepted Proposals are merged with the corresponding specification update in the same PR. The Proposal file remains in the repository as the historical record of the change rationale.

## Numbering

Proposals are numbered sequentially starting from `AHP-001`. Numbers are assigned by the editor at the point a Proposal moves out of Draft. Withdrawn or Rejected Proposals retain their numbers; numbers are never reused.

## Template (forthcoming)

A `TEMPLATE.md` file will be added covering:

- Header (number, title, author, status, dates)
- Motivation
- Current behaviour
- Proposed change
- Backwards-compatibility impact
- Deprecation plan if any
- Reference implementation or implementation sketch
- Alternatives considered
- Unresolved questions

Until the template is published, authors are asked to follow this structure.

## First Proposals

The Working Group expects the following Proposals in early development:

- `AHP-001` — finalise the schema_version 1 envelope shape (currently Draft via SPEC.md)
- `AHP-002` — define the v1.0 stable canonical event type set
- `AHP-003` — define the v1.0 conformance scoring methodology

These will be drafted by the editor team and circulated for Working Group review ahead of the first scheduled meeting.

## Active Drafts

- [`AHP-004` — Runtime Attestation](./AHP-004-runtime-attestation.md)
- [`AHP-005` — Governance Context Metadata](./AHP-005-governance-context-metadata.md)
- [`AHP-006` — Managed Runtime Identity and Device Registry](./AHP-006-managed-runtime-identity.md)
