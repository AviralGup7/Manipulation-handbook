# STYLE GUIDE

How an entry sounds. The goal is that a reader cannot tell three different
authors wrote three different source books: one voice, one rhythm, one shape.

---

## 1. Voice

* **Register:** plain, dry, adult. Not academic, not motivational, not
  conspiratorial.
* **Person:** neutral declarative or second person. "A person who protests
  trustworthiness is selling something." / "Delay before you answer."
  Never first person plural ("we will see"), never first person singular.
* **Tense:** present. These are mechanisms, not events.
* **Sentence length:** mixed, biased short. One long sentence may carry a
  mechanism; the next should be eight words.
* **Vocabulary:** ordinary English. If a source has a good term of art
  ("thumbscrew", "unargue", "cat's paw"), keep it and define it once, in the
  entry's `mechanism` or in a dossier `terms` slot.
* **No hedging stack.** One qualifier maximum per claim. Not "it may often tend
  to work".

## 2. What gets cut

The sources spend most of their length on material this handbook removes:

| Cut | Why |
|-----|-----|
| Historical anecdote and case narrative | Not transferable. Where a case *is* the lesson, it becomes a two-sentence `field` note written by us. |
| Repetition of the same point in three registers | The sources do this for emphasis; it reads as padding. |
| Moral throat-clearing before a tactic | Stated once in the front matter and once per entry in `cost`. |
| Justification of the book's own premise | The reader is already here. |
| Author biography and provenance storytelling | Goes in `registry/books.yaml`. |
| Transitional paragraphs between sections | The slot structure is the transition. |

**Keep:** the mechanism, the observable sign, the sequence of moves, the
counter, the failure mode, and any term of art worth preserving.

## 3. Banned phrases

Enforced by `tools/validate.py` (`FILLER`). Non-exhaustive:

> in today's fast-paced world · it is important to note · it should be noted ·
> it is worth noting · needless to say · it goes without saying · as we have
> seen · as mentioned earlier · in conclusion · to sum up · at the end of the
> day · when it comes to · in the realm of · the landscape of · navigate the
> complexities · delve · tapestry · game-changer · unlock the power ·
> let's dive in · in this section we will · we will explore · first and
> foremost · the bottom line is · without further ado · ever-evolving ·
> harness the power · elevate your · it is crucial · it is essential to
> understand

Add to this list freely. Remove from it only with a reason.

Also banned, though not machine-checked: rhetorical questions used as openers,
exclamation marks, "obviously", "clearly", "simply", "just" as a softener.

## 4. The slots, in detail

### `core` — mandatory, boxed
One to three sentences that make the entry self-contained. Test: read only the
`core` blocks of a chapter in sequence. They should form a coherent argument on
their own.

```latex
\begin{core}
Indispensability is not a feeling, it is a structural fact: the person who
cannot be replaced sets the terms. Everything else in this entry is a way of
manufacturing that fact.
\end{core}
```

### `mechanism` — one short paragraph
Why it lands on a human being. Name the underlying drive: fear of loss, need for
consistency, desire for status, aversion to conflict, the effort economy of
attention. If you cannot name the drive, you have described a habit, not a tactic.

### `tells` — bullets, observable
Behaviour that could be filmed. "He repeats the benefit you stand to gain" is a
tell. "He seems insincere" is not.

### `moves` — numbered, imperative, ≤ 6 steps
The sequence. Short enough to hold in memory. Do not narrate.

### `counters` — bullets, equal weight to `moves`
What the target does. Prefer answers that work without confronting the person
(delay, reframe, refer to a third party, require writing) over answers that
require winning an argument — those usually fail.

### `cost` — one short paragraph
Failure modes, cost to the user, blowback, and illegality where relevant.

### `field` — optional
A modern illustration **written for this handbook**: an office, a family, a
sales call, a negotiation. Never a retold anecdote from a source. Mark it as
ours by not attributing it.

## 5. Provenance notation

```latex
\src{B1}                 % inline: this claim came from Book 1
\sources{B1, B3}         % entry footer: must match @sources exactly
\seealso{T-04-01, T-11-02}
\seesources              % points at Appendix A
```

Tag a claim inline when two sources differ, when a claim is surprising, or when
one book is doing something the others do not. Otherwise the entry footer is
enough. Over-tagging makes the book look like a bibliography.

## 6. Titles

Entry titles are noun phrases naming the thing, not sentences promising a
benefit.

| Yes | No |
|-----|----|
| The Thumbscrew | How to Find Anyone's Weakness |
| Manufactured Indispensability | Why You Should Make Yourself Needed |
| Protest Too Much | The Danger of People Who Insist They Are Honest |

Chapter titles name a subject. Part titles name a movement of the argument.

## 7. LaTeX hygiene

* No layout commands in content files (rule R12). Slots carry the formatting.
* `--` for en dash, `---` for em dash. No UTF-8 punctuation: the lint rejects
  non-ASCII characters outright.
* Escape `\#`, `\&`, `\_`, `\$` in prose. `~` for a non-breaking space before a
  short numeral: `Law~19`.
* Quotes: ``like this'', not "like this".
* Lists: `\item` only inside `tells`, `moves`, `counters`, `distilled`,
  `unique`, `terms`.
* Bold and italic are available but rationed. `\emph{}` for a term being
  introduced, `\textbf{}` almost never inside an entry.
* Never use `\texttt{}` in the body; it is for the docs and the front matter.

## 8. Worked shape of a finished entry

```latex
%% @kind: topic
%% @id: T-11-01
%% @title: Manufactured Indispensability
%% @subtitle: Being needed is a structure, not a sentiment
%% @chapter: c11
%% @order: 10
%% @status: stable
%% @sources: B1, B3
%% @updated: 2026-09-19

\topic{T-11-01}{Manufactured Indispensability}
        {Being needed is a structure, not a sentiment}

\begin{core}
...
\end{core}

\begin{mechanism}
...
\end{mechanism}

\begin{tells}
  \item ...
\end{tells}

\begin{moves}
  \item ...
\end{moves}

\begin{counters}
  \item ...
\end{counters}

\begin{cost}
...
\end{cost}

\sources{B1, B3}
\seesources
\seealso{T-12-02}
```

Word budget: 300–500. If it reaches 700, split it.
