#!/usr/bin/env python3
"""
new_book.py -- register a new source and scaffold its dossier directory.

    python3 tools/new_book.py --id B4 \
        --title "Influence: The Psychology of Persuasion" \
        --author "Robert B. Cialdini" --year 1984 \
        --publisher "HarperBusiness" --rank primary --weight 85 \
        --file "influence.pdf" \
        --short "Cialdini, Influence (1984)"

What it does, and only this:
  1. appends a block to registry/books.yaml   (append-only)
  2. creates sources/B4/                     (empty, ready for dossiers)
  3. regenerates registry/compiled/*

It edits NOTHING that already exists. That is the whole point: Book 4 cannot
damage Book 1 because Book 4 only ever adds files. See docs/INGESTION.md for
the merge procedure that follows.
"""

from __future__ import annotations

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hb_lib import BOOKS_YAML, DIR_SOURCES, ROOT, Repo, rel  # noqa: E402

BLOCK = """
- id: {id}
  rank: {rank}
  weight: {weight}
  status: active
  title: "{title}"
  author: "{author}"
  year: {year}
  publisher: "{publisher}"
  file: "{file}"
  structure: "{structure}"
  short: "{short}"
  notes: >
    {notes}
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True, help="B4, B5, ... never reuse one")
    ap.add_argument("--title", required=True)
    ap.add_argument("--author", default="")
    ap.add_argument("--year", default="")
    ap.add_argument("--publisher", default="")
    ap.add_argument("--file", default="")
    ap.add_argument("--structure", default="")
    ap.add_argument("--short", default="")
    ap.add_argument("--rank", default="primary",
                    choices=["primary", "secondary", "tertiary"])
    ap.add_argument("--weight", type=int, default=80)
    ap.add_argument("--notes", default="")
    args = ap.parse_args()

    if not re.fullmatch(r"B\d+", args.id):
        print("error: --id must look like B4", file=sys.stderr)
        return 2

    repo = Repo.scan(strict=False)
    if repo.book(args.id):
        print(f"error: {args.id} is already registered", file=sys.stderr)
        return 2
    taken = sorted(int(b["id"][1:]) for b in repo.books if b["id"][1:].isdigit())
    if taken and int(args.id[1:]) <= max(taken):
        print(f"error: ids must increase; {max(taken)} is already used",
              file=sys.stderr)
        return 2

    with open(BOOKS_YAML, "r", encoding="utf-8") as fh:
        text = fh.read()

    marker = "# NEXT BOOK GOES HERE. Do not renumber the ones above."
    if marker in text:
        head, tail = text.split(marker, 1)
        tail = tail.split("\n", 1)[1] if "\n" in tail else ""
        new = head.rstrip() + "\n\n" + BLOCK.format(
            id=args.id, rank=args.rank, weight=args.weight,
            title=args.title.replace('"', "'"), author=args.author,
            year=args.year or "0", publisher=args.publisher, file=args.file,
            structure=args.structure or "TODO",
            short=args.short or f"{args.author}, {args.title}",
            notes=(args.notes or "TODO").replace("\n", " "))
        new += "\n" + marker + "\n" + tail.lstrip("\n")
    else:
        new = text.rstrip() + "\n" + BLOCK.format(
            id=args.id, rank=args.rank, weight=args.weight, title=args.title,
            author=args.author, year=args.year or "0",
            publisher=args.publisher, file=args.file,
            structure=args.structure or "TODO",
            short=args.short or args.title, notes=args.notes or "TODO")

    with open(BOOKS_YAML, "w", encoding="utf-8") as fh:
        fh.write(new)
    print(f"registered {args.id} in {rel(BOOKS_YAML)}")

    d = os.path.join(DIR_SOURCES, args.id)
    os.makedirs(d, exist_ok=True)
    keep = os.path.join(d, "README.md")
    if not os.path.exists(keep):
        with open(keep, "w", encoding="utf-8") as fh:
            fh.write(
                f"# sources/{args.id}/ -- {args.title}\n\n"
                "Layer A dossiers for this source. One file per entry, named\n"
                f"`{args.id}-T-nn-nn.tex`.\n\n"
                "**APPEND-ONLY.** Write a dossier once and do not restructure\n"
                "it later. If the source says something new about an entry,\n"
                "add a bullet to that entry's dossier. Superseded material is\n"
                "marked `@status: retired` with a `@reason:` -- never deleted.\n\n"
                "Create dossiers with:\n\n"
                "```\n"
                f"python3 tools/new_dossier.py --book {args.id} --topic T-01-01\n"
                "```\n")
    print(f"created {rel(d)}/")

    os.system(f"{sys.executable} {os.path.join(ROOT,'tools','build_index.py')}")
    print(f"\nnext: read docs/INGESTION.md, then file dossiers into sources/{args.id}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
