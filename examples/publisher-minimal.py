from agenthook import pre_tool_use
from agenthook.transport import emit_http

event = pre_tool_use(
    source="example-runtime",
    session_id="demo",
    tool_name="Bash",
    tool_input={"command": "pwd"},
)

print(emit_http(event, "http://localhost:18800/event", token="replace-me"))
