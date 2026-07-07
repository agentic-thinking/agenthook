# Bronze Conformance Scenarios (DRAFT)

> **Status: pre-implementation draft.** This file describes the planned scenario library for the Bronze tier of the AgentHook conformance harness. The harness itself is not yet built. See [`README.md`](./README.md) for planned shape.

## Purpose

Bronze verifies envelope and lifecycle correctness only:

- Required SPEC envelope fields are present and well-typed (`event_id`, `event_type`, `timestamp`, `source`)
- Scenario-dependent optional fields are present when needed (`session_id`, `tool_name`, `tool_input`, `metadata`)
- `event_id` is a valid UUID and every newly emitted event has its own identifier
- `timestamp` is RFC 3339 / JSON Schema `date-time`
- Each canonical event type is emitted at the expected lifecycle moment where the runtime exposes that lifecycle
- Pre/Post pairing where the operation completes
- 80% pass threshold, so legitimately absent events (e.g. `AgentHandoff` in a single-agent runtime) do not fail Bronze

Token counts, `reasoning_content`, and `correlation_id` chains are Silver/Gold concerns and are out of scope here.

## Spec gaps blocking the harness

Five gaps were identified in earlier drafts of this file. Their resolution status:

1. **Pre/Post pairing under failure. Resolved.** `SPEC.md` section 4 ("Pairing under failure") now mandates one path: a matching `Post*` when the operation returned or threw at the boundary, `ErrorOccurred` (same `session_id` and `tool_call_id`) when it never completed, and never both for the same boundary. Failures after completion are additional `ErrorOccurred` events following the `Post*`.
2. **Canonical payload keys per event type. Resolved.** `SPEC.md` section 3 now defines `metadata.prompt` and `metadata.prompt_chars` for `UserPromptSubmit`, and canonical `ModelResponse` keys (`response_content`, `response_chars`, availability and unavailability fields). Scenarios 3, 4, 5, and 15 can assert payload preservation against `metadata.prompt`.
3. **Implemented spec version declaration. Resolved.** `SPEC.md` section 3 defines `metadata.spec_version` on `SessionStart` (or the first emitted event) as the publisher's declared specification revision, distinct from the wire-format `schema_version`. The harness selects its rule set from that declaration.
4. **Determinism contract. Resolved as a harness design decision.** The agent-driver scripts the tool sequencer; the LLM is not exercised as a nondeterministic component. Scenario assertions are on event shape, counts, pairing, and publication order, plus payload preservation where the driver controls the payload. No seed-fixing or live-model mocking is required for Bronze.
5. **Duplicate `event_id` semantics. Resolved.** `SPEC.md` section 4 ("Idempotency") now distinguishes redelivery (same `event_id`, materially identical payload; idempotent no-op or merge) from an identifier collision (same `event_id`, materially different payload; a publisher-side specification violation that subscribers flag and may reject). Scenario 21 asserts both behaviours.

## Harness architecture (planned)

The harness has two components, not one:

- **Subscriber-shim**: HTTP collector that receives events from the publisher under test, validates against `envelope.schema.json`, and returns realistic verdicts so sync hooks behave normally.
- **Agent-driver**: scripted prompt + simulated tool-use sequencer that stimulates the publisher to produce events. The driver controls tool sequencing deterministically per gap 4 above; no live model is exercised.

These talk over a documented interface. The interface is itself a spec artefact and is out of scope for this draft.

## Scenarios

| # | Scenario name | Publisher behaviour | Expected event sequence | Bronze assertions |
|---|---|---|---|---|
| 1 | Minimal CLI hello | "hello", single LLM call, no tools | SessionStart, UserPromptSubmit, PreLLMCall, PostLLMCall, ModelResponse, SessionEnd | All emitted events validate against `envelope.schema.json`; required SPEC fields present; `event_id` valid UUID; PreLLMCall count == PostLLMCall count == 1 |
| 2 | Single tool call success | "weather in Paris", agent calls weather tool | + PreToolUse, PostToolUse | PreToolUse count == PostToolUse count == 1; `session_id` consistent across paired tool events when emitted; no ErrorOccurred |
| 3 | Empty user prompt | Agent receives `""` | Branched: LLM path or ErrorOccurred | If ErrorOccurred path, all emitted events validate; if LLM path, PreLLMCall count == PostLLMCall count; prompt preserved in `metadata.prompt` |
| 4 | 100KB prompt | Agent receives 100 KB ASCII payload | Normal LLM sequence | All emitted events validate; JSON parses without error; payload preserved in `metadata.prompt` |
| 5 | Unicode and control characters | Prompt contains `日本語 🚀 \u0000 \n \t \\ \"` | Normal LLM sequence | All emitted events validate; JSON parses without error; payload preserved in `metadata.prompt` |
| 6 | Tool call failure | Calculator tool throws an exception | + PostToolUse and/or ErrorOccurred | PreToolUse count == PostToolUse count if tool completion is emitted; ErrorOccurred, if emitted, shares the same `session_id` where available; failure path per SPEC section 4 pairing-under-failure rule: Post* if the tool threw at the boundary, else ErrorOccurred, never both |
| 7 | LLM timeout | LLM call exceeds timeout | SessionStart, UserPromptSubmit, PreLLMCall, ErrorOccurred OR PostLLMCall with standard error indicator, SessionEnd | ErrorOccurred with matching `session_id` when the call never completed, per SPEC section 4 pairing-under-failure rule; `session_id` consistent where emitted |
| 8 | Malformed input to agent | Agent receives raw `{invalid` | Branched: ErrorOccurred or LLM path | Either path, all emitted events validate and `session_id` is consistent where emitted |
| 9 | Three sequential tool calls | Trip planner: weather, flights, hotels | 3x PreToolUse/PostToolUse | PreToolUse count == PostToolUse count == 3; each PostToolUse follows its paired PreToolUse in publication order; no orphan PreToolUse |
| 10 | No tool use path | Factual question, no tool call | LLM-only sequence | PreToolUse count == 0; PostToolUse count == 0; no ErrorOccurred |
| 11 | AgentHandoff present | Primary agent delegates to specialist | + AgentHandoff between LLM rounds | AgentHandoff count == 1; AgentHandoff appears between first PostLLMCall and second PreLLMCall in publication order; `session_id` consistent where emitted |
| 12 | AgentHandoff legitimately absent | Single-agent runtime, no delegation capability | LLM-only sequence | AgentHandoff count == 0; absence does not fail per 80% threshold |
| 13 | Tool succeeds, parse fails | Tool returns 200 OK, response parse throws | PreToolUse, PostToolUse, ErrorOccurred | ErrorOccurred appears after PostToolUse in publication order; PreToolUse count == PostToolUse count == 1 |
| 14 | System-initiated session | Scheduled job starts, no external user prompt | SessionStart, PreLLMCall, PostLLMCall, ModelResponse, SessionEnd | UserPromptSubmit count == 0; absence does not fail per 80% threshold; PreLLMCall count == PostLLMCall count == 1 |
| 15 | CRLF and control bytes in prompt | Prompt contains `line1\r\nline2\x01\x02` | Normal LLM sequence | All emitted events validate; JSON parses without error; payload preserved in `metadata.prompt` |
| 16 | Two rapid sessions | Two independent sessions in sequence | A: full sequence. B: full sequence | A.session_id != B.session_id when sessions expose identifiers; no cross-session Pre/Post pairing; newly emitted event IDs are not reused |
| 17 | Empty tool result | Tool returns `""` | Normal sequence with PreToolUse/PostToolUse | PostToolUse present; PreToolUse count == PostToolUse count; no ErrorOccurred |
| 18 | Empty LLM response | Model generates zero tokens | Normal LLM sequence | PostLLMCall present and valid; PreLLMCall count == PostLLMCall count == 1; no ErrorOccurred |
| 19 | Metadata absent or empty | Publisher omits `metadata` or sets `metadata: {}` | Normal sequence | Both absent metadata and empty-object metadata are acceptable under the envelope; other required fields valid |
| 20 | Catastrophic init failure | Error before any processing | SessionStart, ErrorOccurred, SessionEnd | ErrorOccurred count == 1; SessionEnd appears after ErrorOccurred in publication order; PreLLMCall count == 0; PreToolUse count == 0 |
| 21 | Duplicate `event_id` distinction | Harness observes duplicate delivery or two distinct events with the same `event_id` | Harness classifies duplicate | Redelivery of the same event is idempotent; reuse of one `event_id` for materially different events is a publisher violation per SPEC section 4 and is flagged |

## Coverage breakdown

- Happy paths: 1, 2, 9, 10, 17, 18 (6)
- Error paths: 6, 7, 8, 13, 20 (5)
- Content edges: 3, 4, 5, 15, 19 (5)
- Legitimate absence: 12, 14 (2)
- Multi-session / multi-call: 11, 16 (2)
- Negative/idempotency test: 21 (1)

Twenty-one scenarios. Bronze MVP target.

## Out of scope for this file

- Silver and Gold scenario libraries (token counts, reasoning capture, correlation chains)
- Scoring engine implementation
- Hosted Conformance-as-a-Service
- Conformance registry
- Report signing format

These ship after Bronze MVP is running end-to-end against at least one publisher.
