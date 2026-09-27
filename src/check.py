"""Structural checks for ../aws-organization-redesign.html. Exit code 1 on failure."""
import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / 'aws-organization-redesign.html'
s = PAGE.read_text(encoding='utf-8')
VOID = {'meta', 'br', 'img', 'hr', 'link', 'input'}
errors = []


class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack, self.ids, self.hrefs, self.srcs = [], [], [], []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if 'id' in d:
            self.ids.append(d['id'])
        if tag == 'a' and 'href' in d:
            self.hrefs.append(d['href'])
        if tag == 'img':
            self.srcs.append(d.get('src'))
        if tag not in VOID:
            self.stack.append((tag, self.getpos()))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack:
            errors.append(f'extra </{tag}> at {self.getpos()}')
            return
        top, pos = self.stack.pop()
        if top != tag:
            errors.append(f'<{top}> at {pos} closed by </{tag}> at {self.getpos()}')


p = Parser()
p.feed(s)
if p.stack:
    errors.append(f'unclosed tags: {p.stack[:5]}')
dups = sorted({i for i in p.ids if p.ids.count(i) > 1})
if dups:
    errors.append(f'duplicate ids: {dups}')
broken = sorted({h[1:] for h in p.hrefs if h.startswith('#') and h[1:] not in p.ids})
if broken:
    errors.append(f'broken anchors: {broken}')
for path in p.srcs + [h for h in p.hrefs if h.startswith('diagrams/')]:
    if not (ROOT / path).exists():
        errors.append(f'missing file: {path}')

refs = re.findall(r'<a class="ref( b)?" href="#([sb])(\d+)">\[(B?)(\d+)\]</a>', s)
for blog, prefix, n, label, m in refs:
    if n != m or (prefix == 'b') != bool(blog) or (prefix == 'b') != (label == 'B'):
        errors.append(f'ref label mismatch: #{prefix}{n} [{label}{m}]')
for prefix in ('s', 'b'):
    cited = [int(n) for _, pr, n, _, _ in refs if pr == prefix]
    listed = sorted(int(i[1:]) for i in p.ids if re.fullmatch(prefix + r'\d+', i))
    if listed != list(range(1, len(listed) + 1)):
        errors.append(f'{prefix}-sources not contiguous')
    if set(listed) != set(cited):
        errors.append(f'{prefix}-sources cited/listed differ: {sorted(set(listed) ^ set(cited))}')
    first = []
    for n in cited:
        if n not in first:
            first.append(n)
    if first != sorted(first):
        errors.append(f'{prefix}-sources not numbered by first appearance')
    print(f'{prefix}: {len(listed)} sources')

text = re.sub(r'<[^>]+>', '', s)
for o, c in [('（', '）'), ('「', '」'), ('(', ')'), ('[', ']')]:
    if text.count(o) != text.count(c):
        errors.append(f'unbalanced {o}{c}: {text.count(o)} vs {text.count(c)}')
print('unverified:', s.count('class="unv"'))

if errors:
    print('FAIL')
    for e in errors:
        print(' -', e)
    sys.exit(1)
print('OK')
