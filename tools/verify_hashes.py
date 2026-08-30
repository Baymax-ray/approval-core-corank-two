#!/usr/bin/env python3
"""Strictly verify a SHA-256 manifest and its stable-file coverage."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path, PurePosixPath


UNSTABLE_DIRECTORY_NAMES = {".git", "tmp", "__pycache__"}
UNSTABLE_DIRECTORY_PATHS = {("paper", "build")}
UNSTABLE_SUFFIXES = (
    ".pyc",
    ".aux",
    ".log",
    ".out",
    ".toc",
    ".fls",
    ".fdb_latexmk",
    ".synctex.gz",
)
HEX64 = re.compile(r"[0-9a-f]{64}")


def is_explicitly_unstable(relative: Path) -> bool:
    """Return whether *relative* is one of the documented generated paths."""

    if any(part in UNSTABLE_DIRECTORY_NAMES for part in relative.parts):
        return True
    if any(relative.parts[: len(prefix)] == prefix for prefix in UNSTABLE_DIRECTORY_PATHS):
        return True
    return relative.name.lower().endswith(UNSTABLE_SUFFIXES)


def stable_files(root: Path, manifest: Path) -> list[Path]:
    """List every stable file, excluding *manifest* by its resolved path."""

    resolved_root = root.resolve()
    resolved_manifest = manifest.resolve()
    answer: list[Path] = []
    for path in resolved_root.rglob("*"):
        relative = path.relative_to(resolved_root)
        if is_explicitly_unstable(relative):
            continue
        if path.is_symlink():
            raise ValueError(f"symbolic links are not supported: {relative.as_posix()}")
        if not path.is_file():
            continue
        if path.resolve() == resolved_manifest:
            continue
        answer.append(path)
    return sorted(answer, key=lambda item: item.relative_to(resolved_root).as_posix())


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def parse_manifest(manifest: Path, root: Path) -> dict[str, str]:
    claimed: dict[str, str] = {}
    for line_number, line in enumerate(
        manifest.read_text(encoding="utf-8").splitlines(), 1
    ):
        if "  " not in line:
            raise ValueError(f"malformed manifest line {line_number}")
        expected, name = line.split("  ", 1)
        posix_name = PurePosixPath(name)
        if (
            not HEX64.fullmatch(expected)
            or not name
            or "\\" in name
            or posix_name.is_absolute()
            or any(part in {"", ".", ".."} for part in posix_name.parts)
        ):
            raise ValueError(f"malformed manifest line {line_number}")
        if name in claimed:
            raise ValueError(f"duplicate manifest path: {name}")
        resolved = (root / Path(*posix_name.parts)).resolve()
        if resolved != root and root not in resolved.parents:
            raise ValueError(f"path escapes repository: {name}")
        claimed[name] = expected
    return claimed


def verify(manifest: Path) -> int:
    resolved_manifest = manifest.resolve()
    root = resolved_manifest.parent
    claimed = parse_manifest(resolved_manifest, root)
    actual_paths = stable_files(root, resolved_manifest)
    actual_names = {path.relative_to(root).as_posix() for path in actual_paths}
    if set(claimed) != actual_names:
        missing = sorted(actual_names - set(claimed))
        extra = sorted(set(claimed) - actual_names)
        raise ValueError(f"manifest coverage mismatch: missing={missing}, extra={extra}")
    for path in actual_paths:
        name = path.relative_to(root).as_posix()
        if digest(path) != claimed[name]:
            raise ValueError(f"hash mismatch: {name}")
    print(f"VERIFIED_SHA256SUMS files={len(actual_paths)}")
    return 0


def main() -> int:
    repository_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "manifest",
        nargs="?",
        type=Path,
        default=repository_root / "SHA256SUMS",
    )
    arguments = parser.parse_args()
    try:
        return verify(arguments.manifest)
    except (OSError, ValueError) as error:
        print(f"HASH_VERIFICATION_FAILED: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
