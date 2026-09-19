#!/usr/bin/env python3
"""
selftest.py -- prove the guarantees actually hold.

    make selftest

The claim of this repository is that adding a fourth source cannot destroy what
the first three contributed, and that the format cannot drift. That claim is
worth nothing unless it is tested, so this script copies the repository to a
scratch directory, attacks it, and asserts that each protection fires.

It never touches the real working tree. Every case runs in its own throwaway
copy with its own git history, because two of the protections are
history-based.

Exit 0 = all guarantees hold. Exit 1 = one of them is broken; fix the system
before writing any more content.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Callable, List, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
REAL_ROOT = os.path.dirname(HERE)

EXCLUDE_DIRS = {".git", "corpus", "__pycache__", "build_tmp"}
EXCLUDE_EXT = {".pdf"}

GREEN = "\033[32m" if sys.stdout.isatty() else ""
RED = "\033[31m" if sys.stdout.isatty() else ""
DIM = "\033[2m" if sys.stdout.isatty() else ""
OFF = "\033[0m" if sys.stdout.isatty() else ""


# ---------------------------------------------------------------------------
# scratch copies
# ---------------------------------------------------------------------------
def _ignore(dirpath: str, names: List[str]) -> List[str]:
    out = []
    for n in names:
        if n in EXCLUDE_DIRS:
            out.append(n)
        elif os.path.splitext(n)[1] in EXCLUDE_EXT:
            out.append(n)
    return out


def scratch() -> str:
    """A throwaway copy of the repo, with a clean git baseline commit."""
    tmp = tempfile.mkdtemp(prefix="hb-selftest-")
    root = os.path.join(tmp, "repo")
    shutil.copytree(REAL_ROOT, root, ignore=_ignore)
    corpus = os.path.join(root, "registry", "corpus")
    shutil.rmtree(corpus, ignore_errors=True)
    run(root, "git", "init", "-q")
    run(root, "git", "add", "-A")
    run(root, "git", "-c", "user.email=selftest@local", "-c", "user.name=selftest",
        "commit", "-qm", "baseline")
    return root


def run(root: str, *cmd: str) -> Tuple[int, str]:
    p = subprocess.run(list(cmd), cwd=root, capture_output=True, text=True)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def validate(root: str) -> Tuple[int, str]:
    return run(root, sys.executable, os.path.join(root, "tools", "validate.py"))


def build(root: str) -> Tuple[int, str]:
    return run(root, sys.executable, os.path.join(root, "tools", "build_index.py"))


def guard(root: str, *args: str) -> Tuple[int, str]:
    return run(root, sys.executable, os.path.join(root, "tools", "churn_guard.py"),
               *args)


def read(root: str, relpath: str) -> str:
    with open(os.path.join(root, relpath), "r", encoding="utf-8") as fh:
        return fh.read()


def write(root: str, relpath: str, text: str) -> None:
    p = os.path.join(root, relpath)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(text)


def sources_of(root: str, relpath: str) -> List[str]:
    """Read the current @sources list of a topic file."""
    m = re.search(r"^%% @sources:\s*(.+)$", read(root, relpath), re.M)
    assert m, f"{relpath}: no @sources line"
    return [x.strip() for x in m.group(1).split(",") if x.strip()]


def drop_source(root: str, relpath: str, book: str) -> None:
    """Remove one book from both the header and the footer of a topic.

    Written against the file's *current* contents rather than a hard-coded
    sources line: the whole point of the architecture is that a new book can be
    merged in additively, which legitimately changes that line. A test that
    pins the line would break every time the system worked as designed.
    """
    srcs = sources_of(root, relpath)
    assert book in srcs, f"{relpath}: {book} is not among {srcs}"
    kept = [b for b in srcs if b != book]
    t = read(root, relpath)
    t = re.sub(r"^%% @sources:\s*.+$", "%% @sources: " + ", ".join(kept), t,
               count=1, flags=re.M)
    repl = "\\sources{" + ", ".join(kept) + "}"
    # a lambda, not a string: re.sub would read the backslash in "\sources"
    # as the start of an escape sequence in the replacement.
    t = re.sub(r"^\\sources\{[^}]*\}", lambda _m: repl, t, count=1, flags=re.M)
    write(root, relpath, t)


def sub(root: str, relpath: str, old: str, new: str) -> None:
    t = read(root, relpath)
    if old not in t:
        raise AssertionError(f"{relpath}: pattern not found: {old[:60]!r}")
    write(root, relpath, t.replace(old, new, 1))


# ---------------------------------------------------------------------------
# the cases
# ---------------------------------------------------------------------------
def case_baseline(root: str) -> None:
    """The repository as committed must pass its own gate."""
    rc, out = validate(root)
    assert rc == 0, f"baseline validate failed:\n{out[-1500:]}"
    rc, out = build(root)
    assert rc == 0 and "up to date" in out, f"index not reproducible:\n{out}"


SCRATCH_BOOK = "B97"   # never a real register id; see case_additive


def case_additive(root: str) -> None:
    """Registering a new book and filing dossiers must change NO existing file.

    Uses a scratch id rather than B4 because B4 is now a real source in the
    register; the point of the test is the *operation*, not the number.
    """
    before = {p: read(root, p) for p in (
        "main.tex", "style/entry.sty", "style/handbook.cls",
        "topics/c01/T-01-01.tex", "sources/B1/B1-T-01-01.tex",
        "sources/B3/B3-T-01-01.tex", "registry/books.yaml")}

    rc, out = run(root, sys.executable, os.path.join(root, "tools", "new_book.py"),
                  "--id", SCRATCH_BOOK, "--title", "Test Source", "--author", "Nobody",
                  "--year", "2011", "--rank", "primary", "--weight", "85",
                  "--short", "Test Source")
    assert rc == 0, f"new_book failed:\n{out}"

    rc, out = run(root, sys.executable, os.path.join(root, "tools", "new_dossier.py"),
                  "--book", SCRATCH_BOOK, "--topic", "T-01-01",
                  "--locator", "ch.1, pp.1-9", "--unique", "yes")
    assert rc == 0, f"new_dossier failed:\n{out}"

    # books.yaml is append-only: every original line must still be present,
    # in the same order.
    after = read(root, "registry/books.yaml")
    for p, text in before.items():
        if p == "registry/books.yaml":
            continue
        assert read(root, p) == text, f"{p} was modified by an additive operation"
    for line in before["registry/books.yaml"].splitlines():
        if line.strip() and not line.lstrip().startswith("#"):
            assert line in after, f"books.yaml lost a line: {line[:60]}"
    assert f"- id: {SCRATCH_BOOK}" in after, f"{SCRATCH_BOOK} was not registered"
    assert os.path.exists(os.path.join(root, f"sources/{SCRATCH_BOOK}/{SCRATCH_BOOK}-T-01-01.tex")), \
        "dossier was not created"


def case_no_main_edit(root: str) -> None:
    """A new entry reaches the compiled book without editing main.tex."""
    main_before = read(root, "main.tex")
    # never assume an id is free: the tree grows, and a planned scaffold
    # may legitimately occupy T-11-01 by now. Take the next free serial.
    existing = [n for n in (int(m.group(1)) for m in re.finditer(
        r"T-11-(\d\d)", json.dumps(sorted(
            os.listdir(os.path.join(root, "topics", "c11"))))) ) ] \
        if os.path.isdir(os.path.join(root, "topics", "c11")) else []
    serial = (max(existing) + 1) if existing else 1
    tid = "T-11-%02d" % serial
    rc, out = run(root, sys.executable, os.path.join(root, "tools", "new_topic.py"),
                  "--chapter", "c11", "--id", tid,
                  "--title", "Manufactured Indispensability",
                  "--subtitle", "Being needed is a structure",
                  "--sources", "B1", "--status", "draft")
    assert rc == 0, f"new_topic failed:\n{out}"
    rc, out = build(root)
    assert rc == 0, f"build_index failed:\n{out}"

    assert read(root, "main.tex") == main_before, "main.tex was edited"
    idx = read(root, "registry/compiled/index.tex")
    assert f"topics/c11/{tid}" in idx, "the new entry is not in the generated index"
    assert os.path.exists(os.path.join(root, "topics/c11", tid + ".tex"))


def case_r10_protected(root: str) -> None:
    """Dropping a book that contributed UNIQUE material must fail the build."""
    rc, _ = validate(root)
    assert rc == 0, "baseline should pass"
    drop_source(root, "topics/c01/T-01-01.tex", "B1")
    rc, out = validate(root)
    assert rc != 0, "R10 did not fire: a book with unique material was dropped"
    assert "R10" in out, f"expected an R10 error, got:\n{out[-800:]}"


def case_r11_no_dossier(root: str) -> None:
    """Citing a source with no filed dossier must fail."""
    srcs = sources_of(root, "topics/c01/T-01-02.tex")
    sub(root, "topics/c01/T-01-02.tex",
        "%% @sources: " + ", ".join(srcs),
        "%% @sources: " + ", ".join(srcs + ["B9"]))
    rc, out = validate(root)
    assert rc != 0 and ("R11" in out or "R3" in out), \
        f"a citation with no evidence was accepted:\n{out[-800:]}"


def case_r4_secondary(root: str) -> None:
    """An entry sourced only from a secondary source must fail."""
    drop_source(root, "topics/c01/T-01-04.tex", "B1")
    rc, out = validate(root)
    assert rc != 0 and "R4" in out, \
        f"a secondary-only entry was accepted:\n{out[-800:]}"


def case_churn_rewrite(root: str) -> None:
    """A wholesale rewrite of an entry must fail the churn guard."""
    path = "topics/c01/T-01-01.tex"
    text = read(root, path)
    # the scratch rewrite must not inherit the migration's @allow-rewrite
    # sanction -- an unsanctioned rewrite is what this guarantee tests.
    text = "\n".join(l for l in text.splitlines()
                      if not l.startswith("%% @allow-rewrite:"))
    body_start = text.index("\\topic{")
    rewritten = text[:body_start] + (
        "\\topic{T-01-01}{Completely Different Title}{New strapline}\n\n"
        "\\begin{core}\nAn entirely new core paragraph that shares nothing with\n"
        "the original wording whatsoever, written from scratch.\n\\end{core}\n\n"
        "\\begin{mechanism}\nA brand new mechanism section with different content\n"
        "and different sentences throughout.\n\\end{mechanism}\n\n"
        "\\begin{conditions}\nDifferent conditions text entirely.\n\\end{conditions}\n\n"
        "\\begin{application}\n  \\item a different move\n\\end{application}\n\n"
        "\\begin{feedback}\n  \\item a different sign\n\\end{feedback}\n\n"
        "\\begin{failure}\nDifferent failure text entirely.\n\\end{failure}\n\n"
        "\\begin{countermeasures}\n  \\item a different counter\n\\end{countermeasures}\n\n"
        "\\sources{B1, B3}\n\\seesources\n")
    write(root, path, rewritten)
    rc, out = guard(root)
    assert rc != 0, f"churn guard accepted a wholesale rewrite:\n{out}"
    assert "rewritten" in out, f"unexpected guard output:\n{out}"

    # the escape hatch must work when the reason is stated
    write(root, path, rewritten.replace(
        "%% @updated: 2026-09-19",
        "%% @updated: 2026-09-19\n%% @allow-rewrite: superseded framing, "
        "reason recorded in ingest map"))
    rc, out = guard(root)
    assert rc == 0, f"churn guard rejected a reasoned rewrite:\n{out}"


def case_churn_delete(root: str) -> None:
    """Deleting a Layer A dossier must fail the churn guard."""
    os.remove(os.path.join(root, "sources/B1/B1-T-01-02.tex"))
    rc, out = guard(root)
    assert rc != 0, f"churn guard accepted deletion of a dossier:\n{out}"
    assert "sources/" in out, f"unexpected guard output:\n{out}"


def case_r5_slot_order(root: str) -> None:
    """Slots out of canonical order must fail."""
    path = "topics/c01/T-01-03.tex"
    t = read(root, path)
    mech = re.search(r"\\begin\{mechanism\}.*?\\end\{mechanism\}\n", t, re.S).group(0)
    t2 = t.replace(mech, "", 1)
    t2 = t2.replace("\\end{core}\n", "\\end{core}\n\n" + mech, 1)  # still in order
    # now deliberately break it: move `failure` above `feedback`
    lim = re.search(r"\\begin\{failure\}.*?\\end\{failure\}\n", t, re.S).group(0)
    t3 = t.replace(lim, "", 1)
    t3 = t3.replace("\\begin{feedback}", lim + "\\begin{feedback}", 1)
    write(root, path, t3)
    rc, out = validate(root)
    assert rc != 0 and "R5" in out, f"slot order was not enforced:\n{out[-800:]}"


def case_r6_length(root: str) -> None:
    """An entry over the word ceiling must fail."""
    path = "topics/c01/T-01-05.tex"
    t = read(root, path)
    pad = " ".join("word%03d" % i for i in range(800))
    t = t.replace("\\end{mechanism}", pad + "\n\\end{mechanism}", 1)
    write(root, path, t)
    rc, out = validate(root)
    assert rc != 0 and "R6" in out, f"the length ceiling was not enforced:\n{out[-800:]}"


def case_r23_combines(root: str) -> None:
    """R23 -- a case that weaves an entry which does not exist is caught;
    so is a case carrying source-citation apparatus."""
    v, out = validate(root)
    assert v == 0, f"baseline broken: {out}"
    relp = os.path.join("cases", "C-01.tex")
    t = read(root, relp)
    t = t.replace("@combines: T-04-02,", "@combines: T-99-99,", 1)
    assert "T-99-99" in t, "combine edit did not land"
    write(root, relp, t)
    v, out = validate(root)
    assert v != 0 and "R23" in out, f"fake combine not caught: {out[:400]}"
    # restore, then plant forbidden citation apparatus
    t = read(root, relp)
    t = t.replace("@combines: T-99-99,", "@combines: T-04-02,", 1)
    t = t.replace("\\end{lesson}", "\\end{lesson}\n\\sources{B3}", 1)
    write(root, relp, t)
    v, out = validate(root)
    assert v != 0 and "R23" in out, f"\\sources in a case not caught: {out[:400]}"

def case_r7_filler(root: str) -> None:
    """A banned filler phrase must fail."""
    path = "topics/c01/T-01-03.tex"
    t = read(root, path)
    t = t.replace("\\begin{mechanism}", "\\begin{mechanism}\n"
                  "In today's fast-paced world, it is important to note that", 1)
    write(root, path, t)
    rc, out = validate(root)
    assert rc != 0 and "R7" in out, f"filler was not caught:\n{out[-800:]}"


def case_r12_layout(root: str) -> None:
    """A layout command in a content file must fail."""
    path = "topics/c01/T-01-02.tex"
    t = read(root, path)
    t = t.replace("\\end{failure}", "\\end{failure}\n\\vspace{6pt}\\newpage", 1)
    write(root, path, t)
    rc, out = validate(root)
    assert rc != 0 and ("R12" in out or "R13" in out), \
        f"layout smuggling was not caught:\n{out[-800:]}"


def case_r13_tex(root: str) -> None:
    """Broken LaTeX in a content file must fail."""
    path = "topics/c01/T-01-04.tex"
    t = read(root, path)
    t = t.replace("\\end{core}", "\\end{coreX}", 1)
    write(root, path, t)
    rc, out = validate(root)
    assert rc != 0 and "R13" in out, f"bad LaTeX was not caught:\n{out[-800:]}"

    write(root, path, t.replace("\\end{coreX}", "\\end{core}"))
    sub(root, path, "\\begin{core}", "\\begin{core}\nA 50 & 50 split of the cost.")
    rc, out = validate(root)
    assert rc != 0 and "R13" in out, f"unescaped special was not caught:\n{out[-800:]}"

    sub(root, path, "\nA 50 & 50 split of the cost.", "")
    sub(root, path, "\\begin{core}", "\\begin{core}\nA caf\u00e9 near the \u2014 exit.")
    rc, out = validate(root)
    assert rc != 0 and "R13" in out, f"non-ASCII was not caught:\n{out[-800:]}"

    sub(root, path, "\nA caf\u00e9 near the \u2014 exit.", "")
    sub(root, path, "\\begin{core}", "\\begin{core}\nRoughly 50% of the time.")
    rc, out = validate(root)
    assert rc != 0 and "R13" in out, \
        f"an accidental comment was not caught:\n{out[-800:]}"


def case_r14_stale(root: str) -> None:
    """A stale generated index must fail."""
    sub(root, "topics/c01/T-01-01.tex",
        "%% @title: The Five-Percent Premise",
        "%% @title: The Five Percent Premise Renamed")
    rc, out = validate(root)
    assert rc != 0 and "R14" in out, f"stale index was not caught:\n{out[-800:]}"
    rc, out = build(root)
    assert rc == 0
    rc, out = validate(root)
    assert rc == 0, f"still failing after regeneration:\n{out[-800:]}"


def case_overwrite_refused(root: str) -> None:
    """Scaffolds must refuse to overwrite."""
    rc, out = run(root, sys.executable, os.path.join(root, "tools", "new_dossier.py"),
                  "--book", "B1", "--topic", "T-01-01")
    assert rc != 0 and "append-only" in out, \
        f"new_dossier overwrote an existing file:\n{out}"
    rc, out = run(root, sys.executable, os.path.join(root, "tools", "new_book.py"),
                  "--id", "B1", "--title", "X")
    assert rc != 0, f"new_book reused an existing id:\n{out}"


def case_r18_dangling_input(root: str) -> None:
    """A dangling \\input must fail, and an unreachable entry must fail."""
    sub(root, "main.tex", "\\input{back/colophon}",
        "\\input{back/colophon}\n\\input{back/does-not-exist}")
    rc, out = validate(root)
    assert rc != 0 and "R18" in out, f"a dangling \\input was accepted:\n{out[-800:]}"

    sub(root, "main.tex", "\n\\input{back/does-not-exist}", "")
    rc, out = validate(root)
    assert rc == 0, f"still failing after the dangling input was removed:\n{out[-800:]}"

    # an entry pointed at the wrong chapter becomes unreachable from the index
    sub(root, "topics/c01/T-01-02.tex", "%% @chapter: c01", "%% @chapter: c09")
    rc, _ = build(root)
    assert rc == 0
    rc, out = validate(root)
    assert rc != 0 and ("R18" in out or "R2" in out), \
        f"an unreachable entry was accepted:\n{out[-800:]}"


# ---------------------------------------------------------------------------
CASES: List[Tuple[str, str, Callable[[str], None]]] = [
    ("baseline",       "the repo passes its own gate",                       case_baseline),
    ("additive",       "adding B4 changes no existing file",                 case_additive),
    ("no-main-edit",   "a new entry reaches the book without editing main",  case_no_main_edit),
    ("R10",            "unique knowledge cannot be dropped",                 case_r10_protected),
    ("R11",            "a citation with no dossier fails",                   case_r11_no_dossier),
    ("R4",             "a secondary source cannot originate",                case_r4_secondary),
    ("churn:rewrite",  "a wholesale rewrite fails",                          case_churn_rewrite),
    ("churn:delete",   "deleting a dossier fails",                           case_churn_delete),
    ("R5",             "slot order is enforced",                             case_r5_slot_order),
    ("R6",             "the length ceiling is enforced",                     case_r6_length),
    ("R7",             "filler phrases are caught",                          case_r7_filler),
    ("R12",            "layout commands are kept out of content",            case_r12_layout),
    ("R13",            "broken LaTeX is caught",                             case_r13_tex),
    ("R14",            "a stale generated index is caught",                  case_r14_stale),
    ("R18",            "dangling \\input and orphans are caught",            case_r18_dangling_input),
    ("R23",             "case lattice integrity is enforced",                 case_r23_combines),
    ("scaffold",       "scaffolds refuse to overwrite",                      case_overwrite_refused),
]


def main() -> int:
    only = sys.argv[1:] or None
    passed = failed = 0
    for name, desc, fn in CASES:
        if only and name not in only:
            continue
        root = scratch()
        try:
            fn(root)
            print(f"  {GREEN}PASS{OFF} {name:<16} {DIM}{desc}{OFF}")
            passed += 1
        except AssertionError as exc:
            print(f"  {RED}FAIL{OFF} {name:<16} {desc}\n        {exc}")
            failed += 1
        except Exception as exc:                      # pragma: no cover
            print(f"  {RED}ERROR{OFF} {name:<16} {desc}\n        {type(exc).__name__}: {exc}")
            failed += 1
        finally:
            shutil.rmtree(os.path.dirname(root), ignore_errors=True)
    print()
    if failed:
        print(f"{RED}selftest: {failed} guarantee(s) broken{OFF}, {passed} held")
        return 1
    print(f"{GREEN}selftest: all {passed} guarantees hold{OFF}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
