# Claim and evidence map

## One-sentence argument

Maximize how many two-candidate disapproval sets meet the omitted candidate
set, use averaging to rule out deficit-one deviations, and use a secondary
incidence tie-break to rule out unanimous equal-size deviations.

| Claim | Status | Evidence |
|---|---|---|
| Co-rank-two Hare-core existence for every `m >= k >= 2` | proved restricted-domain theorem | `paper/main.tex`, Theorem 1 |
| Every lexicographic maximizer gives a core committee | proved constructive statement | proof cases `d >= 2`, `d = 1`, `d = 0` |
| Pair-hit probability is strictly greater than `1/k` | proved exact factorization | Lemma 2 |
| Primary finite audit counts | exact finite verification for `m=4..7` at the documented multiplicity bounds | `verification/verify_corank2_global.py` |
| Independent finite audit counts | implementation-level independent exact verification on the same 14 rows plus `m=3,8` | `verification/verify_corank2_global_independent.py` |
| Polynomial-time computation | not claimed | exhaustive evaluation is an explicit finite rule only |
| Co-rank-three or unrestricted existence | open | outside package scope |

## Novelty boundary

The targeted primary-source audit in `../NOVELTY_AUDIT.md` found no equivalent
bounded-disapproval theorem.  The paper therefore says “apparently new after
a targeted audit,” not “first.”  Publicly available results verified for the comparison
cover `k <= 8`, `m <= 15`, and at most seven voter types.  Party-approval and
interval-domain results are credited as structurally different restrictions.
