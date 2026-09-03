# Sparse disapproval and the Hare core

[![Code license: MIT](https://img.shields.io/badge/code%20license-MIT-yellow.svg)](LICENSE)

This self-contained package proves that every approval election in which each
voter disapproves at most two candidates has a nonempty deterministic Hare
core, for every `m >= k >= 2` and arbitrary positive rational voter weights.

The result does **not** resolve unrestricted Hare-core existence.  The
selection rule is explicit: fix a candidate order, maximize pair-disapproval
coverage and total disapproval incidence, and use the induced order to break
any remaining tie.  No
polynomial-time implementation claim is made.

## Contents

- `paper/main.tex` and `paper/main.pdf`: manuscript source and release PDF.
- `paper/references.bib`: primary-source bibliography.
- `CLAIM_EVIDENCE.md`: theorem, proof, novelty, and verifier map.
- `verification/verify_corank2_global.py`: primary set-based exact verifier.
- `verification/verify_corank2_global_independent.py`: implementation-level
  independent bitmask and type-count-vector verifier.
- `verification/*.json`: sealed exact result summaries.
- `reproduce.ps1`: one-command verifier replay and PDF rebuild.
- `LICENSE`: MIT license for files outside `paper/`.
- `LICENSE-PAPER`: copyright and future arXiv-license notice for the
  manuscript files under `paper/`.

## Reproduce

Requirements: Python 3.10 or newer, BibTeX, and pdfTeX 1.40.29 from TeX Live
2026.  No Python package or network access is required.  The TeX version is
pinned only for the byte-identical release-PDF check; the symbolic proof and
finite Python audits do not depend on TeX.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\reproduce.ps1
```

Expected final marker:

```text
PASS_APPROVAL_CORE_SPARSE_DISAPPROVAL_RELEASE
```

The finite verifiers are independent falsification and regression checks.
Their grids overlap on 14 `(m,k)` rows; the bitmask implementation additionally
covers `m=3` and `m=8`.  They enumerate only the documented small integer
multiplicities, while the unbounded rational-weight theorem follows from the
symbolic proof.  The scripts reject disabled Python assertions, and the
reproduction wrapper checks every native-process exit code before printing
the release marker.

## License

This is a mixed-license package:

- Files outside `paper/`, including the source code and verification
  artifacts, are released under the [MIT License](LICENSE).
- Every file under `paper/`, including `main.tex`, `main.pdf`, and
  `references.bib`, is governed by [LICENSE-PAPER](LICENSE-PAPER) and is not
  MIT-licensed.
