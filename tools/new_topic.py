#!/usr/bin/env python3
"""
new_topic.py -- scaffold a new entry so the format cannot drift.

    python3 tools/new_topic.py --chapter c01 --title "The Thumbscrew" \
            --subtitle "Every person has one load-bearing insecurity" \
            --sources B3

It picks the next free entry number in the chapter, writes the file from the
canonical template, and regenerates the index. It never touches an existing
file.

    --status planned   (default)  scaffolding only, not typeset in the body
    --status draft                 typeset, marked unfinished
"""

from __future__ import annotations

import argparse
import datetime as _dt
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hb_lib import DIR_TOPICS, ROOT, Repo, rel, tex_escape  # noqa: E402

TEMPLATE = """\
%% =====================================================================
%%  @{id}  {title}
%%  -------------------------------------------------------------------
%%  RULES (docs/RULES.md): one idea per file. Core is mandatory. Slots in
%%  canonical order. Max {maxwords} words. No layout commands. No filler.
%%  New source material for this entry goes in sources/<BOOK>/{id}.tex --
%%  never by rewriting this file.
%% =====================================================================
%% @kind: topic
%% @id: {id}
%% @title: {title}
%% @subtitle: {subtitle}
%% @chapter: {chapter}
%% @order: {order}
%% @status: {status}
%% @sources: {sources}
%% @updated: {today}

\\topic{{{id}}}{{{title}}}{{{subtitle}}}

\\begin{{core}}
{core}
\\end{{core}}

\\begin{{mechanism}}
{mechanism}
\\end{{mechanism}}

\\begin{{tells}}
  \\item {tell}
\\end{{tells}}

\\begin{{moves}}
  \\item {move}
\\end{{moves}}

\\begin{{counters}}
  \\item {counter}
\\end{{counters}}

\\begin{{limits}}
{limits}
\\end{{limits}}

\\sources{{{sources}}}
\\seesources
\\seealso{{{seealso}}}
"""


def next_ids(repo: Repo, chapter: str) -> tuple:
    nums = []
    for t in repo.topics.values():
        m = re.fullmatch(r"T-(\d{2})-(\d{2})", t.id)
        if m and m.group(1) == chapter[1:]:
            nums.append(int(m.group(2)))
    n = (max(nums) + 1) if nums else 1
    order = n * 10
    return f"T-{chapter[1:]}-{n:02d}", order


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chapter", required=True, help="c01 .. c99")
    ap.add_argument("--id", help="force a specific entry id")
    ap.add_argument("--title", required=True)
    ap.add_argument("--subtitle", default="")
    ap.add_argument("--sources", default="", help="comma-separated book ids")
    ap.add_argument("--status", default="planned",
                    choices=["planned", "draft", "stable"])
    ap.add_argument("--seealso", default="")
    args = ap.parse_args()

    repo = Repo.scan(strict=False)
    if args.chapter not in repo.chapters:
        print(f"error: chapter {args.chapter} does not exist "
              f"(known: {', '.join(sorted(repo.chapters)) or 'none'})",
              file=sys.stderr)
        return 2

    tid, order = (args.id, 0) if args.id else next_ids(repo, args.chapter)
    if args.id:
        order = int(repo.topics[tid].meta.get("order", 0)) if tid in repo.topics else 10
    if tid in repo.topics:
        print(f"error: {tid} already exists at {repo.topics[tid].rel}",
              file=sys.stderr)
        return 2

    cdir = os.path.join(DIR_TOPICS, args.chapter)
    os.makedirs(cdir, exist_ok=True)
    path = os.path.join(cdir, f"{tid}.tex")
    if os.path.exists(path):
        print(f"error: {rel(path)} already exists", file=sys.stderr)
        return 2

    srcs = ", ".join(s.strip() for s in re.split(r"[,;]", args.sources) if s.strip())
    text = TEMPLATE.format(
        id=tid, title=tex_escape(args.title), subtitle=tex_escape(args.subtitle),
        chapter=args.chapter, order=order or 10, status=args.status,
        sources=srcs or "TODO", today=_dt.date.today().isoformat(),
        maxwords=700, core="\\TODO{one to three sentences: the whole entry}",
        mechanism="\\TODO{why this works on a person}",
        tell="\\TODO{observable sign}", move="\\TODO{step}",
        counter="\\TODO{defence}", limits="\\TODO{when it fails / what it costs}",
        seealso=tex_escape(args.seealso) or "\\TODO{id}",
    )
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    print(f"created {rel(path)}")

    # dossiers for the named books, if asked
    for b in [s.strip() for s in srcs.split(",") if s.strip() and s.strip() != "TODO"]:
        dpath = os.path.join(ROOT, "sources", b, f"{b}-{tid}.tex")
        if not os.path.exists(dpath):
            os.makedirs(os.path.dirname(dpath), exist_ok=True)
            with open(dpath, "w", encoding="utf-8") as fh:
                fh.write(DOSSIER_TEMPLATE.format(
                    book=b, id=tid, today=_dt.date.today().isoformat(),
                    title=tex_escape(args.title)))
            print(f"created {rel(dpath)}")

    os.system(f"{sys.executable} {os.path.join(ROOT,'tools','build_index.py')}")
    return 0


DOSSIER_TEMPLATE = """\
%% =====================================================================
%%  @{book}-@{id} -- what {book} contributes to "@{title}"
%%  -------------------------------------------------------------------
%%  LAYER A: APPEND-ONLY. Write once, then leave it alone. If the source
%%  says something new, add a bullet; do not restructure the file.
%% =====================================================================
%% @kind: source
%% @id: {book}-{id}
%% @book: {book}
%% @topic: {id}
%% @locator: TODO chapter / section / pages in the source
%% @status: skeleton
%% @unique: no
%% @integrated: no
%% @updated: {today}

\\dossier{{{book}}}{{{id}}}{{\\bookshort{book}}}{{TODO locator}}

\\begin{{distilled}}
  \\item TODO what this source actually says, compressed and in our words
\\end{{distilled}}
"""


if __name__ == "__main__":
    raise SystemExit(main())
