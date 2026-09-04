#!/usr/bin/env python3
"""Render the Open Graph preview card (public/og.png) from the dataset.

Writes og_card.html, a standalone 1200x630 page. Screenshot that at exactly
1200x630 to produce public/og.png. Colours, projection and hatching are the same
as the map's, so the card and the page cannot drift apart visually.
"""
import json, math, os

H = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(H, 'public', 'hsp_map.json')))
W = d['wards']

DIV = ['#1b6b34', '#3f9b56', '#8ecb9e', '#f0efec', '#f3a3a8', '#de5560', '#a91b2e']
merc_y = lambda lat: 180 / math.pi * math.log(math.tan(math.pi / 4 + lat * math.pi / 360))

def rings(g):
    return [g['coordinates']] if g['type'] == 'Polygon' else g['coordinates']

# Fit the seat to the map panel, same Web Mercator as the page.
xs, ys = [], []
for w in W:
    for poly in rings(w['geometry']):
        for r in poly:
            for x, y in r:
                xs.append(x); ys.append(merc_y(y))
x1, x2, y1, y2 = min(xs), max(xs), min(ys), max(ys)

PANEL_W, PANEL_H, PAD = 560, 630, 30
sc = min((PANEL_W - 2 * PAD) / (x2 - x1), (PANEL_H - 2 * PAD) / (y2 - y1))
ox = (PANEL_W - (x2 - x1) * sc) / 2
oy = (PANEL_H - (y2 - y1) * sc) / 2
to = lambda p: ((p[0] - x1) * sc + ox, (y2 - merc_y(p[1])) * sc + oy)

def colour(lead):
    """Same seven-step diverging ramp as the map, +/-14 points full scale."""
    if lead is None:
        return '#e8e6e1'
    t = max(-1.0, min(1.0, lead / 14.0))
    idx = round((1 - t) / 2 * 6)
    return DIV[int(idx)]

paths = []
for w in W:
    lead = (w.get('derived') or {}).get('green_lab_gap_2026')
    d_attr = ''
    for poly in rings(w['geometry']):
        for r in poly:
            d_attr += 'M' + 'L'.join(f'{to(c)[0]:.1f} {to(c)[1]:.1f}' for c in r) + 'Z'
    paths.append((d_attr, colour(lead), lead is not None and lead < 0))

shapes = '\n'.join(
    f'<path d="{p}" fill="{c}" stroke="#ffffff" stroke-width="1.6"/>' for p, c, _ in paths)
hatch = '\n'.join(
    f'<path d="{p}" fill="url(#h)"/>' for p, _, lab in paths if lab)

html = f'''<!doctype html><meta charset="utf-8">
<style>
  @page {{ size: 1200px 630px; }}
  html,body {{ margin:0; padding:0; width:1200px; height:630px; overflow:hidden;
    background:#faf9f7; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif; }}
  .card {{ display:flex; width:1200px; height:630px; }}
  .txt {{ width:640px; padding:62px 52px 0 62px; }}
  .kick {{ font:600 15px/1 -apple-system,sans-serif; letter-spacing:.13em;
    text-transform:uppercase; color:#1b6b34; margin:0 0 20px; }}
  h1 {{ font-family:'Iowan Old Style',Georgia,serif; font-size:56px; line-height:1.03;
    margin:0 0 22px; color:#16150f; letter-spacing:-.5px; }}
  .sub {{ font-size:21px; line-height:1.42; color:#454239; margin:0 0 30px; }}
  .stat {{ display:flex; gap:44px; margin:0 0 30px; }}
  .stat b {{ display:block; white-space:nowrap; font-family:'Iowan Old Style',Georgia,serif;
    font-size:40px; line-height:1; color:#1b6b34; margin-bottom:7px; }}
  .stat .u {{ display:inline; font-size:22px; color:#3f7d4f; }}
  .stat .d {{ font-size:14px; line-height:1.32; color:#6b675c; display:block; max-width:158px; }}
  .foot {{ font-size:15px; color:#6b675c; border-top:1px solid #e2dfd7; padding-top:16px; }}
  .map {{ width:560px; height:630px; background:#f2f0eb; }}
</style>
<div class="card">
  <div class="txt">
    <p class="kick">A by-election in eleven wards</p>
    <h1>Holborn and<br>St&nbsp;Pancras</h1>
    <p class="sub">Ward-level results, turnout, census and deprivation —
      built from published data only.</p>
    <div class="stat">
      <div><b>2.5<span class="u">&thinsp;pts</span></b>
        <span class="d">Labour lead over the Greens where a Green stood</span></div>
      <div><b>9.2<span class="u">&thinsp;pts</span></b>
        <span class="d">The lead across all eleven wards</span></div>
    </div>
    <p class="foot">holborn-st-pancras-map.pages.dev</p>
  </div>
  <div class="map">
    <svg width="560" height="630" viewBox="0 0 560 630">
      <defs><pattern id="h" width="7" height="7" patternTransform="rotate(45)"
        patternUnits="userSpaceOnUse">
        <line x1="0" y1="0" x2="0" y2="7" stroke="rgba(255,255,255,.85)" stroke-width="2.6"/>
      </pattern></defs>
      {shapes}
      {hatch}
    </svg>
  </div>
</div>'''

open(os.path.join(H, 'og_card.html'), 'w').write(html)
print('og_card.html written — screenshot at exactly 1200x630 to make public/og.png')
