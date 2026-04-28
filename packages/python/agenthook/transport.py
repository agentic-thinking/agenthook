from __future__ import annotations

import json
import urllib.request
from typing import Any


def emit_http(event: dict[str, Any], target: str, token: str = "", timeout: int = 10) -> dict[str, Any]:
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(target, data=json.dumps(event).encode("utf-8"), headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read()
        if not body:
            return {"status": resp.status}
        return json.loads(body)
