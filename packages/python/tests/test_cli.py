from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENV = {**os.environ, "PYTHONPATH": str(ROOT)}


def run_cli(*args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "agenthook.cli", *args],
        cwd=ROOT,
        env=ENV,
        input=input_text,
        text=True,
        capture_output=True,
    )


class AgentHookCliTests(unittest.TestCase):
    def test_emit_pre_tool_use_is_valid_json(self) -> None:
        proc = run_cli(
            "emit",
            "--event",
            "PreToolUse",
            "--source",
            "demo",
            "--session",
            "s",
            "--tool",
            "Bash",
            "--input",
            '{"command":"pwd"}',
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        event = json.loads(proc.stdout)
        self.assertEqual(event["event_type"], "PreToolUse")
        self.assertEqual(event["metadata"]["reasoning_available"], False)
        self.assertEqual(event["metadata"]["enforcement_capable"], True)

    def test_validate_rejects_bad_uuid_and_event(self) -> None:
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            json.dump({"event_id": "bad", "event_type": "Bad", "timestamp": "x", "source": ""}, fh)
            path = fh.name
        try:
            proc = run_cli("validate", path)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("Bad", proc.stderr)
            self.assertIn("uuid", proc.stderr.lower())
        finally:
            Path(path).unlink(missing_ok=True)

    def test_init_dry_run_does_not_require_gate(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            env = {**ENV, "HOME": home}
            proc = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "agenthook.cli",
                    "init",
                    "claude-code",
                    "--target",
                    "http://localhost:18800/event",
                    "--token",
                    "tok",
                    "--dry-run",
                ],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
            )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("HOOKBUS_URL=http://localhost:18800/event", proc.stdout)

    def test_conformance_smoke(self) -> None:
        proc = run_cli("test", "publisher", "--source", "demo")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("Bronze: pass", proc.stdout)
        self.assertIn("Silver: partial", proc.stdout)

    def test_emit_target_posts_bearer_event(self) -> None:
        seen: dict[str, object] = {}

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):  # noqa: N802
                length = int(self.headers.get("Content-Length", "0"))
                seen["auth"] = self.headers.get("Authorization")
                seen["body"] = json.loads(self.rfile.read(length))
                payload = b'{"decision":"allow","reason":"test"}'
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            def log_message(self, *_args):  # noqa: D401
                return

        server = HTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.handle_request, daemon=True)
        thread.start()
        try:
            target = f"http://127.0.0.1:{server.server_port}/event"
            proc = run_cli(
                "emit",
                "--event",
                "PreToolUse",
                "--source",
                "demo",
                "--session",
                "s",
                "--tool",
                "Bash",
                "--input",
                '{"command":"pwd"}',
                "--target",
                target,
                "--token",
                "tok",
            )
        finally:
            server.server_close()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(seen["auth"], "Bearer tok")
        self.assertEqual(seen["body"]["event_type"], "PreToolUse")
        self.assertEqual(json.loads(proc.stdout)["decision"], "allow")

    def test_collector_conformance_posts_canonical_events(self) -> None:
        seen: list[dict] = []

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):  # noqa: N802
                length = int(self.headers.get("Content-Length", "0"))
                body = json.loads(self.rfile.read(length))
                seen.append(body)
                payload = json.dumps({
                    "event_id": body["event_id"],
                    "decision": "allow",
                    "reason": "collector test",
                }).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            def log_message(self, *_args):
                return

        server = HTTPServer(("127.0.0.1", 0), Handler)

        def serve():
            for _ in range(7):
                server.handle_request()

        thread = threading.Thread(target=serve, daemon=True)
        thread.start()
        try:
            target = f"http://127.0.0.1:{server.server_port}/event"
            proc = run_cli("test", "collector", "--target", target, "--token", "tok")
        finally:
            server.server_close()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("Result: pass", proc.stdout)
        self.assertEqual(len(seen), 7)
        self.assertIn("ModelResponse", {event["event_type"] for event in seen})


if __name__ == "__main__":
    unittest.main()
