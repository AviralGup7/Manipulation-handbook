# Ingest record — B9 · Milgram, *Behavioral Study of Obedience* (1963)

- register: B9 (primary, weight 95) — see registry/books.yaml
- file: `books/Milgram 1963 - Behavioral Study of Obedience.txt`
  (text transcript, prepared for the registry corpus; the PDF could not
  be mirrored into the repo because sandbox network access is restricted,
  so the article was read in full through the platform PDF fetcher
  (University of Miami psychology-department copy of the JASP article)
  and the transcript was written verbatim from it, omitting only the
  reference list; `tools/extract_corpus.py` was extended to pass `.txt`
  shelf files straight through to the corpus)
- paper: Journal of Abnormal and Social Psychology, 67(4), 371–378 —
  the classic peer-reviewed obedience experiment
- corpus: registry/corpus/B9.txt (local, git-ignored)
- ingested: 2026-09-20
- structure: abstract; introduction; general procedure; method (subjects,
  personnel, procedure, shock generator, prods); results (predictions,
  tension signs, distribution of scores, defiant remarks); discussion
  (13-feature situational analysis)

## What this source is

The **measured anchor for the authority material**. Where B4 supplies
the authority trigger (symbols fire deference) and B3 the costume and
disarm, B9 measures what the trigger yields when nothing material stands
behind the order: 26 of 40 subjects (65%) obeyed to the 450-volt maximum
on the word of a stranger in a gray technician's coat, against a
predicted 1.2%, with refusal costing nothing. Its claims are
laboratory-measurement claims; wherever the book claims symbols carry
obedience, B9 is the receipt. It adds the mechanics no other source has:
15-volt escalation, the four-prod exit closure, renegotiation denial
(``painful but not dangerous''), and the thirteen-feature situational
analysis.

## Mapping table

| B9 unit | -> entry | disposition |
|---|---|---|
| Method: subjects, rigged drawing, payment, sample shock | `T-18-05` | written |
| Method: experimenter/learner costume + manner; prods 1–4; special prods | `T-18-05`, `T-18-01` | written / additive |
| Method: 15-volt generator ladder; protest schedule (300 wall-pounding, 315 silence) | `T-18-05` | written |
| Results: 65% full obedience; defiance only after 300V; distribution | `T-18-05`, `T-18-01` | written / additive |
| Results: prediction gap (0–3%, mean 1.2%; observers also wrong) | `T-18-05` | written |
| Results: tension signs (14/40 laughter, 3 seizures, halt) | `T-18-05`, `T-23-04` (cross-ref only) | written |
| Footnote: 43 unpaid undergrads, similar results | `T-18-05` (conditions) | written |
| Discussion: 13-feature situational analysis | `T-18-05` (mechanism, compressed) | written |
| Discussion: features 5–6 (payment, fair lottery) | `T-24-02` (cross-ref only) | distilled |

## Numbers used verbatim in the book

26/40 (65%) to 450V; defiers 5@300, 4@315, 2@330, 1 each @345/360/375;
no stop before 300V; predictions 0–3% (mean 1.2%); 15V steps, 30
switches, 15–450V, sample shock 45V; prods 1–4 and the two special
prods, quoted exactly; nervous laughter 14/40, full seizures 3
(46-year-old encyclopedia salesman, experiment halted); pain rating
mean 13.42 on 14; 43 unpaid undergraduates, similar results; \$4.50
payment, "yours no matter what".

## Backlog

- Milgram's later variations (distance, setting de-institutionalization,
  two authorities) are NOT in the 1963 paper and were not used; a future
  ingest of *Obedience to Authority* (1974) could ground a c20/c24 entry
  on situational escape hatches.
