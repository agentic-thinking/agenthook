# Changelog

All notable changes to the AgentHook specification are recorded in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Per [`GOVERNANCE.md`](./GOVERNANCE.md), breaking changes to the specification require a deprecation window of no less than nine months.

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
