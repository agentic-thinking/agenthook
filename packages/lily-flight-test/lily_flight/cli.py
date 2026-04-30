"""CLI for the Lily AgentHook flight test."""

from __future__ import annotations

import argparse
import json
import sys

from .reasoning_smoke import run_reasoning_smoke
from .preflight import run_preflight


def _print_result(result: dict) -> None:
    print(f"session: {result['session_id']}")
    if "events" in result:
        print("hooks:")
        for event_type in result["events"]:
            print(f"  {event_type}")
    else:
        print(
            json.dumps(
                {
                    "reasoning_available": result.get("reasoning_available"),
                    "reasoning_chars": result.get("reasoning_chars"),
                    "response_content": result.get("response_content"),
                },
                indent=2,
            )
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Minimal AgentHook flight-test fixture.")
    parser.add_argument("command", nargs="?", default="preflight", choices=["preflight", "reasoning-smoke"])
    parser.add_argument("prompt", nargs="*", help="Prompt for reasoning-smoke")
    parser.add_argument("--preflight", action="store_true", help="Emit all 10 AgentHook hooks")
    args = parser.parse_args(argv)

    try:
        if args.preflight:
            if args.command != "preflight" or args.prompt:
                parser.error("--preflight cannot be combined with another command or prompt")
            _print_result(run_preflight())
            return 0

        if args.command == "preflight":
            if args.prompt:
                parser.error("preflight does not accept a prompt")
            _print_result(run_preflight())
            return 0

        prompt = " ".join(args.prompt).strip() or "Reply exactly: TASK COMPLETE lily flight reasoning smoke"
        _print_result(run_reasoning_smoke(prompt))
        return 0
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
