#!/usr/bin/env python3

"""
generate-library.py

Generate a conservative public catalogue for the Library repository.

The repository may contain many representations of the same work:

    paper.pdf
    paper.tex
    paper.aux
    paper.log

or:

    A Beautiful Lie.mhtml
    A Beautiful Lie.txt

The filesystem contains all of these objects, but the public library
does not need to present every representation as a distinct artifact.

The generator therefore:

    1. Scans the repository.
    2. Excludes build products, source representations, HTML archives,
       transcripts, and other sidecars.
    3. Groups remaining files conservatively by basename WITHIN the
       same directory.
    4. Selects one preferred representation from each group.
    5. Evaluates the existing library.json against that reduced corpus.
    6. Admits the existing manifest when it remains sufficiently
       representative.
    7. Otherwise regenerates library.json.

No fuzzy title matching is performed. Different directories remain
different historical objects even when their basenames are identical.

Usage:

    python generate-library.py

Optional:

    python generate-library.py --force
    python generate-library.py --dry-run
    python generate-library.py --verbose
"""

from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# =====================================================================
# Configuration
# =====================================================================

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "library.json"

ADMISSION_THRESHOLD = 0.95


# Lower number means a more desirable public representation.
#
# HTML/MHTML and TeX are intentionally absent. They remain in the
# repository but are not default public-library artifacts.

FORMAT_PRIORITY = {
    ".pdf": 10,
    ".md": 20,
    ".txt": 30,
    ".ipynb": 40,
    ".mp3": 50,
    ".wav": 51,
    ".ogg": 52,
    ".lean": 60,
    ".py": 70,
    ".sh": 71,
}


# Files with these extensions are never admitted to the default
# public catalogue.

NEVER_INDEX = {
    # Web/export/archive representations
    ".html",
    ".mhtml",

    # LaTeX source and build products
    ".tex",
    ".aux",
    ".log",
    ".out",
    ".toc",
    ".bbl",
    ".blg",
    ".fls",
    ".fdb_latexmk",
    ".ilg",
    ".ind",
    ".idx",
    ".lof",
    ".lot",

    # Transcript / subtitle sidecars
    ".srt",
    ".vtt",

    # Tabular sidecars
    ".tsv",
    ".csv",

    # Images and font assets are not catalogue entries
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".svg",
    ".ttf",
    ".woff",
    ".woff2",
    ".eot",
    ".g2n",
}


EXCLUDE_DIRECTORIES = {
    ".git",
    ".github",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
}


EXCLUDE_NAMES = {
    "library.json",
    "package-lock.json",
    "file-list.txt",
    "file-list(2).txt",
}


# =====================================================================
# Paths
# =====================================================================

def relative_path(path: Path) -> str:
    """Return a browser-friendly repository-relative path."""

    return path.relative_to(ROOT).as_posix()


def is_inside_excluded_directory(path: Path) -> bool:
    """Return True if any path component belongs to an excluded tree."""

    try:
        relative = path.relative_to(ROOT)
    except ValueError:
        return True

    return any(
        part in EXCLUDE_DIRECTORIES
        for part in relative.parts
    )


# =====================================================================
# Candidate selection
# =====================================================================

def is_candidate(path: Path) -> bool:
    """
    Decide whether a file can represent a public library artifact.

    This is intentionally conservative.
    """

    if not path.is_file():
        return False

    if is_inside_excluded_directory(path):
        return False

    if path.name in EXCLUDE_NAMES:
        return False

    suffix = path.suffix.lower()

    if suffix in NEVER_INDEX:
        return False

    return suffix in FORMAT_PRIORITY


def scan_all_files() -> list[Path]:
    """Return all ordinary files, including files later excluded."""

    return sorted(
        (
            path
            for path in ROOT.rglob("*")
            if path.is_file()
            and not is_inside_excluded_directory(path)
        ),
        key=relative_path,
    )


def scan_candidates(
    all_files: list[Path],
) -> list[Path]:
    """Return files eligible to represent catalogue artifacts."""

    return [
        path
        for path in all_files
        if is_candidate(path)
    ]


# =====================================================================
# Conservative equivalence
# =====================================================================

def artifact_key(path: Path) -> tuple[str, str]:
    """
    Construct a conservative equivalence key.

    Only files with the same stem IN THE SAME DIRECTORY collapse.

    Thus:

        A Beautiful Lie.txt
        A Beautiful Lie.pdf

    can represent one artifact if they occur together.

    But:

        monograph/draft-01/monograph.pdf
        monograph/monograph.pdf

    remain distinct because their directory histories differ.

    No attempt is made here to equate:

        Text as Substrate - v1
        Text as Substrate - v2
        Text as Substrate

    Those may be historically meaningful distinct objects.
    """

    parent = (
        path.parent
        .relative_to(ROOT)
        .as_posix()
        .casefold()
    )

    stem = (
        path.stem
        .strip()
        .casefold()
    )

    return parent, stem


def group_candidates(
    candidates: list[Path],
) -> dict[tuple[str, str], list[Path]]:
    """Group possible representations of the same artifact."""

    groups: dict[
        tuple[str, str],
        list[Path],
    ] = defaultdict(list)

    for path in candidates:
        groups[artifact_key(path)].append(path)

    return dict(groups)


def choose_representative(
    paths: list[Path],
) -> Path:
    """
    Select the preferred representation from an equivalence group.
    """

    return min(
        paths,
        key=lambda path: (
            FORMAT_PRIORITY[path.suffix.lower()],
            relative_path(path).casefold(),
        ),
    )


def select_representatives(
    groups: dict[tuple[str, str], list[Path]],
) -> tuple[list[Path], dict[Path, list[Path]]]:
    """
    Return selected artifacts and the representations collapsed into each.
    """

    selected: list[Path] = []

    collapsed: dict[
        Path,
        list[Path],
    ] = {}

    for paths in groups.values():

        winner = choose_representative(paths)

        selected.append(winner)

        alternatives = [
            path
            for path in paths
            if path != winner
        ]

        if alternatives:
            collapsed[winner] = alternatives

    selected.sort(
        key=relative_path
    )

    return selected, collapsed


# =====================================================================
# Object metadata
# =====================================================================

def make_id(path: Path) -> str:
    """Create a deterministic ID from the repository-relative path."""

    value = relative_path(path).casefold()

    characters: list[str] = []

    previous_dash = False

    for character in value:

        if character.isalnum():

            characters.append(character)
            previous_dash = False

        elif not previous_dash:

            characters.append("-")
            previous_dash = True

    return "".join(
        characters
    ).strip("-")


def title_from_path(path: Path) -> str:
    """Produce a conservative display title from a filename."""

    title = path.stem

    title = title.replace(
        "_",
        " ",
    )

    return " ".join(
        title.split()
    )


def object_type(path: Path) -> str:
    """Map a representation to a useful public type."""

    mapping = {
        ".pdf": "pdf",
        ".md": "text",
        ".txt": "text",
        ".ipynb": "notebook",
        ".mp3": "audio",
        ".wav": "audio",
        ".ogg": "audio",
        ".lean": "formalization",
        ".py": "program",
        ".sh": "program",
    }

    return mapping.get(
        path.suffix.lower(),
        "artifact",
    )


def modified_date(path: Path) -> str:
    """Return filesystem modification time as UTC ISO-8601."""

    return datetime.fromtimestamp(
        path.stat().st_mtime,
        tz=timezone.utc,
    ).isoformat()


def make_object(path: Path) -> dict[str, Any]:
    """Create the initial mechanical description of an artifact."""

    relative = relative_path(path)

    parent = (
        path.parent
        .relative_to(ROOT)
        .as_posix()
    )

    if parent == ".":
        parent = "root"

    return {
        "id": make_id(path),
        "title": title_from_path(path),
        "path": relative,
        "type": object_type(path),
        "date": modified_date(path),

        # These are deliberately conservative defaults.
        # They can later become manually or computationally enriched.
        "status": "documentary",
        "directory": parent,
        "trajectory": None,
        "tags": [],
        "relations": [],
    }


# =====================================================================
# Existing manifest
# =====================================================================

def load_existing_manifest() -> dict[str, Any] | None:
    """Load library.json if it exists and has the expected structure."""

    if not MANIFEST.exists():
        return None

    try:

        with MANIFEST.open(
            "r",
            encoding="utf-8",
        ) as handle:

            data = json.load(handle)

    except (
        json.JSONDecodeError,
        OSError,
    ):
        return None

    if isinstance(data, list):

        data = {
            "objects": data,
        }

    if not isinstance(data, dict):
        return None

    if not isinstance(
        data.get("objects"),
        list,
    ):
        return None

    return data


def manifest_paths(
    manifest: dict[str, Any],
) -> set[str]:
    """Extract represented repository paths."""

    result: set[str] = set()

    for obj in manifest.get(
        "objects",
        [],
    ):

        if not isinstance(
            obj,
            dict,
        ):
            continue

        path = obj.get("path")

        if isinstance(path, str) and path:
            result.add(path)

    return result


# =====================================================================
# Admission
# =====================================================================

def evaluate_manifest(
    manifest: dict[str, Any] | None,
    representatives: list[Path],
) -> tuple[bool, dict[str, Any]]:
    """
    Evaluate the current manifest against the representative corpus.

    Coverage is measured against ARTIFACTS, not raw filesystem objects.
    """

    current = {
        relative_path(path)
        for path in representatives
    }

    if manifest is None:

        return False, {
            "reason": "no valid manifest",
            "coverage": 0.0,
            "current": len(current),
            "represented": 0,
            "missing": len(current),
            "stale": 0,
            "missing_paths": sorted(current),
            "stale_paths": [],
        }

    represented = manifest_paths(
        manifest
    )

    admitted_current = (
        current & represented
    )

    missing = (
        current - represented
    )

    stale = (
        represented - current
    )

    coverage = (
        len(admitted_current) / len(current)
        if current
        else 1.0
    )

    admissible = (
        coverage
        >= ADMISSION_THRESHOLD
    )

    return admissible, {
        "reason": (
            "sufficiently representative"
            if admissible
            else "insufficient coverage"
        ),
        "coverage": coverage,
        "current": len(current),
        "represented": len(admitted_current),
        "missing": len(missing),
        "stale": len(stale),
        "missing_paths": sorted(missing),
        "stale_paths": sorted(stale),
    }


# =====================================================================
# Manifest generation
# =====================================================================

def generate_manifest(
    representatives: list[Path],
) -> dict[str, Any]:
    """Generate a new mechanical manifest."""

    return {
        "schema": 1,
        "generated": datetime.now(
            timezone.utc
        ).isoformat(),
        "generator": "generate-library.py",
        "objects": [
            make_object(path)
            for path in representatives
        ],
    }


def write_manifest(
    manifest: dict[str, Any],
) -> None:
    """
    Write atomically so an interrupted generation does not destroy
    a valid manifest.
    """

    temporary = MANIFEST.with_name(
        MANIFEST.name + ".tmp"
    )

    with temporary.open(
        "w",
        encoding="utf-8",
    ) as handle:

        json.dump(
            manifest,
            handle,
            indent=2,
            ensure_ascii=False,
        )

        handle.write("\n")

    os.replace(
        temporary,
        MANIFEST,
    )


# =====================================================================
# Reporting
# =====================================================================

def report_reduction(
    all_files: list[Path],
    candidates: list[Path],
    representatives: list[Path],
    collapsed: dict[Path, list[Path]],
) -> None:

    collapsed_count = sum(
        len(paths)
        for paths in collapsed.values()
    )

    excluded_count = (
        len(all_files)
        - len(candidates)
    )

    print()
    print("=" * 64)
    print(" LIBRARY CORPUS REDUCTION")
    print("=" * 64)
    print()

    print(
        f"Filesystem files:          {len(all_files)}"
    )

    print(
        f"Candidate representations: {len(candidates)}"
    )

    print(
        f"Representative artifacts:  {len(representatives)}"
    )

    print(
        f"Excluded files:            {excluded_count}"
    )

    print(
        f"Collapsed representations: {collapsed_count}"
    )

    print()


def report_admission(
    decision: str,
    evaluation: dict[str, Any],
) -> None:

    print("=" * 64)
    print(" MANIFEST ADMISSION")
    print("=" * 64)
    print()

    print(
        f"Current artifacts:     "
        f"{evaluation['current']}"
    )

    print(
        f"Represented artifacts: "
        f"{evaluation['represented']}"
    )

    print(
        f"Missing artifacts:     "
        f"{evaluation['missing']}"
    )

    print(
        f"Stale references:      "
        f"{evaluation['stale']}"
    )

    print(
        f"Coverage:              "
        f"{evaluation['coverage']:.1%}"
    )

    print(
        f"Admission threshold:   "
        f"{ADMISSION_THRESHOLD:.1%}"
    )

    print()

    print(
        f"DECISION: {decision}"
    )

    print()


def report_collapses(
    collapsed: dict[Path, list[Path]],
    limit: int = 20,
) -> None:

    if not collapsed:
        return

    print("=" * 64)
    print(" REPRESENTATION COLLAPSES")
    print("=" * 64)
    print()

    items = list(
        collapsed.items()
    )

    for winner, alternatives in items[:limit]:

        print(
            f"ADMIT     {relative_path(winner)}"
        )

        for alternative in alternatives:

            print(
                f"COLLAPSE  {relative_path(alternative)}"
            )

        print()

    remaining = (
        len(items) - limit
    )

    if remaining > 0:

        print(
            f"... {remaining} additional artifact groups"
        )

        print()


def report_missing(
    evaluation: dict[str, Any],
    limit: int = 20,
) -> None:

    missing = evaluation.get(
        "missing_paths",
        [],
    )

    if not missing:
        return

    print("Previously unrepresented:")
    print()

    for path in missing[:limit]:
        print(
            f"    + {path}"
        )

    remaining = (
        len(missing) - limit
    )

    if remaining > 0:

        print(
            f"    ... and {remaining} more"
        )

    print()


# =====================================================================
# Command line
# =====================================================================

def parse_arguments() -> argparse.Namespace:

    parser = argparse.ArgumentParser(
        description=(
            "Generate a conservative public catalogue "
            "for the Library repository."
        )
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "Regenerate even if the current manifest "
            "passes admission."
        ),
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Evaluate and report without writing library.json."
        ),
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help=(
            "Show examples of collapsed representations "
            "and missing artifacts."
        ),
    )

    return parser.parse_args()


# =====================================================================
# Main
# =====================================================================

def main() -> None:

    args = parse_arguments()

    all_files = scan_all_files()

    candidates = scan_candidates(
        all_files
    )

    groups = group_candidates(
        candidates
    )

    representatives, collapsed = (
        select_representatives(
            groups
        )
    )

    report_reduction(
        all_files,
        candidates,
        representatives,
        collapsed,
    )

    existing = (
        load_existing_manifest()
    )

    admissible, evaluation = (
        evaluate_manifest(
            existing,
            representatives,
        )
    )

    if args.verbose:

        report_collapses(
            collapsed
        )

    if admissible and not args.force:

        report_admission(
            "ADMIT EXISTING MANIFEST",
            evaluation,
        )

        print(
            "library.json remains unchanged."
        )

        return

    decision = (
        "FORCE REGENERATE MANIFEST"
        if args.force
        else "REGENERATE MANIFEST"
    )

    report_admission(
        decision,
        evaluation,
    )

    if args.verbose:

        report_missing(
            evaluation
        )

    if args.dry_run:

        print(
            "DRY RUN: library.json was not modified."
        )

        return

    manifest = generate_manifest(
        representatives
    )

    write_manifest(
        manifest
    )

    print(
        f"Wrote {len(representatives)} representative "
        f"artifacts to {MANIFEST.name}."
    )


if __name__ == "__main__":
    main()
