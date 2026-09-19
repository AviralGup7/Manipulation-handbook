# Ingest record — B4 · Cialdini, *Influence: The Psychology of Persuasion* (1984)

**Status: mapped, ingestion started.** 279 PDF pages. Structure verified against
the book's own contents page (PDF p. 5).

| ch. | title (as label) | pages |
|---|---|---|
| intro | Primitive Consent for an Automatic Age | 1–12 |
| 1 | Weapons of Influence | 13–42 |
| 2 | Reciprocation | 43–86 |
| 3 | Commitment and Consistency | 87–125 |
| 4 | Social Proof | 126–156 |
| 5 | Liking | 157–177 |
| 6 | Authority | 178–204 |
| 7 | Scarcity | 205–210 |
| epilogue | Instant Influence | 210 |
| — | Notes / Bibliography / Index | 211–279 |

Source shape: seven chapters, each one compliance principle. Every chapter runs
the same argument — a principle, the cue that triggers it, the field evidence,
the conditions under which it fails, and how a target can defend against it.

## Why this book ingests additively rather than competitively

This is the important structural finding, and it is the reason the whole
architecture survives a fourth source.

**B4 originates almost no new tactic names.** It supplies the causal layer
underneath structures the handbook already has. Where B1 says *do this* and B3
says *this is the strategic shape of it*, B4 says *here is the automatic
response being exploited, here is the single cue that fires it, and here is the
condition under which it stops working.*

That maps one-to-one onto slots that already exist:

| B4's argument move | handbook slot |
|---|---|
| the compliance pattern and its trigger cue | `mechanism` |
| observable signs a target can watch for | `tells` |
| conditions under which the principle fails | `cost` |
| the defence, including redirecting the technique's own force | `counters` |
| the field setting it was observed in | `field` |

So ingestion splits into two kinds of work, and neither one edits a sentence
that B1 or B3 already wrote:

1. **Additive dossiers onto existing entries** (`sources/B4/B4-T-nn-nn.tex`).
   A dossier is a *new file*, so rule R10 structurally guarantees that no B1 or
   B3 material can be displaced. The Layer B entry gains a sentence in
   `mechanism` or `cost` only where B4 says something the other two do not, and
   the entry's `@sources` list grows by one token.
2. **New entries in the empty scaffolding of Parts III–VI**, where B4 is often
   the primary source and there is nothing to conflict with.

## Weight: 85, and why that number does not decide mechanism claims

Register weights are tie-break priorities for *strategic* claims: B3 (95)
outranks B1 (90) outranks B4 (85). That ordering is correct for questions of
position, timing and reputation, which is B3's domain.

It is **not** used for empirical questions. On "what actually happens in the
target's head", B4 is the only laboratory source in the register, so there is
no tie to break and the weight never fires. Where B4 and B1 make competing
*empirical* claims, B4 wins on evidence and the disagreement is recorded in the
entry's `cost` slot as a named minority view rather than deleted (rule R6, docs/
INGESTION.md).

## What was cut as padding

* **Experimental apparatus.** Study designs, sample sizes, control conditions
  and the citation trail. The finding is kept; the methodology narrative is
  dropped. Where a study's design *is* the reason to believe the finding, one
  clause of it survives in `mechanism`.
* **Case narrative.** The author's own undercover stints, the dealership, the
  restaurant, the cult, the telephone survey. Where the case is the lesson the
  lesson is extracted and the story dropped; where a modern illustration
  genuinely helps, one is written fresh for this handbook and filed as a `field`
  note. Nothing is borrowed.
* **Notes, Bibliography, Index** (pp. 211–279). Not ingested.
* **Restatement of the ch. 1 frame.** Every chapter re-establishes the
  automatic-response premise. It is stated once, at `T-14-01`, and the later
  chapters cite it rather than repeat it.
* **Authorial self-positioning.** The first-person account of being a "patsy"
  is dropped as framing. The *method* it justifies — infiltrating the trade to
  learn the technique from inside — is recorded here and at `T-01-05` as a
  distinctive research stance, in the handbook's own words.

## What was kept that is structurally distinctive

* **The trigger-feature model.** A single salient cue fires an entire
  compliance routine without the substance being evaluated. This is what makes
  the `mechanism` slot non-hand-wavy across the whole book, and it is unique to
  B4.
* **Boundary conditions as first-class content.** Each principle ships with the
  circumstances that defeat it. This is the same function B3's *reversal*
  device performs, from the opposite direction — B3 asks *when should the
  practitioner stop*, B4 asks *when does it stop working*. Both land in `cost`.
* **The redirect defence.** The observation that the correct answer to a
  compliance technique is usually not to attack it but to let it spend itself
  on a false premise. Recorded at `T-24-01`; it is a distinctive framing and is
  not in B1 or B3.
* **Contrast as a framing device.** Perceptual contrast — a second option
  judged against a first rather than on its own merits. Recorded at `T-14-02`;
  B3 has the strategic cousin (law 16, absence) but not the mechanism.

## Mapping table

`additive` = a B4 dossier is filed against an entry that already exists, and
the entry's prose changes only by addition. `new` = B4 is the primary source
for an entry that has not been written yet.

### ch. 1 — Weapons of Influence (pp. 13–42)

| material | → entry | disposition |
|---|---|---|
| automatic compliance; a cue fires a whole routine | `T-14-01` | **new** (c14) |
| why the operating minority succeeds: most responses are not deliberated | `T-01-01` | additive |
| influence vs manipulation vs persuasion, mechanism view | `T-01-02` | additive |
| perceptual contrast; the decoy second option | `T-14-02` | **new** (c14) |
| the epilogue's "instant" acceleration of the same frame | `T-14-01` | merged into the same entry |

### ch. 2 — Reciprocation (pp. 43–86)

| material | → entry | disposition |
|---|---|---|
| the favour as a load-bearing obligation | `T-04-02` | additive (B4 becomes the mechanism authority) |
| debt created without being asked for | `T-19-01` | **new** (c19) |
| unequal exchange: a small gift buys a large concession | `T-19-02` | **new** (c19) |
| rejection-then-retreat; the reciprocal concession | `T-16-01` | **new** (c16) |
| refusing a debt you did not authorise | `T-24-01` | **new** (c24) |
| the sample as a purchase already begun | `T-25-01` | **planned** (c25) |

### ch. 3 — Commitment and Consistency (pp. 87–125)

| material | → entry | disposition |
|---|---|---|
| a stated position is defended regardless of its origin | `T-06-04` | additive |
| the small first yes | `T-14-03` | **new** (c14) |
| written, active, public, effortful — the four amplifiers | `T-14-04` | **new** (c14) |
| the price that changes after the commitment is made | `T-25-02` | **new** (c25) |
| spotting a commitment you did not choose | `T-24-02` | **new** (c24) |

### ch. 4 — Social Proof (pp. 126–156)

| material | → entry | disposition |
|---|---|---|
| the crowd as evidence | `T-15-01` | **new** (c15) |
| uncertainty and similarity: the two conditions that switch it on | `T-15-02` | **new** (c15) |
| a manufactured consensus; planted audiences | `T-13-01` | **new** (c13) |
| reading a room that has been seeded | `T-23-01` | **new** (c23) |
| reputation as accumulated social proof | `T-09-01` | **planned** (c09) |
| bystander diffusion | `T-21-03` | **planned** (c21) |

### ch. 5 — Liking (pp. 157–177)

| material | → entry | disposition |
|---|---|---|
| liking as a handle, and its five components | `T-22-01` | **new** (c22) |
| association and borrowed warmth | `T-22-02` | **new** (c22) |
| flattery works on the person who knows it is flattery | `T-04-03` | additive |
| familiarity manufactured on purpose | `T-22-03` | **planned** (c22) |
| spotting manufactured rapport | `T-23-02` | **new** (c23) |

### ch. 6 — Authority (pp. 178–204)

| material | → entry | disposition |
|---|---|---|
| the symbols of authority, separable from the substance | `T-18-01` | **new** (c18) |
| titles, uniform, trappings | `T-18-02` | **new** (c18) |
| deference to a claimed credential | `T-08-01` | additive |
| testing a credential before deferring | `T-23-03` | **new** (c23) |

### ch. 7 — Scarcity (pp. 205–210)

| material | → entry | disposition |
|---|---|---|
| value as a function of availability | `T-10-01` | **new** (c10) |
| the reactance trigger: a loss of freedom is defended | `T-10-02` | **new** (c10) |
| limited numbers, deadlines, and newness | `T-10-03` | **new** (c10) |
| refusing a deadline | `T-24-03` | **new** (c24) |
| absence as deliberate scarcity | `T-10-02` | cross-reference to B3 law 16 |

## Sequencing

Ingestion proceeds one chapter at a time, in book order, because ch. 1's frame
is cited by every later chapter. Each chapter is a separate batch:

1. ch. 1 → `T-14-01`, `T-14-02` + additive dossiers on `T-01-01`, `T-01-02`
2. ch. 2 → `T-19-01`, `T-19-02`, `T-16-01`, `T-24-01` + additive on `T-04-02`
3. ch. 3 → `T-14-03`, `T-14-04`, `T-25-02`, `T-24-02` + additive on `T-06-04`
4. ch. 4 → `T-15-01`, `T-15-02`, `T-13-01`, `T-23-01`
5. ch. 5 → `T-22-01`, `T-22-02`, `T-23-02` + additive on `T-04-03`
6. ch. 6 → `T-18-01`, `T-18-02`, `T-23-03` + additive on `T-08-01`
7. ch. 7 → `T-10-01`, `T-10-02`, `T-10-03`, `T-24-03`

**planned** rows are deliberately left unwritten. They are recorded so that
nothing is silently dropped, and they will be filled by later batches or by a
fifth source that covers the ground better.

## Verification

* `python3 tools/extract_corpus.py --only B4` → `registry/corpus/B4.txt`
  (658 KB) and its normalised form, which rule R15 reads to machine-check that
  no run of nine or more words of source expression has leaked into the
  handbook. The corpus is git-ignored: it is large, regenerable, and third-party
  expression.
* The scan lives at `books/The Psychology of Persuasion.pdf`, recorded in the
  `file:` field of B4's register block. See `books/README.md`.
* Rule R4: B4 is `rank: primary`, so it may originate claims. Rule R11: every
  B4 citation requires a dossier in `sources/B4/`.
