# 🤖 AI-Augmented Task — Student Grade Merger

---

## 1️⃣ Exact Prompt Used

> *"Write a Python function that takes two dictionaries representing student grades
> from two different semesters and produces a merged report showing: combined GPA,
> grade trend (improving/declining/stable), and subjects common to both semesters.
> Use defaultdict and dict comprehension."*

---

## 2️⃣ AI Output (Claude)

```python
from collections import defaultdict

def merge_grade_report(sem1: dict, sem2: dict) -> dict:
    sem1_gpa = sum(sem1.values()) / len(sem1) if sem1 else 0
    sem2_gpa = sum(sem2.values()) / len(sem2) if sem2 else 0
    combined_gpa = (sem1_gpa + sem2_gpa) / 2

    if sem2_gpa > sem1_gpa:
        trend = "improving"
    elif sem2_gpa < sem1_gpa:
        trend = "declining"
    else:
        trend = "stable"

    common_subjects = {subj: (sem1[subj], sem2[subj])
                       for subj in sem1 if subj in sem2}

    all_subjects = defaultdict(list)
    for subj, grade in sem1.items():
        all_subjects[subj].append(grade)
    for subj, grade in sem2.items():
        all_subjects[subj].append(grade)

    return {
        "sem1_gpa": round(sem1_gpa, 2),
        "sem2_gpa": round(sem2_gpa, 2),
        "combined_gpa": round(combined_gpa, 2),
        "trend": trend,
        "common_subjects": common_subjects,
        "all_subjects": dict(all_subjects),
    }
```

---

## 3️⃣ Critical Evaluation of AI Output

| Check | Result | Notes |
|-------|--------|-------|
| Handles empty dicts | ✅ | Guards `if sem1 else 0` prevent ZeroDivisionError |
| Uses `.get()` for safe access | ❌ | `sem1[subj]` in comprehension will `KeyError` if dict is modified concurrently or subclassed |
| Trend calculation correct | ⚠️ Partially | Compares **averages** — correct in principle, but a 0.01 difference triggers "improving". No threshold for "stable". |
| Handles single semester | ⚠️ | `combined_gpa = (0 + sem2_gpa) / 2` underestimates if sem1 is empty |
| Subjects with no overlap | ✅ | `common_subjects` will be `{}` |
| Uses defaultdict correctly | ✅ | Groups all grades by subject |
| Uses dict comprehension | ✅ | `common_subjects` comprehension is clean |
| Type hints | ❌ | Missing return type annotation |
| Docstring | ❌ | No documentation |
| GPA scale assumption | ❌ | Assumes raw numeric grades, not validated (could receive strings) |
| `combined_gpa` calculation | ❌ | Simple mean of two averages is wrong when semesters have different subject counts. Should weight by total subjects. |

---

## 4️⃣ Improved Version

```python
from collections import defaultdict
from typing import Optional


def merge_grade_report(
    sem1: dict[str, float],
    sem2: dict[str, float],
    stable_threshold: float = 0.1,
) -> dict:
    """
    Merge two semester grade dicts into a combined academic report.

    Args:
        sem1: Semester 1 grades — {subject: grade}.
        sem2: Semester 2 grades — {subject: grade}.
        stable_threshold: Max GPA difference to still call trend 'stable'.
                          Defaults to 0.1 grade points.

    Returns:
        Dict with keys:
          - sem1_gpa         : float | None
          - sem2_gpa         : float | None
          - combined_gpa     : float | None  (weighted by subject count)
          - trend            : 'improving' | 'declining' | 'stable' | 'insufficient_data'
          - common_subjects  : {subject: (sem1_grade, sem2_grade)}
          - all_subjects     : {subject: [grade, ...]}  (all grades per subject)
          - subjects_only_sem1 : list of subjects unique to semester 1
          - subjects_only_sem2 : list of subjects unique to semester 2

    Edge cases handled:
      - Empty dicts → GPA reported as None
      - Single semester → combined_gpa = that semester's GPA
      - Non-numeric grades → skipped with warning
      - Different subject counts → weighted combined GPA

    Example:
        >>> sem1 = {'Math': 85, 'Science': 90, 'English': 78}
        >>> sem2 = {'Math': 88, 'Science': 92, 'History': 75}
        >>> merge_grade_report(sem1, sem2)
    """
    def _safe_gpa(grades: dict[str, float]) -> Optional[float]:
        """Compute average, ignoring non-numeric values."""
        valid = [v for v in grades.values() if isinstance(v, (int, float))]
        return round(sum(valid) / len(valid), 2) if valid else None

    sem1_gpa = _safe_gpa(sem1)
    sem2_gpa = _safe_gpa(sem2)

    # Weighted combined GPA (accounts for different subject counts)
    if sem1_gpa is not None and sem2_gpa is not None:
        total = len(sem1) + len(sem2)
        combined_gpa = round(
            (sem1_gpa * len(sem1) + sem2_gpa * len(sem2)) / total, 2
        )
    elif sem1_gpa is not None:
        combined_gpa = sem1_gpa
    elif sem2_gpa is not None:
        combined_gpa = sem2_gpa
    else:
        combined_gpa = None

    # Trend with threshold to avoid noise
    if sem1_gpa is None or sem2_gpa is None:
        trend = "insufficient_data"
    elif abs(sem2_gpa - sem1_gpa) <= stable_threshold:
        trend = "stable"
    elif sem2_gpa > sem1_gpa:
        trend = "improving"
    else:
        trend = "declining"

    # Common subjects — safe .get() access
    common_subjects: dict[str, tuple] = {
        subj: (sem1.get(subj), sem2.get(subj))
        for subj in sem1
        if subj in sem2
    }

    # All subjects grouped by name — defaultdict(list)
    all_subjects: defaultdict[str, list] = defaultdict(list)
    for subj, grade in sem1.items():
        all_subjects[subj].append(("sem1", grade))
    for subj, grade in sem2.items():
        all_subjects[subj].append(("sem2", grade))

    sem1_keys = set(sem1)
    sem2_keys = set(sem2)

    return {
        "sem1_gpa":           sem1_gpa,
        "sem2_gpa":           sem2_gpa,
        "combined_gpa":       combined_gpa,
        "trend":              trend,
        "common_subjects":    common_subjects,
        "all_subjects":       dict(all_subjects),
        "subjects_only_sem1": sorted(sem1_keys - sem2_keys),
        "subjects_only_sem2": sorted(sem2_keys - sem1_keys),
    }


# ── Tests ──────────────────────────────────────────────────────

def run_tests():
    print("Running tests...\n")

    # Normal case
    sem1 = {"Math": 85, "Science": 90, "English": 78}
    sem2 = {"Math": 88, "Science": 92, "History": 75}
    r = merge_grade_report(sem1, sem2)
    print(f"[Normal]        trend={r['trend']}, combined_gpa={r['combined_gpa']}")
    assert r["trend"] == "improving"
    assert r["common_subjects"] == {"Math": (85, 88), "Science": (90, 92)}
    assert r["subjects_only_sem1"] == ["English"]
    assert r["subjects_only_sem2"] == ["History"]

    # Both empty
    r2 = merge_grade_report({}, {})
    print(f"[Both empty]    trend={r2['trend']}, combined_gpa={r2['combined_gpa']}")
    assert r2["trend"] == "insufficient_data"
    assert r2["combined_gpa"] is None

    # Single semester (sem1 empty)
    r3 = merge_grade_report({}, {"Math": 90})
    print(f"[Single sem]    trend={r3['trend']}, combined_gpa={r3['combined_gpa']}")
    assert r3["combined_gpa"] == 90.0
    assert r3["trend"] == "insufficient_data"

    # Stable (within threshold)
    r4 = merge_grade_report({"Math": 85}, {"Math": 85.05}, stable_threshold=0.1)
    print(f"[Stable]        trend={r4['trend']}")
    assert r4["trend"] == "stable"

    # No common subjects
    r5 = merge_grade_report({"Math": 80}, {"Science": 90})
    print(f"[No overlap]    common_subjects={r5['common_subjects']}")
    assert r5["common_subjects"] == {}

    print("\n✅ All tests passed!")


if __name__ == "__main__":
    run_tests()

    sem1 = {"Math": 85, "Science": 90, "English": 78}
    sem2 = {"Math": 88, "Science": 92, "History": 75}
    report = merge_grade_report(sem1, sem2)

    print("\n📊 Sample Report:")
    for k, v in report.items():
        print(f"  {k:<22}: {v}")
```

---

## Summary: AI vs Improved Version

| Aspect | AI Version | Improved Version |
|--------|-----------|-----------------|
| Empty dict handling | Basic (0 GPA) | Returns `None`, not misleading 0 |
| Safe key access | ❌ `sem1[subj]` | ✅ `.get(subj)` |
| Trend stability | Binary comparison | Configurable `stable_threshold` |
| Combined GPA formula | Mean of means (wrong) | Weighted by subject count |
| Single semester | Underestimates | Returns actual GPA |
| Type hints | ❌ | ✅ Full annotations |
| Docstring | ❌ | ✅ Google-style with edge cases |
| Tests | ❌ | ✅ 5 edge-case tests |
| Subject exclusives | ❌ Not reported | ✅ `subjects_only_sem1/2` |
