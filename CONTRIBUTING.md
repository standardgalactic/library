# Contributing to the library

This repository is a themed collection of essays, papers, notes, and audio overviews. Follow these rules so files stay searchable and scripts keep working.

## File naming

Use **kebab-case** for all new content files (and for folders), including `.tex` sources:

- Lowercase ASCII letters, digits, and hyphens only
- No spaces, underscores, or mixed capitalization
- Keep the original extension

Examples:

| Avoid | Use |
| --- | --- |
| `A Beautiful Lie.txt` | `a-beautiful-lie.txt` |
| `Action Theory Resolving Problems.txt` | `action-theory-resolving-problems.txt` |
| `AI Balance Debate.txt` | `ai-balance-debate.txt` |
| `RSVP Cosmology - Scalar Field.pdf` | `rsvp-cosmology-scalar-field.pdf` |

Sidecars of the same work must share the same stem: `text-as-substrate.txt`, `text-as-substrate.mp3`, `text-as-substrate.pdf`.

Do not rename tooling (`generate-library.py`, `extract-text.py`, `get-context.sh`) or GitHub Pages entrypoints (`index.html`, `library.html`).

## Metadata (YAML front matter)

Every new `.md` or `.txt` document must start with YAML front matter:

```yaml
---
title: "AI Balance Debate"
author: "Author Name if known"
date: "YYYY-MM-DD"
tags: ["AI", "ethics", "philosophy"]
summary: "A brief summary of the content..."
type: "essay"
---
```

Allowed `type` values: `essay`, `theory`, `audio`, `summary`.

If the author or date is unknown, use `author: "unknown"` and `date: "undated"`.

Do not add front matter to `README.md`, `INDEX.md`, `CONTRIBUTING.md`, `file-list.txt`, or generated/build files.

## Where to put new files

Place work in the folder that matches its **topic**, not its file type. Audio overviews live next to the essay they accompany.

| Folder | Put material here when it is about… |
| --- | --- |
| `analysis/` | Applied AI commentary (autonomy, labour, training practice) |
| `astrophysics/` | Cosmic / stellar physics papers and drafts |
| `baseline/` | Semantic compression and text-as-substrate media |
| `codex-singularis/` | Exported conversation archives |
| `complexity/` | Complexity vs intelligence arguments |
| `computing/` | Computing thought experiments (e.g. magnetic-fluidic) |
| `conceptual-spaces/` | Conceptual spaces and RSVP field essays |
| `current-projects/` | Short project notes and mixed overviews |
| `epistemology/` | Knowledge, memory models, epistemic dynamics |
| `essay/` | Standalone literary/philosophical essays |
| `fonts/` | Typeface files only |
| `geology/` | Geological papers and drafts |
| `infrastructure/` | Systems design (swarms, traffic, compression infrastructure) |
| `mimetic-proxy-theory/` | Mimetic Proxy Theory audio/notes |
| `monograph/` | Identity, constraint, and meaning monograph chapters |
| `physics/` | RSVP / geometric physics and supporting monograph sources |
| `pipeline/` | In-progress monograph pipeline drafts |
| `processing/` | Civilization/coordination as computational process |
| `projects/` | Geometry-of-cognition project writeups |
| `protocols/` | Event-historical frameworks, commitment, mute compulsion |
| `research/` | Research notes, architectures, and literature mappings |
| `resources/` | Shared LaTeX/resource papers |
| `semantic-ladle-theory/` | Semantic Ladle Theory audio/notes |
| `spectral-universality/` | Spectral universality paper sources |
| `system/` | Viewpoint-diversity / system-level papers |
| `vault/` | Political economy of exclusion, affective/Solms mappings |
| `workspace/` | Verification, commitment, measurement, and related notes |
| repository root | Cross-cutting essays that do not fit a theme above |

If nothing fits, add a **new kebab-case folder** and document it in the root `README.md` and in this table.

## Formats and duplicates

Canonical readable text is **`.txt` or `.md`**. Prefer `.md` when the document is already structured Markdown.

Do **not** add a second format of the same work unless it adds information:

| Format | Keep when… |
| --- | --- |
| `.md` / `.txt` | Source of truth for prose |
| `.pdf` | Typeset paper or graphic that is not fully represented in text |
| `.mp3` (+ `.srt` / `.vtt` / `.tsv`) | Audio overview of that stem |
| `.html` | Optional GitHub Pages rendering of an existing text |
| `.tex` / `.bib` | Paper source; do not duplicate as a second essay |
| `.mhtml` / `.mht` | **Avoid.** Browser archives of ChatGPT/pages. If you only have an archive, extract text first (`extract-text.py` or equivalent) and commit the `.txt`. Do not keep `.mhtml` beside an equivalent `.txt`. |

Identical `.md` and `.txt` pairs should be reduced to `.md` only.

LaTeX build artifacts (`.aux`, `.log`, `.out`, `.toc`, `.bbl`, `.blg`, …) should not be treated as library entries.

After adding files, update [INDEX.md](INDEX.md) (or regenerate a catalogue with `python generate-library.py` if you maintain `library.json`).
