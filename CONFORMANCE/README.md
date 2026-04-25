# Conformance

The conformance test suite verifies that a publisher implementation emits events that match the AgentHook specification at one of three tiers (Bronze, Silver, Gold; see [`SPEC.md`](../SPEC.md) section 5).

The suite is **not yet implemented**. It will ship alongside specification v1.0.

## Planned shape

### Open-source self-test rig

A repository (planned: `github.com/agenticthinking/agenthook-conformance`, separate from the spec) contains:

- A test harness that the publisher under test connects to as a subscriber endpoint
- A scenario library: hundreds of scripted prompt + tool-use sequences that exercise each event type and metadata key
- A scoring engine that emits a per-tier pass/fail breakdown and a JSON report
- An optional signature appendix using the steward's public key for provenance

A publisher implementer runs the harness locally, points their hook surface at it, and gets a self-attested score. Free, Apache-licensed, no certification value.

### Hosted Conformance-as-a-Service

A managed instance, operated by the steward (or successor body), where:

- Publishers POST their hook implementation (or grant access to a test endpoint)
- The harness exercises it under controlled conditions
- A signed report is returned, suitable for publication and procurement use
- Re-tests run on every specification minor version bump

Cost-recovery fees are permitted for the hosted service (see [`GOVERNANCE.md`](../GOVERNANCE.md) section "Conformance"); they may not be used to gate participation in the Working Group or in the specification.

### Conformance registry

Once the rig ships, conformant implementations and their tier are listed in `REGISTRY.md` (planned), updated automatically on each successful test run. Procurement teams can reference the registry directly when evaluating agent runtimes for compliance with EU AI Act Article 12.

## Test categories (planned, illustrative)

### Bronze (lifecycle correctness)

- Envelope shape: required fields populated, types correct, JSON valid
- Event_id uniqueness across a session
- Timestamps monotonically non-decreasing within a session
- Each canonical event type emitted at the expected lifecycle moment
- Pre/Post pairing where applicable

### Silver (LLM transcript)

- Every `PreLLMCall` matched by exactly one `PostLLMCall` within the same session
- `model`, `provider`, `tokens_input`, `tokens_output`, `total_tokens`, `response_content` populated on every `PostLLMCall`
- Token counts internally consistent (input + output ≈ total)

### Gold (reasoning + correlation)

- `reasoning_content` populated when the provider exposes it (Anthropic thinking, OpenAI reasoning, MiniMax reasoning_details, etc.)
- `reasoning_chars` correctly reflects pre-truncation length
- `correlation_id` set on Pre\* events that initiate sub-agent calls or retries
- Cross-session correlation traceable via `correlation_id` chains

## Timeline

- v1.0 specification: target Q3 2026 (subject to Working Group decision)
- Self-test rig: ships with v1.0
- Hosted Conformance-as-a-Service: ships within 90 days of v1.0
- First public conformance reports: target Q4 2026

This timeline is provisional and will be updated as Working Group composition is confirmed.
