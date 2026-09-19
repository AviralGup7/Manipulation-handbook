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
                 ("tells", ["...", "..."]), ...],
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

LIST_SLOTS = ("tells", "moves", "counters", "distilled", "unique", "terms")

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
