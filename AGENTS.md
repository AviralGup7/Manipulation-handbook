# AGENTS.md — hard rules for automated writers

Read this before touching anything. The full reasoning is in
[`docs/RULES.md`](docs/RULES.md); this is the short, load-bearing version.

## You are working in a repository, not a scratchpad

Everything that must survive lives here. Nothing you write in `/tmp` persists.
The `.tex` files **are** the database — there is no CSV or JSON registry that
can drift from them.

## The five things that break this project

1. **Rewriting a file instead of adding one.** Book 4's contribution goes in a
   *new* file, `sources/B4/T-...tex`. It never goes into Book 1's file.
2. **Dropping a source from an entry.** If `sources/B1/B1-T-02-03.tex` has
   `@unique: yes`, then `B1` must stay in that entry's `@sources`. The
   validator fails the build otherwise — that is deliberate.
3. **Writing prose with no filed evidence.** No dossier → no citation → no
   claim. Write the dossier first, always.
4. **Padding.** 90 words of real content beats 400 words that look thorough.
   The banned-phrase list is enforced.
5. **Changing the format.** Slots and layout are fixed. You fill them; you do
   not redesign them.

## Deepening an entry a previous book already wrote

This is the additive merge, and there is one sanctioned way to do it:

```python
from hb_author import add_source
add_source("T-04-03", "B4",
           mechanism_addition="One sentence that only this book supports.")
```

It appends to `mechanism` and adds the book to `@sources` in both the header
and the footer. It reads the entry's **current** source list rather than
assuming register order — entries do not list their books in id order
(`T-04-03` is `B3, B1`), so a string replacement built on an assumed ordering
silently does nothing, and the build then fails R10 in a way that looks like a
rule bug rather than a typo in the merge.

Rules for the sentence you add:

* one idea, and one that **no other filed source already supports**;
* if the new book *contradicts* the existing prose rather than deepening it,
  the old claim moves to `cost` as a named minority view — it is not deleted;
* if the new book supports nothing the entry lacks, **file no dossier**. A
  dossier that backs no sentence is padding, and R7 bans padding. Record the
  withdrawn mapping in the book's ingest map instead.

## Rules that exist because a build actually broke

* **R19** — a style file must never define a command or environment whose name
  collides with a TeX primitive or a LaTeX kernel command. The sixth slot was
  originally called `limits`; `\newenvironment{limits}` silently redefines the
  `\limits` primitive and breaks every math display in the book. It is `cost`
  now. Namespace new macros `\hb…` and they are exempt.
* **R20** — the "entries in this chapter are not yet written" notice is
  generated (`\hbchapterstate{n}`), never hand-authored. Authored, it went
  stale the moment a chapter gained its first entry, and the PDF printed that
  sentence above three printed entries.
* Counts are generated everywhere — front matter, colophon, README. Never
  hand-write a number that the tree already knows.

## Where things live

Source scans are in `books/`, apart from the working tree; `main.tex` never
reads that directory. See `books/README.md`. Extracted source text goes to
`registry/corpus/`, which is git-ignored.

## Building the PDF

```bash
make pdf                                              # real TeX Live
make pdf HB_TEXLIVE_JS=/tmp/tex/node_modules/texlive  # WASM fallback
```

The fallback drives pdftex compiled to WebAssembly via
`tools/wasm-pdftex/build.js` and needs no TeX Live at all. It is a fallback,
not an equivalent: that texmf tree ships no EC (T1) or TS1 metrics and no
xcolor, so the class downgrades to OT1/Computer Modern and monochrome, and
WASM pdftex emits no PDF bookmarks. `style/handbook.cls` probes for each of
these at compile time — nothing needs editing, and a real TeX Live build gets
the full treatment automatically.

## Workflow — always in this order

```
1. read   registry/coverage.md            what already exists?
2. read   docs/TAXONOMY.md                where does this idea belong?
3. write  sources/<BOOK>/<BOOK>-<T>.tex   Layer A, evidence first
4. write  topics/<chapter>/T-..-...tex    Layer B, OR surgically extend it
5. run    make index && make verify       must pass, zero errors
6. commit one entry at a time
```

## Creating files — use the scaffolds, do not copy-paste a neighbour

```bash
python3 tools/new_book.py    --id B5 --title "..." --author "..." --year 0000 \
                             --rank primary --weight 85 --short "..."
python3 tools/new_topic.py   --chapter c03 --title "..." --subtitle "..." --sources B5
python3 tools/new_dossier.py --book B5 --topic T-03-01 --locator "ch.2, pp.41-47"
```

Scaffolds guarantee the header contract and refuse to overwrite.

## The header contract

Every managed `.tex` file starts with:

```latex
%% @kind: topic            # part | chapter | topic | source
%% @id: T-02-03            # must match the filename exactly
%% @title: ...
%% @chapter: c02           # topics
%% @order: 30              # multiples of 10, unique within the parent
%% @status: stable         # planned | draft | stable  (topics)
%% @sources: B1, B3        # topics: exactly the books with filed dossiers
%% @updated: 2026-09-19
```

Dossiers add `@book`, `@topic`, `@locator`, `@unique: yes|no`,
`@integrated: yes|no`.

## Style, in one paragraph

Second person or neutral declarative, present tense, concrete behaviour rather
than feelings. Slots in canonical order: `core → mechanism → tells → moves →
counters → cost → field → sources → seesources → seealso`. `core` is
mandatory. `counters` gets as much room as `moves`. Under 700 words per entry,
comfortably under 560. No `\vspace`, no `\newpage`, no colour, no centring —
layout lives in `style/`. Sources are cited with `\src{B1}` inline and
`\sources{B1, B3}` at the end.

## Copyright

These are copyrighted books. Never copy their prose. State ideas in original
words; use short titles only as labels. The `quotable` dossier slot permits at
most one short quoted line with a page number. If you find yourself
transcribing, stop.

## If you are unsure

Stop and ask. Do not guess an entry into existence, and do not "improve" a file
you were not asked to touch.
