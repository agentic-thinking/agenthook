import json
import pytest

from lily_flight.cli import main
from lily_flight.collector import CollectorClient, CollectorConfig
from lily_flight.preflight import AGENTHOOK_HOOKS, run_preflight


class CaptureTransport:
    def __init__(self):
        self.events = []

    def __call__(self, url, headers, body):
        self.events.append({
            "url": url,
            "headers": headers,
            "body": json.loads(body.decode()),
        })
        return {"decision": "allow"}


def test_preflight_emits_all_10_hooks_in_order():
    capture = CaptureTransport()
    client = CollectorClient(CollectorConfig(url="http://collector.test/event", token="", source="test"), capture)
    result = run_preflight(client, session_id="sess-test")

    assert result["events"] == AGENTHOOK_HOOKS
    assert [event["body"]["event_type"] for event in capture.events] == AGENTHOOK_HOOKS
    assert {event["body"]["session_id"] for event in capture.events} == {"sess-test"}


def test_envelopes_carry_agenthook_metadata_and_reasoning():
    capture = CaptureTransport()
    client = CollectorClient(CollectorConfig(url="http://collector.test/event", source="test"), capture)
    run_preflight(client, session_id="sess-test")

    model_response = next(
        event["body"] for event in capture.events
        if event["body"]["event_type"] == "ModelResponse"
    )
    assert model_response["metadata"]["publisher"] == "lily-flight"
    assert model_response["metadata"]["agenthook_standard"] == "https://agenthook.org"
    assert model_response["metadata"]["reasoning_available"] is True
    assert model_response["metadata"]["reasoning_content"]


def test_auth_header_is_added_when_token_present():
    capture = CaptureTransport()
    client = CollectorClient(CollectorConfig(url="http://collector.test/event", token="token-123"), capture)
    client.emit("SessionStart", "sess-test")

    assert capture.events[0]["headers"]["Authorization"] == "Bearer token-123"


def test_preflight_flag_cannot_shadow_reasoning_smoke():
    with pytest.raises(SystemExit):
        main(["reasoning-smoke", "--preflight"])


def test_transport_failure_is_reported_without_traceback(monkeypatch, capsys):
    def fail():
        raise RuntimeError("Collector request failed: refused")

    monkeypatch.setattr("lily_flight.cli.run_preflight", fail)
    assert main(["preflight"]) == 1
    captured = capsys.readouterr()
    assert "error: Collector request failed: refused" in captured.err
