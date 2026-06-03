#!/usr/bin/env python3

import re
import difflib
import pathlib
import sys

REPLACEMENT = "Flyxion"
TARGET = "flyxion"

LOG_FILE = "flyxion_corrections.log"
CANDIDATE_LOG = "flyxion_candidates.log"
APPROVED_FILE = ".flyxion_approved_variants"

extensions = {".json", ".srt", ".tsv", ".txt", ".vtt"}

# ------------------------------------------------------------------
# INTERACTIVE MODES
# ------------------------------------------------------------------

def get_mode():
    try:
        if sys.stdin.isatty():
            mode = input(
                "Treat 'affliction/infliction' as (n)ame → replace with Flyxion, "
                "or (c)oncept → leave untouched? [n/c]: "
            ).strip().lower()
        else:
            with open("/dev/tty") as tty:
                mode = tty.readline().strip().lower()
    except Exception:
        mode = "c"

    return "n" if mode == "n" else "c"


mode = get_mode()
REPLACE_PROTECTED = (mode == "n")

# ------------------------------------------------------------------
# VARIANT DATABASE
# ------------------------------------------------------------------

KNOWN_VARIANTS = {
    "FLECTION",
    "FLICTION",
    "Flaccion",
    "Flakirin",
    "Flakiron",
    "Flaxian",
    "Flaxion",
    "Flaxon",
    "Flaxson",
    "Fleckession",
    "Fleckstown",
    "Flection",
    "Flectional",
    "Fleekshin",
    "Fleishness",
    "Fleishon",
    "Fleixing",
    "Fleksheen",
    "Flekshun",
    "Fleksian",
    "Fleksion",
    "Flekzion",
    "Fletchian",
    "Fletchion",
    "Fletian",
    "Fletuchin",
    "Flexian",
    "Flexion",
    "Flexition",
    "Flexiton",
    "Flexivision",
    "Flextion",
    "Flexumian",
    "Fliccine",
    "Flickditschian",
    "Flickenden",
    "Flickening",
    "Flickession",
    "Flickian",
    "Flickiewen",
    "Flickishin",
    "Flicklian",
    "Flickpnam",
    "Flickrinnian",
    "Flickshahn",
    "Flicksham",
    "Flickshan",
    "Flickshane",
    "Flickshank",
    "Flickshanth",
    "Flicksheen",
    "Flicksheens",
    "Flickshen",
    "Flickshian",
    "Flickshin",
    "Flickshion",
    "Flickshon",
    "Flicksion",
    "Flickson",
    "Flickstahn",
    "Flickstein",
    "Flickxion",
    "Flickzion",
    "Fliction",
    "Flictionon",
    "Flijnen",
    "Flikshun",
    "Flikstian",
    "Flikxion",
    "Flikzion",
    "Flinchin",
    "Flipchin",
    "Flippshen",
    "Flipschen",
    "Flischin",
    "Flisham",
    "Flishan",
    "Flishen",
    "Flitchian",
    "Flitchin",
    "Flitchinan",
    "Flitian",
    "Flitschen",
    "Flitscheon",
    "Flitschernard",
    "Flitschian",
    "Flixam",
    "Flixan",
    "Flixbyan",
    "Flixchan",
    "Flixchen",
    "Flixen",
    "Flixgen",
    "Flixheen",
    "Flixia",
    "Flixian",
    "Flixidan",
    "Flixie",
    "Flixien",
    "Flixim",
    "Flixing",
    "Flixingen",
    "Flixion",
    "Flixionne",
    "Flixium",
    "Flixjan",
    "Flixman",
    "Flixon",
    "Flixson",
    "Flixten",
    "Flixtion",
    "Flixuen",
    "Flixxion",
    "Flixxon",
    "Flixyon",
    "Fluxian",
    "Fluxin",
    "Fluxion",
    "Fluxium",
    "Fluxunian",
    "Flykem",
    "Flykshion",
    "Flykshun",
    "Flyxen",
    "Flyxian",
    "Flyxionn",
    "Flyxionne",
    "Flyxionu",
    "Flyzion",
    "Fouiches",
    "Fuchin",
    "Fugchin",
    "Slikin",
}

QUESTIONABLE_VARIANTS = {
    "Felican",
    "Felician",
    "Felictian",
    "Felixian",
    "Flagellian",
    "Floodioxin",
    "Fletcher",
    "Fletchen",
    "Folicurian",
}

KNOWN_VARIANTS_RE = re.compile(
    r'(?i)(?<![A-Za-z])(' +
    '|'.join(
        re.escape(v)
        for v in sorted(
            KNOWN_VARIANTS | QUESTIONABLE_VARIANTS,
            key=len,
            reverse=True
        )
    ) +
    r')(?![A-Za-z])'
)

# ------------------------------------------------------------------
# APPROVAL DATABASE
# ------------------------------------------------------------------

approved_variants = set()

if pathlib.Path(APPROVED_FILE).exists():
    approved_variants = {
        line.strip()
        for line in pathlib.Path(APPROVED_FILE).read_text(
            encoding="utf-8",
            errors="ignore"
        ).splitlines()
        if line.strip()
    }

decision_cache = {}

# ------------------------------------------------------------------
# PROTECTED WORDS
# ------------------------------------------------------------------

PROTECTED = {
    "affliction": "__PROTECTED_AFFLICTION__",
    "Affliction": "__PROTECTED_CAP_AFFLICTION__",
    "infliction": "__PROTECTED_INFLICTION__",
    "Infliction": "__PROTECTED_CAP_INFLICTION__",
} if not REPLACE_PROTECTED else {}

FORCE_REPLACE = {"affliction", "infliction"} if REPLACE_PROTECTED else set()

# ------------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------------

def strip_invisible_chars(text):
    return re.sub(r'[\u200B-\u200D\uFEFF]', '', text)


def protect_real_words(text):
    for word, marker in PROTECTED.items():
        text = re.sub(
            rf'(?<![A-Za-z]){re.escape(word)}(?![A-Za-z])',
            marker,
            text
        )
    return text


def restore_real_words(text):
    for word, marker in PROTECTED.items():
        text = text.replace(marker, word)
    return text


def ask_about_variant(word):

    if word in approved_variants:
        return True

    if word in decision_cache:
        return decision_cache[word]

    prompt = (
        f"\nQuestionable Flyxion variant detected:\n"
        f"    {word}\n\n"
        f"Replace with Flyxion?\n"
        f"[y] yes  [n] no  [a] always  [q] quit : "
    )

    try:
        if sys.stdin.isatty():
            answer = input(prompt).strip().lower()
        else:
            with open("/dev/tty") as tty:
                print(prompt, end="", flush=True)
                answer = tty.readline().strip().lower()
    except Exception:
        answer = "n"

    if answer == "q":
        sys.exit(0)

    if answer == "a":
        approved_variants.add(word)

        with open(APPROVED_FILE, "a", encoding="utf-8") as f:
            f.write(word + "\n")

        decision_cache[word] = True
        return True

    decision_cache[word] = (answer == "y")
    return decision_cache[word]


def replace_known_variants(text):

    def repl(match):

        word = match.group(0)

        if word in QUESTIONABLE_VARIANTS:
            if ask_about_variant(word):
                return REPLACEMENT
            return word

        return REPLACEMENT

    return KNOWN_VARIANTS_RE.sub(repl, text)


# ------------------------------------------------------------------
# FUZZY MATCHER
# ------------------------------------------------------------------

def log_candidate(word):

    with open(CANDIDATE_LOG, "a", encoding="utf-8") as f:
        f.write(word + "\n")


def close_to_flyxion(word):

    w = word.lower()

    if w == TARGET:
        return False

    if w in FORCE_REPLACE:
        return True

    if len(w) < 5 or len(w) > 16:
        return False

    prefixes = (
        "fl",
        "fly",
        "fli",
        "fle",
        "flu",
    )

    if not any(w.startswith(p) for p in prefixes):
        return False

    score = difflib.SequenceMatcher(
        None,
        w,
        TARGET
    ).ratio()

    if 0.60 <= score < 0.75:
        log_candidate(word)

    return score >= 0.75


def fuzzy_replace_line(line):

    def repl(match):

        word = match.group(0)

        if close_to_flyxion(word):
            return REPLACEMENT

        return word

    return re.sub(
        r'\b[A-Za-z]{5,16}\b',
        repl,
        line
    )

# ------------------------------------------------------------------
# MAIN NORMALIZATION
# ------------------------------------------------------------------

def normalize_text_preserving_layout(text):

    text = strip_invisible_chars(text)

    text = protect_real_words(text)

    text = replace_known_variants(text)

    text = (
        text.replace("oblocosm", "oblicosm")
            .replace("Oblocosm", "Oblicosm")
    )

    lines = text.splitlines(keepends=True)

    lines = [
        fuzzy_replace_line(line)
        for line in lines
    ]

    text = ''.join(lines)

    text = restore_real_words(text)

    return text

# ------------------------------------------------------------------
# FILE PASS
# ------------------------------------------------------------------

with open(LOG_FILE, "a", encoding="utf-8") as log:

    log.write("\nFlyxion correction pass\n")
    log.write("----------------------------------------\n")

    for path in pathlib.Path(".").rglob("*"):

        if path.suffix.lower() not in extensions:
            continue

        if "backup_" in str(path):
            continue

        try:
            original = path.read_text(
                encoding="utf-8",
                errors="ignore"
            )
        except Exception:
            continue

        corrected = normalize_text_preserving_layout(original)

        if corrected != original:

            path.write_text(
                corrected,
                encoding="utf-8"
            )

            print(f"Updated: {path}")

            log.write(f"Updated: {path}\n")

        else:

            log.write(f"[no changes] {path}\n")

    log.write("----------------------------------------\n")
    log.write("Done.\n")

