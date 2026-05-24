# AHP-012: Web Evidence and Browser Provenance

| Field | Value |
|---|---|
| Identifier | AHP-012 |
| Title | Web Evidence and Browser Provenance |
| Author | Agentic Thinking editor team |
| Status | Draft |
| Created | 2026-05-24 |
| Updated | 2026-05-24 |
| Supersedes |  |
| Superseded by |  |

## Motivation

Agent runtimes and extensions increasingly expose web search, URL fetch, browser navigation, page extraction, and citation tools. A bare `PreToolUse` event that says `tool_name: WebSearch` is not enough to reconstruct what the agent saw, which result it selected, which page was read, or which evidence influenced an answer or downstream action.

This matters for enterprise audit, incident review, and regulated deployments. For example, EU AI Act style record keeping and human oversight workflows may require more than proof that a web tool was called. Operators need comparable evidence for the query, returned results, selected source, fetched page, extracted content reference, and evidence used in model output.

The capability may be native to a runtime or added by an extension. The standard therefore needs a common web evidence vocabulary independent of whether the base runtime ships a web search tool.

## Current behaviour

SPEC.md section 2 defines the v0.2 core lifecycle event types. SPEC.md section 1 allows publishers to emit additional PascalCase event types, and AHP-011 adds normalized action/resource fields such as `action: search` and `resource_kind: url`.

This is sufficient to record that a search, fetch, or open operation happened. It is not sufficient to standardise result sets, selected results, page evidence, action IDs, content hashes, or the relationship between model output and web evidence.

## Proposed change

Add an AgentHook Web Evidence extension to the specification. The extension defines canonical event names and canonical `metadata.web` fields for publishers, browser runtimes, and extensions that emit web/search/browser activity.

A publisher is not required to implement a web/search/browser tool. However, if a publisher or extension emits web/search/browser activity and claims AgentHook Web Evidence conformance, it MUST use these event types and metadata shapes where the host runtime exposes the data.

Canonical Web Evidence event types:

| Event type | Phase | Description |
|---|---|---|
| `WebSearchRequested` | before | A publisher or extension is about to perform a web search query |
| `WebSearchResultsReturned` | after | A search provider returned a result set for a query |
| `WebResultSelected` | before | A result from a result set was selected for opening, fetching, browsing, or citation |
| `WebPageRead` | after | A URL was fetched or rendered and page evidence was extracted |
| `WebActionRequested` | before | A browser/page action such as click, fill, submit, download, or screenshot is about to run |
| `WebActionCompleted` | after | A browser/page action completed and resulting page/action evidence is available |
| `EvidenceUsedInOutput` | after | A model response or agent output declared which web evidence items influenced the output |

Canonical `metadata.web` fields:

| Field | Type | Purpose |
|---|---|---|
| `query` | string | Search query or equivalent retrieval request |
| `provider` | string | Search, fetch, or browser provider, for example `brave`, `tavily`, `firecrawl`, `playwright`, or `runtime_native` |
| `search_id` | string | Stable identifier linking a search request to its result set and selected result |
| `result_set_id` | string | Stable identifier for one provider result set |
| `results` | array | Ordered result objects with `result_id`, `rank`, `url`, `title`, `snippet`, and optional provider metadata |
| `selected_result_id` | string | Identifier of the selected result from `results` |
| `selected_rank` | integer | Rank of the selected result in the result set |
| `url` | string | Requested URL before redirects |
| `final_url` | string | Final URL after redirects or browser navigation |
| `page_title` | string | Page title extracted from the fetched/rendered page |
| `content_ref` | string | Reference to content stored outside the envelope |
| `content_hash` | string | Digest of extracted content or page model, preferably `sha256:<hex>` |
| `content_summary` | string | Optional short summary when full content is not embedded |
| `evidence_id` | string | Stable identifier for a page, content chunk, screenshot, or extracted evidence record |
| `evidence_ids` | array | Evidence identifiers used by a later output or action |
| `parent_event_id` | string | Previous event in the web evidence chain |
| `action_id` | string | Stable page/browser action identifier such as a link/button action ID |
| `action` | string | Browser/page action such as `click`, `fill`, `submit`, `download`, `screenshot`, or `read` |
| `actions` | array | Available page actions after a read or completed browser action |
| `screenshot_ref` | string | Reference to a screenshot artefact stored outside the envelope |
| `screenshot_hash` | string | Digest of the screenshot artefact |

Recommended normalized fields:

- `WebSearchRequested`: `action: search`, `resource_kind: url`, `resource_scope: public_web` unless the target is known to be internal.
- `WebResultSelected`: `action: open`, `resource_kind: url`, `resource` set to the selected URL.
- `WebPageRead`: `action: read`, `resource_kind: url`, `resource` set to the final URL.
- `WebActionRequested`: `action` set to `open`, `write`, `send`, or `execute` where more specific than browser `click`; otherwise use `open` and place browser-specific action in `metadata.web.action`.
- `EvidenceUsedInOutput`: `action: publish` or `read` depending on whether the evidence is being cited in an output or merely recorded.

The envelope schema should list these names as recognised event types while retaining the existing PascalCase extension rule.

## Backwards-compatibility impact

- Wire format change: no. This uses existing `event_type`, `metadata`, and normalized action/resource fields.
- `schema_version` bump: no. Existing consumers already permit additional PascalCase event types.
- Existing publishers: unaffected unless they claim Web Evidence conformance.
- Existing subscribers: can ignore unknown event types. Subscribers that care about web provenance can begin consuming `metadata.web` without parsing runtime-specific tool payloads.

## Deprecation plan

No existing event type or field is removed or renamed.

Publishers that currently emit ad hoc `PreToolUse`/`PostToolUse` web records MAY continue to do so, but SHOULD add the Web Evidence events when the runtime exposes search results, selected result, page evidence, or evidence-use data.

## Reference implementation

The HookBus agnostic publisher already contains a browser runtime that emits pre/post browser action events and page evidence. This Proposal standardises that pattern for AgentHook and extends it to search result provenance and evidence use.

A future reference implementation should add a `hookbus-webtools` or equivalent package with:

- `search(query)`
- `open_result(result_id)`
- `read_page(url)`
- `click_action(action_id)`
- `cite(evidence_id)`

Each step should emit the relevant Web Evidence event.

## Security considerations

Web evidence may contain personal data, confidential URLs, authentication state, query terms, page excerpts, screenshots, and content that could expose regulated or sensitive information. Publishers MUST NOT place secrets, bearer tokens, session cookies, or raw credentials in `metadata.web`.

Full page content SHOULD be stored by reference where possible. The envelope SHOULD carry `content_ref`, `content_hash`, summaries, and evidence IDs rather than unbounded page text. Operators SHOULD apply retention, redaction, tenant separation, and access-control policies to external evidence stores.

Search result snippets and page titles may still contain personal or sensitive data. Subscribers and storage backends SHOULD treat Web Evidence events as auditable records subject to the same controls as prompts, model responses, and tool outputs.

`WebResultSelected` and `WebActionRequested` are admission-capable events. Publishers that claim admission-bound Web Evidence conformance MUST emit them before navigation or action execution and respect the configured allow/deny/ask/fail-mode semantics.

## Alternatives considered

1. Use only `PreToolUse` and `PostToolUse` with runtime-specific `tool_name` values. Rejected because it leaves every subscriber to reverse-engineer result sets, selected links, page evidence, and citation mapping from incompatible tool payloads.
2. Put all web evidence in `ModelResponse` metadata. Rejected because it loses pre-commit control points and cannot block unsafe navigation or form actions before they occur.
3. Require every AgentHook publisher to implement Web Evidence. Rejected because many runtimes do not expose web/search/browser capabilities. The standard should define the vocabulary, but conformance should be capability-based.

## Unresolved questions

- Whether `EvidenceUsedInOutput` should be required for all model responses that cite web evidence, or only for publishers that expose source-attribution hooks.
- Whether screenshots need a separate canonical artefact schema.
- Whether search result snippets should be hash-only by default in high-privacy profiles.
- How the conformance suite should test native web tools where provider APIs do not expose full result sets.

## Status history

| Date | Status | Note |
|---|---|---|
| 2026-05-24 | Draft | Initial submission |
