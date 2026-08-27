#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: ./cleanup-minor-errors.sh [--apply]

Without --apply, reports what would change. With --apply, it:
  - deletes tracked text files containing the whole word "oblicosm"
  - removes invalid `date: "undated"` front-matter fields
  - removes mechanically generated `summary:` front-matter fields
  - protects a known LaTeX fragment from Jekyll/Liquid parsing
  - normalizes line endings, trailing whitespace, blank-line runs, and EOF newlines

The script never commits or pushes changes.
EOF
}

apply=false
case "${1:-}" in
  "") ;;
  --apply) apply=true ;;
  -h|--help) usage; exit 0 ;;
  *) usage >&2; exit 2 ;;
esac

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || {
  echo "error: run this script inside a Git repository" >&2
  exit 1
}

repo_root=$(git rev-parse --show-toplevel)
script_rel=$(realpath --relative-to="$repo_root" "${BASH_SOURCE[0]}")

mapfile -d '' oblicosm_candidates < <(
  git grep -Ilzi -w -- 'oblicosm' -- 2>/dev/null || true
)

oblicosm_files=()
for file in "${oblicosm_candidates[@]}"; do
  [[ "$file" == "$script_rel" ]] || oblicosm_files+=("$file")
done

mapfile -d '' document_files < <(
  git ls-files -z -- '*.txt' '*.md'
)

echo "Tracked text files containing the word 'oblicosm': ${#oblicosm_files[@]}"
if ((${#oblicosm_files[@]})); then
  printf '  delete: %s\n' "${oblicosm_files[@]}"
fi

echo "Tracked .txt/.md files eligible for conservative cleanup: ${#document_files[@]}"

if [[ "$apply" != true ]]; then
  echo
  echo "Preview only; no files were changed. Run with --apply to proceed."
  exit 0
fi

if ((${#oblicosm_files[@]})); then
  git rm -- "${oblicosm_files[@]}"
fi

for file in "${document_files[@]}"; do
  [[ -f "$file" ]] || continue

  # Work byte-for-byte so unusual Unicode prose is preserved.
  perl -0777 -pi -e '
    s/\r\n?/\n/g;
    s/^\h*date:\h*["'"'"']?undated["'"'"']?\h*\n//gmi;
    s/^summary:\h*.*\n//gm;
    s#\Q{{figures/}{images/}}\E#{% raw %}{{figures/}{images/}}{% endraw %}#g
      unless index($_, "{% raw %}{{figures/}{images/}}{% endraw %}") >= 0;
    s/[\t ]+\n/\n/g;
    s/\n{4,}/\n\n\n/g;
    s/\n*\z/\n/;
  ' -- "$file"
done

echo
echo "Cleanup applied. Review before committing:"
echo "  git status --short"
echo "  git diff --check"
echo "  git diff --stat"
echo
echo "The script did not commit or push anything."

