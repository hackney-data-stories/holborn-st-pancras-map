#!/usr/bin/env python3
"""Inline data/../public/hsp_map.json into page_template.html to make public/index.html.

The published page makes no network requests at all: no tiles, no map library, no
fonts, no analytics. That is a deliberate constraint, so the data has to be inside
the HTML rather than fetched beside it.
"""
import os, re, sys
H = os.path.dirname(os.path.abspath(__file__))
tpl = open(os.path.join(H, 'page_template.html')).read()
data = open(os.path.join(H, 'public', 'hsp_map.json')).read()
assert '__DATA__' in tpl, 'template has no __DATA__ token'
out = tpl.replace('__DATA__', data)

# Guard the zero-request promise and the framing, so neither can regress silently.
banned = [(r'<script[^>]+\ssrc=', 'external script'),
          (r'<link[^>]+\shref=', 'external stylesheet'),
          (r'@import', 'css import'),
          (r'\bfetch\s*\(', 'fetch call'),
          (r'Not for publication', 'internal-only marking'),
          (r'(?i)campaign brief', 'campaign branding')]
scan = re.sub(r'<a\s[^>]*>', '', out)
for pat, what in banned:
    m = re.search(pat, scan)
    if m:
        sys.exit(f'refusing to build: found {what} at offset {m.start()}')

open(os.path.join(H, 'public', 'index.html'), 'w').write(out)
print(f'public/index.html written, {len(out):,} bytes, no external requests')
