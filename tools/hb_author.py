#!/usr/bin/env python3
"""
hb_author.py -- authoring helpers used when writing entries in batches.

Not part of the build. It exists so that content can be written in reviewed
batches without hand-copying the header contract every time, and so the header
format has exactly one implementation.

    from hb_author import topic, dossier

    topic("T-02-01", "c02", 10, "Affect Control", "Subtitle",
          sources=["B3"],
          slots=[("core", "..."), ("mechanism", "..."),
                 ("feedback", ["...", "..."]), ...],
          seealso="T-02-03")

    dossier("B3", "T-02-01", "Affect Control", "Law 39, pp. 325--332",
            distilled=["...", "..."],
            unique=["..."],
            terms=[r"\\emph{...} --- definition"])

Both refuse to overwrite an existing file unless force=True. That is
deliberate: overwriting is how Layer A gets destroyed.
"""

from __future__ import annotations

import os
import sys
from typing import Dict, List, Optional, Sequence, Tuple, Union

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hb_lib import DIR_SOURCES, DIR_TOPICS, rel   # noqa: E402

TODAY = os.environ.get("HB_DATE", "2026-09-19")

LIST_SLOTS = ("application", "feedback", "countermeasures", "distilled", "unique", "terms")

TOPIC_HEADER = """\
%% =====================================================================
%%  {tid}  {title}
%%  -------------------------------------------------------------------
%%  One idea per file. Core is mandatory. Slots in canonical order.
%%  Max 700 words. No layout commands. No filler. New source material
%%  for this entry goes in sources/<BOOK>/{tid}.tex -- never by
%%  rewriting this file (docs/RULES.md R0.1).
%% =====================================================================
%% @kind: topic
%% @id: {tid}
%% @title: {title}
%% @subtitle: {subtitle}
%% @chapter: {chapter}
%% @order: {order}
%% @status: {status}
%% @sources: {sources}
%% @updated: {updated}
"""

DOSSIER_HEADER = """\
%% =====================================================================
%%  {book}-{tid} -- what {book} contributes to "{title}"
%%  -------------------------------------------------------------------
%%  LAYER A: APPEND-ONLY. Written once, then left alone. Material found
%%  only here sits in the `unique` slot and is protected by rule R10.
%% =====================================================================
%% @kind: source
%% @id: {book}-{tid}
%% @book: {book}
%% @topic: {tid}
%% @locator: {locator}
%% @status: {status}
%% @unique: {unique}
%% @integrated: {integrated}
%% @updated: {updated}
"""


def _emit_slots(slots: Sequence[Tuple[str, Union[str, List[str]]]]) -> List[str]:
    out: List[str] = []
    for name, body in slots:
        if isinstance(body, (list, tuple)):
            if name not in LIST_SLOTS:
                raise ValueError(f"slot {name!r} takes prose, not a list")
            out.append(f"\\begin{{{name}}}")
            out.extend(f"  \\item {b}" for b in body)
            out.append(f"\\end{{{name}}}")
        else:
            out.append(f"\\begin{{{name}}}")
            out.append(body)
            out.append(f"\\end{{{name}}}")
    return out


def topic(tid: str, chapter: str, order: int, title: str, subtitle: str,
          sources: Sequence[str],
          slots: Sequence[Tuple[str, Union[str, List[str]]]],
          seealso: str = "", status: str = "stable", updated: str = TODAY,
          force: bool = False) -> str:
    srcs = ", ".join(sources)
    path = os.path.join(DIR_TOPICS, chapter, f"{tid}.tex")
    if os.path.exists(path) and not force:
        raise FileExistsError(f"refusing to overwrite {rel(path)} (force=True to override)")
    parts = [TOPIC_HEADER.format(tid=tid, title=title, subtitle=subtitle,
                                 chapter=chapter, order=order, status=status,
                                 sources=srcs, updated=updated)]
    parts.append(f"\\topic{{{tid}}}{{{title}}}{{{subtitle}}}\n")
    parts.extend(_emit_slots(slots))
    parts.append("")
    parts.append(f"\\sources{{{srcs}}}")
    parts.append("\\seesources")
    if seealso:
        parts.append(f"\\seealso{{{seealso}}}")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(parts) + "\n")
    return rel(path)


def dossier(book: str, tid: str, title: str, locator: str,
            distilled: Sequence[str],
            unique: Optional[Sequence[str]] = None,
            terms: Optional[Sequence[str]] = None,
            quotable: Optional[str] = None,
            status: str = "distilled", integrated: str = "yes",
            updated: str = TODAY, force: bool = False) -> str:
    path = os.path.join(DIR_SOURCES, book, f"{book}-{tid}.tex")
    if os.path.exists(path) and not force:
        raise FileExistsError(f"refusing to overwrite {rel(path)} -- Layer A is append-only")
    parts = [DOSSIER_HEADER.format(book=book, tid=tid, title=title, locator=locator,
                                   status=status, unique="yes" if unique else "no",
                                   integrated=integrated, updated=updated)]
    parts.append(f"\\dossier{{{book}}}{{{tid}}}{{\\bookshort{{{book}}}}}{{{locator}}}\n")
    parts.extend(_emit_slots([("distilled", list(distilled))]))
    if unique:
        parts.append("")
        parts.extend(_emit_slots([("unique", list(unique))]))
    if terms:
        parts.append("")
        parts.extend(_emit_slots([("terms", list(terms))]))
    if quotable:
        parts.append("")
        parts.append("\\begin{quotable}")
        parts.append(quotable)
        parts.append("\\end{quotable}")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(parts) + "\n")
    return rel(path)


def report(paths: Sequence[str]) -> None:
    for p in paths:
        print("  + " + p)
    print(f"{len(paths)} file(s)")


# ---------------------------------------------------------------------------
# Additive merge helper
# ---------------------------------------------------------------------------
def add_source(tid: str, book: str, chapter: str = "", mechanism_addition: str = "") -> str:
    """Add `book` to an existing entry's source list, and optionally append a
    sentence to its `mechanism` slot.

    This is the sanctioned way a new source deepens an entry that B1 or B3
    already wrote. It never rewrites prose: it appends to one slot and adds
    one token to two lines.

    The source list is read from the file rather than hard-coded. Entries do
    not list their books in register order --- T-04-03 is `B3, B1` --- so a
    replacement built on an assumed ordering silently does nothing, and the
    build then fails R10 because a dossier exists for a book the entry never
    cited.
    """
    import re as _re

    path = os.path.join(DIR_TOPICS, chapter, f"{tid}.tex") if chapter else ""
    if not path or not os.path.exists(path):
        hits = []
        for ch in sorted(os.listdir(DIR_TOPICS)):
            cand = os.path.join(DIR_TOPICS, ch, f"{tid}.tex")
            if os.path.isfile(cand):
                hits.append(cand)
        if len(hits) != 1:
            raise FileNotFoundError(f"{tid}: expected exactly one file, found {hits}")
        path = hits[0]

    s = open(path, encoding="utf-8").read()

    m = _re.search(r"^%% @sources:\s*(.+)$", s, _re.M)
    if not m:
        raise ValueError(f"{tid}: no @sources line")
    srcs = [x.strip() for x in m.group(1).split(",") if x.strip()]
    if book not in srcs:
        srcs.append(book)
        joined = ", ".join(srcs)
        s = _re.sub(r"^%% @sources:\s*.+$", lambda _x: "%% @sources: " + joined,
                    s, count=1, flags=_re.M)
        repl = "\\sources{" + joined + "}"
        s = _re.sub(r"^\\sources\{[^}]*\}", lambda _x: repl, s, count=1, flags=_re.M)

    if mechanism_addition:
        mm = _re.search(r"(\\begin\{mechanism\}\n)(.*?)(\n\\end\{mechanism\})", s, _re.S)
        if not mm:
            raise ValueError(f"{tid}: no mechanism slot to append to")
        body = mm.group(2).rstrip()
        if mechanism_addition.strip() in body:
            pass                      # idempotent: already applied
        else:
            s = s[:mm.start(2)] + body + " " + mechanism_addition.strip() + s[mm.end(2):]

    open(path, "w", encoding="utf-8").write(s)
    return rel(path)
