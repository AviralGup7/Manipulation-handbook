#!/usr/bin/env python3
"""
build_index.py -- regenerate every derived file from the .tex headers.

Run it after adding ANY file:

    make index          (or: python3 tools/build_index.py)

It writes, and is the ONLY thing allowed to write:

    registry/compiled/booknames.tex   book register -> TeX macros
    registry/compiled/index.tex       parts -> chapters -> entries
    registry/compiled/dossiers.tex    Appendix A, the audit trail
    registry/compiled/coverage.tex    "State of the build" appendix
    registry/coverage.md              the table a human or agent reads first

Idempotent: running it twice changes nothing. Files are only rewritten when
their content actually differs, so git diffs stay meaningful.

Adding a book never requires editing main.tex, this script, or any existing
content file. See docs/INGESTION.md.
"""

from __future__ import annotations

import datetime as _dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hb_lib import (DIR_COMPILED, ROOT, Repo, rel, tex_escape,  # noqa: E402
                    write_if_changed)

BANNER = ("%% =====================================================================\n"
          "%%  GENERATED FILE -- DO NOT EDIT BY HAND.\n"
          "%%  Regenerate with:  make index   (tools/build_index.py)\n"
          "%%  Source of truth: the '%% @...' header block of every managed .tex.\n"
          "%% =====================================================================\n")

BODY_STATUSES = ("stable", "draft")


# ---------------------------------------------------------------------------
def gen_titles(repo: Repo) -> str:
    out = [BANNER]
    out.append("%% Entry-title lookups, emitted from the %% @title headers.")
    out.append("%% \\seealso resolves ids against this file, so the reader never")
    out.append("%% sees a bare id (rule R22). \\csname is required because a TeX")
    out.append("%% control word cannot contain a digit.")
    out.append("%%")
    out.append("%% Written entries define \\hbtitle@<id>; entries that are only")
    out.append("%% planned define \\hbpending@<id>, so \\seealso can mark them")
    out.append("%% honestly as unwritten instead of pointing at a missing")
    out.append("%% section. Each id is defined twice -- plain, and with one")
    out.append("%% leading space, because comma lists are written \"A, B\" and a")
    out.append("%% list element may carry the space after the comma with it.\n")
    for t in sorted(repo.topics.values(), key=lambda t: t.id):
        val = tex_escape(t.title)
        written = t.status in BODY_STATUSES
        macro = "hbtitle" if written else "hbpending"
        out.append(f"\\expandafter\\newcommand\\csname {macro}@{t.id}"
                   f"\\endcsname{{{val}}}")
        out.append(f"\\expandafter\\newcommand\\csname {macro}@ {t.id}"
                   f"\\endcsname{{{val}}}")
    return "\n".join(out) + "\n"


def gen_sourceslist(repo: Repo) -> str:
    out = [BANNER]
    out.append("%% The reader-facing source register, emitted from")
    out.append("%% registry/books.yaml (rule: the front matter never")
    out.append("%% hand-lists sources -- a hand list is how B4 and B5")
    out.append("%% went missing from it).\n")
    out.append("\\begingroup\\small")
    out.append("\\begin{itemize}")
    for b in repo.books:
        if b.get("status") != "active":
            continue
        name = tex_escape(str(b.get("author", "") or b["id"]))
        title = tex_escape(str(b.get("title", "")))
        year = tex_escape(str(b.get("year", "")))
        contrib = tex_escape(str(b.get("contributed", "") or ""))
        line = f"\\item[\\textbf{{{b['id']}}}] {name}, \\emph{{{title}}} ({year})."
        if contrib:
            line += " Contributed: " + contrib
        out.append(line)
    out.append("\\end{itemize}")
    out.append("\\par\\endgroup")
    return "\n".join(out) + "\n"


def gen_booknames(repo: Repo) -> str:
    out = [BANNER]
    out.append("%% Book register, emitted from registry/books.yaml.")
    out.append("%% Accessors (\\bookname{B1} etc.) are defined in style/entry.sty.")
    out.append("%% \\csname is required because a TeX control word cannot contain a")
    out.append("%% digit: \\booknameB1 would be read as \\booknameB followed by 1.\n")
    for b in repo.books:
        bid = b["id"]
        for field, key in (("name", "title"), ("author", "author"),
                           ("year", "year"), ("short", "short")):
            val = tex_escape(str(b.get(key, "") or bid))
            out.append(f"\\expandafter\\newcommand\\csname hb@book@{bid}@{field}"
                       f"\\endcsname{{{val}}}")
    out.append("")
    out.append("%% Front-matter counters")
    out.append("\\newcommand{\\hbedition}{1}")
    stamp = os.environ.get("HB_BUILD_STAMP") or _dt.date.today().isoformat()
    out.append(f"\\newcommand{{\\hbbuildstamp}}{{{stamp}}}")
    n_pub = sum(1 for t in repo.topics.values() if t.status in BODY_STATUSES)
    n_draft = sum(1 for t in repo.topics.values() if t.status == "draft")
    n_ch_done = sum(1 for c in repo.chapters.values()
                    if any(t.status in BODY_STATUSES
                           for t in repo.topics_in_chapter(c.id)))
    out.append(f"\\newcommand{{\\hbtopiccount}}{{{n_pub} written "
               f"({n_draft} in draft) across {n_ch_done} of "
               f"{len(repo.chapters)} chapters}}")
    n_active = sum(1 for b in repo.books if b.get("status") == "active")
    out.append(f"\\newcommand{{\\hbbookcount}}{{{n_active}}}")
    n_cases = sum(1 for c in repo.cases.values() if c.status == "stable")
    out.append(f"\\newcommand{{\\hbcasecount}}{{{n_cases}}}")
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------------------
def gen_index(repo: Repo) -> str:
    out = [BANNER]
    out.append("%% Reading order: Part -> Chapter -> Entry.\n")
    for part in repo.ordered_parts():
        pid = part.id
        out.append(f"%% ---- {pid}: {part.title} ----")
        out.append(f"\\part{{{tex_escape(part.title)}}}")
        out.append(f"\\label{{{pid}}}")
        out.append(f"\\input{{{rel(part.path)[:-4]}}}")
        chapters = repo.chapters_in_part(pid)
        if not chapters:
            out.append(f"%% (no chapters yet in {pid})")
        for ch in chapters:
            out.append(f"%% ---- {ch.id}: {ch.title} ----")
            sub = ch.meta.get("subtitle", "")
            out.append(f"\\chaphead{{{tex_escape(ch.title)}}}"
                       f"{{{tex_escape(sub)}}}")
            n_pub = sum(1 for t in repo.topics_in_chapter(ch.id)
                        if t.status in BODY_STATUSES)
            out.append(f"\\hbchapterstate{{{n_pub}}}")
            out.append(f"\\label{{{ch.id}}}")
            out.append(f"\\input{{{rel(ch.path)[:-4]}}}")
            topics = repo.topics_in_chapter(ch.id)
            published = [t for t in topics if t.status in BODY_STATUSES]
            for t in published:
                out.append(f"\\input{{{rel(t.path)[:-4]}}}")
            planned = [t for t in topics if t.status not in BODY_STATUSES]
            if planned:
                ids = ", ".join(t.id for t in planned)
                out.append(f"%% deferred to the build-state appendix: {ids}")
        # case interludes positioned at the end of this part
        for c in repo.cases_after_part(pid):
            out.append(f"%% ---- case {c.id}: {c.title} ----")
            out.append(f"\\input{{{rel(c.path)[:-4]}}}")
        out.append("")
    if not repo.parts:
        out.append("%% no parts declared yet -- nothing to typeset")
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------------------
def gen_dossiers(repo: Repo) -> str:
    out = [BANNER]
    out.append("%% Appendix A. Grouped by entry, then by book, in ingest order.\n")
    emitted = 0
    for part in repo.ordered_parts():
        for ch in repo.chapters_in_part(part.id):
            topics = repo.topics_in_chapter(ch.id)
            block = []
            for t in topics:
                ds = repo.dossiers_for(t.id)
                # skeleton dossiers are scaffolds, not content: their bodies
                # are TODO templates and must never be typeset into the book
                ds = [d for d in ds
                      if getattr(d, "status", "") != "skeleton"]
                if not ds:
                    continue
                block.append(f"\\subsection*{{{t.id}\\ \\textbar\\ "
                             f"{tex_escape(t.title)}}}")
                for d in ds:
                    block.append(f"\\input{{{rel(d.path)[:-4]}}}")
            if block:
                out.append(f"%% ===== {part.title} / {ch.title} =====")
                out.append(f"\\section*{{{tex_escape(ch.title)}}}")
                out.extend(block)
                out.append("")
                emitted += len(block)
    if emitted == 0:
        out.append("%% no dossiers filed yet")
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------------------
def gen_coverage_tex(repo: Repo) -> str:
    out = [BANNER]
    out.append("%% State of the build: what is written, what is outstanding.\n")
    out.append("\\chapter{State of the Build}")
    out.append("\\label{app:coverage}")
    out.append("\\begin{chapterblurb}")
    out.append("This book is written incrementally, one entry at a time. The")
    out.append("table below is generated, so it always tells the truth about")
    out.append("what is finished and what is still scaffolding.")
    out.append("\\end{chapterblurb}")

    n_pub = sum(1 for t in repo.topics.values() if t.status == "stable")
    n_draft = sum(1 for t in repo.topics.values() if t.status == "draft")
    n_plan = sum(1 for t in repo.topics.values()
                 if t.status not in ("stable", "draft"))
    out.append("")
    out.append(f"\\noindent Published: \\textbf{{{n_pub}}}\\quad "
               f"In draft: \\textbf{{{n_draft}}}\\quad "
               f"Planned: \\textbf{{{n_plan}}}\\quad "
               f"Sources ingested: \\textbf{{{len(repo.books)}}}")
    out.append("")
    roll = []
    pub = [t for t in repo.topics.values() if t.status in BODY_STATUSES]
    for b in repo.books:
        bid = b["id"]
        cited = sum(1 for t in pub if bid in t.sources)
        orig = sum(1 for t in pub if t.sources and t.sources[0] == bid)
        doss = sum(1 for d in repo.dossiers.values() if d.meta.get("book") == bid)
        roll.append(f"\\textbf{{{bid}}} originates {orig}, "
                    f"is cited in {cited}, files {doss} dossiers")
    out.append("\\noindent\\small\\hbcolor{hbmuted}Contribution by source: "
               + "; ".join(roll) + ".")
    out.append("")

    for part in repo.ordered_parts():
        out.append(f"\\section*{{{tex_escape(part.title)}}}")
        out.append("\\begingroup\\small")
        out.append("\\begin{itemize}")
        for ch in repo.chapters_in_part(part.id):
            topics = repo.topics_in_chapter(ch.id)
            marks = []
            for t in topics:
                sym = {"stable": "$\\bullet$", "draft": "$\\circ$"}.get(t.status, "$\\cdot$")
                srcs = ",".join(t.sources) or "--"
                marks.append(f"{sym}\\,\\texttt{{{t.id}}} "
                             f"{tex_escape(t.title)} [{srcs}]")
            body = "; ".join(marks) if marks else "\\emph{no entries yet}"
            out.append(f"\\item \\textbf{{{tex_escape(ch.title)}}} --- {body}")
        out.append("\\end{itemize}")
        out.append("\\par\\endgroup")
        out.append("")
    cases = sorted(repo.cases.values(), key=lambda c: c.id)
    if cases:
        out.append("\\section*{Case interludes}")
        out.append("\\begingroup\\small")
        out.append("\\begin{itemize}")
        for c in cases:
            comb = [x.strip() for x in c.meta.get("combines", "").split(",") if x.strip()]
            out.append(f"\\item \\textbf{{{c.id} {tex_escape(c.title)}}} --- "
                       f"after {c.meta.get('after-part','?')}; "
                       f"weaves {len(comb)} entries: "
                       + ", ".join(f"\\texttt{{{x}}}" for x in comb))
        out.append("\\end{itemize}")
        out.append("\\par\\endgroup")
        out.append("")
    out.append("\\begingroup\\footnotesize\\hbcolor{hbmuted}")
    out.append("$\\bullet$ published\\quad $\\circ$ draft\\quad "
               "$\\cdot$ planned scaffolding\\par\\endgroup")
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------------------
def gen_coverage_md(repo: Repo) -> str:
    L = []
    L.append("# Coverage map\n")
    L.append("_GENERATED by `tools/build_index.py`. Do not edit._\n")
    L.append("Read this file **before** writing anything. It is the fastest way")
    L.append("to find out whether a topic already exists, and which books have")
    L.append("already contributed to it.\n")
    L.append("## Sources\n")
    L.append("| id | rank | w | title | author | year | dossiers | cited-in | originates |")
    L.append("|----|------|---|-------|--------|------|----------|----------|------------|")
    pub = [t for t in repo.topics.values() if t.status in BODY_STATUSES]
    for b in repo.books:
        n = sum(1 for d in repo.dossiers.values() if d.meta.get("book") == b["id"])
        cited = sum(1 for t in pub if b["id"] in t.sources)
        orig = sum(1 for t in pub if t.sources and t.sources[0] == b["id"])
        L.append(f"| {b['id']} | {b.get('rank','')} | {b.get('weight','')} "
                 f"| {b.get('title','')} | {b.get('author','')} "
                 f"| {b.get('year','')} | {n} | {cited} | {orig} |")
    L.append("")
    L.append("## Entries\n")
    L.append("| entry | status | sources | title | chapter | words |")
    L.append("|-------|--------|---------|-------|---------|-------|")
    for part in repo.ordered_parts():
        for ch in repo.chapters_in_part(part.id):
            for t in repo.topics_in_chapter(ch.id):
                L.append(f"| `{t.id}` | {t.status or '?'} | "
                         f"{', '.join(t.sources) or '--'} | {t.title} | "
                         f"{ch.title} | {t.word_count()} |")
    L.append("")
    L.append("## Case interludes\n")
    L.append("Narratives that weave existing entries against one situation. "
             "No new doctrine; every move names its entry.\n")
    L.append("| case | title | after part | combines | words |")
    L.append("|------|-------|------------|----------|-------|")
    for c in sorted(repo.cases.values(), key=lambda x: x.id):
        comb = [x.strip() for x in c.meta.get("combines", "").split(",") if x.strip()]
        L.append(f"| `{c.id}` | {c.title} | {c.meta.get('after-part','?')} "
                 f"| {len(comb)} | {c.word_count()} |")
    L.append("")
    L.append("## Un-filed dossiers (source material not yet merged)\n")
    orphans = [d for d in repo.dossiers.values()
               if d.meta.get("integrated", "no").lower() != "yes"]
    if orphans:
        for d in sorted(orphans, key=lambda x: x.id):
            L.append(f"- `{d.id}` -- {d.meta.get('locator','?')} "
                     f"(unique: {d.meta.get('unique','?')})")
    else:
        L.append("_none -- every filed dossier has been merged_")
    L.append("")
    return "\n".join(L)


# ---------------------------------------------------------------------------
def gen_counts(repo: Repo) -> str:
    """Plain-number macros, available in the preamble.

    These MUST be literals rather than counters incremented during
    typesetting: the title page and the colophon quote them before the
    body is read, so any counter would still hold its initial value.
    """
    published = [t for t in repo.topics.values()
                 if t.status in BODY_STATUSES]
    contrib = sum(1 for t in published if len(set(t.sources)) >= 2)
    stats = {
        "hbpartcount": len(repo.parts),
        "hbchaptercount": len(repo.chapters),
        "hbtopiccount": len(published),
        "hbdossiercount": len(repo.dossiers),
        "hbcontribcount": contrib,
    }
    out = [BANNER,
           "%% Statistics quoted by front/ and back/. Literals, not counters:",
           "%% the title page is typeset before the body, so a counter would",
           "%% still read zero there.", ""]
    for k, v in stats.items():
        out.append(f"\\expandafter\\def\\csname {k}\\endcsname{{{v}}}")
    out.append("")
    return "\n".join(out)


def main() -> int:
    repo = Repo.scan(strict=False)
    if repo.problems:
        print("build_index: could not load some files:", file=sys.stderr)
        for p in repo.problems:
            print("  ! " + p, file=sys.stderr)
        print("  (continuing; run 'make check' for the full report)",
              file=sys.stderr)

    os.makedirs(DIR_COMPILED, exist_ok=True)
    targets = {
        os.path.join(DIR_COMPILED, "booknames.tex"): gen_booknames(repo),
        os.path.join(DIR_COMPILED, "titles.tex"): gen_titles(repo),
        os.path.join(DIR_COMPILED, "counts.tex"): gen_counts(repo),
        os.path.join(DIR_COMPILED, "sources.tex"): gen_sourceslist(repo),
        os.path.join(DIR_COMPILED, "index.tex"): gen_index(repo),
        os.path.join(DIR_COMPILED, "dossiers.tex"): gen_dossiers(repo),
        os.path.join(DIR_COMPILED, "coverage.tex"): gen_coverage_tex(repo),
        os.path.join(ROOT, "registry", "coverage.md"): gen_coverage_md(repo),
    }
    changed = []
    for path, text in targets.items():
        if write_if_changed(path, text):
            changed.append(rel(path))
    if changed:
        print("build_index: wrote " + ", ".join(changed))
    else:
        print("build_index: up to date")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
