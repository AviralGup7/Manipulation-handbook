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
python3 tools/new_book.py    --id B4 --title "..." --author "..." --year 0000 \
                             --rank primary --weight 85 --short "..."
python3 tools/new_topic.py   --chapter c03 --title "..." --subtitle "..." --sources B4
python3 tools/new_dossier.py --book B4 --topic T-03-01 --locator "ch.2, pp.41-47"
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
