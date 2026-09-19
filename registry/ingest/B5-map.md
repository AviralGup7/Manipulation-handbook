# B5 ingest map -- Never Split the Difference (Voss, 2016)

- register: B5 (primary, weight 85) -- see registry/books.yaml
- file: books/E001005.pdf (uploaded to origin/main, relocated here per the shelf rule)
- corpus: registry/corpus/B5.txt (local, git-ignored)
- ingested: 2026-09-19 (start)
- structure: 10 chapters + preparation appendix

## What this source is

FBI hostage-negotiation method written up for business negotiation. Where B1
gives street tactics, B3 strategy, and B4 the laboratory trigger, B5 gives the
live interaction protocol: what to say, in which order, and what to listen
for while it lands. Its claims are domain-bound (high-stakes bargains), so
*strategic* claims defer to B3 and *mechanism* claims to B4 where they
overlap; B5 owns turn-by-turn interaction structure, which slots directly
into `application` and `feedback`.

Chapter page ranges (printed): ch1 pp.13, ch2 pp.36, ch3 pp.70, ch4 pp.102,
ch5 pp.130, ch6 pp.152, ch7 pp.188, ch8 pp.216, ch9 pp.249, ch10 pp.281.

## Mapping table

| B5 unit | -> entry | disposition |
|---|---|---|
| ch.1 the new rules (System 1/2, life is negotiation) | `T-14-01` | additive |
| ch.2 be a mirror (isopraxism, late-night FM DJ voice, dynamic silence) | `T-07-04` | written |
| ch.2 late-night FM DJ voice (voice-down as de-escalation) | `T-07-01` | additive |
| ch.3 label their pain (labels, tactical empathy, accusation audit) | `T-14-07` | written |
| ch.4 beware yes / master no (autonomy, no-oriented questions) | `T-24-05` | written |
| ch.5 get a "that's right" (summary as commitment device; "you're right" as counterfeit) | `T-16-05` | written |
| ch.6 bend their reality (loss aversion, anchoring, ranges, the fair trap) | `T-25-03` | written |
| ch.7 illusion of control (calibrated How/What questions) | `T-14-08` | written |
| ch.8 guarantee execution (7-38-55, three kinds of yes, Pinocchio effect) | `T-06-05` | written |
| ch.9 bargain hard (Ackerman system, precise odd numbers, throw-in) | `T-25-04` | written |
| ch.10 find the black swan (unknown unknowns, similarity, face time) | `T-05-03` | written |
| appendix: negotiation one-sheet | folded into ch.9 entry | merged |

## Slot routing for B5 material

| B5's argument move | handbook slot |
|---|---|
| the compliance pattern and its trigger cue | `mechanism` |
| what the counterpart can observe changing live | `feedback` |
| conditions under which the tool misfires | `failure` |
| the defence, including turning the tool around | `countermeasures` |
| domain boundary (hostage/bargain vs everyday) | `conditions` |

## Open items

* ch.1 is mostly manifesto; its usable content is the System 1/2 framing,
  which deepens `T-14-01` additively. Do not build an entry from it.
* The Mehrabian 7-38-55 figures are contested in the literature (they come
  from two studies on feeling/attitude communication, not general
  conversation). `T-06-05` must carry that boundary in `conditions`.
* "Complete redesign" latitude (user, 2026-09-19) does NOT reopen the
  seven-question format; it covers restructuring placement -- B5 entries go
  where the handbook's chapters say, not where B5's ToC says.
