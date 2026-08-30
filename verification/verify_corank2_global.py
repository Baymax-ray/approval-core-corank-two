"""Independent exact audit of the global co-rank-two Hare-core theorem.

The finite audit enumerates anonymous profiles, checks every lexicographic
maximizing missing set, and tests every nonempty target by the literal
integral Hare inequality.  It does not assume that only the top two target
sizes matter.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def subsets(candidates: tuple[int, ...], size: int):
    return itertools.combinations(candidates, size)


def disapproval_types(m: int) -> list[frozenset[int]]:
    types = [frozenset()]
    for size in (1, 2):
        types.extend(frozenset(x) for x in itertools.combinations(range(m), size))
    return types


def score(profile: tuple[frozenset[int], ...], b: frozenset[int]) -> tuple[int, int]:
    coverage = sum(len(h) == 2 and bool(h & b) for h in profile)
    incidence = sum(len(h & b) for h in profile)
    return coverage, incidence


def utility(h: frozenset[int], committee: frozenset[int]) -> int:
    return len(committee) - len(h & committee)


def literal_core_check(
    m: int,
    k: int,
    profile: tuple[frozenset[int], ...],
    committee: frozenset[int],
) -> tuple[bool, int]:
    n = len(profile)
    checks = 0
    for size in range(1, k + 1):
        for raw_target in subsets(tuple(range(m)), size):
            target = frozenset(raw_target)
            gainers = sum(utility(h, target) > utility(h, committee) for h in profile)
            checks += 1
            assert k * gainers < n * size, {
                "m": m,
                "k": k,
                "profile": [sorted(h) for h in profile],
                "committee": sorted(committee),
                "target": sorted(target),
                "gainers": gainers,
            }
    return True, checks


def audit_grid() -> dict[str, object]:
    rows: list[dict[str, int]] = []
    totals = {"profile_parameter_cases": 0, "maximizing_committees": 0, "committee_target_checks": 0}
    for m in range(4, 8):
        types = disapproval_types(m)
        n_max = 4 if m <= 6 else 3
        profiles = [
            tuple(types[j] for j in indices)
            for n in range(1, n_max + 1)
            for indices in itertools.combinations_with_replacement(range(len(types)), n)
        ]
        for k in range(2, m):
            missing_size = m - k
            missing_sets = [frozenset(x) for x in subsets(tuple(range(m)), missing_size)]
            row_profiles = 0
            row_maximizers = 0
            row_checks = 0
            for profile in profiles:
                scores = [score(profile, b) for b in missing_sets]
                best = max(scores)
                maximizers = [b for b, value in zip(missing_sets, scores) if value == best]
                for b in maximizers:
                    committee = frozenset(range(m)) - b
                    _, checks = literal_core_check(m, k, profile, committee)
                    row_checks += checks
                row_profiles += 1
                row_maximizers += len(maximizers)
            rows.append(
                {
                    "m": m,
                    "k": k,
                    "n_max": n_max,
                    "anonymous_profiles": row_profiles,
                    "maximizing_committees": row_maximizers,
                    "committee_target_checks": row_checks,
                }
            )
            totals["profile_parameter_cases"] += row_profiles
            totals["maximizing_committees"] += row_maximizers
            totals["committee_target_checks"] += row_checks
    return {"rows": rows, "totals": totals}


def audit_probability_inequality() -> dict[str, int]:
    cases = 0
    for k in range(2, 101):
        for missing_size in range(1, 101):
            m = k + missing_size
            numerator = m * (m - 1) - k * (k - 1)
            denominator = m * (m - 1)
            assert k * numerator > denominator
            cases += 1
    return {"k_max": 100, "missing_size_max": 100, "exact_cases": cases}


def main() -> None:
    result = {
        "theorem": (
            "For every m>k>=2, if every voter disapproves at most two "
            "candidates, every lexicographic (edge coverage, incidence) "
            "maximizing missing set B yields a Hare-core committee C\\B."
        ),
        "probability_inequality_audit": audit_probability_inequality(),
        "exhaustive_grid": audit_grid(),
    }
    output = HERE / "corank2_global_exact.json"
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    print("PASS_CORANK2_GLOBAL")


if __name__ == "__main__":
    main()
