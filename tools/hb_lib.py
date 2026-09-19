#!/usr/bin/env python3
"""
hb_lib.py -- shared machinery for The Manipulation Handbook build system.

Everything the tools need to know about the repository's CONTRACT lives here:
  * the file layout
  * the header-metadata format
  * the registry of books

THE HEADER CONTRACT
-------------------
Every managed .tex file starts with a comment block of the form:

    %% @kind: topic
    %% @id:   T-01-01
    %% ...

The block ends at the first line that is not `%% @key: value`. There is no
CSV, no JSON database and no second copy of the truth: the .tex files ARE the
registry, and every generated file (index, dossiers, coverage report) is
derived from them. That is deliberate -- a table that can drift from the files
is the usual reason systems like this rot.

Nothing in here may import a third-party package. Python 3.8+ stdlib only.
"""

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DIR_TOPICS = os.path.join(ROOT, "topics")
DIR_SOURCES = os.path.join(ROOT, "sources")
DIR_COMPILED = os.path.join(ROOT, "registry", "compiled")
DIR_PARTS = os.path.join(DIR_TOPICS, "_parts")
BOOKS_YAML = os.path.join(ROOT, "registry", "books.yaml")

KINDS = ("part", "chapter", "topic", "source")
STATUSES = ("stable", "draft", "planned", "distilled", "skeleton", "retired")

# Slot order inside a published topic. Enforced by validate.py (rule R5).
SLOT_ORDER = [
    "core", "mechanism", "tells", "moves", "counters",
    "limits", "field", "sources", "seesources", "seealso",
]
MANDATORY_SLOTS = ["core"]

# Dossier slot order. Enforced by validate.py (rule R9).
DOSSIER_SLOT_ORDER = ["distilled", "unique", "terms", "quotable"]
DOSSIER_MANDATORY_SLOTS = ["distilled"]

ID_RE_TOPIC = re.compile(r"^T-(\d{2})-(\d{2})$")
ID_RE_CHAPTER = re.compile(r"^c(\d{2})$")
ID_RE_PART = re.compile(r"^P(\d{1,2})$")
ID_RE_SOURCE = re.compile(r"^(B\d+)-(T-\d{2}-\d{2})$")

HEADER_RE = re.compile(r"^\s*%%\s*@([a-z][a-z0-9-]*)\s*:\s*(.*?)\s*$")


class HbError(Exception):
    """A contract violation the user must fix."""


# ---------------------------------------------------------------------------
# Managed files
# ---------------------------------------------------------------------------
@dataclass
class Managed:
    """One metadata-bearing .tex file."""
    path: str                 # absolute
    rel: str                  # relative to repo root
    kind: str                 # part | chapter | topic | source
    meta: Dict[str, str] = field(default_factory=dict)
    body: str = ""            # everything after the header block
    raw: str = ""
    lineno_body: int = 0

    # convenience -------------------------------------------------------
    @property
    def id(self) -> str:
        return self.meta.get("id", "")

    @property
    def title(self) -> str:
        return self.meta.get("title", "")

    @property
    def status(self) -> str:
        return self.meta.get("status", "")

    @property
    def sources(self) -> List[str]:
        raw = self.meta.get("sources", "")
        return [s.strip() for s in re.split(r"[,;]+", raw) if s.strip()]

    def word_count(self) -> int:
        """Word count of the body with LaTeX noise stripped."""
        t = strip_latex(self.body)
        return len([w for w in t.split() if any(c.isalnum() for c in w)])

    def slots(self) -> List[str]:
        """Environments/commands used, in order of appearance."""
        found: List[Tuple[int, str]] = []
        for m in re.finditer(r"\\begin\{([a-zA-Z*]+)\}", self.body):
            name = m.group(1)
            if name in SLOT_ORDER or name in DOSSIER_SLOT_ORDER:
                found.append((m.start(), name))
        for m in re.finditer(r"\\(sources|seesources|seealso)\b", self.body):
            found.append((m.start(), m.group(1)))
        seen, out = set(), []
        for _, name in sorted(found):
            if name not in seen:
                seen.add(name)
                out.append(name)
        return out


def strip_latex(text: str) -> str:
    """Remove comments, commands and braces, leaving readable prose."""
    text = re.sub(r"(?<!\\)%.*", "", text)
    text = re.sub(r"\\begin\{[^}]*\}|\\end\{[^}]*\}", " ", text)
    text = re.sub(r"\\[a-zA-Z@]+\*?(?:\[[^\]]*\])?", " ", text)
    text = text.replace("{", " ").replace("}", " ")
    text = re.sub(r"[~$&_^\\]", " ", text)
    return re.sub(r"\s+", " ", text)


def parse_header(text: str) -> Tuple[Dict[str, str], str, int]:
    """Return (meta, body, first_body_lineno)."""
    meta: Dict[str, str] = {}
    lines = text.splitlines(keepends=True)
    i = 0
    while i < len(lines):
        m = HEADER_RE.match(lines[i])
        if m:
            key, val = m.group(1), m.group(2)
            if key in meta:
                raise HbError(f"duplicate header key '@{key}'")
            meta[key] = val
            i += 1
            continue
        # tolerate %% banner / blank lines *before* the first key
        if not meta and (lines[i].startswith("%%") or not lines[i].strip()):
            i += 1
            continue
        break
    if not meta:
        raise HbError("no header block found (expected '%% @kind: ...')")
    return meta, "".join(lines[i:]), i + 1


def load(path: str) -> Managed:
    with open(path, "r", encoding="utf-8") as fh:
        raw = fh.read()
    meta, body, ln = parse_header(raw)
    kind = meta.get("kind", "")
    if kind not in KINDS:
        raise HbError(f"{path}: @kind must be one of {KINDS}, got {kind!r}")
    return Managed(path=path, rel=os.path.relpath(path, ROOT), kind=kind,
                   meta=meta, body=body, raw=raw, lineno_body=ln)


# ---------------------------------------------------------------------------
# Scanning
# ---------------------------------------------------------------------------
def _walk_tex(base: str) -> List[str]:
    out = []
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames.sort()
        for fn in sorted(filenames):
            if fn.endswith(".tex") and not fn.startswith("."):
                out.append(os.path.join(dirpath, fn))
    return out


class Repo:
    """The whole managed tree, loaded and indexed."""

    def __init__(self) -> None:
        self.parts: Dict[str, Managed] = {}
        self.chapters: Dict[str, Managed] = {}
        self.topics: Dict[str, Managed] = {}
        self.dossiers: Dict[str, Managed] = {}
        self.books: List[Dict[str, str]] = []
        self.all: List[Managed] = []
        self.problems: List[str] = []

    # -- loaders --------------------------------------------------------
    @classmethod
    def scan(cls, strict: bool = True) -> "Repo":
        repo = cls()
        repo.books = load_books()

        for path in _walk_tex(DIR_PARTS) if os.path.isdir(DIR_PARTS) else []:
            repo._add(path, "part", repo.parts, strict)
        for path in _walk_tex(DIR_TOPICS):
            if os.sep + "_parts" + os.sep in path:
                continue
            base = os.path.basename(path)
            if base.startswith("_"):
                repo._add(path, "chapter", repo.chapters, strict)
            else:
                repo._add(path, "topic", repo.topics, strict)
        for path in _walk_tex(DIR_SOURCES) if os.path.isdir(DIR_SOURCES) else []:
            repo._add(path, "source", repo.dossiers, strict)
        return repo

    def _add(self, path: str, expect: str, bucket: Dict[str, Managed],
             strict: bool) -> None:
        try:
            m = load(path)
        except HbError as exc:
            self.problems.append(f"{os.path.relpath(path, ROOT)}: {exc}")
            return
        except Exception as exc:                      # pragma: no cover
            self.problems.append(f"{os.path.relpath(path, ROOT)}: unreadable ({exc})")
            return
        if m.kind != expect:
            msg = (f"{m.rel}: lives in a {expect} directory but declares "
                   f"@kind: {m.kind}")
            if strict:
                self.problems.append(msg)
                return
        if m.id in bucket:
            self.problems.append(
                f"{m.rel}: duplicate @{expect} id {m.id!r} "
                f"(also {bucket[m.id].rel})")
            return
        bucket[m.id] = m
        self.all.append(m)

    # -- queries --------------------------------------------------------
    def book_ids(self) -> List[str]:
        return [b["id"] for b in self.books]

    def book(self, bid: str) -> Optional[Dict[str, str]]:
        for b in self.books:
            if b["id"] == bid:
                return b
        return None

    def chapters_in_part(self, pid: str) -> List[Managed]:
        return sorted([c for c in self.chapters.values()
                       if c.meta.get("part") == pid],
                      key=lambda c: (int(c.meta.get("order", 9999)), c.id))

    def topics_in_chapter(self, cid: str) -> List[Managed]:
        return sorted([t for t in self.topics.values()
                       if t.meta.get("chapter") == cid],
                      key=lambda t: (int(t.meta.get("order", 9999)), t.id))

    def dossiers_for(self, tid: str) -> List[Managed]:
        out = [d for d in self.dossiers.values() if d.meta.get("topic") == tid]
        return sorted(out, key=lambda d: d.meta.get("book", ""))

    def ordered_parts(self) -> List[Managed]:
        return sorted(self.parts.values(),
                      key=lambda p: (int(p.meta.get("order", 9999)), p.id))


# ---------------------------------------------------------------------------
# books.yaml -- a deliberately tiny parser (no PyYAML dependency)
# ---------------------------------------------------------------------------
def load_books(path: str = BOOKS_YAML) -> List[Dict[str, str]]:
    if not os.path.exists(path):
        return []
    books: List[Dict[str, str]] = []
    cur: Optional[Dict[str, str]] = None
    block_key: Optional[str] = None
    block_indent = 0
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip() or line.lstrip().startswith("#"):
                if block_key and cur is not None and line.strip():
                    pass
                continue
            stripped = line.rstrip("\n")
            if stripped.startswith("- "):
                cur = {}
                books.append(cur)
                block_key = None
                stripped = "  " + stripped[2:]
            indent = len(stripped) - len(stripped.lstrip())
            m = re.match(r"\s*([a-z][a-z0-9_]*)\s*:\s*(.*)$", stripped)
            if not m or cur is None:
                if block_key and cur is not None and indent >= block_indent:
                    cur[block_key] += " " + stripped.strip()
                continue
            key, val = m.group(1), m.group(2).strip()
            if val in (">", "|"):
                cur[key] = ""
                block_key, block_indent = key, indent + 1
                continue
            block_key = None
            if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
                val = val[1:-1]
            cur[key] = val
    return [b for b in books if b.get("id")]


# ---------------------------------------------------------------------------
# Small helpers shared by the tools
# ---------------------------------------------------------------------------
def rel(path: str) -> str:
    return os.path.relpath(path, ROOT)


def tex_escape(s: str) -> str:
    """Escape the characters that break LaTeX in generated files."""
    out = []
    for ch in s:
        if ch in "#$%&_{}":
            out.append("\\" + ch)
        elif ch == "~":
            out.append(r"\textasciitilde{}")
        elif ch == "^":
            out.append(r"\textasciicircum{}")
        elif ch == "\\":
            out.append(r"\textbackslash{}")
        else:
            out.append(ch)
    return "".join(out)


def write_if_changed(path: str, text: str) -> bool:
    """Write only when content differs -- keeps git diffs honest."""
    old = None
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as fh:
            old = fh.read()
    if old == text:
        return False
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return True


def fail(msgs: List[str], code: int = 1) -> None:
    for m in msgs:
        print("  ! " + m, file=sys.stderr)
    sys.exit(code)
