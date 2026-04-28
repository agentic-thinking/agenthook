from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from .envelope import build_event, evidence_defaults, model_response, pre_tool_use, user_prompt_submit
from .transport import emit_http
from .validate import validate_event


def _load_json_arg(value: str) -> dict:
    if not value:
        return {}
    if value.startswith("@"):
        return json.loads(Path(value[1:]).read_text(encoding="utf-8"))
    return json.loads(value)


def _print(obj) -> None:
    print(json.dumps(obj, indent=2, sort_keys=False))


def cmd_validate(args) -> int:
    event = json.loads(Path(args.file).read_text(encoding="utf-8")) if args.file != "-" else json.load(sys.stdin)
    errors = validate_event(event, args.schema)
    if errors:
        for err in errors:
            print(f"error: {err}", file=sys.stderr)
        return 1
    print("valid")
    return 0


def cmd_emit(args) -> int:
    if args.event == "PreToolUse":
        event = pre_tool_use(args.source, args.session, args.tool or "", _load_json_arg(args.input))
    elif args.event == "UserPromptSubmit":
        event = user_prompt_submit(args.source, args.session, args.prompt or "")
    elif args.event == "ModelResponse":
        event = model_response(
            args.source,
            args.session,
            response_text=args.response,
            reasoning_content=args.reasoning,
            provider=args.provider,
            model=args.model,
            transcript_path=args.transcript,
        )
    else:
        event = build_event(
            args.event,
            args.source,
            args.session,
            tool_name=args.tool or "",
            tool_input=_load_json_arg(args.input),
            metadata=evidence_defaults(),
        )
    errors = validate_event(event, args.schema)
    if errors:
        for err in errors:
            print(f"error: {err}", file=sys.stderr)
        return 1
    if not args.target:
        _print(event)
        return 0
    result = emit_http(event, args.target, args.token or os.environ.get("AGENTHOOK_TOKEN", ""))
    _print(result)
    return 0


def _merge_claude_settings(settings_path: Path, command: str) -> None:
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    if settings_path.exists():
        backup = settings_path.with_name(settings_path.name + ".bak.agenthook")
        shutil.copy2(settings_path, backup)
        data = json.loads(settings_path.read_text(encoding="utf-8") or "{}")
    else:
        data = {}
    hooks = data.setdefault("hooks", {})
    for event in ("UserPromptSubmit", "PreToolUse", "PostToolUse", "Stop"):
        matcher = "" if event in {"UserPromptSubmit", "Stop"} else ".*"
        existing = hooks.get(event) if isinstance(hooks.get(event), list) else []
        kept = []
        for entry in existing:
            commands = entry.get("hooks") if isinstance(entry, dict) else None
            if not isinstance(commands, list):
                kept.append(entry)
                continue
            filtered = [
                item
                for item in commands
                if not (
                    isinstance(item, dict)
                    and item.get("type") == "command"
                    and ("claude-code-gate" in str(item.get("command", "")) or "agenthook" in str(item.get("command", "")))
                )
            ]
            if filtered:
                clone = dict(entry)
                clone["hooks"] = filtered
                kept.append(clone)
        kept.append({"matcher": matcher, "hooks": [{"type": "command", "command": command}]})
        hooks[event] = kept
    settings_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    settings_path.chmod(0o600)


def cmd_init(args) -> int:
    if args.runtime != "claude-code":
        print(f"runtime not implemented yet: {args.runtime}", file=sys.stderr)
        return 2
    gate = shutil.which("claude-code-gate") or str(Path.home() / ".local/bin/claude-code-gate")
    if not Path(gate).exists() and not args.dry_run:
        print("claude-code-gate not found. Install hookbus-publisher-claude-code first.", file=sys.stderr)
        return 1
    token = args.token or os.environ.get("HOOKBUS_TOKEN") or os.environ.get("AGENTHOOK_TOKEN") or ""
    command = f"env HOOKBUS_URL={args.target} HOOKBUS_TOKEN={token} HOOKBUS_SOURCE=claude-code {gate}"
    settings = Path(args.settings).expanduser()
    if args.dry_run:
        print(command)
        return 0
    _merge_claude_settings(settings, command)
    print(f"updated {settings}")
    print("restart Claude Code so settings are reloaded")
    return 0


def cmd_doctor(args) -> int:
    event = pre_tool_use("agenthook-doctor", "doctor", "Bash", {"command": "pwd"})
    errors = validate_event(event, args.schema)
    if errors:
        print("schema: fail")
        for err in errors:
            print(f"  {err}")
        return 1
    print("schema: pass")
    if args.target:
        result = emit_http(event, args.target, args.token or os.environ.get("AGENTHOOK_TOKEN", ""))
        print(f"target: pass ({result.get('decision', 'unknown')})")
    return 0


def cmd_test(args) -> int:
    events = [
        user_prompt_submit(args.source, "conformance", "hello"),
        pre_tool_use(args.source, "conformance", "Bash", {"command": "pwd"}),
        model_response(args.source, "conformance", response_text="hello", provider=args.provider),
    ]
    failed = 0
    for event in events:
        errors = validate_event(event, args.schema)
        if errors:
            failed += 1
            print(f"{event['event_type']}: fail")
            for err in errors:
                print(f"  {err}")
        else:
            print(f"{event['event_type']}: pass")
    print("Bronze:", "pass" if failed == 0 else "fail")
    print("Silver: partial (runtime evidence availability depends on adapter)")
    print("Gold: partial (reasoning may be unavailable or redacted)")
    return 1 if failed else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="agenthook")
    parser.add_argument("--schema", default=None)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("validate")
    p.add_argument("file")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("emit")
    p.add_argument("--event", default="PreToolUse")
    p.add_argument("--source", default="agenthook-cli")
    p.add_argument("--session", default="cli")
    p.add_argument("--tool", default="")
    p.add_argument("--input", default="{}")
    p.add_argument("--prompt", default="")
    p.add_argument("--response", default="")
    p.add_argument("--reasoning", default="")
    p.add_argument("--provider", default="")
    p.add_argument("--model", default="")
    p.add_argument("--transcript", default="")
    p.add_argument("--target", default="")
    p.add_argument("--token", default="")
    p.set_defaults(func=cmd_emit)

    p = sub.add_parser("init")
    p.add_argument("runtime", choices=["claude-code"])
    p.add_argument("--target", default="http://localhost:18800/event")
    p.add_argument("--token", default="")
    p.add_argument("--settings", default="~/.claude/settings.json")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("doctor")
    p.add_argument("--target", default="")
    p.add_argument("--token", default="")
    p.set_defaults(func=cmd_doctor)

    p = sub.add_parser("test")
    p.add_argument("kind", choices=["publisher"])
    p.add_argument("--source", default="agenthook-cli")
    p.add_argument("--provider", default="")
    p.set_defaults(func=cmd_test)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
