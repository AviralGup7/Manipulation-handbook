# `books/` — the source shelf

This directory holds the **input** scans: the PDFs the handbook is compiled
*from*. Nothing in here is part of the build. `main.tex` never reads this
directory, and no `.tex` file `\input`s anything from it.

Keeping them apart from the working tree is deliberate:

- the repo root stays readable — `main.tex`, `handbook.pdf` and the
  directories that actually compose the book;
- a new source is added by dropping one file here and appending one block to
  `registry/books.yaml`, with no chance of disturbing the manuscript;
- the shelf can be pruned, mirrored or excluded from a checkout without
  touching a single line of prose.

## Rules

1. **One file per registered source.** The filename is recorded in the `file:`
   field of that source's block in `registry/books.yaml`, resolved relative to
   the repository root (so `books/foo.pdf`).
2. **Never rename a file without updating `books.yaml` in the same commit.**
   `tools/extract_corpus.py` walks the register and skips any source whose
   file is missing, so a stale path fails silently rather than loudly.
3. **Never delete a source file that has dossiers against it.** Layer A files
   in `sources/<ID>/` cite it by locator; removing the scan makes those
   locators unverifiable. Retire it in the register (`status: retired`) and
   leave the file in place.
4. **Add, do not replace.** If a better edition of an already-ingested book
   arrives, register it as a *new* id and note the relationship in `notes:`.
   Existing dossiers keep pointing at the id they were written against.

## What lives where

| Path | Contents | In the build? |
| --- | --- | --- |
| `books/` | source scans (this directory) | no |
| `registry/corpus/` | extracted plain text, regenerable, git-ignored | no |
| `sources/<ID>/` | Layer A dossiers — append-only provenance | appendix only |
| `topics/` | Layer B entries — the book itself | yes |
| `registry/compiled/` | generated indices, counts, book register | yes |

## Extracting text from a scan

```sh
python3 tools/extract_corpus.py            # every registered source
python3 tools/extract_corpus.py --only B4  # one source
```

Output goes to `registry/corpus/`, which is git-ignored: it is large, it is
third-party expression, and it is trivially regenerable from the scans here.
Rule R15 reads that corpus to machine-check that no run of nine or more words
of source expression has leaked into the handbook.

A registered source may also be a **plain-text transcript** (`.txt`) instead
of a PDF — the format used for journal articles whose PDFs cannot be mirrored
here (the register records the DOI instead). `tools/extract_corpus.py`
recognises the extension and passes the transcript through to the corpus
(normalised like any other), so grounding checks work identically.
