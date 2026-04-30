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

The following must be resolved in `SPEC.md` before all scenarios can be encoded as machine-checkable manifests:

1. **Pre/Post pairing under failure.** When a `Pre*` event fires and the operation never completes (timeout, crash, abort), the publisher should have one mandated failure path. Either require a matching `Post*` carrying a standard error indicator, or require `ErrorOccurred`, but do not leave both paths equally valid for conformance.
2. **Canonical payload keys per event type.** Several scenarios need to assert on prompt or response preservation. `SPEC.md` does not currently define a canonical prompt field for `UserPromptSubmit`, and the current Python helper places prompts in `tool_input.prompt`. Without a canonical key, scenarios 3, 4, 5, and 15 can only assert envelope validity, not payload preservation.
3. **Implemented spec version declaration.** The envelope `schema_version` is a wire-format version, not a declaration of the AgentHook spec revision or conformance rule set implemented by the publisher. The harness needs a declared target to select the right rules.
4. **Determinism contract.** Scenarios 2, 6, and 9 assume the publisher will produce specific tool calls. LLM outputs are not deterministic. The harness must either mock the LLM, fix a seed, script the tool sequencer, or assert only on event shape. Pick one.
5. **Duplicate `event_id` semantics.** `SPEC.md` requires `event_id` to be a unique identifier and requires duplicate redelivery to be idempotent, but it does not distinguish redelivery of the same event from two distinct events that incorrectly share an `event_id`. Scenario 21 needs that distinction before it can require a rejection or violation.

## Harness architecture (planned)

The harness has two components, not one:

- **Subscriber-shim**: HTTP collector that receives events from the publisher under test, validates against `envelope.schema.json`, and returns realistic verdicts so sync hooks behave normally.
- **Agent-driver**: scripted prompt + simulated tool-use sequencer that stimulates the publisher to produce events. LLM determinism is deferred per gap 4 above.

These talk over a documented interface. The interface is itself a spec artefact and is out of scope for this draft.

## Scenarios

| # | Scenario name | Publisher behaviour | Expected event sequence | Bronze assertions |
|---|---|---|---|---|
| 1 | Minimal CLI hello | "hello", single LLM call, no tools | SessionStart, UserPromptSubmit, PreLLMCall, PostLLMCall, ModelResponse, SessionEnd | All emitted events validate against `envelope.schema.json`; required SPEC fields present; `event_id` valid UUID; PreLLMCall count == PostLLMCall count == 1 |
| 2 | Single tool call success | "weather in Paris", agent calls weather tool | + PreToolUse, PostToolUse | PreToolUse count == PostToolUse count == 1; `session_id` consistent across paired tool events when emitted; no ErrorOccurred |
| 3 | Empty user prompt | Agent receives `""` | Branched: LLM path or ErrorOccurred | If ErrorOccurred path, all emitted events validate; if LLM path, PreLLMCall count == PostLLMCall count; prompt preservation pending gap 2 |
| 4 | 100KB prompt | Agent receives 100 KB ASCII payload | Normal LLM sequence | All emitted events validate; JSON parses without error; payload preservation pending gap 2 |
| 5 | Unicode and control characters | Prompt contains `日本語 🚀 \u0000 \n \t \\ \"` | Normal LLM sequence | All emitted events validate; JSON parses without error; payload preservation pending gap 2 |
| 6 | Tool call failure | Calculator tool throws an exception | + PostToolUse and/or ErrorOccurred | PreToolUse count == PostToolUse count if tool completion is emitted; ErrorOccurred, if emitted, shares the same `session_id` where available; exact failure path pending gap 1 |
| 7 | LLM timeout | LLM call exceeds timeout | SessionStart, UserPromptSubmit, PreLLMCall, ErrorOccurred OR PostLLMCall with standard error indicator, SessionEnd | Whichever path the spec mandates per gap 1; `session_id` consistent where emitted |
| 8 | Malformed input to agent | Agent receives raw `{invalid` | Branched: ErrorOccurred or LLM path | Either path, all emitted events validate and `session_id` is consistent where emitted |
| 9 | Three sequential tool calls | Trip planner: weather, flights, hotels | 3x PreToolUse/PostToolUse | PreToolUse count == PostToolUse count == 3; each PostToolUse follows its paired PreToolUse in publication order; no orphan PreToolUse |
| 10 | No tool use path | Factual question, no tool call | LLM-only sequence | PreToolUse count == 0; PostToolUse count == 0; no ErrorOccurred |
| 11 | AgentHandoff present | Primary agent delegates to specialist | + AgentHandoff between LLM rounds | AgentHandoff count == 1; AgentHandoff appears between first PostLLMCall and second PreLLMCall in publication order; `session_id` consistent where emitted |
| 12 | AgentHandoff legitimately absent | Single-agent runtime, no delegation capability | LLM-only sequence | AgentHandoff count == 0; absence does not fail per 80% threshold |
| 13 | Tool succeeds, parse fails | Tool returns 200 OK, response parse throws | PreToolUse, PostToolUse, ErrorOccurred | ErrorOccurred appears after PostToolUse in publication order; PreToolUse count == PostToolUse count == 1 |
| 14 | System-initiated session | Scheduled job starts, no external user prompt | SessionStart, PreLLMCall, PostLLMCall, ModelResponse, SessionEnd | UserPromptSubmit count == 0; absence does not fail per 80% threshold; PreLLMCall count == PostLLMCall count == 1 |
| 15 | CRLF and control bytes in prompt | Prompt contains `line1\r\nline2\x01\x02` | Normal LLM sequence | All emitted events validate; JSON parses without error; payload preservation pending gap 2 |
| 16 | Two rapid sessions | Two independent sessions in sequence | A: full sequence. B: full sequence | A.session_id != B.session_id when sessions expose identifiers; no cross-session Pre/Post pairing; newly emitted event IDs are not reused |
| 17 | Empty tool result | Tool returns `""` | Normal sequence with PreToolUse/PostToolUse | PostToolUse present; PreToolUse count == PostToolUse count; no ErrorOccurred |
| 18 | Empty LLM response | Model generates zero tokens | Normal LLM sequence | PostLLMCall present and valid; PreLLMCall count == PostLLMCall count == 1; no ErrorOccurred |
| 19 | Metadata absent or empty | Publisher omits `metadata` or sets `metadata: {}` | Normal sequence | Both absent metadata and empty-object metadata are acceptable under the envelope; other required fields valid |
| 20 | Catastrophic init failure | Error before any processing | SessionStart, ErrorOccurred, SessionEnd | ErrorOccurred count == 1; SessionEnd appears after ErrorOccurred in publication order; PreLLMCall count == 0; PreToolUse count == 0 |
| 21 | Duplicate `event_id` distinction | Harness observes duplicate delivery or two distinct events with the same `event_id` | Harness classifies duplicate | Redelivery of the same event is idempotent; reuse of one `event_id` for distinct events is flagged only after gap 5 is resolved |

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
