# The Manipulation Handbook

A merged, de-padded reference on how influence is applied, how it is spotted,
and how it is refused — built from primary sources as a **LaTeX** project that is
meant to grow for years without breaking.

**Current state:** Parts I–II written (27 entries), Parts III–VII scaffolded
(28 chapters, 7 parts). Sources ingested: 3. Build the PDF with `make pdf`.

---

## The problem this repository is built to solve

Merging several books into one tends to fail in four specific ways:

| Failure | What this repo does about it |
|---|---|
| Book 4 overwrites Book 1's unique material | **Two layers.** Evidence lives in `sources/<BOOK>/…` — append-only, one file per source per entry, never rewritten. The book lives in `topics/…`. A source that contributed *unique* material **cannot** be dropped from an entry: the build fails. |
| The result reads like three books stapled together | Organised **by subject, never by book**. A fixed six-slot entry format, one style file for all layout, one voice spec. |
| Quality collapses in long files | **One idea per file**, hard-capped at 700 words. Over the cap you split, you do not compress. |
| The rules get forgotten | They are **written down** in `docs/RULES.md`, short-form in `AGENTS.md`, and **enforced by code** in `tools/validate.py` + `tools/churn_guard.py`. |

Adding a source touches: `registry/books.yaml` (append), `sources/B<n>/` (new
files), `registry/ingest/B<n>-map.md` (new), and — surgically — individual
entries. It never touches `main.tex`, the style files, the tools, or any other
source's directory.

---

## Layout

```
main.tex                     the only file you compile (never edit it)
handbook.pdf                 the built book

style/handbook.cls           ALL layout: page, headings, colour, lists
style/entry.sty              ALL structure: the entry DSL and slot commands

topics/
  _parts/P1.tex …P7.tex      part metadata + blurb
  c01/_meta.tex …c28/        chapter metadata + blurb
  c01/T-01-01.tex …          ONE ENTRY PER FILE  (Layer B: the book)

sources/
  B1/B1-T-01-01.tex …        ONE FILE PER SOURCE PER ENTRY
                             (Layer A: append-only evidence)

registry/
  books.yaml                 the source register (append-only)
  coverage.md                GENERATED: what exists, what is outstanding
  compiled/*.tex             GENERATED: index, dossiers, book macros
  ingest/B<n>-map.md         the mapping plan for each source

tools/                       build system (stdlib Python 3.8+, no deps)
docs/                        RULES · TAXONOMY · STYLE-GUIDE · INGESTION
AGENTS.md                    the short form for automated writers
front/ back/                 title page, notices, colophon
```

## The entry format

Every entry is the same six slots, in this order. That uniformity is what makes
the merged book read as one book.

```latex
\topic{T-04-01}{The Thumbscrew}{Everyone has one load-bearing insecurity}

\begin{core}      one to three sentences: the whole entry      \end{core}
\begin{mechanism} why it works on a person                     \end{mechanism}
\begin{tells}     how to see it being used         (bullets)   \end{tells}
\begin{moves}     how it is executed               (numbered)  \end{moves}
\begin{counters}  how to refuse it — equal weight  (bullets)   \end{counters}
\begin{cost}    when it fails and what it costs              \end{cost}

\sources{B1, B3}  \seesources  \seealso{T-04-03}
```

Prose carries inline provenance tags (`\src{B1}`) and the entry footer lists
every source that contributed. Source dossiers in Appendix A are the audit
trail, including a `unique` slot for material found in one book only.

## Build

```bash
make            # index + validate + PDF
make check      # the policy gate — run before every commit
make guard      # the no-wholesale-rewrite gate
make verify     # both, which is what CI runs
make index      # regenerate every derived file
make pdf        # typeset handbook.pdf
make corpus     # extract the source PDFs' text (enables the verbatim check)
make selftest   # prove the guarantees hold (see below)
make clean      # remove build debris; never touches content
```

Requirements: **Python 3.8+** for everything except typesetting; a **TeX Live**
(or MiKTeX/MacTeX) install for `make pdf`. If no TeX engine is present,
`make check` still validates the project structurally — no layout commands in
content files, balanced braces and environments, no non-ASCII, no unescaped
specials, all `\input` targets present — so a first compile rarely fails. The
project also compiles unchanged on [Overleaf](https://www.overleaf.com): upload
it and build `main.tex`.

## Scaffolding

```bash
python3 tools/new_book.py    --id B4 --title "..." --author "..." --year 2011 \
                             --rank primary --weight 85 --short "..."
python3 tools/new_topic.py   --chapter c11 --title "Manufactured Indispensability" \
                             --subtitle "..." --sources B4
python3 tools/new_dossier.py --book B4 --topic T-11-01 --locator "ch.3, pp.41-58"
```

All three refuse to overwrite an existing file. That is deliberate.

## The guarantees, and how they are proven

`tools/selftest.py` (`make selftest`) copies the repository to a scratch
directory and attacks it, asserting that each protection actually fires:

1. registering a new source and filing new dossiers changes **no existing file**;
2. dropping a book that contributed `unique` material from an entry's
   `@sources` **fails** the build (R10);
3. citing a source with no filed dossier **fails** (R11);
4. citing only a secondary source **fails** (R4);
5. a wholesale rewrite of an entry **fails** `churn_guard`;
6. deleting a dossier **fails** `churn_guard`;
7. slots out of order, over-length entries, filler phrases, layout commands in
   content files, stale generated indexes — all **fail**;
8. new files appear in the compiled book **without editing `main.tex`**.

## Documentation

| file | what it is for |
|---|---|
| [`docs/RULES.md`](docs/RULES.md) | the constitution — every rule, with the failure it prevents |
| [`docs/TAXONOMY.md`](docs/TAXONOMY.md) | the map: which idea goes in which part/chapter |
| [`docs/STYLE-GUIDE.md`](docs/STYLE-GUIDE.md) | voice, banned filler, what gets cut |
| [`docs/INGESTION.md`](docs/INGESTION.md) | the six-stage procedure for adding a book |
| [`AGENTS.md`](AGENTS.md) | the short form for automated writers |

## Legal and ethical position

These sources are copyrighted. This handbook reproduces none of their
expression: it is an original synthesis, using short titles only as labels and
stating every idea in its own prose. `make corpus` + rule R15 machine-check
that no run of nine or more words is lifted from a source. The purpose of the
book is defensive competence — each entry carries its counters before its
limits — and nothing in it is advice to defraud, coerce or exploit anyone.
See `front/notice.tex`.
