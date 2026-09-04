# Holborn and St Pancras: a by-election in eleven wards

A ward-level map of the Holborn and St Pancras constituency, built for the
by-election called on 1 September 2026 following the resignation of Keir Starmer.
Every figure comes from published sources.

**Live map:** https://holborn-st-pancras-map.pages.dev

Open `public/index.html` in any browser and it works offline. The page makes no
network requests at all: no map tiles, no mapping library, no web fonts, no
analytics. The build refuses to produce a page that would. (`og.png` is named in
the metadata for link previews, but only crawlers ever fetch it — rendering the
page still touches nothing.)

## What it shows

Eleven wards, coloured by any of fifteen measures: the Green lead over Labour in
the May 2026 locals, each party's share, the change since 2022, turnout and its
change, electorate, and then census and deprivation context — private and social
renting, students, age, and the Index of Multiple Deprivation. Click a ward for
its full 2026 and 2022 results, its census profile and its polling districts.
Everything the colours encode is also available as plain text through the
"Table view" button.

## Four things in it

1. **The nine-point gap is mostly an artefact of not standing.** Across all
   eleven wards Labour led the Greens by 9.2 points in May 2026. Across the nine
   wards where a Green candidate was actually on the ballot, the lead was 2.5
   points. The Greens fielded nobody in King's Cross or St Pancras and Somers
   Town, which between them hold about a fifth of the electorate.
2. **The Green vote here does not track the graduate vote.** Across the nine
   contested wards the Green lead over Labour correlates +0.66 with social
   renting and −0.57 with degree holding. Bloomsbury has the most students in the
   seat, 39.7%, and the Greens did not win it. Nine wards is a very small sample
   and these are correlations between ward averages, not between voters — the
   page says so at more length.
3. **The one clean by-election test points the wrong way for the Greens.**
   Regent's Park voted again on 9 July 2026 on a 21.9% turnout, against 35.1% ten
   weeks earlier. Labour took back a ward the Greens had swept in May, by 94
   votes, with an independent on 407. The Green share fell 11.2 points on turnout
   down 13.2. Same ward, same register, ten weeks apart.

   Two earlier by-elections, Camden Square and Kentish Town South on 5 September
   2024, are in the data too, but they sit *before* the Green advance, so their
   low Green shares measure eighteen months of change rather than a turnout
   effect. The dataset marks this with a `comparable` flag on every comparison and
   the page refuses to draw the turnout inference from them. Only Regent's Park is
   a turnout test.

4. **Every ward's last seat was won across party lines, eight of them by under
   fifty votes.** Camden Square by 18, Bloomsbury by 19, St Pancras and Somers
   Town by 21, then four more under fifty. Six of those eight were Green against
   Labour. Labour holds 23 of the seat's 30 council seats and the Greens 6, but
   those totals sit on margins a single canvassing round could cover.

## On the vote outside the main parties

One layer shows the largest vote in each ward for a candidate outside Labour, the
Conservatives, the Liberal Democrats, the Greens and Reform. **These candidates
are not a bloc** — the two large figures are the Camden People's Alliance, a
community slate; the two small ones are the National Housing Party, which stood on
the opposite side of the argument. The layer names the party in every case.

It exists because Andrew Feinstein took 18.9% here as an independent in 2024 and is
not standing again, which makes that the largest unattached vote in the seat. It is
**not** an estimate of where his votes came from, and this repository deliberately
does not contain one. No ward-level 2024 general election data exists, so any such
estimate would be a single constituency total allocated across eleven wards by an
assumed proxy, unverifiable in principle because no ground truth will ever exist at
that geography. The obvious proxy would be religious and ethnic demography, which
would amount to profiling an electorate and presenting it as measurement.

What the observed data supports is narrower and still useful: the Camden People's
Alliance took 32.9% and 30.3% in St Pancras and Somers Town and King's Cross, and
independents took 22.9%, 20.1% and 16.8% in the three by-elections since 2022.
Feinstein's 18.9% sits inside that band. That indicates the size of the
unaligned vote, not its location, and nothing here says whose it is now.

## What it is not

There is no ward-level 2024 general election data. None exists. The 2024 result
appears here as a single constituency figure and every ward-level number is from
a local election. Local election shares are not a general election forecast, and
a by-election is a third kind of contest again. Nothing here is a prediction.

## Confidence

| Tier | What |
|---|---|
| **A** | Ward vote counts and turnout percentages, from Camden's own declarations. So are all three by-elections, which being single-member contests have real shares of ballot papers rather than best-candidate shares. |
| **B** | Electorates and ballot counts. Camden publishes turnout only as a percentage, so these are derived: ballots = votes ÷ published candidate share, electorate = ballots ÷ turnout. Where the shares are not published the 2022 register stands in; in the four wards where both years can be derived the two differ by under 5%. Census and deprivation figures, aggregated to wards by best-fit small area, are also Tier B. |
| **C** | Anything about Primrose Hill, which straddles two constituencies. Only polling district TB is in this seat, roughly a third of the ward. |

Two independent checks. The derived electorates total 73,831 against a published
2024 register of 71,300, 3.5% high, which is the right direction and order for
two years of register growth. The seat-wide May shares computed here, Labour
38.3% to Green 29.1%, fall within half a point of PollCheck's separately
calculated 38.8% and 28.8%.

## Rebuilding it

```bash
python3 -m venv .venv
.venv/bin/pip install shapely beautifulsoup4 lxml
.venv/bin/python fetch_sources.py     # downloads ~21 MB into raw/
.venv/bin/python build_hsp_data.py    # writes public/hsp_map.json
.venv/bin/python build_page.py        # inlines it into public/index.html
```

A clean checkout reproduces `public/hsp_map.json` byte for byte.

The site is a git-connected Cloudflare Pages project: **pushing to `main`
rebuilds and redeploys it**, and pull requests get their own preview URL. There is
no build command — Pages serves `public/` as it finds it — so if you change the
dataset or the template, run `build_page.py` and commit the regenerated
`public/index.html` along with it. `./deploy.sh` still works for deploying
without a push.

The link-preview card is generated too, so it cannot drift from the data. Run
`make_og_image.py` to rebuild `og_card.html`, then screenshot it at exactly
1200x630 at 2x device scale:

```bash
python3 make_og_image.py
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless \
  --disable-gpu --hide-scrollbars --force-device-scale-factor=2 \
  --window-size=1200,630 --screenshot=public/og.png og_card.html
```

One input is not fetchable. Camden's ward result pages sit behind bot protection
and refuse a scripted request, so the 7 May 2026 declarations were read from the
rendered pages by hand and are committed at `data/camden_2026_hsp_wards.json`.
Every vote in that file was checked against camden.gov.uk and independently
against the Wikipedia transcription, which agrees on all eleven wards.

## Layout

| Path | What |
|---|---|
| `public/index.html` | The map. Self-contained, offline-capable. |
| `public/hsp_map.json` | The dataset: 11 wards, 64 small areas, 31 polling stations. |
| `page_template.html` | Page source, with a `__DATA__` token where the JSON goes. |
| `fetch_sources.py` | Downloads every machine-fetchable source into `raw/`. |
| `build_hsp_data.py` | Builds the dataset. |
| `build_page.py` | Inlines the dataset; refuses to emit a page with external requests. |
| `data/camden_2026_hsp_wards.json` | The 7 May 2026 declarations, hand-transcribed. |
| `data/camden_byelections.json` | All three by-elections held in the seat since 2022. |
| `BRIEFING.md` | The longer written analysis. |
| `deploy.sh` | Rebuilds the page and deploys it out of band, without a push. |
| `make_og_image.py` | Regenerates `og_card.html`, the link-preview card, from the dataset. |
| `public/og.png` | The link preview, 2400x1260. Rendered from `og_card.html`. |

## Who made this

Built by George Sheldon Grün, 4 September 2026, from published sources only. No
canvass data, no private polling, no voter records. The author is a Green Party
member, which is a reason to check the workings rather than to take them on
trust: the code, the dataset and every source are here, and the page marks where
each figure is official and where it is derived.

Corrections are welcome as issues.

## Licence

Code MIT (`LICENSE`). Data is not — see [`DATA-LICENCE.md`](DATA-LICENCE.md).
Sources are Open Government Licence v3.0, except the Wikipedia transcriptions,
which are CC BY-SA 4.0.

> Contains public sector information licensed under the Open Government Licence
> v3.0. Source: Office for National Statistics licensed under the Open Government
> Licence v.3.0. Contains OS data © Crown copyright and database right 2026.

