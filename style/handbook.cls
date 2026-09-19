%% =====================================================================
%%  handbook.cls  --  document class for The Manipulation Handbook
%% ---------------------------------------------------------------------
%%  DESIGN INTENT
%%  * Every optional package is loaded behind \IfFileExists and every
%%    fallback is self-consistent, so the book still compiles on a bare
%%    TeX Live install. Nothing here may ever be the reason a build breaks.
%%  * ALL visual decisions live here and in style/entry.sty. Content files
%%    must never contain layout commands (docs/RULES.md, rule R12).
%% =====================================================================
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{style/handbook}[2026/09/19 v1.0 The Manipulation Handbook class]

\DeclareOption*{\PassOptionsToClass{\CurrentOption}{book}}
\ProcessOptions\relax
\LoadClass[11pt,twoside,openany]{book}

%% ---------------------------------------------------------------------
%% 1. Optional packages
%% ---------------------------------------------------------------------
\newif\ifhbcolor   \hbcolorfalse
\newif\ifhbenumitem\hbenumitemfalse
\newif\ifhbfancyhdr\hbfancyhdrfalse
\newif\ifhbtitlesec\hbtitlesecfalse
\newif\ifhbhyperref\hbhyperreffalse

\IfFileExists{geometry.sty}{%
  \RequirePackage[a5paper,left=19mm,right=17mm,top=20mm,bottom=20mm,
                  headheight=14pt,footskip=11mm]{geometry}}{}

\IfFileExists{xcolor.sty}{\RequirePackage{xcolor}\hbcolortrue}{}
%% Latin Modern / T1 are only usable if their font metrics actually exist.
%% A minimal TeX tree (or a WASM build) may ship fontenc.sty and lmodern.sty
%% but no EC or TS1 metrics, and a missing .tfm is a fatal error, not a
%% warning. Probe for the metrics themselves, not the package files.
\IfFileExists{lmodern.sty}{%
  \IfFileExists{ecrm1000.tfm}{\RequirePackage{lmodern}}{}}{}
\IfFileExists{fontenc.sty}{%
  \IfFileExists{ecrm1000.tfm}{\RequirePackage[T1]{fontenc}}{}}{}
\IfFileExists{textcomp.sty}{%
  \IfFileExists{tcrm1000.tfm}{\RequirePackage{textcomp}}{}}{}
\IfFileExists{microtype.sty}{\RequirePackage[protrusion=true,expansion=false]{microtype}}{}
\IfFileExists{enumitem.sty}{\RequirePackage{enumitem}\hbenumitemtrue}{}
\IfFileExists{ragged2e.sty}{\RequirePackage[newcommands]{ragged2e}}{}
\IfFileExists{fancyhdr.sty}{\RequirePackage{fancyhdr}\hbfancyhdrtrue}{}
\IfFileExists{titlesec.sty}{\RequirePackage{titlesec}\hbtitlesectrue}{}
\IfFileExists{needspace.sty}{\RequirePackage{needspace}}{}

%% ---------------------------------------------------------------------
%% 2. Palette (defined as real colour NAMES only when xcolor exists;
%%    otherwise every colour command below degrades to a no-op)
%% ---------------------------------------------------------------------
\ifhbcolor
  \definecolor{hbink}{gray}{0.10}
  \definecolor{hbmuted}{gray}{0.42}
  \definecolor{hbrule}{gray}{0.72}
  \definecolor{hbtint}{gray}{0.945}
  \definecolor{hbtintb}{gray}{0.905}
  \definecolor{hblink}{gray}{0.20}
  \definecolor{hbaccent}{rgb}{0.44,0.10,0.10}
  \newcommand{\hbcolor}[1]{\color{#1}}
\else
  \newcommand{\hbcolor}[1]{}
\fi

%% ---------------------------------------------------------------------
%% 3. Paragraph shape.
%%    No justification stretch, no padding paragraphs, no ragged bottom.
%% ---------------------------------------------------------------------
\setlength{\parindent}{0pt}
\setlength{\parskip}{5.5pt plus 1.5pt minus 1pt}
\renewcommand{\baselinestretch}{1.05}
\clubpenalty=10000
\widowpenalty=10000
\displaywidowpenalty=10000
\raggedbottom
\sloppy
\emergencystretch=2em
%% Ragged right: full justification hides weak prose and forces padding.
\AtBeginDocument{%
  \@ifundefined{RaggedRight}{\raggedright}{\RaggedRight}}

%% ---------------------------------------------------------------------
%% 4. Lists
%% ---------------------------------------------------------------------
\ifhbenumitem
  \setlist{nosep,leftmargin=1.4em,itemsep=1.6pt,topsep=2.5pt,parsep=0pt}
  \setlist[itemize,1]{label=\hbcolor{hbmuted}\textbullet}
  \setlist[enumerate,1]{label=\arabic*.,leftmargin=1.8em}
\fi

%% ---------------------------------------------------------------------
%% 5. Headings
%% ---------------------------------------------------------------------
\ifhbtitlesec
  \titleformat{\part}[display]
    {\normalfont\huge\bfseries\hbcolor{hbaccent}}
    {\MakeUppercase{\partname}~\thepart}{12pt}{\Huge}
  \titleformat{\chapter}[display]
    {\normalfont\LARGE\bfseries}
    {\hbcolor{hbmuted}\small\MakeUppercase{\chaptertitlename}~\thechapter}{4pt}{\LARGE}
  \titlespacing*{\part}{0pt}{-20pt}{40pt}
  \titlespacing*{\chapter}{0pt}{-12pt}{18pt}
  \titleformat{\section}{\normalfont\large\bfseries}{\thesection}{0.7em}{}
  \titlespacing*{\section}{0pt}{15pt plus 4pt minus 2pt}{6pt}
  \titleformat{\subsection}{\normalfont\normalsize\bfseries}{\thesubsection}{0.6em}{}
  \titlespacing*{\subsection}{0pt}{11pt}{4pt}
\fi

%% ---------------------------------------------------------------------
%% 6. Running heads
%% ---------------------------------------------------------------------
\ifhbfancyhdr
  \pagestyle{fancy}
  \fancyhf{}
  \renewcommand{\headrulewidth}{0.4pt}
  \renewcommand{\footrulewidth}{0pt}
  \fancyhead[LE]{\footnotesize\hbcolor{hbmuted}\nouppercase{\leftmark}}
  \fancyhead[RO]{\footnotesize\hbcolor{hbmuted}\nouppercase{\rightmark}}
  \fancyfoot[C]{\footnotesize\hbcolor{hbmuted}\thepage}
  \fancypagestyle{plain}{%
    \fancyhf{}\fancyfoot[C]{\footnotesize\thepage}%
    \renewcommand{\headrulewidth}{0pt}}
\fi

%% entry.sty calls this so the running head always names the CURRENT entry.
\newcommand{\hbtopicmark}[1]{\markboth{}{#1}}

%% ---------------------------------------------------------------------
%% 7. hyperref. Loaded at the END OF THE PREAMBLE, not inside
%%    \AtBeginDocument: loading it there makes it emit material before
%%    \begin{document} and produces "Missing \begin{document}".
%% ---------------------------------------------------------------------
\IfFileExists{hyperref.sty}{%
  \hbhyperreftrue
  \ifhbcolor
    \RequirePackage[colorlinks=true,linkcolor=hblink,urlcolor=hblink,
      citecolor=hblink,pdftitle={The Manipulation Handbook},
      bookmarksnumbered=true,bookmarksopen=true,
      bookmarksopenlevel=1]{hyperref}%
  \else
    \RequirePackage[hidelinks,pdftitle={The Manipulation Handbook},
      bookmarksnumbered=true]{hyperref}%
  \fi}{}
\newcommand{\hbphantomsection}{\@ifundefined{phantomsection}{}{\phantomsection}}

%% ---------------------------------------------------------------------
%% 8. Status banner (draft entries only)
%% ---------------------------------------------------------------------
\newcommand{\hbstatusbanner}[1]{%
  \par\vspace{3pt}\noindent
  \begingroup\fboxsep=4pt\fboxrule=0.6pt
  \ifhbcolor\fcolorbox{hbrule}{hbtintb}\else\fbox\fi
  {\footnotesize\textbf{STATUS:} #1}\endgroup\par\vspace{5pt}}

\endinput
