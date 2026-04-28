# agenthook Python Kit

Small implementation kit for the AgentHook draft standard.

```bash
pipx install .
agenthook emit --event PreToolUse --source demo --session demo --tool Bash --input '{"command":"pwd"}'
agenthook validate event.json
agenthook init claude-code --target http://localhost:18800/event --token "$HOOKBUS_TOKEN"
agenthook doctor --target http://localhost:18800/event --token "$HOOKBUS_TOKEN"
```

The package is intentionally boring: envelope builders, schema validation, a
CLI, and runtime adapter scaffolding.
