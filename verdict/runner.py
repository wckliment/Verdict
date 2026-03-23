from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from verdict.client import run_axon
from verdict.evaluator import evaluate_output


ROOT_DIR = Path(__file__).resolve().parent.parent
TEST_CASES_DIR = ROOT_DIR / "test_cases"
RESULTS_DIR = ROOT_DIR / "results"
LATEST_RUN_PATH = RESULTS_DIR / "latest_run.json"


def load_test_cases(folder_path: str) -> list[dict[str, Any]]:
    folder = Path(folder_path)
    test_cases: list[dict[str, Any]] = []

    for path in sorted(folder.glob("*.json")):
        with path.open("r", encoding="utf-8") as file:
            payload = json.load(file)
        if isinstance(payload, dict):
            test_cases.append(payload)

    return test_cases


def run_all_tests() -> list[dict[str, Any]]:
    test_cases = load_test_cases(str(TEST_CASES_DIR))
    results: list[dict[str, Any]] = []

    for test_case in test_cases:
        trace: list[dict[str, Any]] = []
        documents: list[str] = []

        try:
            response = run_axon(test_case["input"])

            # Output normalization
            output = response.get("output", "")
            if not isinstance(output, str):
                output = str(output)

            # Trace normalization
            trace = response.get("trace", [])
            if not isinstance(trace, list):
                trace = []

            # 🔥 CRITICAL: propagate retrieved documents
            documents = response.get("documents", [])
            if not isinstance(documents, list):
                documents = []

            execution_error = False

        except Exception as exc:
            output = str(exc)
            execution_error = True

        if execution_error:
            evaluation = {
                "passed": False,
                "score": 0,
                "failures": ["execution_error"],
                "failure_type": "execution_error",
            }
        else:
            evaluation = evaluate_output(output, test_case["expected"])

        results.append(
            {
                "test_id": test_case["id"],
                "input": test_case["input"],
                "output": output,
                "trace": trace,
                "documents": documents,  # 🔥 THIS FIXES YOUR FAILURE
                "passed": evaluation["passed"],
                "score": evaluation["score"],
                "failure_type": evaluation["failure_type"],
                "failures": evaluation["failures"],
            }
        )

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with LATEST_RUN_PATH.open("w", encoding="utf-8") as file:
        json.dump(results, file, indent=2)

    return results