# Ingest record — B3 · Greene, *The 48 Laws of Power* (1998)

**Status: partially ingested.** 476 PDF pages. The laws feeding Parts I–II are
mapped and merged. The remainder is mapped below and scheduled against Parts
III–VII.

Source shape: a preface on the amoral treatment of power, then 48 laws. Each law
runs to a judgement, one or more transgressions, one or more observances, keys
to power, an image, a symbol, and a reversal.

## What was cut as padding

* Historical case narrative. This is roughly 80% of the book's length. Where a
  case *is* the lesson, the lesson is extracted and the case dropped; where a
  modern illustration genuinely helps, one is written for this handbook and
  filed as a `field` note rather than borrowed.
* The image and symbol apparatus. It is mnemonic decoration and does not
  transfer.
* Repeated restatement of a law inside its own keys-to-power section.

## What was kept that is structurally distinctive

* The **reversal** device — each law states when it should be broken. This
  handbook carries the same content in the `cost` slot of every entry, which
  is why no entry here is allowed to be missing one.
* The **transgression / observance** argument form: a rule justified by what
  happened to those who broke it and to those who kept it. Recorded as unique
  material at `T-01-05`.

## Mapping table

| law | → entry | disposition |
|---|---|---|
| preface — power as amoral | `T-01-03` | merged |
| 1 — never outshine the master | `T-04-03` additive; `T-09-02` written |
| 2 — friends and enemies | `T-12-03` | **planned** |
| 3 — conceal your intentions | `T-13-03` | **planned** |
| 4 — say less than necessary | `T-06-04`; `T-13-03` | partly merged / **planned** |
| 5 — reputation | `T-09-01` | written |
| 6 — court attention | `T-10-04` | **planned** |
| 7 — others do the work, you take the credit | `T-05-02`; `T-12-04` | partly merged / **planned** |
| 8 — make people come to you | `T-14-05` | **planned** |
| 9 — win through actions, not argument | `T-02-02`, `T-06-04`; `T-16-01` | additive: dossier pending for each |
| 10 — avoid the unhappy and unlucky | `T-08-01`; `T-26-03` | partly merged / **planned** |
| 11 — keep people dependent | `T-11-01`, `T-11-03` | partly written; **planned** |
| 12 — selective honesty to disarm | `T-04-02`; `T-18-01` | additive: dossier pending for each |
| 13 — appeal to self-interest | `T-04-02`, `T-05-02`; `T-15-01` | additive: dossier pending for each |
| 14 — pose as a friend, work as a spy | `T-07-01`, `T-07-02` | merged |
| 15 — crush your enemy totally | `T-21-01` | written |
| 16 — use absence | `T-10-05` | **planned** |
| 17 — cultivated unpredictability | `T-19-03` | **planned** |
| 18 — no fortresses; isolation is dangerous | `T-01-03`; `T-12-02`, `T-27-03` | partly merged / **planned** |
| 19 — know who you are dealing with | `T-03-01`, `T-08-01` | merged |
| 20 — do not commit | `T-01-03`; `T-08-02`, `T-12-02` | partly merged / **planned** |
| 21 — play a sucker to catch a sucker | `T-18-03` | **planned** |
| 22 — the surrender tactic | `T-08-02`; `T-21-02` | partly merged / written |
| 23 — concentrate your forces | `T-12-01` | written |
| 24 — the perfect courtier | `T-12-05` | written |
| 25 — re-create yourself | `T-17-04` | **planned** |
| 26 — keep your hands clean | `T-13-04` | written |
| 27 — cultlike following | `T-15-03` | **planned** |
| 28 — enter with boldness | `T-17-02` | written |
| 29 — plan to the end | `T-02-03`; `T-17-01` | partly merged / written |
| 30 — seem effortless | `T-02-04` | merged |
| 31 — control the options | `T-14-05`, `T-14-06` | **planned** |
| 32 — play to fantasies | `T-15-03` | **planned** |
| 33 — the thumbscrew | `T-04-01`, `T-04-04` | merged |
| 34 — act like a king | `T-09-02` | written |
| 35 — master timing | `T-02-03`; `T-17-01` | partly merged / written |
| 36 — disdain what you cannot have | `T-08-02`; `T-21-03` | partly merged / written |
| 37 — compelling spectacles | `T-10-06`; `T-17-05` | **planned** |
| 38 — think as you like, behave like others | `T-18-04` | written |
| 39 — stir up waters | `T-02-01`, `T-04-03`; `T-21-04` | partly merged / **planned** |
| 40 — despise the free lunch | `T-04-02`; `T-25-02` | partly merged / written |
| 41 — avoid a great man's shoes | `T-09-03` | written |
| 42 — strike the shepherd | `T-21-05` | **planned** |
| 43 — work on hearts and minds | `T-01-02`, `T-02-01`; `T-22-01` | additive: dossier pending for each |
| 44 — the mirror effect | `T-22-03` | **planned** |
| 45 — preach change, reform slowly | `T-17-06` | **planned** |
| 46 — never appear too perfect | `T-09-04` | **planned** (provisional; re-map before writing) |
| 47 — do not go past the mark | `T-28-02` | written |
| 48 — assume formlessness | `T-28-01` | written |

## Open items

* Laws 47–48 have been read and mapped (47 → `T-28-02` self-mastery: stopping at
  the mark is self-command; 48 → `T-28-01`). Law 46 remains provisional at
  `T-09-04` and must be read before writing; `T-13-05` is free again.
* Several laws map to more than one entry (1, 13, 39, 43). Each mapping needs
  its own dossier file — `B3-T-04-03.tex` and `B3-T-22-01.tex` are separate
  files even though they draw on the same law.
* The reversal sections must be read for every law before its entry is written.
  They are the source's own `cost` slot and skipping them produces entries
  that overstate.

## Revisions

* 2026-09-19 — laws 5, 1+34 and 41 written as `T-09-01`, `T-09-02`, `T-09-03`
  (chapter c09), each with a Layer A dossier; the law-1 residual beyond the
  vanity additive is the two-sided pricing rule, not a re-ingestion of `T-04-03`.
* 2026-09-19 — the scaffolded-then-written round: Laws 11, 15, 22, 23, 24, 26,
  28, 29, 35, 36, 38, 40 and 48 entries written. Two ids had been planned here
  but were committed as B1 slots by scaffold: `T-26-02` (Ordered Exit, B1 ch. 16)
  and `T-27-01` (The Bill for the Method, B1 ch. 16); this map's Law 10 planned
  half re-pointed `T-26-02` → `T-26-03` and Law 18's `T-27-01` → `T-27-03` per
  rule R21. B1's need-posture entry took `T-11-02`; Law 11's residual re-pointed
  to `T-11-03`. Law 47 read and mapped to the new c28 slot `T-28-02`.
* 2026-09-19 — renumbered 11 planned rows whose ids B4's merge had taken
  (`T-13-01`, `T-10-01`, `T-14-01/02`, `T-10-02`, `T-19-02`, `T-18-02`,
  `T-15-02`, `T-10-01`, `T-22-02`); each now points at the next free id in its
  chapter. Rows whose planned half had come to point at an already-written
  entry were re-marked `additive`. Law 5 keeps `T-09-01`; the provisional
  46–48 row moves to `T-09-04`. Drift of this kind is now rule R21.
