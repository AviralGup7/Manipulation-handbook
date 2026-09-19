#!/usr/bin/env python3
"""grounding_scan.py -- flag entry claims that do not trace to any claimed source.

Extracts hard-claim markers (numbers, percentages, years, money, multi-word
proper nouns) from every topic entry and checks each against
  (a) the corpus text of every source in the entry's @sources line, and
  (b) the entry's dossier files.
Markers found in neither are printed as suspects. Human review decides.
"""
import re, os, glob

corp = {}
for f in glob.glob('registry/corpus/B*.txt'):
    bid = os.path.basename(f)[:-4]
    if bid.endswith('.norm'):
        continue
    corp[bid] = ' '.join(open(f, errors='ignore').read().lower().split())

entries = []
for f in sorted(glob.glob('topics/c*/T-*.tex')):
    s = open(f).read()
    hid = re.search(r'%%\s*@id:\s*(\S+)', s)
    src = re.search(r'%%\s*@sources:\s*(.+)', s)
    ttl = re.search(r'%%\s*@title:\s*(.+)', s)
    body = '\n'.join(l for l in s.splitlines() if not l.startswith('%%'))
    entries.append((hid.group(1), ttl.group(1).strip(),
                    [x.strip() for x in src.group(1).split(',')], body))

STOP = set("""the a an and or but of in on at to for with by from as is are was were be been it its this that these those
he she they you i we his her their your our them him me us not no if then than so such can could may might will would
shall should must have has had do does did done what when where which who whom how why all any both each few more most
other some only own same too very just also into over under again once about against between through during before after
above below up down out off there here one two three four five six seven eight nine ten new old part chapter book source
core mechanism conditions application feedback failure countermeasures related see sources law laws tactic rule chapter""".split())

def proper_nouns(body):
    out = set()
    for m in re.finditer(r'(?<! [."])\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b', body, re.X):
        w = m.group(1)
        if w.split()[0].lower() in STOP:
            continue
        if any(k in w for k in ('Core', 'Mechanism', 'Application', 'Feedback',
                                'Failure', 'Conditions', 'Source', 'Related')):
            continue
        out.add(w)
    return out

def numbers(body):
    return set(m.group(1).strip() for m in re.finditer(
        r'(\d+(?:\.\d+)?\s*%|\b(?:19|20)\d{2}\b|\$\s?\d[\d,\.]*|\b\d{2,}\b)', body))

rows = []
for eid, ttl, srcs, body in entries:
    doss = ''
    for b in srcs:
        p = 'sources/%s/%s-%s.tex' % (b, b, eid)
        if os.path.exists(p):
            doss += open(p, errors='ignore').read().lower()
    nums = numbers(body)
    names = proper_nouns(body)
    miss_nums = [n for n in nums
                 if not any(n in corp.get(b, '') or
                            n.replace('%', '').replace('$', '').replace(',', '')
                            in corp.get(b, '') for b in srcs)
                 and n not in doss]
    miss_names = [w for w in names
                  if not any(w.lower() in corp.get(b, '') for b in srcs)
                  and w.lower() not in doss]
    rows.append((eid, ','.join(srcs), len(nums), len(nums) - len(miss_nums),
                 miss_nums, miss_names, ttl))

rows.sort(key=lambda r: -(len(r[4]) + len(r[5])))
suspicious = 0
for eid, srcs, nn, nh, mn, mname, ttl in rows:
    if not mn and not mname:
        continue
    suspicious += 1
    print('%-10s %-9s nums %d/%d | %s' % (eid, srcs, nh, nn, ttl[:36]))
    if mn:
        print('%31s nums missing: %s' % ('', mn))
    if mname:
        print('%31s names missing: %s' % ('', mname[:8]))
print('\n%d of %d entries have untraced hard markers' % (suspicious, len(rows)))
