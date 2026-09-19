#!/usr/bin/env python3
"""
extract_corpus.py -- pull plain text out of the source PDFs so that rule R15
(the near-verbatim check) can run.

    make corpus

Output goes to registry/corpus/, which is .gitignored: the extracted text is
third-party copyright and is far too large for the repository. It is a local,
regenerable working file, nothing more.

Uses pdftotext when available, otherwise falls back to pypdf, otherwise it
explains what to install and exits without failing the build.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hb_lib import ROOT, load_books, rel  # noqa: E402


def with_pdftotext(pdf: str, out: str) -> bool:
    try:
        subprocess.run(["pdftotext", "-layout", pdf, out], check=True,
                       capture_output=True)
        return True
    except (OSError, subprocess.CalledProcessError):
        return False


def with_pypdf(pdf: str, out: str) -> bool:
    try:
        import warnings
        warnings.filterwarnings("ignore")
        from pypdf import PdfReader      # type: ignore
    except Exception:
        return False
    try:
        r = PdfReader(pdf)
        chunks = []
        for i, p in enumerate(r.pages):
            try:
                chunks.append(f"\n<<<PAGE {i+1}>>>\n" + (p.extract_text() or ""))
            except Exception:
                chunks.append("")
        with open(out, "w", encoding="utf-8") as fh:
            fh.write("".join(chunks))
        return True
    except Exception:
        return False


def normalise(pdf: str, text_path: str) -> None:
    """Reduce to a word soup so a copied run matches regardless of layout."""
    with open(text_path, "r", encoding="utf-8", errors="replace") as fh:
        t = fh.read()
    t = re.sub(r"<<<PAGE \d+>>>", " ", t)
    t = t.lower()
    t = re.sub(r"[^a-z0-9 ]+", " ", t)
    t = re.sub(r"\s+", " ", t)
    with open(text_path + ".norm.txt", "w", encoding="utf-8") as fh:
        fh.write(t)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "registry", "corpus"))
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    books = load_books()
    if not books:
        print("no books registered")
        return 1
    done = 0
    for b in books:
        f = b.get("file") or ""
        pdf = f if os.path.isabs(f) else os.path.join(ROOT, f)
        if not f or not os.path.exists(pdf):
            print(f"  ~ {b['id']}: source file {f!r} not in the repo -- skipped")
            continue
        out = os.path.join(args.out, f"{b['id']}.txt")
        ok = with_pdftotext(pdf, out) or with_pypdf(pdf, out)
        if not ok:
            print(f"  ~ {b['id']}: no PDF text extractor available "
                  "(install poppler-utils, or: pip install pypdf)")
            continue
        normalise(pdf, out)
        n = os.path.getsize(out)
        print(f"  + {b['id']}: {rel(out)} ({n//1024} KB)")
        done += 1
    if not done:
        print("nothing extracted")
        return 1
    print(f"corpus: {done} file(s) in {rel(args.out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
