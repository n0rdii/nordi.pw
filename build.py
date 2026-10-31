#!/usr/bin/env python3
import json
import os
import re
from pathlib import Path
from html import escape
from datetime import datetime

ROOT = Path(__file__).parent
ARTICLES = ROOT / 'articles'
DIST = ROOT / 'dist'

ARTICLE_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — nordi_</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🐾</text></svg>">
<style>
{styles}
.article-page{{padding-top:100px}}
.article-page .container{{max-width:720px;margin:0 auto;padding:0 24px}}
.article-back{{display:inline-flex;align-items:center;gap:6px;color:#a1a1aa;font-size:.9rem;margin-bottom:32px;cursor:pointer;text-decoration:none}}
.article-back:hover{{color:#fff}}
.article-content{{line-height:1.8;font-size:1.05rem}}
.article-content h1{{font-size:2rem;margin-bottom:16px;color:#fff}}
.article-content h2{{font-size:1.4rem;margin-top:32px;margin-bottom:12px;color:#fff}}
.article-content h3{{font-size:1.15rem;margin-top:24px;margin-bottom:8px;color:#fff}}
.article-content p{{margin-bottom:16px;color:#d4d4d8}}
.article-content ul,.article-content ol{{padding-left:24px;margin-bottom:16px;color:#d4d4d8}}
.article-content li{{margin-bottom:4px}}
.article-content a{{color:#67e8f9;text-decoration:underline}}
.article-content a:hover{{color:#22d3ee}}
.article-content code{{background:rgba(255,255,255,.06);padding:2px 6px;border-radius:4px;font-size:.9em}}
.article-content pre{{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.08);border-radius:8px;padding:16px;overflow-x:auto;margin-bottom:16px}}
.article-content pre code{{background:none;padding:0;font-size:.85rem;color:#e4e4e7}}
.article-content strong{{color:#fff}}
.article-content blockquote{{border-left:3px solid rgba(34,211,238,.3);padding-left:16px;color:#a1a1aa;margin-bottom:16px;font-style:italic}}
.article-content img{{max-width:100%;border-radius:8px;margin:16px 0}}
.article-content hr{{border:none;height:1px;background:rgba(255,255,255,.06);margin:32px 0}}
</style>
</head>
<body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Oxygen,Ubuntu,Cantarell,sans-serif;background:#0a0a0f;color:#e4e4e7;line-height:1.6;margin:0">
<div class="article-page">
<div class="container">
<a class="article-back" href="/">← Back to home</a>
<div class="article-content">
{body}
</div>
</div>
</div>
</body>
</html>'''

def extract_frontmatter(text):
    meta = {}
    rest = text
    if text.startswith('---'):
        end = text.find('---', 3)
        if end > 0:
            for line in text[3:end].strip().split('\n'):
                m = re.match(r'^(\w+):\s*(.+)', line)
                if m:
                    val = m.group(2).strip()
                    if val.startswith('[') and val.endswith(']'):
                        meta[m.group(1)] = [t.strip().strip('\'"') for t in val[1:-1].split(',') if t.strip()]
                    else:
                        meta[m.group(1)] = val.strip('\'"')
            rest = text[end+3:].strip()
    return meta, rest

def md_to_html(src):
    lines = src.split('\n')
    out = []
    i = 0
    def inline(s):
        s = escape(s)
        s = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', s)
        s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
        s = re.sub(r'\*(.+?)\*', r'<em>\1</em>', s)
        s = re.sub(r'`(.+?)`', r'<code>\1</code>', s)
        s = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2" target="_blank">\1</a>', s)
        return s

    while i < len(lines):
        l = lines[i]
        if l.startswith('```'):
            code = []
            i += 1
            while i < len(lines) and not lines[i].startswith('```'):
                code.append(lines[i])
                i += 1
            out.append(f'<pre><code>{escape(chr(10).join(code))}</code></pre>')
            i += 1
            continue
        if l.startswith('### '):
            out.append(f'<h3>{inline(l[4:])}</h3>')
            i += 1
            continue
        if l.startswith('## '):
            out.append(f'<h2>{inline(l[3:])}</h2>')
            i += 1
            continue
        if l.startswith('# '):
            out.append(f'<h1>{inline(l[2:])}</h1>')
            i += 1
            continue
        if l.startswith('> '):
            out.append(f'<blockquote>{inline(l[2:])}</blockquote>')
            i += 1
            continue
        if l.startswith('- '):
            items = []
            while i < len(lines) and lines[i].startswith('- '):
                items.append(f'<li>{inline(lines[i][2:])}</li>')
                i += 1
            out.append(f'<ul>{"".join(items)}</ul>')
            continue
        if re.match(r'^\d+\. ', l):
            items = []
            while i < len(lines) and re.match(r'^\d+\. ', lines[i]):
                items.append(f'<li>{inline(re.sub(r"^\d+\. ", "", lines[i]))}</li>')
                i += 1
            out.append(f'<ol>{"".join(items)}</ol>')
            continue
        if l == '':
            out.append('<br>')
            i += 1
            continue
        if l == '---':
            out.append('<hr>')
            i += 1
            continue
        out.append(f'<p>{inline(l)}</p>')
        i += 1

    return '\n'.join(out)

def main():
    styles = (ROOT / 'index.html').read_text()
    m = re.search(r'<style>(.*?)</style>', styles, re.DOTALL)
    base_styles = m.group(1).strip() if m else ''

    DIST.mkdir(exist_ok=True)

    index = []
    for md_file in sorted(ARTICLES.glob('*.md'), reverse=True):
        text = md_file.read_text()
        meta, body = extract_frontmatter(text)
        slug = md_file.stem

        html_body = md_to_html(body)
        html_out = ARTICLE_TEMPLATE.format(
            title=escape(meta.get('title', slug)),
            styles=base_styles,
            body=html_body
        )
        (DIST / f'{slug}.html').write_text(html_out)
        print(f'  built: dist/{slug}.html')

        index.append({
            'slug': slug,
            'title': meta.get('title', slug),
            'date': meta.get('date', ''),
            'description': meta.get('description', ''),
            'tags': meta.get('tags', []) if isinstance(meta.get('tags'), list) else [t.strip() for t in meta.get('tags', '').split(',') if t.strip()],
        })

    (DIST / 'index.json').write_text(json.dumps(index, indent=2, ensure_ascii=False))
    print(f'\n  index: dist/index.json ({len(index)} articles)')

if __name__ == '__main__':
    main()
