# Ingest record — B8 · Bond & DePaulo, *Accuracy of Deception Judgments* (2006)

- register: B8 (primary, weight 95) — see registry/books.yaml
- file: `books/Bond & DePaulo 2006 - Accuracy of Deception Judgments.txt`
  (text transcript, prepared for the registry corpus; the PDF could not be
  mirrored into the repo because sandbox network access is restricted, so
  the article was read in full through the platform PDF fetcher — ACLU
  court-filed copy of the PSPR article — and the transcript was written
  verbatim from it, omitting only the reference list and OCR-garbled
  figure tables; `tools/extract_corpus.py` was extended to pass `.txt`
  shelf files straight through to the corpus)
- paper: Personality and Social Psychology Review, 10(3), 214–234,
  DOI 10.1207/s15327957pspr1003_2 — peer-reviewed meta-analysis,
  one of the most-cited works in deception research
- corpus: registry/corpus/B8.txt (local, git-ignored)
- ingested: 2026-09-20
- structure: abstract; characterizations of deception and the
  double-standard framework; the review (206 documents, 24,483 judges,
  4,435 senders, 384 receiver samples); results (percentage correct,
  standardized mean differences, six moderator analyses); discussion

## What this source is

The **measured ground truth beneath the detection chapters**. Where B7
supplies a practitioner's detection method and B5 detects stress in live
negotiation, B8 quantifies what any unaided behavioural detection can
achieve: a 53.98% mean accuracy ceiling, an asymmetric error pattern
(truths accepted 61.34%, lies caught 47.55%), a channel hierarchy (ear
over eye), a motivation backfire, and a null result for expertise. Its
claims are laboratory-measurement claims; they anchor, and where they
conflict override, practitioner confidence anywhere in the book. The
double-standard framework also explains why the liar stereotype fails:
calm, rationalized deceit does not match the moral caricature judges
carry.

## Mapping table

| B8 unit | -> entry | disposition |
|---|---|---|
| abstract + Results: percentage correct, weighted means, asymmetry | `T-23-09` | written |
| Results: deception medium (video/audio/audiovisual; face/body nulls) | `T-23-09`, `T-23-05` | written / additive |
| Results: motivation (motivated senders look deceptive) | `T-23-09`, `T-23-04` | written / additive |
| Results: baseline exposure (55.91% vs 52.26%) | `T-23-09`, `T-23-05`, `T-23-04` | written / additive |
| Results: preparation (unprepared senders easier) | `T-23-09` | written |
| Results: receiver expertise null (d = −.025) | `T-23-09`, `T-23-05`, `T-23-04` | written / additive |
| Results: interaction-partner truth bias (d = .26) | `T-23-09` (dossier only) | distilled |
| Discussion: double standard, liar stereotype | `T-23-04`, `T-23-09` | additive / written |
| Discussion: real-world discovery via evidence + third parties (Park et al. 2002) | `T-23-09`, `T-24-06` (cross-ref only) | written |

## Numbers used verbatim in the book

All figures carried into entries were taken from the read transcript:
53.98% / 53.46% weighted (CI 53.31–53.59); 61.34% truths vs 47.55% lies;
55.23% truth classifications; d′ = .24 (max 54.79%); d ≈ .39–.40 (60th
percentile of 474 effects); video .077 / audio .419 / audiovisual .438;
face-only .01 / body-only −.15; motivation 46.84% vs 54.44% (video truth
calls); baseline 55.91% vs 52.26% (d = .239); preparation d = −.144 (and
planned-appears-truthful d = .133); expertise d = −.025 (CI −.105 to
.055), experts 52.28% vs novices 55.69% truth calls; partners d = .26;
quartiles 50.07–58.00; true between-study SD 4.52 points.

## Backlog

- The motivation moderator's implications for interview design could
  ground a future entry (motivated-to-be-believed reads as guilty);
  left unbuilt — no natural home yet that would not duplicate T-23-09.
