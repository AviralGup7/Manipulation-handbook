#!/usr/bin/env python3
"""
new_dossier.py -- scaffold a Layer A dossier (one source's contribution to one
entry).

    python3 tools/new_dossier.py --book B1 --topic T-02-03
    python3 tools/new_dossier.py --book B1 --topic T-02-03 --locator "ch.6, pp.71-76"

Append-only by construction: it refuses to overwrite an existing dossier.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hb_lib import ROOT, Repo, rel, tex_escape  # noqa: E402

TEMPLATE = """\
%% =====================================================================
%%  @{book}-{topic} -- what {book} contributes to "{title}"
%%  -------------------------------------------------------------------
%%  LAYER A: APPEND-ONLY. Write this once and leave the structure alone.
%%  If the source has more to say about this entry later, add a bullet --
%%  do not rewrite. Material found ONLY here must go in the `unique` slot
%%  and set @unique: yes; that makes it undeletable (rule R10).
%% =====================================================================
%% @kind: source
%% @id: {book}-{topic}
%% @book: {book}
%% @topic: {topic}
%% @locator: {locator}
%% @status: skeleton
%% @unique: {unique}
%% @integrated: no
%% @updated: {today}

\\dossier{{{book}}}{{{topic}}}{{\\bookshort{{book}}}}{{{locator}}}

\\begin{{distilled}}
  \\item {point}
\\end{{distilled}}
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", required=True)
    ap.add_argument("--topic", required=True)
    ap.add_argument("--locator", default="TODO locator")
    ap.add_argument("--unique", default="no", choices=["yes", "no"])
    args = ap.parse_args()

    repo = Repo.scan(strict=False)
    if not repo.book(args.book):
        print(f"error: {args.book} is not in registry/books.yaml "
              "(run tools/new_book.py first)", file=sys.stderr)
        return 2
    t = repo.topics.get(args.topic)
    if not t:
        print(f"error: entry {args.topic} does not exist", file=sys.stderr)
        return 2

    path = os.path.join(ROOT, "sources", args.book, f"{args.book}-{args.topic}.tex")
    if os.path.exists(path):
        print(f"refusing to overwrite {rel(path)} -- Layer A is append-only. "
              "Edit it surgically instead.", file=sys.stderr)
        return 2
    os.makedirs(os.path.dirname(path), exist_ok=True)

    body = TEMPLATE.format(
        book=args.book, topic=args.topic, title=tex_escape(t.title),
        locator=tex_escape(args.locator), unique=args.unique,
        today=_dt.date.today().isoformat(),
        point="\\TODO{what this source says, compressed and in our own words}",
    )
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(body)
    print(f"created {rel(path)}")
    print("reminder: after merging it into the entry, set "
          "'@integrated: yes' and add "
          f"{args.book} to @{args.topic}'s @sources")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
