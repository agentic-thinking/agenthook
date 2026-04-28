# Contributing to AgentHook

Thank you for considering a contribution. AgentHook is an open specification stewarded by Agentic Thinking Limited (UK) under the terms set out in [`CHARTER.md`](./CHARTER.md) and [`GOVERNANCE.md`](./GOVERNANCE.md).

## What contributions look like

| Kind | Where it goes |
|---|---|
| Typo, formatting, link fix, clarification | Pull request directly against `main`. One Working Group member seconds, then merged. |
| Substantive specification change (event types, required fields, conformance levels, schema version) | Numbered AgentHook Proposal in [`PROPOSALS/`](./PROPOSALS/). See [`PROPOSALS/TEMPLATE.md`](./PROPOSALS/TEMPLATE.md). |
| Conformance test contributions | Pull request to the conformance harness, once it is published. See [`CONFORMANCE/`](./CONFORMANCE/). |
| Implementation, integration notes, edge cases | Open an issue. We will route the discussion or convert it into a Proposal if material. |
| Code of Conduct concerns | Email contact@agenticthinking.uk. The steward is the initial enforcement point per GOVERNANCE.md. |

## Proposal flow

1. Read [`SPEC.md`](./SPEC.md) and [`GOVERNANCE.md`](./GOVERNANCE.md) sections 1-3.
2. Open a draft Proposal as `PROPOSALS/AHP-NNN-short-title.md` using [`PROPOSALS/TEMPLATE.md`](./PROPOSALS/TEMPLATE.md). Number is assigned by the editor when the Proposal moves out of Draft.
3. Open a pull request against `main`. The Working Group reviews on the PR and at the next monthly meeting.
4. Status changes (Draft → Accepted | Rejected | Withdrawn | Superseded) follow the rules in [`GOVERNANCE.md`](./GOVERNANCE.md).

## Sign-off (required)

Every commit must be signed off using the [Developer Certificate of Origin](https://developercertificate.org/). This is a lightweight assertion that you have the right to submit the contribution under the project licence. Sign-off is added with:

```
git commit -s -m "your commit message"
```

Pull requests with unsigned commits will not be merged. The pull request template includes a DCO checkbox.

## Protected main branch

The `main` branch is protected. Changes to AgentHook must land through a pull request, not by direct push.

Required process:

1. Create a branch from the latest `main`.
2. Commit with DCO sign-off using `git commit -s`.
3. Open a pull request against `main`.
4. Wait for the DCO check to pass.
5. Merge through GitHub after the required review/approval path for the change type.

Direct pushes to `main`, force-pushes to `main`, and unsigned commits are not acceptable for this repository. If a direct push happens by mistake, correct it by opening a signed revert pull request and re-landing the change through a signed pull request.

## Licensing of contributions

By submitting a contribution you agree that your contribution is licensed under the same Apache License 2.0 that covers the specification (see [`LICENSE`](./LICENSE)). Per [`CHARTER.md`](./CHARTER.md), the licence may not be changed by the steward or any successor.

## Code of Conduct

Participation is governed by the [Contributor Covenant Code of Conduct](./CODE_OF_CONDUCT.md), version 2.1.

## Questions

Open an issue, or contact contact@agenticthinking.uk.
