# =====================================================================
#  The Manipulation Handbook -- build system
# ---------------------------------------------------------------------
#  make            validate + regenerate the index (+ build the PDF if a
#                  TeX engine is installed)
#  make check      policy + LaTeX gate          (run before every commit)
#  make guard      "no whole-file rewrites" gate
#  make index      regenerate all derived files
#  make pdf        typeset handbook.pdf (TeX engine, else WASM fallback)
#  make verify     check + guard (what CI runs)
#  make corpus     extract the source PDFs' text for the verbatim check
#  make clean      remove LaTeX build debris (never touches content)
#
#  Adding material never needs a new Makefile target. See docs/INGESTION.md.
# =====================================================================

PY      ?= python3
MAIN    := main.tex
PDF     := handbook.pdf
BASE    ?= HEAD
CORPUS  := registry/corpus
SOURCES := $(wildcard books/*.pdf)

.PHONY: all check guard index pdf pdf-wasm verify corpus clean help selftest \
        new-topic new-book new-dossier lint

all: index check pdf

help:
	@sed -n '2,16p' Makefile

# ---------------------------------------------------------------------
# The gate. Always run this.
# ---------------------------------------------------------------------
check:
	@$(PY) tools/build_index.py
	@$(PY) tools/validate.py $(if $(wildcard $(CORPUS)),--corpus $(CORPUS),)

guard:
	@$(PY) tools/churn_guard.py --base $(BASE)

lint:
	@$(PY) tools/texlint.py $$(find topics sources front back -name '*.tex' | sort)

verify: check guard
	@echo "== verify passed =="

# Prove the guarantees hold. Copies the repo to a scratch dir and attacks it.
selftest:
	@$(PY) tools/selftest.py

# ---------------------------------------------------------------------
# Derived files
# ---------------------------------------------------------------------
index:
	@$(PY) tools/build_index.py

# ---------------------------------------------------------------------
# Typesetting. Prefers a real TeX engine; falls back to texlive.js
# (pdftex compiled to WebAssembly) so that 'make pdf' still produces a
# PDF on a machine with no TeX Live at all. Never silently does nothing.
#
# The WASM fallback needs the texlive npm package. Point HB_TEXLIVE_JS at
# its install directory:
#     npm install texlive@1.2.0 --prefix /tmp/tex
#     make pdf HB_TEXLIVE_JS=/tmp/tex/node_modules/texlive
# It is a fallback, not an equivalent: that texmf tree ships no EC (T1) or
# TS1 font metrics and no xcolor, so the class downgrades to OT1/CM and
# monochrome, and pdftex-in-WASM emits no PDF bookmarks. style/handbook.cls
# detects all of this at compile time -- nothing needs editing.
# ---------------------------------------------------------------------
pdf: index
	@if command -v latexmk >/dev/null 2>&1; then \
	  echo "== latexmk =="; \
	  latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error $(MAIN); \
	elif command -v pdflatex >/dev/null 2>&1; then \
	  echo "== pdflatex (3 passes) =="; \
	  pdflatex -interaction=nonstopmode -halt-on-error -file-line-error $(MAIN) && \
	  pdflatex -interaction=nonstopmode -halt-on-error -file-line-error $(MAIN) && \
	  pdflatex -interaction=nonstopmode -halt-on-error -file-line-error $(MAIN); \
	elif [ -n "$(HB_TEXLIVE_JS)" ] || [ -d node_modules/texlive ]; \
	  then \
	  echo "== texlive.js (WebAssembly fallback) =="; \
	  $(MAKE) --no-print-directory pdf-wasm; \
	else \
	  echo ""; \
	  echo "!! No TeX engine found. 'make check' has still verified the"; \
	  echo "!! project structurally. To get the PDF, either:"; \
	  echo "!!   - use the WASM fallback (needs no TeX Live at all):"; \
	  echo "!!       npm install texlive@1.2.0 --prefix /tmp/tex"; \
	  echo "!!       make pdf HB_TEXLIVE_JS=/tmp/tex/node_modules/texlive"; \
	  echo "!!   - upload this repository to Overleaf and compile main.tex"; \
	  echo "!!   - install TeX Live:  apt install texlive-latex-extra"; \
	  echo "!!     (or MacTeX / MiKTeX), then run 'make pdf'"; \
	  echo "!!   - let CI build it: push, then download the artifact"; \
	  echo ""; \
	  exit 1; \
	fi
	@echo "built $(PDF)"

# The WebAssembly engine on its own.
pdf-wasm: index
	@node --max-old-space-size=6144 tools/wasm-pdftex/build.js . $(MAIN) $(PDF)

# ---------------------------------------------------------------------
# Source text extraction (gitignored; only needed for the R15 verbatim check)
# ---------------------------------------------------------------------
corpus:
	@mkdir -p $(CORPUS)
	@$(PY) tools/extract_corpus.py --out $(CORPUS)
	@echo "corpus ready: $(CORPUS) (gitignored)"

# ---------------------------------------------------------------------
# Scaffolding helpers
# ---------------------------------------------------------------------
new-book:
	@$(PY) tools/new_book.py $(ARGS)

new-topic:
	@$(PY) tools/new_topic.py $(ARGS)

new-dossier:
	@$(PY) tools/new_dossier.py $(ARGS)

clean:
	@rm -f *.aux *.log *.out *.toc *.lof *.lot *.fls *.fdb_latexmk \
	       *.synctex.gz *.bbl *.blg *.idx *.ind *.ilg
	@find . -name '*.aux' -not -path './.git/*' -delete
	@echo "cleaned build debris (content untouched)"
