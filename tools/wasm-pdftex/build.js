/*
 * build.js -- compile the handbook with texlive.js (pdftex 1.40.11 compiled to
 * asm.js by Emscripten) when no native TeX engine is available.
 *
 * Why this exists: some environments (locked-down CI, sandboxes without apt or
 * CTAN access) cannot install TeX Live. texlive.js has no glibc, no shared
 * libraries and no network dependency -- the whole TeX Live tree is served from
 * disk through an XHR shim. It is a fallback, not the preferred build path.
 *
 * Usage:
 *   npm install texlive            (once, into tools/wasm-pdftex/)
 *   node tools/wasm-pdftex/build.js <repo-root> <main.tex> <out.pdf>
 *
 * Exit codes: 0 = PDF written, 1 = compile failed.
 */
'use strict';

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(process.argv[2] || '.');
const MAIN = process.argv[3] || 'main.tex';
const OUT = path.resolve(process.argv[4] || 'handbook.pdf');

const TEXLIVE = (() => {
  const cands = [
    process.env.HB_TEXLIVE_JS,
    path.join(__dirname, 'node_modules', 'texlive'),
    path.join(ROOT, 'node_modules', 'texlive'),
    path.join(ROOT, 'tools', 'wasm-pdftex', 'node_modules', 'texlive'),
  ].filter(Boolean);
  for (const c of cands) if (fs.existsSync(path.join(c, 'pdftex-worker.js'))) return c;
  console.error('texlive.js not found. Run:  npm install texlive   in ' + __dirname);
  process.exit(2);
})();

/* ------------------------------------------------------------------ *
 * XHR shim: serve the TeX Live tree from disk, synchronously.
 * texlive.js populates its MEMFS with "lazy files" that fetch their
 * contents over XHR on first access, so only what pdftex actually
 * opens is ever read into memory.
 * ------------------------------------------------------------------ */
function resolveUrl(url) {
  let u = String(url).split('?')[0];
  u = u.replace(/^file:\/\//, '');
  // An absolute filesystem path that really exists wins outright.
  if (u.startsWith('/') && fs.existsSync(u)) return u;
  let rel = u.replace(/^\.\//, '').replace(/^\/+/, '');
  if (rel.startsWith('texlive')) {
    const direct = path.join(TEXLIVE, rel.replace(/^texlive\//, ''));
    if (fs.existsSync(direct)) return direct;
  }
  return path.join(TEXLIVE, rel.replace(/\/{2,}/g, '/'));
}

class ShimXHR {
  constructor() { this.status = 0; this.response = null; this.responseType = ''; this._hdr = {}; }
  open(method, url) { this.method = method; this.url = url; }
  setRequestHeader() {}
  getAllResponseHeaders() {
    return Object.entries(this._hdr).map(([k, v]) => `${k}: ${v}\r\n`).join('');
  }
  getResponseHeader(name) {
    const k = String(name).toLowerCase();
    for (const [hk, hv] of Object.entries(this._hdr)) if (hk.toLowerCase() === k) return hv;
    return null;
  }
  send() {
    const p = resolveUrl(this.url);
    let st = null;
    try { st = fs.statSync(p); } catch (e) { st = null; }
    if (!st || !st.isFile()) {
      this.status = 404;
      this._hdr = {};
      this.response = this.responseType === 'arraybuffer' ? new Uint8Array(0).buffer : '';
    } else {
      this.status = 200;
      // LazyUint8Array issues a HEAD first to learn the length and whether
      // byte ranges are supported. Claim no range support so it fetches whole.
      this._hdr = { 'Content-length': String(st.size), 'Accept-Ranges': 'none' };
      if (this.method === 'HEAD') { this.response = null; }
      else {
        const buf = fs.readFileSync(p);
        if (this.responseType === 'arraybuffer') {
          const copy = new Uint8Array(buf.length);
          copy.set(buf);
          this.response = copy.buffer;
        } else {
          this.response = buf.toString('latin1');
        }
      }
    }
    if (typeof this.onload === 'function') this.onload();
    if (typeof this.onreadystatechange === 'function') this.onreadystatechange();
  }
}

/* ------------------------------------------------------------------ *
 * Drive the worker script in-process. It expects `self`, and answers
 * every message synchronously, so a flat request/response queue works.
 * ------------------------------------------------------------------ */
const log = [];
let lastResult;
let msgId = 0;

global.XMLHttpRequest = ShimXHR;
// Emscripten refuses synchronous binary XHR unless ENVIRONMENT_IS_WORKER, which
// it infers from `typeof importScripts === 'function'`. Declaring it puts the
// module in worker mode, where the lazy-file loader will use our shim. The node
// branch we give up only provided process-based file reads, which the shim
// replaces anyway.
global.importScripts = function (p) {
  const code = fs.readFileSync(resolveUrl(p), 'utf8');
  (0, eval)(code);
};
global.self = {
  postMessage(raw) {
    let data;
    try { data = JSON.parse(raw); } catch (e) { return; }
    switch (data.command) {
      case 'stdout': log.push(data.contents); break;
      case 'stderr': log.push('E: ' + data.contents); break;
      case 'ready': break;
      case 'error':
        lastResult = { error: data.message };
        break;
      default:
        lastResult = data;
    }
  },
};

process.chdir(ROOT);
require(path.join(TEXLIVE, 'pdftex-worker.js'));

function send(command, args) {
  lastResult = undefined;
  const id = msgId++;
  global.self.onmessage({ data: JSON.stringify({ command, arguments: args, msg_id: id }) });
  return lastResult;
}

/* ------------------------------------------------------------------ *
 * Materialise the project into MEMFS.
 * ------------------------------------------------------------------ */
function walk(dir, out) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    if (e.name === '.git' || e.name === 'node_modules' || e.name === 'corpus') continue;
    const p = path.join(dir, e.name);
    if (e.isDirectory()) walk(p, out);
    else if (/\.(tex|sty|cls|def|cfg|fd|clo|enc|map|pfb|tfm|vf)$/i.test(e.name)) out.push(p);
  }
  return out;
}

function mkdirp(vfsPath) {
  const parts = vfsPath.split('/').filter(Boolean);
  let cur = '';
  for (const part of parts) {
    cur += '/' + part;
    try { send('FS_createPath', [path.posix.dirname(cur), part, true, true]); } catch (e) {}
  }
}

const files = walk(ROOT, []);
const byDir = new Map();
for (const f of files) {
  const relPath = path.relative(ROOT, f).split(path.sep).join('/');
  const dir = path.posix.dirname('/' + relPath);
  if (!byDir.has(dir)) byDir.set(dir, []);
  byDir.get(dir).push([relPath, f]);
}

console.log(`texlive.js: loading ${files.length} project files into MEMFS`);
for (const [dir] of byDir) if (dir !== '/') mkdirp(dir);

for (const [, list] of byDir) {
  for (const [relPath, abs] of list) {
    const dir = path.posix.dirname('/' + relPath);
    const name = path.posix.basename('/' + relPath);
    send('FS_createDataFile', [dir, name, fs.readFileSync(abs, 'latin1'), true, true]);
  }
}

// The npm package nests the tree one level deeper than the package root.
const TEXMF_ROOT = fs.existsSync(path.join(TEXLIVE, 'texlive', 'texmf-dist'))
  ? path.join(TEXLIVE, 'texlive') : TEXLIVE;

console.log('texlive.js: mounting the TeX Live tree (lazy) from ' + TEXMF_ROOT);
send('FS_createLazyFilesFromList', ['/', path.join(TEXLIVE, 'texlive.lst'),
     TEXMF_ROOT + '/', true, true]);

// Verify the mount before burning a compile pass on a missing tree.
function probeFile(p, min) {
  try {
    const r = send('FS_readFile', [p]);
    const n = (r && typeof r.result === 'string') ? r.result.length : -1;
    return n >= (min || 1);
  } catch (e) { return false; }
}
for (const [p, min, what] of [
  ['/texmf-dist/tex/latex/base/book.cls', 100, 'LaTeX base'],
  ['/texmf.cnf', 10, 'kpathsea config'],
  ['/texmf-var/web2c/pdftex/latex.fmt', 1000, 'LaTeX format'],
  ['/' + MAIN, 10, 'the document'],
]) {
  if (!probeFile(p, min)) {
    console.error(`texlive.js: ${what} is not readable in MEMFS: ${p}`);
    console.error(log.slice(-30).join('\n'));
    process.exit(1);
  }
}
console.log('texlive.js: TeX Live tree + document mounted and verified');

// pdftex aborts by throwing; make sure we always see what it printed first.
process.on('uncaughtException', (e) => {
  console.error('texlive.js: pdftex aborted: ' + (e && e.message || e));
  console.error('--- pdftex output ---');
  console.error(log.slice(-200).join('\n'));
  process.exit(1);
});

/* ------------------------------------------------------------------ *
 * Passes until convergence.
 * aux/toc/out all need extra runs; hyperref's rerunfilecheck in
 * particular drops PDF bookmarks for any pass in which main.out moved,
 * so a fixed pass count can silently ship a bookmark-less document.
 * Run until no pass asks for a rerun, with a hard ceiling.
 * ------------------------------------------------------------------ */
// This build's default format is already LaTeX, so no '&latex' prefix.
// Putting it first makes web2c read the following option as a filename.
const RUN_ARGSETS = [
  ['-interaction=nonstopmode', '-output-format', 'pdf'],
  ['-interaction=nonstopmode', '-output-format', 'pdf', '-fmt', 'latex'],
  ['&latex', '-interaction=nonstopmode', '-output-format', 'pdf'],
];
const MAX_PASSES = Number(process.env.HB_TEX_PASSES || 8);
const RERUN = /Rerun to get|has changed\.|Label\(s\) may have changed/;
let argset = RUN_ARGSETS[0];
let ok = false;
for (let pass = 1; pass <= MAX_PASSES; pass++) {
  const logMark = log.length;
  console.log(`texlive.js: pdflatex pass ${pass}`);
  let r;
  try {
    r = send('run', argset.concat([MAIN]));
  } catch (e) {
    r = { error: String(e && e.message || e) };
  }
  if (r && r.error && pass === 1) {
    // try the remaining argument spellings before giving up
    for (const alt of RUN_ARGSETS.slice(1)) {
      console.log('texlive.js: retrying with ' + alt[0]);
      try { r = send('run', alt.concat([MAIN])); } catch (e) { r = { error: String(e) }; }
      if (!(r && r.error)) { argset = alt; break; }
    }
  }
  if (r && r.error) console.error('worker error: ' + r.error);
  const pdf = send('FS_readFile', ['/' + MAIN.replace(/\.tex$/, '.pdf')]);
  if (pdf && typeof pdf.result === 'string' && pdf.result.startsWith('%PDF')) {
    fs.writeFileSync(OUT, Buffer.from(pdf.result, 'latin1'));
    console.log(`texlive.js: wrote ${OUT} (${(fs.statSync(OUT).size / 1024).toFixed(0)} KB)`);
    ok = true;
  } else if (!ok) {
    console.error('--- pdftex output (tail) ---');
    console.error(log.slice(-400).join('\n').split('\n').slice(-70).join('\n'));
    break;
  }
  // stop as soon as a pass is clean -- nothing left to settle
  const thisPass = log.slice(logMark);
  if (!thisPass.some((l) => RERUN.test(l))) {
    console.log(`texlive.js: converged after ${pass} pass(es)`);
    break;
  }
  if (pass === MAX_PASSES) console.log('texlive.js: still not converged at the pass ceiling');
}

if (!ok || !fs.existsSync(OUT)) {
  console.error('--- last output ---');
  console.error(log.slice(-120).join('\n'));
  process.exit(1);
}
if (process.env.HB_TEX_LOG) fs.writeFileSync(process.env.HB_TEX_LOG, log.join('\n'));
const warns = log.filter(l => /^(!|E:)/.test(l)).slice(0, 40);
if (warns.length) console.log('notes:\n' + warns.join('\n'));
console.log('texlive.js: done');
