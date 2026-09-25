import json
from pathlib import Path

import jsonschema
import pytest

from agenthook_fixture.collector import CollectorClient, CollectorConfig
from agenthook_fixture.preflight import run_preflight

REPO_ROOT = Path(__file__).resolve().parents[3]
ENVELOPE = json.loads((REPO_ROOT / "envelope.schema.json").read_text())


class CaptureTransport:
    def __init__(self):
        self.events = []

    def __call__(self, url, headers, body):
        self.events.append(json.loads(body.decode()))
        return {"decision": "allow"}


@pytest.fixture()
def events():
    capture = CaptureTransport()
    client = CollectorClient(CollectorConfig(url="http://collector.test/event", source="test"), capture)
    run_preflight(client, session_id="sess-schema")
    return capture.events


def test_every_preflight_event_validates_against_envelope_schema(events):
    validator = jsonschema.Draft202012Validator(ENVELOPE, format_checker=jsonschema.FormatChecker())
    for event in events:
        errors = [e.message for e in validator.iter_errors(event)]
        assert not errors, (event["event_type"], errors)


def test_prompt_uses_canonical_metadata_keys(events):
    prompt_event = next(e for e in events if e["event_type"] == "UserPromptSubmit")
    assert "prompt" not in prompt_event.get("tool_input", {})
    assert prompt_event["metadata"]["prompt"]
    assert prompt_event["metadata"]["prompt_chars"] == len(prompt_event["metadata"]["prompt"])


def test_session_start_declares_spec_version(events):
    start = next(e for e in events if e["event_type"] == "SessionStart")
    assert start["metadata"]["spec_version"] == "0.2"
