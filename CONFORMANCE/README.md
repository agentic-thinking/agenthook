# Conformance

The conformance test suite verifies that a publisher implementation emits events that match the AgentHook specification at one of three tiers (Bronze, Silver, Gold; see [`SPEC.md`](../SPEC.md) section 5).

The formal Bronze/Silver/Gold conformance suite is **not yet implemented**. It will ship alongside specification v1.0.

The Python implementation kit already includes smoke-test commands for early adopters:

- `agenthook test publisher` checks locally generated sample events against the draft envelope schema.
- `agenthook test collector --target <url>` posts representative lifecycle events to a collector or bus and verifies that the response has the expected decision shape.

These smoke tests are useful for development, but they are not a formal conformance score and carry no certification value.

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

Once the rig ships, conformant implementations and their tier are listed in `REGISTRY.md` (planned), updated automatically on each successful test run. Procurement teams can reference the registry directly when evaluating runtime evidence support in agent runtimes. The registry is an interoperability aid, not a legal compliance certification.

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

The conformance harness ships alongside specification v1.0. Specific dates will be set when the Working Group is confirmed and the editor team has scoped the work. We do not publish target dates without commits behind them.
