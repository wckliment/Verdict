from __future__ import annotations

from typing import Any

import requests


AXON_URL = "http://localhost:8000/run"
REQUEST_TIMEOUT_SECONDS = 30


def run_axon(input_text: str) -> dict[str, Any]:
    try:
        response = requests.post(
            AXON_URL,
            json={"input": input_text},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(f"Failed to call Axon: {exc}") from exc

    try:
        payload = response.json()
    except ValueError as exc:
        raise RuntimeError("Axon returned invalid JSON.") from exc

    if not isinstance(payload, dict):
        raise RuntimeError("Axon response must be a JSON object.")

    if "result" not in payload:
        raise RuntimeError("Axon response missing 'result' field.")

    result_block = payload.get("result", {})
    raw_output = result_block.get("result")
    trace = result_block.get("trace", [])
    output = str(raw_output)

    return {
        "output": output,
        "trace": trace,
    }
