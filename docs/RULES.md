# RULES — the constitution of this handbook

**Version 1.0 · 2026-09-19 · These rules are binding on humans and on AI writers.**

They are written down because they are the things that get forgotten. Every rule
below exists to prevent a specific, observed failure. `tools/validate.py`
enforces the ones marked **[enforced]**; the rest are enforced by review, and by
`tools/churn_guard.py` where noted.

If a rule is wrong, change it here, bump the version, and change the tool in the
same commit. Never work around a rule quietly.

---

## 0. The two-layer rule (this is the whole system)

The repository separates **evidence** from **prose**.

| Layer | Where | Rule |
|-------|-------|------|
| **A — Source dossiers** | `sources/<BOOK>/<BOOK>-<T-id>.tex` | **Append-only. Write-once.** One file per (book × entry). Never restructured, never deleted, never overwritten. |
| **B — The handbook** | `topics/<chapter>/T-<cc>-<nn>.tex` | Curated synthesis. Edited **surgically**, slot by slot. |

Layer A is the audit trail and the insurance policy. Layer B is the book people
read. **Nothing is ever written into Layer B that does not first exist in
Layer A.** That single dependency is what stops an entry from being silently
rewritten from memory — i.e. hallucinated — when a new source arrives.

> Why this shape: if the book and the evidence lived in the same file, then
> "improving an entry with Book 4" would mean rewriting Book 1's contribution,
> and Book 1's unique material would be lost with no record that it ever
> existed. Separate files make that physically impossible.

**[enforced]** R0.1 A Layer A file may only be created, appended to, or marked
`@status: retired` with `@reason:`. It may never be deleted or wholesale
rewritten. `tools/churn_guard.py` fails on >40% line churn without
`@allow-rewrite: <reason>` in the header, and fails on any deletion under
`sources/`.

R0.2 Layer B prose must be **written afresh** in this handbook's voice. It is a
synthesis of the sources, never a transcription of them. **[enforced R15]**
against a local corpus when one is present.

---

## 1. Organisation

R1.1 The book is organised **by subject, never by book**. No reader should be
able to tell where one source stops and another starts. Provenance is carried
by tags, not by structure.

R1.2 **One idea per file.** An entry is one technique, one type, one principle
— something you could name in a sentence. If you need "and" to name it, it is
two entries.

R1.3 Three levels only: **Part → Chapter → Entry**. Parts are big movements of
the argument (terrain, reading, positioning, persuasion, pressure, defence,
cost). Chapters are one subject each. Entries are the unit of work.

R1.4 IDs are permanent. `T-02-03` means chapter 2, entry 3, forever. Never
renumber an entry to tidy up, even when chapters are reorganised — other files,
links and git history refer to it. Move the file; keep the ID.

R1.5 **[enforced]** The reading order is **generated** from the headers into
`registry/compiled/index.tex`. `main.tex` is never edited to add content.

R1.6 **[enforced]** Entry, chapter, part and dossier IDs must agree with their
filenames and directory names (`check_ids`).

---

## 2. The entry format (fixed, on purpose)

R2.1 **[enforced]** Slot order is:

```
core → mechanism → tells → moves → counters → limits → field
     → sources → seesources → seealso
```

All optional except **`core`**. Never invent a new slot; if the existing six
cannot hold a fact, the fact does not belong in this handbook.

R2.2 What each slot is for:

| Slot | Question it answers | Shape |
|------|--------------------|-------|
| `core` | What is this, irreducibly? | 1–3 sentences, boxed |
| `mechanism` | Why does it work on a person? | 1 short paragraph |
| `tells` | How do I see it being used? | bullets, observable behaviour |
| `moves` | How is it done? | numbered, imperative, ≤6 steps |
| `counters` | How do I refuse it? | bullets, equal weight to `moves` |
| `limits` | When does it fail, and what does it cost? | 1 short paragraph |
| `field` | A modern illustration | optional, **written by us**, never lifted |

R2.3 `counters` is not decoration. An entry that teaches only the offensive
half is incomplete and will be rejected.

R2.4 `limits` must be honest. Every technique here has a failure mode. If you
cannot find one, you have not understood the technique.

---

## 3. Size — small portions are a quality control, not a preference

R3.1 **[enforced]** An entry's body is **≤ 700 words**, with a comfort band
under 560. Over the ceiling: split the entry. Never compress two ideas into
one to fit.

R3.2 **[enforced]** A `stable` entry is **≥ 45 words**. Anything thinner is
`draft`.

R3.3 Files stay small so a writer (human or AI) can hold the whole thing in
view. Long files are where quality collapses: repetition creeps in, the voice
drifts, and previously written material gets paraphrased back at itself.

R3.4 No padding to reach a target length. If an entry is 90 words of real
content, it is 90 words. The sources spend most of their length on anecdote and
hedging; that material is removed, not replaced with new hedging.

---

## 4. Voice

R4.1 Second person or neutral declarative. Present tense. No "we will explore".

R4.2 **[enforced]** Filler is banned by an explicit phrase list in
`tools/validate.py` (`FILLER`). Adding to that list is encouraged; removing from
it requires a reason.

R4.3 No moral preamble and no moral postscript inside an entry. The ethical
position is stated once, in the front matter, and in each entry's `limits`.
Hedging every paragraph is exactly the padding this handbook exists to remove.

R4.4 Concrete beats abstract. Name the behaviour, not the feeling.

R4.5 See `docs/STYLE-GUIDE.md` for the full voice spec and worked examples.

---

## 5. Merging a new source

R5.1 **Read the whole source before writing anything.** Ingest book-shaped, not
chapter-shaped: understand its argument first, then map it.

R5.2 **Map before merge.** For each candidate idea, search `registry/coverage.md`
and the existing entries. Three outcomes, and only three:

| Outcome | Action |
|---------|--------|
| **New idea** | Create a new entry in the right chapter. |
| **Same idea, new detail** | File a Layer A dossier; then **append** to the existing entry's slots and add the book to `@sources`. |
| **Same idea, contradiction** | File a dossier; record both positions in the entry; resolve by `weight` in `registry/books.yaml`. Never delete the losing position — mark it as the minority view. |

R5.3 **[enforced]** A source may only be listed in an entry's `@sources` if a
Layer A dossier exists for that (book, entry) pair. No dossier, no citation.
Conversely a dossier marked `@integrated: yes` must be cited.

R5.4 **[enforced — the protection rule]** If a dossier has `@unique: yes`, its
book **cannot be removed** from that entry's `@sources`. The validator fails the
build. This is the mechanical guarantee that Book 1's unique knowledge survives
Book 4 being "better on the topic".

R5.5 **[enforced]** A **secondary** source (e.g. a summary of another source)
may corroborate but **never originate**. An entry citing only secondary sources
fails.

R5.6 Conflicts are resolved by `weight`, and the resolution is recorded in the
entry, not hidden. Higher weight wins the main text; the loser goes to `limits`
or to a named minority view.

R5.7 Do not re-ingest. If a dossier already exists for (book, entry), append to
it — do not create a second file.

---

## 6. Layout

R6.1 **[enforced]** Content files (`topics/`, `sources/`) contain **no layout
commands**: no `\vspace`, `\newpage`, `\color`, `\setlength`, `\newcommand`,
`\begin{center}`, `\rule`, `\pagestyle`. Layout lives in `style/handbook.cls`
and `style/entry.sty` only.

R6.2 Consequence: the look of the entire book can be changed by editing two
files, and no content file can break the build by inventing formatting.

R6.3 Front matter (`front/`, `back/`) is exempt and may use layout directly.

---

## 7. Generated files

R7.1 `registry/compiled/*.tex` and `registry/coverage.md` are **generated**.
They are committed (so the project compiles with zero tooling, e.g. on
Overleaf) but never hand-edited.

R7.2 **[enforced]** `validate.py` regenerates them in memory and fails if the
committed copies differ. Run `make index` before committing.

R7.3 The `.tex` sources and the generated index live in the repository, not in a
scratch directory. Anything that must survive belongs in git; anything that can
be regenerated and is third-party copyright (extracted corpus text, PDFs'
intermediate output) is gitignored.

---

## 8. Before you commit

```
make verify      # = make check  +  make guard
```

R8.1 **[enforced]** `make check` must pass with zero errors. Warnings are read
and either fixed or consciously accepted.

R8.2 **[enforced]** `make guard` must pass. It compares against `HEAD` (or
`BASE=…`) and fails on wholesale rewrites and on deletions of Layer A.

R8.3 One commit = one entry, or one source dossier batch, or one system change.
Never mix a content change with a style change.

R8.4 If the build is done somewhere with no TeX engine, say so in the commit
message. `make check` is the substitute gate; it is not equivalent to a compile.

---

## 9. Legal and ethical

R9.1 Sources are copyrighted. This handbook reproduces **none** of their
expression. It uses short titles as labels and states ideas in original prose.
The `quotable` dossier slot allows at most one short quoted line, with a page
locator, for identification purposes.

R9.2 Do not paste source prose into an entry "to clean up later". It will not be
cleaned up later.

R9.3 Entries describing conduct that is illegal in many jurisdictions (fraud,
extortion, blackmail, coercion) must state that in `limits`, and must carry
`counters` of equal or greater length than `moves`.

R9.4 The handbook's stated purpose is defensive competence. That framing lives
in `front/notice.tex` and is not optional.

---

## 10. Changing these rules

R10.1 Rules are changed by editing this file, bumping the version and date at
the top, and updating the enforcing tool **in the same commit**.

R10.2 A rule may be relaxed but not silently ignored. If a specific entry must
break a rule, use the escape hatch that rule provides
(`@allow-rewrite:`, `@status: draft`) and state the reason in the header where
the validator can see it.
