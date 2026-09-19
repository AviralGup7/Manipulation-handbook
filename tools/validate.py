#!/usr/bin/env python3
"""
validate.py -- the policy gate.  `make check`  /  CI.

Every rule below exists because it is a way this project has been seen to rot,
or a way an automated writer silently destroys existing work. The rule numbers
match docs/RULES.md so an error message can be looked up.

Exit code 0 = clean, 1 = errors (do not commit), warnings never fail a build.

    R1   header block is complete and well-formed
    R2   id/filename/path agree with each other
    R3   every referenced book exists in registry/books.yaml and is active
    R4   a secondary source may corroborate but never originate
    R5   slot order is canonical and `core` is present
    R6   entry length stays inside the band (small portions, no padding)
    R7   no filler phrases
    R8   dossier metadata is complete
    R9   dossier slots are canonical
    R10  PROTECTED KNOWLEDGE: a source that contributed unique material can
         never be silently dropped from an entry
    R11  citation integrity both ways (\\sources <-> @sources <-> dossiers
         <-> inline \\src tags)
    R12  no layout commands inside content files
    R13  LaTeX structural lint
    R14  generated files are up to date
    R15  no near-verbatim runs copied from the source PDFs (if corpus present)
    R16  no two entries covering the same ground under different titles
    R17  no draft markers in a `stable` entry
    R18  every \\input resolves and every managed file is reachable
         from main.tex (the usual first-compile failure)
"""

from __future__ import annotations

import datetime as _dt
import difflib
import os
import re
import sys
from typing import Dict, List, Optional, Set, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import build_index                                              # noqa: E402
import texlint                                                  # noqa: E402
from hb_lib import (DIR_COMPILED, DIR_SOURCES, DIR_TOPICS, ID_RE_CHAPTER,  # noqa: E402
                    ID_RE_PART, ID_RE_SOURCE, ID_RE_TOPIC, ROOT,
                    DOSSIER_MANDATORY_SLOTS, DOSSIER_SLOT_ORDER,
                    MANDATORY_SLOTS, SLOT_ORDER, Managed, Repo, rel)

MAX_WORDS = 700        # hard ceiling for one entry
SOFT_WORDS = 560       # above this you get a warning
MIN_WORDS_STABLE = 45  # below this an entry is a stub pretending to be done

FILLER = [
    "in today's", "in todays fast", "fast-paced world", "it is important to note",
    "it should be noted", "it is worth noting", "it is important to remember",
    "needless to say", "it goes without saying", "as we have seen",
    "as mentioned earlier", "as discussed above", "in conclusion",
    "to sum up", "at the end of the day", "when it comes to",
    "in the realm of", "the landscape of", "navigate the complexities",
    "delve", "tapestry", "game-changer", "unlock the power",
    "let us dive in", "let's dive in", "in this section we will",
    "in this chapter we will", "we will explore", "first and foremost",
    "the bottom line is", "needless to say", "without further ado",
    "in the modern world", "ever-evolving", "harness the power",
    "elevate your", "take your ... to the next level",
    "it is crucial", "it is essential to understand",
]

LAYOUT_OK_DIRS = ("front", "back", "style", "registry")


class Report:
    def __init__(self) -> None:
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def err(self, rule: str, where: str, msg: str) -> None:
        self.errors.append(f"[{rule}] {where}: {msg}")

    def warn(self, rule: str, where: str, msg: str) -> None:
        self.warnings.append(f"[{rule}] {where}: {msg}")

    def dump(self) -> int:
        for w in self.warnings:
            print("  ~ " + w)
        for e in self.errors:
            print("  ! " + e)
        print()
        if self.errors:
            print(f"FAILED: {len(self.errors)} error(s), "
                  f"{len(self.warnings)} warning(s)")
            return 1
        print(f"OK: {len(self.warnings)} warning(s), 0 errors")
        return 0


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def prose_of(m: Managed) -> str:
    from hb_lib import strip_latex
    return strip_latex(m.body)


def parse_date(s: str) -> Optional[_dt.date]:
    try:
        return _dt.date.fromisoformat(s.strip())
    except Exception:
        return None


# ---------------------------------------------------------------------------
def check_headers(repo: Repo, rep: Report) -> None:
    for m in repo.all:
        w = m.rel
        for key in ("kind", "id"):
            if not m.meta.get(key):
                rep.err("R1", w, f"missing '@{key}' in header")
        if not m.meta.get("title") and m.kind in ("part", "chapter", "topic"):
            rep.err("R1", w, "missing '@title' in header")
        if m.kind != "part" and not m.meta.get("status"):
            rep.err("R1", w, "missing '@status' in header")
        elif m.kind != "part" and m.status not in (
                "stable", "draft", "planned", "distilled", "skeleton", "retired"):
            rep.err("R1", w, f"@status {m.status!r} is not a known status")
        upd = m.meta.get("updated")
        if not upd:
            rep.warn("R1", w, "missing '@updated' (set it to today's date)")
        elif parse_date(upd) is None:
            rep.err("R1", w, f"@updated {upd!r} is not YYYY-MM-DD")
        order = m.meta.get("order")
        if order is not None and not re.fullmatch(r"\d+", order):
            rep.err("R1", w, f"@order must be an integer, got {order!r}")


def check_ids(repo: Repo, rep: Report) -> None:
    for pid, m in repo.parts.items():
        if not ID_RE_PART.match(pid):
            rep.err("R2", m.rel, f"part id {pid!r} must look like P1..P99")
        if not m.rel.endswith(f"{pid}.tex"):
            rep.err("R2", m.rel, f"part file must be named {pid}.tex")
    for cid, m in repo.chapters.items():
        if not ID_RE_CHAPTER.match(cid):
            rep.err("R2", m.rel, f"chapter id {cid!r} must look like c01..c99")
        if os.path.basename(m.path) != "_meta.tex":
            rep.err("R2", m.rel, "chapter metadata file must be named _meta.tex")
        if os.path.basename(os.path.dirname(m.path)) != cid:
            rep.err("R2", m.rel, f"chapter dir must be named {cid}/")
        if m.meta.get("part") not in repo.parts:
            rep.err("R2", m.rel,
                    f"@part {m.meta.get('part')!r} is not a declared part")
    for tid, m in repo.topics.items():
        mm = ID_RE_TOPIC.match(tid)
        if not mm:
            rep.err("R2", m.rel, f"topic id {tid!r} must look like T-01-01")
        else:
            ch = m.meta.get("chapter")
            if not ch:
                rep.err("R2", m.rel, "topic has no '@chapter'")
            elif ch not in repo.chapters:
                rep.err("R2", m.rel, f"@chapter {ch!r} does not exist")
            elif f"c{mm.group(1)}" != ch:
                rep.err("R2", m.rel,
                        f"id says chapter {mm.group(1)} but @chapter is {ch!r}")
            if os.path.basename(m.path) != f"{tid}.tex":
                rep.err("R2", m.rel, f"topic file must be named {tid}.tex")
    for did, m in repo.dossiers.items():
        if not ID_RE_SOURCE.match(did):
            rep.err("R2", m.rel, f"dossier id {did!r} must look like B1-T-01-01")
        if os.path.basename(m.path) != f"{did}.tex":
            rep.err("R2", m.rel, f"dossier file must be named {did}.tex")


def check_books(repo: Repo, rep: Report) -> None:
    known = {b["id"]: b for b in repo.books}
    for b in repo.books:
        for key in ("id", "rank", "title", "short"):
            if not b.get(key):
                rep.err("R3", "registry/books.yaml", f"{b.get('id','?')}: missing '{key}'")
        if b.get("rank") not in ("primary", "secondary", "tertiary"):
            rep.err("R3", "registry/books.yaml",
                    f"{b.get('id')}: rank must be primary|secondary|tertiary")

    for t in repo.topics.values():
        for s in t.sources:
            b = known.get(s)
            if not b:
                rep.err("R3", t.rel, f"@sources names unknown book {s!r}")
            elif b.get("status") == "retired":
                rep.err("R3", t.rel, f"@sources names retired book {s!r}")
        # R4: secondary may corroborate, never originate
        ranks = [known[s].get("rank") for s in t.sources if s in known]
        if ranks and not any(r == "primary" for r in ranks):
            rep.err("R4", t.rel,
                    "@sources contains no primary source; a secondary or "
                    "tertiary source may corroborate but never originate")
    for d in repo.dossiers.values():
        bk = d.meta.get("book")
        if bk not in known:
            rep.err("R3", d.rel, f"@book {bk!r} is not in registry/books.yaml")
        if known.get(bk, {}).get("rank") == "tertiary":
            rep.warn("R3", d.rel, f"{bk} is tertiary -- should not be cited in entries")


def check_slots(repo: Repo, rep: Report) -> None:
    for t in repo.topics.values():
        if t.status == "planned":
            continue
        slots = t.slots()
        for req in MANDATORY_SLOTS:
            if req not in slots:
                rep.err("R5", t.rel, f"missing mandatory slot '{req}'")
        idx = {s: i for i, s in enumerate(SLOT_ORDER)}
        pos = [idx[s] for s in slots if s in idx]
        if pos != sorted(pos):
            got = " -> ".join(slots)
            rep.err("R5", t.rel,
                    f"slots out of canonical order: {got} "
                    f"(expected {' -> '.join(SLOT_ORDER)})")
        for s in slots:
            if s not in SLOT_ORDER:
                rep.err("R5", t.rel, f"unknown slot '{s}'")
    for d in repo.dossiers.values():
        slots = d.slots()
        for req in DOSSIER_MANDATORY_SLOTS:
            if req not in slots:
                rep.err("R9", d.rel, f"missing mandatory dossier slot '{req}'")
        idx = {s: i for i, s in enumerate(DOSSIER_SLOT_ORDER)}
        pos = [idx[s] for s in slots if s in idx]
        if pos != sorted(pos):
            rep.err("R9", d.rel, "dossier slots out of order: " + " -> ".join(slots))
        for s in slots:
            if s not in DOSSIER_SLOT_ORDER:
                rep.err("R9", d.rel, f"unknown dossier slot '{s}'")


def check_length(repo: Repo, rep: Report) -> None:
    for t in repo.topics.values():
        if t.status == "planned":
            continue
        n = t.word_count()
        if n > MAX_WORDS:
            rep.err("R6", t.rel,
                    f"{n} words > {MAX_WORDS}: split it into a second entry, "
                    "do not pad or compress into mush")
        elif n > SOFT_WORDS:
            rep.warn("R6", t.rel, f"{n} words is above the {SOFT_WORDS} comfort band")
        elif t.status == "stable" and n < MIN_WORDS_STABLE:
            rep.err("R6", t.rel,
                    f"{n} words is too thin to call 'stable' "
                    f"(minimum {MIN_WORDS_STABLE}) -- mark it @status: draft")


def check_filler(repo: Repo, rep: Report) -> None:
    for m in repo.topics.values():
        p = prose_of(m).lower()
        for phrase in FILLER:
            if phrase in p:
                rep.err("R7", m.rel, f"filler phrase '{phrase}' -- cut it")


def check_dossiers(repo: Repo, rep: Report) -> None:
    for d in repo.dossiers.values():
        w = d.rel
        if not d.meta.get("locator"):
            rep.err("R8", w, "missing '@locator' (chapter/section/page in the source)")
        for key in ("unique", "integrated"):
            v = d.meta.get(key)
            if v not in ("yes", "no"):
                rep.err("R8", w, f"@{key} must be yes|no, got {v!r}")
        if not d.meta.get("topic"):
            rep.err("R8", w, "missing '@topic'")
        elif d.meta["topic"] not in repo.topics:
            rep.err("R8", w, f"@topic {d.meta['topic']!r} does not exist")


def check_protection(repo: Repo, rep: Report) -> None:
    """R10/R11 -- the anti-overwrite guarantee."""
    for d in repo.dossiers.values():
        tid = d.meta.get("topic")
        t = repo.topics.get(tid)
        if not t:
            continue
        bid = d.meta.get("book")
        w = t.rel
        if t.status == "planned":
            if d.meta.get("integrated") == "yes":
                rep.err("R11", w, f"dossier {d.id} claims to be integrated "
                                  "but the entry is still 'planned'")
            continue
        # R10 unique knowledge must stay cited
        if d.meta.get("unique") == "yes" and bid not in t.sources:
            rep.err("R10", w,
                    f"{d.id} carries material unique to {bid}, but {bid} is "
                    "not in this entry's @sources. Unique knowledge may not be "
                    "dropped; either cite it, or set the dossier "
                    "@status: retired with @reason.")
        # R11a integrated dossier must be cited
        if d.meta.get("integrated") == "yes" and bid not in t.sources:
            rep.err("R11", w, f"dossier {d.id} is marked integrated but "
                              f"{bid} is missing from @sources")
        # R11b cited book must have a dossier
    for t in repo.topics.values():
        if t.status == "planned":
            continue
        filed = {d.meta.get("book") for d in repo.dossiers_for(t.id)}
        for s in t.sources:
            if s not in filed:
                rep.err("R11", t.rel,
                        f"@sources cites {s} but sources/{s}/{s}-{t.id}.tex "
                        "does not exist -- a claim with no filed evidence")
        # R11c inline \src tags must be within @sources
        for tag in set(re.findall(r"\\src\{(B\d+)\}", t.body)):
            if tag not in t.sources:
                rep.err("R11", t.rel, f"inline \\src{{{tag}}} not in @sources")
        # R11d the printed \sources{} line must match the header
        m = re.search(r"\\sources\{([^}]*)\}", t.body)
        if m:
            printed = {x.strip() for x in re.split(r"[,;]+", m.group(1)) if x.strip()}
            printed = {x for x in printed if re.fullmatch(r"B\d+", x)}
            hdr = set(t.sources)
            if printed != hdr:
                rep.err("R11", t.rel,
                        f"\\sources{{...}} prints {sorted(printed)} but the "
                        f"header says {sorted(hdr)} -- they must match")
        else:
            rep.err("R11", t.rel, "entry has no \\sources{...} attribution line")


def check_layout(repo: Repo, rep: Report) -> None:
    for m in repo.topics.values():
        for n, line in enumerate(m.body.splitlines(), start=m.lineno_body):
            for cmd in texlint.BANNED_LAYOUT:
                if cmd in line:
                    rep.err("R12", f"{m.rel}:{n}",
                            f"layout command {cmd} in a content file")
    for d in repo.dossiers.values():
        for n, line in enumerate(d.body.splitlines(), start=d.lineno_body):
            for cmd in texlint.BANNED_LAYOUT:
                if cmd in line:
                    rep.err("R12", f"{d.rel}:{n}",
                            f"layout command {cmd} in a content file")


def check_texlint(repo: Repo, rep: Report) -> None:
    targets = [m for m in repo.all]
    for sub in ("front", "back"):
        d = os.path.join(ROOT, sub)
        if os.path.isdir(d):
            for fn in sorted(os.listdir(d)):
                if fn.endswith(".tex"):
                    targets.append(Managed(path=os.path.join(d, fn),
                                           rel=os.path.join(sub, fn),
                                           kind="topic", meta={}, body="", raw=""))
    for m in targets:
        try:
            with open(m.path, "r", encoding="utf-8") as fh:
                text = fh.read()
        except Exception as exc:
            rep.err("R13", m.rel, f"unreadable: {exc}")
            continue
        skip_layout = m.rel.split(os.sep)[0] in LAYOUT_OK_DIRS
        for sev, n, msg in texlint.lint_text(text, skip_layout=skip_layout):
            (rep.err if sev == "error" else rep.warn)("R13", f"{m.rel}:{n}", msg)


def check_generated(repo: Repo, rep: Report) -> None:
    expect = {
        os.path.join(DIR_COMPILED, "booknames.tex"): build_index.gen_booknames(repo),
        os.path.join(DIR_COMPILED, "index.tex"): build_index.gen_index(repo),
        os.path.join(DIR_COMPILED, "dossiers.tex"): build_index.gen_dossiers(repo),
        os.path.join(DIR_COMPILED, "coverage.tex"): build_index.gen_coverage_tex(repo),
        os.path.join(ROOT, "registry", "coverage.md"): build_index.gen_coverage_md(repo),
    }
    for path, want in expect.items():
        if not os.path.exists(path):
            rep.err("R14", rel(path), "missing -- run 'make index'")
            continue
        with open(path, "r", encoding="utf-8") as fh:
            got = fh.read()
        if got != want:
            diff = list(difflib.unified_diff(got.splitlines(), want.splitlines(),
                                             lineterm="", n=0))[:6]
            rep.err("R14", rel(path),
                    "stale -- run 'make index'. first diff: "
                    + " | ".join(x for x in diff if x.startswith(("+", "-"))
                                 and not x.startswith(("+++", "---"))))


def check_verbatim(repo: Repo, rep: Report, corpus: Optional[str]) -> None:
    """R15 -- refuse long runs lifted straight out of a source PDF."""
    if not corpus or not os.path.isdir(corpus):
        rep.warn("R15", "registry/corpus/",
                 "no extracted source text found; run 'make corpus' to enable "
                 "the near-verbatim check (skipped)")
        return
    src_text: Dict[str, str] = {}
    for fn in os.listdir(corpus):
        if fn.endswith(".norm.txt"):
            with open(os.path.join(corpus, fn), "r", encoding="utf-8",
                      errors="replace") as fh:
                src_text[fn] = norm_words(fh.read())
    N = 9   # consecutive matching words is never a coincidence
    for t in repo.topics.values():
        words = norm_words(prose_of(t)).split()
        for i in range(len(words) - N):
            run = " ".join(words[i:i + N])
            for fn, body in src_text.items():
                if run in body:
                    rep.err("R15", t.rel,
                            f"{N}-word run appears verbatim in {fn}: "
                            f"'{run[:60]}...' -- rewrite it")
                    break


def norm_words(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def check_duplicates(repo: Repo, rep: Report) -> None:
    seen: Dict[str, str] = {}
    for t in sorted(repo.topics.values(), key=lambda x: x.id):
        key = norm_words(t.title)
        if key in seen:
            rep.err("R16", t.rel,
                    f"title duplicates {seen[key]} -- merge them, do not "
                    "keep two entries for one idea")
        seen[key] = t.rel
    # near-duplicate titles
    titles = [(t.id, norm_words(t.title)) for t in repo.topics.values()]
    for i in range(len(titles)):
        for j in range(i + 1, len(titles)):
            r = difflib.SequenceMatcher(None, titles[i][1], titles[j][1]).ratio()
            if r > 0.86:
                rep.warn("R16", titles[j][0],
                         f"title is {r:.0%} similar to {titles[i][0]} "
                         f"('{titles[i][1]}') -- check they are not the same idea")


def check_stable(repo: Repo, rep: Report) -> None:
    for t in repo.topics.values():
        if t.status != "stable":
            continue
        for marker in ("\\TODO", "\\GAP"):
            if re.search(re.escape(marker) + r"\b", t.body):
                rep.err("R17", t.rel,
                        f"{marker} present in a 'stable' entry")


def check_structure(repo: Repo, rep: Report) -> None:
    """Tree sanity: no orphans, orders unique inside a parent."""
    for m in repo.topics.values():
        cid = m.meta.get("chapter")
        if cid and cid not in repo.chapters:
            rep.err("R2", m.rel, "orphan: its chapter does not exist")
    for parent, kids in (("part", list(repo.chapters.values())),
                         ("chapter", list(repo.topics.values()))):
        buckets: Dict[str, List[str]] = {}
        for k in kids:
            key = k.meta.get(parent) or "?"
            buckets.setdefault(key, []).append(k.meta.get("order", "?") + ":" + k.id)
        for key, orders in buckets.items():
            nums = [o.split(":")[0] for o in orders]
            dupes = {n for n in nums if nums.count(n) > 1}
            if dupes:
                rep.err("R2", f"{parent}={key}",
                        f"duplicate @order values {sorted(dupes)} among "
                        f"{[o.split(':')[1] for o in orders]}")
    # every dossier directory must belong to a declared book
    if os.path.isdir(DIR_SOURCES):
        for d in sorted(os.listdir(DIR_SOURCES)):
            full = os.path.join(DIR_SOURCES, d)
            if os.path.isdir(full) and not repo.book(d):
                rep.err("R3", f"sources/{d}/",
                        "directory for a book that is not in registry/books.yaml")


def check_inputs(repo: Repo, rep: Report) -> None:
    """R18 -- every \\input/\\include must resolve, and every managed file
    must be reachable from main.tex. A dangling \\input is the single most
    common first-compile failure in a project assembled from many files."""
    seen: Set[str] = set()
    queue = ["main.tex"]
    reachable: Set[str] = set()
    while queue:
        relp = queue.pop()
        absp = os.path.join(ROOT, relp)
        if not os.path.exists(absp):
            if not os.path.exists(absp + ".tex"):
                rep.err("R18", relp, "file does not exist")
                continue
            relp = relp + ".tex"
            absp = absp + ".tex"
        if relp in reachable:
            continue
        reachable.add(relp)
        try:
            with open(absp, "r", encoding="utf-8") as fh:
                text = fh.read()
        except Exception as exc:
            rep.err("R18", relp, f"unreadable: {exc}")
            continue
        for m in re.finditer(r"\\(?:input|include)\{([^}]*)\}", text):
            target = m.group(1).strip()
            if target.startswith("style/") or target in ("registry/books.yaml",):
                continue
            cand = target if target.endswith(".tex") else target + ".tex"
            if not os.path.exists(os.path.join(ROOT, cand)):
                rep.err("R18", relp, f"\\input{{{target}}} does not resolve")
            elif cand not in seen:
                seen.add(cand)
                queue.append(cand)

    # orphan check: a managed file nothing points at
    for m in repo.all:
        if m.kind == "source" and m.status == "skeleton":
            continue                      # scaffolded but not yet merged
        if m.rel.replace(os.sep, "/") not in reachable:
            rep.err("R18", m.rel,
                    "not reachable from main.tex -- it will never be typeset "
                    "(run 'make index', or check its @status/@chapter)")


def main(argv: List[str]) -> int:
    corpus = None
    args = list(argv)
    if "--corpus" in args:
        i = args.index("--corpus")
        corpus = args[i + 1] if i + 1 < len(args) else None
        del args[i:i + 2]
    default_corpus = os.path.join(ROOT, "registry", "corpus")
    if corpus is None and os.path.isdir(default_corpus):
        corpus = default_corpus

    repo = Repo.scan(strict=True)
    rep = Report()
    for p in repo.problems:
        rep.err("R1", p.split(":")[0], p)

    check_headers(repo, rep)
    check_ids(repo, rep)
    check_books(repo, rep)
    check_structure(repo, rep)
    check_slots(repo, rep)
    check_length(repo, rep)
    check_filler(repo, rep)
    check_dossiers(repo, rep)
    check_protection(repo, rep)
    check_layout(repo, rep)
    check_texlint(repo, rep)
    check_generated(repo, rep)
    check_verbatim(repo, rep, corpus)
    check_duplicates(repo, rep)
    check_stable(repo, rep)
    check_inputs(repo, rep)

    print(f"scanned: {len(repo.parts)} parts, {len(repo.chapters)} chapters, "
          f"{len(repo.topics)} entries, {len(repo.dossiers)} dossiers, "
          f"{len(repo.books)} sources")
    return rep.dump()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
