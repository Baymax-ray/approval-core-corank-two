# Sparse disapproval and the Hare core

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

This self-contained package proves that every approval election in which each
voter disapproves at most two candidates has a nonempty deterministic Hare
core, for every `m >= k >= 2` and arbitrary positive rational voter weights.

The result does **not** resolve unrestricted Hare-core existence.  The
selection rule is explicit: choose a missing set that lexicographically
maximizes pair-disapproval coverage and total disapproval incidence.  No
polynomial-time implementation claim is made.

## Contents

- `paper/main.tex` and `paper/main.pdf`: manuscript source and release PDF.
- `paper/references.bib`: primary-source bibliography.
- `CLAIM_EVIDENCE.md`: theorem, proof, novelty, and verifier map.
- `verification/verify_corank2_global.py`: originating exact verifier.
- `verification/verify_corank2_global_independent.py`: independent bitmask and
  count-vector verifier.
- `verification/*.json`: sealed exact result summaries.
- `reproduce.ps1`: one-command verifier replay and PDF rebuild.
- `LICENSE`: MIT license for the manuscript, code, and verification artifacts.

## Reproduce

Requirements: Python 3.10 or newer and `pdflatex`.  No Python package or
network access is required.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\reproduce.ps1
```

Expected final marker:

```text
PASS_APPROVAL_CORE_SPARSE_DISAPPROVAL_RELEASE
```

The finite verifiers are independent falsification and regression checks.
The unbounded theorem follows from the symbolic proof in the manuscript.

## License

The manuscript, source code, and verification artifacts are released under
the [MIT License](LICENSE).
