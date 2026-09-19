# TAXONOMY — where things go

The single most important decision when adding material is **which entry it
belongs to**. Get that wrong and the book becomes a pile. This file is the map.
It is authoritative: if an idea does not fit anywhere here, that is a discussion,
not a new part.

Organised **by subject**. Books are merged into it; the reader never sees the
book boundaries.

---

## Part I — THE TERRAIN  (`P1`)

What manipulation is, who does it, and what in you makes it work.
*Prerequisite for everything else.*

| ch | chapter | holds |
|----|---------|-------|
| `c01` | What Manipulation Actually Is | definitions, the 5/95 premise, manipulation vs persuasion vs power, the amoral-instrument view, intent as the ethical switch |
| `c02` | The Manipulator's Equipment | what the practitioner is actually good at: reading motive, controlling their own affect, patience, indifference to being liked |
| `c03` | Character Types | typologies of the person working you **and** of the person being worked. Sparkman's street types, Greene's five dangerous marks |
| `c04` | Your Own Load-Bearing Points | the thumbscrew: insecurity, need, guilt, vanity, fear of conflict; self-audit |

## Part II — READING  (`P2`)

Intelligence before action. Every tactic in Parts III–V fails without this.

| ch | chapter | holds |
|----|---------|-------|
| `c05` | Motives Before Words | why stated reasons are never the reason; how to find the real one |
| `c06` | Tells and Consistency | protesting too much, story drift, the two-tellings test, behaviour over declaration |
| `c07` | Gathering Information | asking indirectly, posing as a friend, listening as an instrument, what to record |
| `c08` | Judging Who You Are Dealing With | do-not-offend-the-wrong-person; cost/benefit of engaging a given type |

## Part III — POSITIONING  (`P3`)

Structure, not conversation. Power that exists before anyone speaks.

| ch | chapter | holds |
|----|---------|-------|
| `c09` | Reputation | building it, guarding it, attacking someone else's |
| `c10` | Attention, Absence and Scarcity | court attention, use absence, create value by withdrawing, conspicuousness |
| `c11` | Dependence | "I don't need you, you need me"; indispensability; keeping people unable to do without you; favouritism as a lever |
| `c12` | Alliances, Patrons and Courts | courtiership, concentration of force on one patron, not committing, using enemies rather than friends |
| `c13` | Concealment and Indirection | conceal intentions, say less, keep hands clean, cat's-paws and scapegoats, formlessness |

## Part IV — PERSUASION  (`P4`)

Moving a mind without moving a muscle.

| ch | chapter | holds |
|----|---------|-------|
| `c14` | Framing and Controlled Choice | dealing the cards, the lesser of two evils, controlled options, contrast |
| `c15` | The Appeals | self-interest over gratitude, fantasy over truth, the need to believe, cultlike followings |
| `c16` | Argument and Demonstration | win through actions, the unargue technique, when to shut up, whose mind can actually be changed |
| `c17` | Delivery | timing, boldness, effortlessness, re-creating yourself, acting the part, spectacles |
| `c18` | Appearance and Compliance | selective honesty to disarm, the Trojan-horse gift, playing the sucker, seeming dumber, the mirror effect |

## Part V — PRESSURE  (`P5`)

Hard tactics. Highest cost, highest blowback. Read `limits` twice here.

| ch | chapter | holds |
|----|---------|-------|
| `c19` | Guilt, Fear and Obligation | a little pressure and its place, suspended terror, unpredictability as a weapon |
| `c20` | Coercion and the Dirty Way | ultimatums, when all else fails, the legal and relational cost |
| `c21` | Conflict | crush totally, strike the shepherd, surrender as a tactic, disdain as revenge, stirring waters |
| `c22` | Working the Hearts | seduction over coercion, operating on what a person holds dear and fears |

## Part VI — DEFENCE  (`P6`)

The half of the book that pays for itself. Can be read first.

| ch | chapter | holds |
|----|---------|-------|
| `c23` | Detection | assembling the tells from Parts I–V into a live checklist |
| `c24` | Inoculation and Refusal | pre-commitments, delay, naming the move aloud, the counters that work across tactics |
| `c25` | Money and Contracts | avoiding being taken in financial dealings, free lunches, where the money actually goes |
| `c26` | Exit and Aftermath | disengaging, boundaries, handling ingratitude, not becoming what you studied |

## Part VII — COST  (`P7`)

| ch | chapter | holds |
|----|---------|-------|
| `c27` | What You Get Out of Using People | the price of the practice, isolation, the court you end up living in |
| `c28` | Self-Mastery | emotional control as the precondition, formlessness as the end state |

---

## Numbering

* Entry id: `T-<chapter>-<nn>`, e.g. `T-11-02` = chapter `c11`, entry 2.
* `@order` inside a chapter: multiples of 10 (10, 20, 30) so entries can be
  inserted without renumbering.
* Chapters are numbered globally `c01`…`c99`; parts group them. Moving a chapter
  between parts changes only its `@part` field.
* **IDs are permanent.** Never renumber to tidy up.

## Deciding where something goes — the test

Ask, in order:

1. Is it about **what a person is** → Part I.
2. Is it about **finding something out** → Part II.
3. Is it about **a standing arrangement** (reputation, dependence, alliances,
   secrecy) → Part III.
4. Is it about **changing a mind in a conversation** → Part IV.
5. Is it about **applying pressure or fighting** → Part V.
6. Is it about **resisting any of the above** → Part VI.
7. Is it about **the bill that arrives afterwards** → Part VII.

If it is about both an attack and its defence, the attack goes in Parts III–V
and the defence goes in its `counters` slot **and**, if it generalises, in
Part VI. Never duplicate the same content in both places; cross-reference with
`\seealso{}`.
