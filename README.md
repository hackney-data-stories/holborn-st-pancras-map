# Holborn and St Pancras: a by-election in eleven wards

A ward-level map of the Holborn and St Pancras constituency, built for the
by-election called on 1 September 2026 following the resignation of Keir Starmer.
Every figure comes from published sources.

**Live map:** https://holborn-st-pancras-map.pages.dev

Open `public/index.html` in any browser and it works offline. The page makes no
network requests at all: no map tiles, no mapping library, no web fonts, no
analytics. The build refuses to produce a page that would.

## What it shows

Eleven wards, coloured by any of twelve measures: the Green lead over Labour in
the May 2026 locals, each party's share, the change since 2022, turnout and its
change, electorate, and then census and deprivation context — private and social
renting, students, age, and the Index of Multiple Deprivation. Click a ward for
its full 2026 and 2022 results, its census profile and its polling districts.
Everything the colours encode is also available as plain text through the
"Table view" button.

## Three things in it

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
3. **The July by-election shows what differential turnout does.** Regent's Park
   voted again on 9 July 2026 on a 21.9% turnout, against 35.1% ten weeks
   earlier. Labour took back a ward the Greens had swept in May, by 94 votes,
   with an independent on 407.

## What it is not

There is no ward-level 2024 general election data. None exists. The 2024 result
appears here as a single constituency figure and every ward-level number is from
a local election. Local election shares are not a general election forecast, and
a by-election is a third kind of contest again. Nothing here is a prediction.

## Confidence

| Tier | What |
|---|---|
| **A** | Ward vote counts and turnout percentages, from Camden's own declarations. |
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
| `data/camden_2026_hsp_wards.json` | The one hand-transcribed input. |
| `BRIEFING.md` | The longer written analysis. |

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
