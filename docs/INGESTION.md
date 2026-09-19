# INGESTION — adding a book without breaking anything

This is the procedure that makes the system scale. It is append-only at every
step: **no existing content file is rewritten to make room for a new source.**

Estimated effort for a 300-page source: 6–10 working sessions. It is meant to be
done slowly. Do not try to ingest a book in one pass.

---

## Stage 0 — Register the source  (5 minutes)

```bash
python3 tools/new_book.py \
  --id B4 \
  --title "Influence: The Psychology of Persuasion" \
  --author "Robert B. Cialdini" \
  --year 1984 \
  --publisher "HarperBusiness" \
  --file "books/influence.pdf" \
  --rank primary \
  --weight 85 \
  --short "Cialdini, Influence (1984)" \
  --structure "7 principles, each with studies and defence"
```

* `--id` must be new and larger than every existing one. IDs are never reused.
* `--rank`
  * `primary` — may originate claims.
  * `secondary` — may corroborate only (summaries, study guides, wikis). The
    validator rejects an entry whose only sources are secondary.
  * `tertiary` — background; never cited in entries.
* `--weight` — tie-break priority when sources conflict. Higher wins the main
  text; the loser is recorded as a minority view, never deleted.
* Drop the PDF in the repository root and name it in `--file`.

Then `make index` and commit: `registry: add B4`.

## Stage 1 — Read the source, whole  (do not skip)

Read it end to end before writing a single entry. Then answer, in a scratch note
(not committed):

1. What is this book's *unit of analysis*? (law / tactic / principle / type)
2. What is it strongest on that the existing sources are weak on?
3. What does it cover that is already covered — and does it cover it better,
   differently, or contradictorily?
4. What is padding? Anecdote volume, repetition, case-narrative ratio.

Skipping this stage is how a merged book ends up scrambled: the second source
gets bolted on in its own order instead of being dissolved into the taxonomy.

## Stage 2 — Map to the taxonomy  (the important stage)

Go through the source's units one at a time. For each, open
`registry/coverage.md` and decide — using the test at the bottom of
`docs/TAXONOMY.md`:

| Situation | Action |
|-----------|--------|
| **No existing entry covers it** | Plan a new entry. Note the chapter. |
| **An existing entry covers it, source adds detail** | Plan a dossier + surgical append to that entry. |
| **An existing entry covers it, source contradicts** | Plan a dossier + record both, resolve by `weight`. |
| **It is padding** | Record the decision and drop it. Write down *why* so the next reader does not re-litigate it. |
| **It duplicates another part of the same source** | Merge into one dossier. |

Produce a **mapping table** before writing anything:

```
B4 ch.2 reciprocity      -> T-18-01 (exists, adds detail)     dossier + append
B4 ch.3 commitment       -> T-14-02 (new: "Escalating Commitments")
B4 ch.4 social proof     -> T-15-03 (exists, contradicts B3)  record minority view
B4 ch.1 weapons of ...   -> padding (framing only)
```

Commit the mapping table as `registry/ingest/B4-map.md`. It is the plan of
record, and it is what stops a half-finished ingest from being restarted from
memory.

## Stage 3 — File dossiers (Layer A)  — evidence first

For every row in the mapping table:

```bash
python3 tools/new_dossier.py --book B4 --topic T-18-01 \
        --locator "ch.2, pp.47-63"
```

Then fill in the scaffold:

* `distilled` — the source's contribution, compressed and **in our own words**.
  Bullets, not paragraphs. This is the evidence, so it should be complete enough
  that the entry could be rebuilt from it.
* `unique` — anything this source says that no other source says. **Set
  `@unique: yes`.** This is the protection mechanism: once set, the validator
  will refuse to let `B4` be dropped from that entry's `@sources`, forever.
* `terms` — vocabulary worth keeping, with a one-line definition.
* `quotable` — at most one short line, with a page number. Optional.

Set `@status: distilled` and leave `@integrated: no` for now.

Commit in small batches: `sources(B4): T-18-01, T-15-03`.

## Stage 4 — Merge into the handbook (Layer B)

Two cases.

### 4a. A new entry

```bash
python3 tools/new_topic.py --chapter c14 --title "Escalating Commitments" \
  --subtitle "A small yes is bought to make the large yes cheap" \
  --sources B4 --status draft
```

Fill the slots. Mark `@status: stable` only when `counters` and `cost` are
both real.

### 4b. An existing entry — **surgical edit only**

Open `topics/cNN/T-..-...tex` and make the smallest change that carries the new
material:

* add a bullet to `tells` / `moves` / `counters`;
* add a sentence to `mechanism` or `cost`;
* add the new book to the header `@sources` **and** to the `\sources{}` line
  (they must match — validated);
* add `\src{B4}` inline only where the new source specifically differs.

Then set `@integrated: yes` in the dossier and bump the entry's `@updated`.

**Never:** re-order the slots, rewrite the `core` block wholesale, restate the
whole entry in the new source's framing, or delete a bullet whose only support
is another book's dossier. If the new source genuinely supersedes an old claim,
the old claim moves to `cost` as a named minority view — it is not deleted.

`make guard` enforces this: more than 40% of an entry's lines changing fails the
build unless you add `@allow-rewrite: <reason>` to the header. That escape hatch
exists, and using it should be rare and visible.

## Stage 5 — Verify and commit

```bash
make index
make verify      # check + guard, must be zero errors
make pdf         # if a TeX engine is available
```

Read the entry **in the compiled PDF**, in context, not in the editor. That is
the only reliable way to catch a merge that reads like two books stapled
together.

Commit: `topics(T-18-01): merge B4 reciprocity material`.

## Stage 6 — Retire the mapping table row

Tick it off in `registry/ingest/B4-map.md`. When every row is ticked, add a
line to `registry/ingest/B4-map.md` recording: pages read, entries created,
entries extended, material dropped as padding, and any open contradictions.

---

## If a mistake happens

| Symptom | Cause | Fix |
|---------|-------|-----|
| `R10` error: unique knowledge dropped | a book was removed from `@sources` | put it back; the dossier's `unique` block is the record of why |
| `R11` error: citation without a dossier | prose was written from memory | write the dossier, or remove the citation |
| `R14` error: generated file stale | `make index` not run | run it and commit |
| `churn_guard` failure | wholesale rewrite | revert to surgical edits, or add `@allow-rewrite:` with a real reason |
| The merged chapter reads like two books | the new source was appended in its own order instead of dissolved | re-map against `docs/TAXONOMY.md`; move the material to the right entries |
| Entry over 700 words after a merge | two ideas have been fused | split it: new ID, new file, `\seealso` between them |

## What never changes

`main.tex`, `style/`, `tools/`, and every other book's `sources/` directory.
Adding Book 7 touches: `registry/books.yaml` (append),
`registry/ingest/B7-map.md` (new), `sources/B7/` (new files), and — surgically —
individual entries in `topics/`. Nothing else.
