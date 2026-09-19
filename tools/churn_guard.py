#!/usr/bin/env python3
"""
churn_guard.py -- mechanical enforcement of "never rewrite a whole file".

This is the rule that protects Book 1 from Book 4. It is the one rule an
automated writer is most likely to break by accident, so it is checked by a
program rather than by memory.

    make guard                    # working tree vs HEAD
    make guard BASE=origin/main   # vs any other ref

What it refuses:

  * a content file whose lines changed by more than --threshold (default 40%)
    unless the new version adds  '@allow-rewrite: <reason>'  to its header;
  * any deletion of a file under sources/ -- Layer A is append-only and
    immutable. A superseded dossier is marked '@status: retired', never
    removed;
  * any deletion of a topic file, which is almost always an accident.

Deliberate rewrites are allowed: add the header key, state the reason, and the
guard steps aside. The point is that it must be a decision, not a side effect.
"""

from __future__ import annotations

import argparse
import difflib
import os
import re
import subprocess
import sys
from typing import List, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hb_lib import DIR_SOURCES, DIR_TOPICS, ROOT, rel   # noqa: E402

CONTENT_PREFIXES = ("topics/", "sources/", "front/", "back/")
HEADER_LINE_RE = re.compile(r"^\s*%%\s*@[a-z][a-z0-9-]*\s*:")


def git(*args: str) -> Tuple[int, str]:
    p = subprocess.run(["git"] + list(args), cwd=ROOT,
                       capture_output=True, text=True)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def changed_files(base: str) -> List[Tuple[str, str]]:
    """Return [(status, path)] for content files differing from base."""
    rc, out = git("diff", "--name-status", base, "--", *CONTENT_PREFIXES)
    if rc != 0:
        # base may not exist yet; fall back to the whole working tree
        rc, out = git("ls-files", "-mo", "--exclude-standard",
                      "--", *CONTENT_PREFIXES)
        return [("?", f) for f in out.split() if f.endswith(".tex")]
    res = []
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        st, path = parts[0], parts[-1]
        if path.endswith(".tex") and not path.startswith("registry/compiled/"):
            res.append((st[0], path))
    return res


def show(base: str, path: str) -> str:
    rc, out = git("show", f"{base}:{path}")
    return out if rc == 0 else ""


def churn(old: str, new: str) -> float:
    """How much of a file was replaced, 0.0 (untouched) to 1.0 (all new).

    Two measures, and the larger one wins:

      * LINE churn  -- catches structural reorganisation.
      * PROSE churn -- catches content replacement.

    Prose churn is the one that matters, and line churn alone is not enough:
    the entry DSL contributes ~15 identical skeleton lines (\\begin{core},
    \\end{core}, \\sources{}, ...) to every file, so a file whose every word
    was replaced can still look 60% similar line-by-line. Measuring the word
    stream with the LaTeX stripped removes that blind spot.
    """
    a = [l.strip() for l in old.splitlines() if l.strip()]
    b = [l.strip() for l in new.strip().splitlines() if l.strip()]
    if not a and not b:
        return 0.0
    if not a:
        return 1.0
    line_churn = 1.0 - difflib.SequenceMatcher(None, a, b).ratio()

    from hb_lib import strip_latex
    wa = _words(strip_latex(_body_only(old)))
    wb = _words(strip_latex(_body_only(new)))
    if not wa:
        prose_churn = 1.0 if wb else 0.0
    else:
        prose_churn = 1.0 - difflib.SequenceMatcher(None, wa, wb).ratio()
    return max(line_churn, prose_churn)


def _body_only(text: str) -> str:
    """Drop the '%% @...' header block so metadata edits do not count as prose."""
    out, in_header = [], False
    for line in text.splitlines():
        if HEADER_LINE_RE.match(line):
            in_header = True
            continue
        if in_header and (line.startswith("%%") or not line.strip()):
            # keep skipping banner/comment lines directly attached to the header
            if line.startswith("%%") and not line.strip("% "):
                in_header = False
                out.append(line)
            continue
        in_header = False
        out.append(line)
    return "\n".join(out)


def _words(s: str) -> List[str]:
    return [w for w in re.split(r"\s+", s) if any(c.isalnum() for c in w)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="HEAD",
                    help="git ref to compare against (default HEAD)")
    ap.add_argument("--threshold", type=float, default=0.40,
                    help="max allowed line churn before a reason is required")
    args = ap.parse_args()

    rc, _ = git("rev-parse", "--git-dir")
    if rc != 0:
        print("churn_guard: not a git repository -- skipped")
        return 0

    errors: List[str] = []
    warns: List[str] = []
    seen = 0

    for st, path in changed_files(args.base):
        seen += 1
        if st == "D":
            if path.startswith("sources/"):
                errors.append(f"{path}: DELETED. sources/ is append-only. "
                              "Restore it and set '@status: retired' instead.")
            elif path.startswith("topics/"):
                errors.append(f"{path}: DELETED. Entries are retired, not "
                              "removed; their knowledge is referenced elsewhere.")
            continue

        abspath = os.path.join(ROOT, path)
        if not os.path.exists(abspath):
            continue
        with open(abspath, "r", encoding="utf-8") as fh:
            new = fh.read()
        old = show(args.base, path)
        if not old:
            continue                      # brand new file: nothing to protect
        ratio = churn(old, new)
        if ratio > args.threshold:
            if "@allow-rewrite:" in new:
                warns.append(f"{path}: {ratio:.0%} rewritten, reason given "
                             "(@allow-rewrite) -- accepted")
            else:
                errors.append(
                    f"{path}: {ratio:.0%} of lines rewritten "
                    f"(threshold {args.threshold:.0%}). Surgical edits only; "
                    "new material goes in NEW files (sources/<book>/ for a new "
                    "book, a new topic for a new idea). If a full rewrite is "
                    "genuinely intended, add '@allow-rewrite: <reason>' to the "
                    "header block.")

    print(f"churn_guard: {seen} content file(s) changed vs {args.base}")
    for w in warns:
        print("  ~ " + w)
    for e in errors:
        print("  ! " + e)
    if errors:
        print(f"\nFAILED: {len(errors)} destructive change(s)")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
