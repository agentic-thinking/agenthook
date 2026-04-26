# Security policy

## Reporting a vulnerability

If you believe you have found a security vulnerability in the AgentHook specification, the conformance test rig, or any reference implementation operated by the steward, please report it privately.

| Channel | Address |
|---|---|
| Email | security@agenticthinking.uk |
| Backup | contact@agenticthinking.uk |
| PGP key | (forthcoming with the v1.0 release; until then please use a service such as ProtonMail for encrypted reports) |

Please do **not** open a public issue for security reports.

## Scope

This policy covers:

- Logical or cryptographic flaws in the envelope format defined in [`SPEC.md`](./SPEC.md) section 1
- Conformance test suite issues that allow a non-conforming implementation to claim conformance
- Vulnerabilities in `envelope.schema.json` validation behaviour

The policy does not cover the live `agenthook.org` website infrastructure, nor any third-party implementation that has not been certified through the conformance process.

## Disclosure

We aim to respond within 5 working days, agree a coordinated disclosure window, and credit the reporter publicly unless they prefer otherwise. Default coordinated disclosure window is 90 days from initial report; extensions are negotiated where a complex fix or coordinated upstream patch is required.

## Threat model (informative)

The specification assumes:

- Publishers and subscribers run within an operator-controlled trust boundary, OR connect over an authenticated, integrity-protected transport. Authentication and authorisation are recommended but currently out of scope of the normative specification (see [`SPEC.md`](./SPEC.md) section "It does not cover").
- The bus operator is trusted to enrich `agent_id` from a bearer token without forging publisher-side fields.
- Subscribers are not assumed to be mutually trusting.

A future Proposal will likely address transport security normatively. Please flag transport-layer concerns now — they shape AHP-002 and beyond.
