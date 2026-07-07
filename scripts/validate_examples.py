#!/usr/bin/env python3
"""Validate every published example against its schema.

Run from the repository root:

    python scripts/validate_examples.py

Exits non-zero if any example fails validation or if a JSON example file
exists that is not registered below. New examples must be added to RULES so
they are validated in CI.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]

# (document, schema, optional JSON pointer into the document to validate)
RULES: list[tuple[str, str, list[str] | None]] = [
    ("sample-event.json", "envelope.schema.json", None),
    ("examples/managed-runtime-identity.json", "envelope.schema.json", None),
    ("examples/pre-tool-use-normalized-resource.json", "envelope.schema.json", None),
    ("examples/session-start-with-attestation.json", "envelope.schema.json", None),
    ("examples/tool-use-resumed-after-approval.json", "envelope.schema.json", None),
    ("examples/web-search-results-returned.json", "envelope.schema.json", None),
    ("examples/pre-tool-use-action-governance-email-send.json", "envelope.schema.json", None),
    ("examples/pre-tool-use-action-governance-email-send.json", "action-governance-profile.schema.json", None),
    ("examples/pre-tool-use-action-governance-mcp-call.json", "envelope.schema.json", None),
    ("examples/pre-tool-use-action-governance-mcp-call.json", "action-governance-profile.schema.json", None),
    ("examples/post-tool-use-action-governance-email-send.json", "envelope.schema.json", None),
    ("examples/post-tool-use-action-governance-email-send.json", "action-governance-profile.schema.json", None),
    ("examples/publisher-manifest.claude-code.json", "publisher-manifest.schema.json", None),
    ("examples/publisher-manifest.codex.json", "publisher-manifest.schema.json", None),
    ("examples/hookbus-runtime-attestation.json", "runtime-attestation.schema.json", None),
    # The approval example is a synchronous subscriber response (SPEC section 4);
    # its schema covers the metadata.approval object (SPEC section 10).
    ("examples/approval-lifecycle-ask.json", "approval-lifecycle.schema.json", ["metadata", "approval"]),
]

# JSON files in examples/ that are intentionally not schema-validated.
EXEMPT = {
    "examples/agenthook.lock.json",  # draft runtime contract lock file, no schema yet (AHP-009)
}


def main() -> int:
    failures = 0
    covered: set[str] = set(EXEMPT)
    for doc_path, schema_path, pointer in RULES:
        covered.add(doc_path)
        doc = json.loads((ROOT / doc_path).read_text())
        schema = json.loads((ROOT / schema_path).read_text())
        target = doc
        for key in pointer or []:
            target = target[key]
        try:
            jsonschema.validate(target, schema)
            print(f"PASS {doc_path} vs {schema_path}")
        except jsonschema.ValidationError as exc:
            failures += 1
            print(f"FAIL {doc_path} vs {schema_path}: {exc.message}", file=sys.stderr)

    unregistered = sorted(
        str(p.relative_to(ROOT))
        for p in (ROOT / "examples").glob("*.json")
        if str(p.relative_to(ROOT)) not in covered
    )
    if str((ROOT / "sample-event.json").relative_to(ROOT)) not in covered:
        unregistered.append("sample-event.json")
    for path in unregistered:
        failures += 1
        print(f"FAIL {path} is not registered in scripts/validate_examples.py", file=sys.stderr)

    print(f"{len(RULES)} checks, {failures} failures")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
