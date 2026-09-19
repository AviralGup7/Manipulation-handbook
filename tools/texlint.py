#!/usr/bin/env python3
"""
texlint.py -- a structural LaTeX checker.

There is no TeX engine in every environment this repo gets edited in (CI
sandboxes, phones, a browser editor). This is the gate that stands in for a
first compile pass: it catches the classes of error that actually break
pdflatex, so a build failure is rare rather than routine.

Checks
  1. balanced braces (respecting \\{ \\} and comment lines)
  2. \\begin{env} / \\end{env} pairing and correct nesting
  3. environments that are neither standard nor defined by style/entry.sty
  4. unescaped # & _ in prose
  5. odd number of unescaped $ on a line
  6. non-ASCII characters (use LaTeX sequences, not UTF-8 punctuation)
  7. \\item outside a list environment
  8. layout commands smuggled into content files
  9. unterminated \\begin{...} at end of file
"""

from __future__ import annotations

import re
import sys
from typing import List, Tuple

# Environments provided by LaTeX base + the packages we load + entry.sty.
KNOWN_ENVS = {
    "document", "center", "flushleft", "flushright", "minipage", "picture",
    "itemize", "enumerate", "description", "list", "trivlist", "quote",
    "quotation", "verse", "verbatim", "tabular", "tabular*", "array",
    "table", "figure", "titlepage", "abstract", "lrbox", "sloppypar",
    "thebibliography", "appendix", "filecontents", "comment",
    # entry.sty
    "hbbox", "core", "mechanism", "tells", "moves", "counters", "limits",
    "field", "distilled", "unique", "terms", "quotable",
    "partblurb", "chapterblurb",
}

LIST_ENVS = {"itemize", "enumerate", "description", "list", "trivlist",
             "thebibliography",
             # entry.sty slots that open a list internally
             "tells", "moves", "counters", "distilled", "unique", "terms"}

# Layout commands that must never appear in a content file (rule R12).
BANNED_LAYOUT = [
    r"\vspace", r"\hspace", r"\newpage", r"\clearpage", r"\pagebreak",
    r"\fontsize", r"\setlength", r"\addtolength", r"\pagestyle",
    r"\thispagestyle", r"\textcolor", r"\color", r"\colorbox", r"\fcolorbox",
    r"\newcommand", r"\renewcommand", r"\providecommand", r"\newenvironment",
    r"\makeatletter", r"\makeatother", r"\begin{center}", r"\rule",
    r"\enlargethispage", r"\markboth", r"\addcontentsline", r"\setcounter",
]

Issue = Tuple[str, int, str]   # (severity, line, message)


def _strip_comment(line: str) -> str:
    out, i = [], 0
    while i < len(line):
        c = line[i]
        if c == "\\" and i + 1 < len(line):
            out.append(line[i:i + 2])
            i += 2
            continue
        if c == "%":
            break
        out.append(c)
        i += 1
    return "".join(out)


def lint_text(text: str, fname: str = "<string>",
              skip_layout: bool = False) -> List[Issue]:
    """skip_layout=True for front matter and style files, which legitimately
    contain \\vspace, \\rule, \\begin{center} and friends."""
    issues: List[Issue] = []
    depth = 0
    stack: List[Tuple[str, int]] = []
    list_depth = 0

    for n, raw in enumerate(text.splitlines(), start=1):
        line = _strip_comment(raw)
        if not line.strip():
            continue

        # 0. accidental comment: an unescaped % AFTER prose silently deletes
        #    the rest of the line. A line that STARTS with % is a real comment.
        pre = raw.lstrip()
        if not pre.startswith("%"):
            mm = re.search(r"(?<!\\)%(.*)$", raw)
            if mm and mm.group(1).strip():
                issues.append(("error", n,
                               "unescaped '%' after text -- LaTeX discards "
                               "everything after it. Write \\% instead: "
                               f"...{raw.strip()[:60]}"))

        # 6. non-ASCII -------------------------------------------------
        for ch in line:
            if ord(ch) > 126:
                issues.append(("error", n,
                               f"non-ASCII character U+{ord(ch):04X} ({ch!r}); "
                               "use a LaTeX sequence instead"))
                break

        # 4. unescaped specials ---------------------------------------
        for pat, name in ((r"(?<!\\)#", "'#'"),
                          (r"(?<!\\)&", "'&'"),
                          (r"(?<!\\)_", "'_'")):
            m = re.search(pat, line)
            if m:
                ctx = line[max(0, m.start() - 25):m.start() + 25].strip()
                issues.append(("error", n,
                               f"unescaped {name} in text: ...{ctx}..."))

        # 5. math-mode $ parity ---------------------------------------
        dollars = len(re.findall(r"(?<!\\)(?<!\$)\$(?!\$)", line))
        if dollars % 2:
            issues.append(("error", n,
                           f"odd number of unescaped '$' ({dollars}) "
                           "-- math mode left open"))

        # 1. braces ---------------------------------------------------
        for m in re.finditer(r"(?<!\\)(\{|\})", line):
            depth += 1 if m.group(1) == "{" else -1
            if depth < 0:
                issues.append(("error", n, "extra '}' -- brace depth went negative"))
                depth = 0

        # 2/3/9. environments -----------------------------------------
        for m in re.finditer(r"\\(begin|end)\{([^}]*)\}", line):
            kind, env = m.group(1), m.group(2)
            if env not in KNOWN_ENVS:
                issues.append(("error", n,
                               f"unknown environment '{env}' -- not in LaTeX "
                               "base nor defined by style/entry.sty"))
            if kind == "begin":
                stack.append((env, n))
                if env in LIST_ENVS:
                    list_depth += 1
            else:
                if not stack:
                    issues.append(("error", n, f"\\end{{{env}}} with no open environment"))
                else:
                    top, tline = stack.pop()
                    if top != env:
                        issues.append(("error", n,
                                       f"\\end{{{env}}} closes \\begin{{{top}}} "
                                       f"opened on line {tline}"))
                    if top in LIST_ENVS:
                        list_depth -= 1

        # 7. \item outside a list --------------------------------------
        if re.search(r"^\s*\\item\b", line) and list_depth == 0:
            issues.append(("error", n, "\\item outside any list environment"))

        # 8. layout smuggling ------------------------------------------
        if not skip_layout:
            for cmd in BANNED_LAYOUT:
                if cmd in line:
                    issues.append(("error", n,
                                   f"layout command {cmd} in a content file "
                                   "(rule R12: layout lives in style/ only)"))

    if depth != 0:
        issues.append(("error", 0,
                       f"unbalanced braces at end of file (depth {depth})"))
    for env, n in stack:
        issues.append(("error", n, f"\\begin{{{env}}} never closed"))
    return issues


def lint_file(path: str) -> List[Issue]:
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return lint_text(fh.read(), path)


def main(argv: List[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    bad = 0
    for p in argv:
        issues = lint_file(p)
        if issues:
            bad += 1
            print(f"{p}")
            for sev, n, msg in issues:
                print(f"  {sev}:{n}: {msg}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
