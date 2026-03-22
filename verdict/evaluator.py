from __future__ import annotations

from typing import Any


def evaluate_output(output: str, expected: dict[str, Any]) -> dict[str, Any]:
    score = 0
    failures: list[str] = []

    for value in expected.get("contains", []):
        if value in output:
            score += 1
        else:
            failures.append(f"missing:{value}")

    contains_any = expected.get("contains_any", [])
    if contains_any:
        if any(value in output for value in contains_any):
            score += 1
        else:
            failures.append("missing_any")

    for value in expected.get("not_contains", []):
        if value in output:
            failures.append(f"forbidden:{value}")

    min_length = expected.get("min_length")
    if min_length is not None and len(output) < min_length:
        failures.append("too_short")

    passed = not failures

    if any(failure.startswith("forbidden:") for failure in failures):
        failure_type = "hallucination"
    elif any(failure.startswith("missing") for failure in failures):
        failure_type = "retrieval_missing"
    elif "too_short" in failures:
        failure_type = "execution_error"
    else:
        failure_type = "unknown"

    return {
        "passed": passed,
        "score": score,
        "failures": failures,
        "failure_type": failure_type,
    }
