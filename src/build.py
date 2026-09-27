"""Build ../aws-organization-redesign.html from body.html and sources.json.

Citations in body.html are written as {{r:key,key}} and {{U}} marks an
unverified item. Official documentation (user guides, API references, FAQs,
What's New) is numbered [1], [2], ...; AWS blogs and re:Post are numbered
[B1], [B2], ... Both are numbered in order of first appearance, and only
cited sources are listed.
"""
import html
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / 'aws-organization-redesign.html'

SOURCES = {k: tuple(v) for k, v in json.loads((HERE / 'sources.json').read_text(encoding='utf-8')).items()}
UNV = '<span class="unv">unverified:</span>'


def is_blog(url):
    return '/blogs/' in url or 'repost.aws' in url


body = (HERE / 'body.html').read_text(encoding='utf-8').replace('{{U}}', UNV)
order = {'doc': [], 'blog': []}


def ref(m):
    out = []
    for key in [k.strip() for k in m.group(1).split(',')]:
        if key not in SOURCES:
            sys.exit(f'unknown source key: {key}')
        kind = 'blog' if is_blog(SOURCES[key][1]) else 'doc'
        if key not in order[kind]:
            order[kind].append(key)
        n = order[kind].index(key) + 1
        if kind == 'doc':
            out.append(f'<a class="ref" href="#s{n}">[{n}]</a>')
        else:
            out.append(f'<a class="ref b" href="#b{n}">[B{n}]</a>')
    return ''.join(out)


body = re.sub(r'\{\{r:([^}]+)\}\}', ref, body)
if '{{' in body:
    sys.exit('unresolved template marker')


def items(kind, prefix, label):
    rows = []
    for i, key in enumerate(order[kind], 1):
        title, url = SOURCES[key]
        u = html.escape(url)
        rows.append(f'  <li id="{prefix}{i}"><span class="no">[{label}{i}]</span> {title} — <a href="{u}">{u}</a></li>')
    return '\n'.join(rows)


unused = sorted(set(SOURCES) - set(order['doc']) - set(order['blog']))
if unused:
    sys.exit(f'sources.json has uncited entries: {unused}')

CSS = """
:root{
  --bg:#f7f7f5; --surface:#ffffff; --surface-2:#f0f0ec; --text:#1d1d1b; --muted:#5d5d58;
  --line:#dcdcd6; --accent:#1f5fa8; --accent-soft:#e6eef8;
  --ok:#1d7a46; --ok-soft:#e5f3eb; --warn:#9a5b00; --warn-soft:#fbf0dc; --bad:#a8322b; --bad-soft:#f8e6e4;
  --code-bg:#f3f3ef;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --bg:#161615; --surface:#1f1f1d; --surface-2:#272725; --text:#ebebe6; --muted:#a3a39c;
    --line:#3a3a37; --accent:#7fb0ea; --accent-soft:#1d2a3a;
    --ok:#6cc893; --ok-soft:#18291f; --warn:#e3a94d; --warn-soft:#2e2414; --bad:#ec8a82; --bad-soft:#321b19;
    --code-bg:#232321;
  }
}
:root[data-theme="dark"]{
  --bg:#161615; --surface:#1f1f1d; --surface-2:#272725; --text:#ebebe6; --muted:#a3a39c;
  --line:#3a3a37; --accent:#7fb0ea; --accent-soft:#1d2a3a;
  --ok:#6cc893; --ok-soft:#18291f; --warn:#e3a94d; --warn-soft:#2e2414; --bad:#ec8a82; --bad-soft:#321b19;
  --code-bg:#232321;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--text);font-family:"Segoe UI","Hiragino Sans","Noto Sans JP","Yu Gothic UI",sans-serif;line-height:1.75;font-size:15.5px}
.wrap{max-width:1120px;margin:0 auto;padding:32px 16px 80px}
header.hero{border-bottom:1px solid var(--line);padding-bottom:20px;margin-bottom:28px}
.hero h1{font-size:1.9rem;margin:0 0 6px}
.hero p{margin:4px 0;color:var(--muted)}
.meta{font-size:.85rem}
p.meta{color:var(--muted)}
nav.toc{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:14px 18px;margin-bottom:32px}
nav.toc ol{margin:0;padding-left:1.3em;columns:2;column-gap:32px}
nav.toc a{color:var(--accent);text-decoration:none}
nav.toc a:hover{text-decoration:underline}
h2{font-size:1.4rem;margin:52px 0 12px;padding-top:8px;border-top:2px solid var(--text)}
h3{font-size:1.1rem;margin:30px 0 8px}
h4{font-size:1rem;margin:22px 0 6px}
p{margin:8px 0}
a{color:var(--accent)}
.table-wrap{overflow-x:auto;margin:12px 0;border:1px solid var(--line);border-radius:8px;background:var(--surface)}
table{border-collapse:collapse;width:100%;font-size:.88rem}
th,td{padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top;text-align:left}
th{background:var(--surface-2);font-weight:600;white-space:nowrap}
tr:last-child td{border-bottom:none}
td.nw{white-space:nowrap}
table.kv td:first-child{white-space:nowrap}
table.lbl td:first-child{min-width:11em}
code{font-family:"Cascadia Code",Consolas,"SFMono-Regular",monospace;font-size:.85em;background:var(--code-bg);padding:1px 5px;border-radius:4px;overflow-wrap:anywhere}
pre{background:var(--code-bg);border:1px solid var(--line);border-radius:8px;padding:12px 14px;overflow-x:auto;font-size:.8rem;line-height:1.5}
pre code{background:none;padding:0;overflow-wrap:normal}
.tag{display:inline-block;font-size:.75rem;font-weight:600;padding:1px 8px;border-radius:99px;white-space:nowrap}
.t-must{background:var(--bad-soft);color:var(--bad)}
.t-rec{background:var(--ok-soft);color:var(--ok)}
.ok-mark{color:var(--ok);font-weight:700;white-space:nowrap}
.ng-mark{color:var(--bad);font-weight:700;white-space:nowrap}
.unv{font-family:"Cascadia Code",Consolas,monospace;font-size:.78em;font-weight:700;color:var(--warn);background:var(--warn-soft);padding:0 5px;border-radius:4px;white-space:nowrap}
a.ref{font-size:.72em;vertical-align:super;text-decoration:none;margin-left:1px;white-space:nowrap}
a.ref.b{color:var(--muted)}
figure.diagram{margin:16px 0 20px;width:min(1780px,calc(100vw - 48px));position:relative;left:50%;transform:translateX(-50%)}
figure.diagram .canvas{background:#ffffff;border:1px solid var(--line);border-radius:10px;padding:10px;overflow-x:auto}
figure.diagram .canvas a{display:block}
figure.diagram img{display:block;max-width:100%;min-width:760px;height:auto;margin:0 auto}
figure.diagram figcaption{font-size:.86rem;color:var(--muted);margin:8px auto 0;max-width:1088px}
ol.steps>li,ul.list>li{margin:7px 0}
dl.notes{margin:12px 0}
dl.notes dt{font-weight:700;margin-top:14px}
dl.notes dd{margin:2px 0 0}
.src{font-size:.82rem;list-style:none;padding-left:0}
.src li{margin:3px 0;overflow-wrap:anywhere;padding-left:3.6em;text-indent:-3.6em}
.src .no{display:inline-block;min-width:3.4em;color:var(--muted)}
footer{margin-top:56px;padding-top:16px;border-top:1px solid var(--line);font-size:.82rem;color:var(--muted)}
@media (max-width:720px){nav.toc ol{columns:1}.hero h1{font-size:1.5rem}}
@media print{nav.toc{display:none}}
""".strip('\n')

doc = f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AWS Organization 再設計</title>
<style>
{CSS}
</style>
</head>
<body>
<div class="wrap">

{body.rstrip()}

<!-- 11 -->
<h2 id="sources">11. 出典</h2>
<h3>公式ドキュメント（ユーザーガイド、API リファレンス、FAQ、What's New）</h3>
<ul class="src">
{items('doc', 's', '')}
</ul>
<h3>AWS のブログと re:Post</h3>
<ul class="src">
{items('blog', 'b', 'B')}
</ul>

<footer>
図は AWS Architecture Icons（draw.io の AWS4 シェイプ）で作成した。図をクリックすると原寸で開く。編集用のファイルは <a href="diagrams/org-structure.drawio">org-structure.drawio</a> と <a href="diagrams/migration-bridge-share.drawio">migration-bridge-share.drawio</a>。
</footer>
</div>
</body>
</html>
"""

# JSON samples must parse; SCP/RCP samples must fit the size limits.
for block in re.findall(r'<pre><code>(.*?)</code></pre>', doc, re.S):
    text = html.unescape(block)
    obj = json.loads(text)
    if 'Statement' in obj:
        kind = 'RCP' if any('Principal' in st for st in obj['Statement']) else 'SCP'
        limit = 5120 if kind == 'RCP' else 10240
        assert len(text) <= limit, (kind, len(text))
        print(f'{kind} sample OK: {len(text)} chars')
    else:
        print('declarative sample OK')

OUT.write_text(doc, encoding='utf-8')
print(f'written {OUT.name}: {len(doc.encode("utf-8"))} bytes; docs {len(order["doc"])}, blogs/re:Post {len(order["blog"])}')
