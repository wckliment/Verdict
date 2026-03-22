from __future__ import annotations

from verdict.runner import run_all_tests


def main() -> None:
    results = run_all_tests()
    total = len(results)
    passed = sum(1 for result in results if result["passed"])
    failed = total - passed

    print(f"Total tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")


if __name__ == "__main__":
    main()
