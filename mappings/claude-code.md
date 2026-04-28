# Claude Code mapping

Status: AgentHook-compatible through publisher shim.

| Claude Code hook / evidence | AgentHook event | Notes |
|---|---|---|
| `UserPromptSubmit` | `UserPromptSubmit` | Captures submitted prompt. |
| `PreToolUse` | `PreToolUse` | Sync, enforcement-capable. |
| `PostToolUse` | `PostToolUse` | Captures tool result where exposed. |
| `Stop.last_assistant_message` | `ModelResponse.metadata.response_text` | Captures final assistant response. |
| `Stop.transcript_path` | `ModelResponse.metadata.transcript_path` | Transcript reference, if exposed. |
| transcript `thinking` blocks | `ModelResponse.metadata.reasoning_content` | Best-effort only. Claude Code may expose signed/redacted/empty thinking. |

Canonical unavailability fields must still be emitted:

```json
{
  "reasoning_available": false,
  "reasoning_unavailable_reason": "not_exposed_by_runtime",
  "reasoning_redacted": false,
  "reasoning_signature_present": false
}
```
