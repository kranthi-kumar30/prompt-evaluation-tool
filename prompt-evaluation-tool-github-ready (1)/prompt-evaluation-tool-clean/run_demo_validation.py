"""Run all student demo examples and report pass/fail per sub-metric."""

from evaluator.demo_examples import ALL_DEMO_CASES, SUB_METRIC_FIELD
from evaluator.prompt_framework import evaluate_prompt


def _get_score(result, field: str) -> float:
    if field == "final_score":
        return float(result.final_score())
    val = getattr(result, field)
    return float(val() if callable(val) else val)


def run_demo_validation() -> int:
    print("Student Demo Examples — sub-metric validation\n")
    failed = 0
    current_pillar = ""

    for case in ALL_DEMO_CASES:
        if case.pillar != current_pillar:
            current_pillar = case.pillar
            print(f"\n{'=' * 60}")
            print(f"  {current_pillar}")
            print(f"{'=' * 60}")

        result = evaluate_prompt(case.prompt, case.question)
        field = SUB_METRIC_FIELD[case.sub_metric]
        score = _get_score(result, field)
        ok = case.min_score <= score <= case.max_score
        tag = "PASS" if ok else "FAIL"
        print(
            f"  {tag} [{case.quality.upper():4}] {case.sub_metric}: "
            f"{score:.2f} (expected {case.min_score:.2f}–{case.max_score:.2f})"
        )
        print(f"         {case.label}")
        if not ok:
            failed += 1
            print(f"         >>> Prompt: {case.prompt[:80]!r}...")

    print(f"\n{'=' * 60}")
    total = len(ALL_DEMO_CASES)
    passed = total - failed
    print(f"Results: {passed}/{total} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(run_demo_validation())
