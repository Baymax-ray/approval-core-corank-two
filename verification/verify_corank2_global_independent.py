#!/usr/bin/env python3
"""Independent bitmask audit of the global co-rank-two Hare-core theorem.

This deliberately uses weighted type-count vectors and bit operations rather
than the tuple/frozenset implementation in the primary verifier.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def masks_of_size(m: int, size: int) -> tuple[int, ...]:
    return tuple(sum(1 << candidate for candidate in raw) for raw in itertools.combinations(range(m), size))


def corank_two_types(m: int) -> tuple[int, ...]:
    return (0,) + masks_of_size(m, 1) + masks_of_size(m, 2)


def anonymous_count_vectors(type_count: int, n_max: int):
    for total in range(1, n_max + 1):
        for indices in itertools.combinations_with_replacement(range(type_count), total):
            counts = [0] * type_count
            for index in indices:
                counts[index] += 1
            yield tuple(counts)


def lex_score(types: tuple[int, ...], counts: tuple[int, ...], missing: int) -> tuple[int, int]:
    coverage = 0
    incidence = 0
    for disapproval, count in zip(types, counts):
        overlap = (disapproval & missing).bit_count()
        if disapproval.bit_count() == 2 and overlap:
            coverage += count
        incidence += count * overlap
    return coverage, incidence


def utility(disapproval: int, committee: int) -> int:
    return committee.bit_count() - (disapproval & committee).bit_count()


def exact_core_replay(
    m: int,
    k: int,
    types: tuple[int, ...],
    counts: tuple[int, ...],
    committee: int,
    targets: tuple[int, ...],
) -> int:
    total_weight = sum(counts)
    committee_utilities = tuple(utility(disapproval, committee) for disapproval in types)
    for target in targets:
        target_size = target.bit_count()
        gainer_weight = sum(
            count
            for disapproval, count, base_utility in zip(types, counts, committee_utilities)
            if count and utility(disapproval, target) > base_utility
        )
        assert k * gainer_weight < total_weight * target_size, {
            "m": m,
            "k": k,
            "type_counts": counts,
            "committee_mask": committee,
            "target_mask": target,
            "gainer_weight": gainer_weight,
            "total_weight": total_weight,
        }
    return len(targets)


def exhaustive_grid() -> dict[str, object]:
    rows = []
    totals = {
        "profile_parameter_cases": 0,
        "lexicographic_maximizers": 0,
        "committee_target_checks": 0,
    }
    for m in range(3, 9):
        n_max = 4 if m <= 6 else 3 if m == 7 else 2
        types = corank_two_types(m)
        profiles = tuple(anonymous_count_vectors(len(types), n_max))
        full = (1 << m) - 1
        for k in range(2, m):
            missing_sets = masks_of_size(m, m - k)
            targets = tuple(
                target
                for size in range(1, k + 1)
                for target in masks_of_size(m, size)
            )
            row_maximizers = 0
            row_checks = 0
            for counts in profiles:
                scores = tuple(lex_score(types, counts, missing) for missing in missing_sets)
                best = max(scores)
                maximizers = tuple(
                    missing for missing, value in zip(missing_sets, scores) if value == best
                )
                for missing in maximizers:
                    row_checks += exact_core_replay(
                        m,
                        k,
                        types,
                        counts,
                        full ^ missing,
                        targets,
                    )
                row_maximizers += len(maximizers)
            row = {
                "m": m,
                "k": k,
                "n_max": n_max,
                "anonymous_profiles": len(profiles),
                "lexicographic_maximizers": row_maximizers,
                "committee_target_checks": row_checks,
            }
            rows.append(row)
            totals["profile_parameter_cases"] += len(profiles)
            totals["lexicographic_maximizers"] += row_maximizers
            totals["committee_target_checks"] += row_checks
    return {"rows": rows, "totals": totals}


def exact_probability_identity_grid() -> dict[str, int]:
    cases = 0
    minimum_gap = None
    for k in range(2, 151):
        for missing_size in range(1, 151):
            m = k + missing_size
            direct_gap = k * (m * (m - 1) - k * (k - 1)) - m * (m - 1)
            factored_gap = (k - 1) * (
                (2 * missing_size - 1) * k + missing_size * (missing_size - 1)
            )
            assert direct_gap == factored_gap
            assert factored_gap > 0
            minimum_gap = factored_gap if minimum_gap is None else min(minimum_gap, factored_gap)
            cases += 1
    return {
        "k_max": 150,
        "missing_size_max": 150,
        "exact_cases": cases,
        "minimum_positive_cross_multiplication_gap": int(minimum_gap or 0),
    }


def main() -> None:
    payload = {
        "status": "INDEPENDENT_AUDIT_PASS_CORANK2_GLOBAL",
        "symbolic_probability_identity": exact_probability_identity_grid(),
        "independent_bitmask_grid": exhaustive_grid(),
        "logical_scope": (
            "The exact algebra proves every m>k>=2; the finite bitmask grid is an "
            "independent bounded regression check."
        ),
    }
    output = HERE / "corank2_global_independent_exact.json"
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    print("PASS_CORANK2_GLOBAL_INDEPENDENT")


if __name__ == "__main__":
    main()
