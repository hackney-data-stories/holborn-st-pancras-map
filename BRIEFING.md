# Holborn and St Pancras: what the public data says

**4 September 2026.**

By-election called 1 September 2026 on the resignation of Keir Starmer. Polling day
not yet set. Everything below is built from public sources: Camden Council's own
result declarations, the ONS Census 2021, MHCLG deprivation statistics and ONS
boundaries. No canvass data, no membership data, no private polling.

The companion map is `public/index.html`. It opens in any browser with no network
connection and no server. Every figure it colours is also available as plain text
through the "Table view" button.

Written by George Sheldon Grün, a Green Party member. That is a reason to check the
workings rather than to take them on trust, so the code, the dataset and every
source are in this repository, and each figure below is marked for where it is
official and where it is derived. Corrections are welcome as issues.

---

## 1. The headline everyone will quote is misleading

After May's locals the press line was that Labour leads the Greens by about nine
points across this seat. Summing the best candidate for each party across the
eleven wards, weighted into the constituency, gives:

| Party | All eleven wards | The nine wards with a Green candidate |
|---|---|---|
| Labour | 38.3% | 38.4% |
| Green | 29.1% | 35.9% |
| Reform UK | 9.2% | 8.7% |
| Conservative | 8.4% | 8.7% |
| Liberal Democrat | 7.0% | 6.6% |
| Camden People's Alliance | 6.0% | — |

The Greens fielded no candidate in King's Cross or St Pancras and Somers Town. In
a local election that costs you those wards. In a by-election there is one ballot
paper across the whole seat and a Green name is on it everywhere. The right
starting point is a **2.5-point deficit**, not a 9-point one.

That is the single most important number in this document, and it is also the
most easily overstated. It assumes the Greens can reach in those two wards what
they reach elsewhere, and section 4 gives a concrete reason to doubt that.

## 2. Every ward, ranked by Green share

| Ward | Electorate | Turnout | Green | Labour | Green lead | Social rent | Private rent | Students | Deprivation |
|---|---|---|---|---|---|---|---|---|---|
| Kentish Town North | 5,531 | 49.59% | 40.4% | 47.5% | -7.1 | 26.7% | 36.3% | 8.8% | 18.7 |
| Holborn and Covent Garden | 7,982 | 37.4% | 38.9% | 31.7% | +7.2 | 45.4% | 34.7% | 20.1% | 27.8 |
| Regent's Park | 8,079 | 35.12% | 38.3% | 32.7% | +5.6 | 51.3% | 30.1% | 22.3% | 30.9 |
| Kentish Town South | 7,425 | 41.26% | 37.8% | 42.6% | -4.8 | 41.0% | 28.8% | 14.5% | 26.4 |
| Camden Square | 5,703 | 36.89% | 35.7% | 38.2% | -2.5 | 38.7% | 33.6% | 14.7% | 27.3 |
| Camden Town | 4,832 | 32.42% | 34.4% | 44.0% | -9.6 | 41.9% | 38.2% | 17.6% | 34.7 |
| Bloomsbury | 6,706 | 33.76% | 34.2% | 36.8% | -2.6 | 32.1% | 43.3% | 39.7% | 21.7 |
| Haverstock | 8,585 | 37.99% | 34.0% | 38.4% | -4.4 | 47.5% | 27.6% | 12.2% | 31.4 |
| Primrose Hill | 8,620 | 39.07% | 21.6% | 33.2% | -11.6 | 25.4% | 36.2% | 10.5% | 15.2 |
| King's Cross | 7,244 | 31.93% | — | 40.8% | — | 47.3% | 33.7% | 31.8% | 30.2 |
| St Pancras and Somers Town | 8,280 | 32.81% | — | 35.9% | — | 60.4% | 25.6% | 24.9% | 36.3 |

Shares are of the best-performing candidate per party, which is the standard
comparator in multi-member wards. Only about a third of Primrose Hill is in this
seat, so treat its row as background rather than as votes available.

**The pattern across the table is not the national Green pattern.** The two wards
the Greens topped, Holborn and Covent Garden and Regent's Park, are the second and
third most social-rented in the seat. The ward with by far the most students,
Bloomsbury at 39.7%, they did not win.

## 3. Where the Green vote actually sits

Correlations across the nine wards where a Green candidate stood, between ward
characteristics and vote shares:

| Ward characteristic | Green share | Labour share | Green lead |
|---|---|---|---|
| Turnout, May 2026 | +0.23 | +0.50 | -0.23 |
| Social renting | +0.45 | -0.30 | **+0.66** |
| Private renting | -0.21 | +0.06 | -0.24 |
| Owner occupied | -0.42 | +0.33 | **-0.66** |
| Full-time students | +0.12 | -0.33 | +0.39 |
| Aged 20 to 34 | **+0.61** | +0.18 | +0.38 |
| Aged 65 and over | **-0.63** | -0.41 | -0.20 |
| Degree or above | -0.33 | +0.32 | **-0.57** |
| White residents | -0.11 | **+0.62** | **-0.64** |
| Deprivation score | +0.44 | +0.02 | +0.36 |

**These describe wards, not voters.** Nine wards is a very small sample, and a
correlation between ward averages cannot tell you how any group of people voted.
This is the ecological fallacy, and it has embarrassed better-resourced analyses
than this one. Treat every line as a hypothesis, not a result.

With that said, three patterns are worth noting:

1. **The Green lead runs with social housing and against owner occupation.** The
   strongest two relationships in the table, and they point the same way.
2. **The Green lead runs against degree holding and with ethnic diversity.** In a
   seat this graduate-heavy that inverts the usual assumption about where Green
   canvassing time goes.
3. **Age is the clearest signal.** Green share runs with the 20-to-34 population
   and against the over-65s. That one does match the national picture.

## 4. The July by-election is the most relevant data point in the file

On 9 July 2026 Regent's Park held a by-election after the Green councillor
Muhammad Abu Naser was declared ineligible.

| Candidate | Party | Votes |
|---|---|---|
| Nanouche Umeadi | Labour | 576 |
| Alice Amelia Brown | Green | 482 |
| Mohammad Junayd Khan | Independent | 407 |
| Vladimir Chorniy | Conservative | 137 |
| Beverley Janet Martin | Reform UK | 123 |
| Henry William Windle Potts | Liberal Democrat | 51 |

Turnout 21.93%, against 35.12% in the same ward ten weeks earlier. In May the
Greens took all three seats there with 38.3%. In July, on a turnout that fell by
thirteen points, they lost. An independent took 407 votes.

Two things follow. **Differential turnout erased a 5.6-point Green lead in ten
weeks.** And **an independent took a fifth of the vote in this part of the seat**,
which is the same signal as the Camden People's Alliance results and as Andrew
Feinstein's 18.9% in 2024.

## 5. The two uncontested wards

King's Cross and St Pancras and Somers Town hold about 15,524 electors between
them, close to a fifth of the seat. No Green candidate stood in either in May.
They are the two most social-rented wards in the constituency: 47.3% and 60.4%.

The Camden People's Alliance stood full slates in both, took 30.3% and 32.9%, and
won a seat in St Pancras and Somers Town. Section 3 finds the Green lead running with
social renting. These two wards would be the strongest test of that, and no Green
candidate has stood in either to provide it.

Whether that vote is available to a Green candidate, is attached to the Camden
People's Alliance, or belongs to whoever inherits Feinstein's 7,312 votes from
2024, nothing in the public data can say. It is the largest open question in the
constituency.

## 6. What this document does not tell you

- **There is no ward-level 2024 general election data.** None exists anywhere.
  The 2024 result is a single constituency figure. Every ward-level number here
  is from a local election.
- **Local election shares are not a general election forecast**, and a by-election
  is a third kind of contest again. Nothing here is a prediction.
- **Where Feinstein's 18.9% sits is unknown.** He has declined to stand.
- **Turnout at the by-election is unknown and matters more than anything else
  here.** May's locals ran from 31.9% to 49.6% by ward; the July by-election ran
  at 21.9%; the 2024 general election ran at 54.1%.

## 7. Confidence

| Tier | What |
|---|---|
| **A** | Ward vote counts and turnout percentages. Camden's own declarations. |
| **B** | Electorates and ballot counts. Camden publishes turnout only as a percentage, so these are derived: ballots = votes ÷ published candidate share, electorate = ballots ÷ turnout. Where the shares are not published the 2022 register is used; in the four wards where both years can be derived the two differ by under 5%. Census and deprivation figures, aggregated to wards by best-fit small area, are also Tier B. |
| **C** | Anything about Primrose Hill, which straddles two constituencies. Only polling district TB is in this seat. |

**Validation.** The derived electorates sum to 73,831 against a published 2024
register of 71,300, 3.5% high, which is the right direction and the right order
for two years of register growth. The seat-wide May shares computed here, Labour
38.3% to Green 29.1%, land within half a point of PollCheck's independently
calculated 38.8% and 28.8%.

**Corrections log.** Two claims were drafted and cut after checking them against
the data: that turnout rose in every ward (it fell in St Pancras and Somers Town, by
0.09 of a point), and that the Green share is highest at middling turnout (it is
highest in Kentish Town North, the highest-turnout ward in the seat, which Labour
nonetheless won).

## 8. Sources

1. Camden Council, ward result declarations for 7 May 2026 and the Regent's Park
   by-election of 9 July 2026.
2. Wikipedia transcriptions of the 2022 and 2026 Camden declarations, used only to
   recover candidate percentages. Every vote count was cross-checked against
   Camden's own page and all eleven wards matched.
3. ONS Open Geography Portal: Westminster constituencies July 2024, wards
   December 2024, LSOAs December 2021.
4. ONS Census 2021 via Nomis: TS054 tenure, TS021 ethnic group, TS007A age,
   TS067 qualifications, TS062 NS-SeC.
5. MHCLG, English Indices of Deprivation 2025, File 7, LSOA 2021.
6. Camden Open Data, polling stations and polling district codes.

All Open Government Licence v3.0, except the Wikipedia transcriptions, which are
CC BY-SA.

## 9. Rebuilding it

```bash
python3 -m venv .venv
.venv/bin/pip install shapely beautifulsoup4 lxml
.venv/bin/python fetch_sources.py     # downloads ~21 MB into raw/
.venv/bin/python build_hsp_data.py    # writes public/hsp_map.json
.venv/bin/python build_page.py        # inlines it into public/index.html
```

A clean checkout reproduces `public/hsp_map.json` byte for byte. See the README
for the one input that cannot be fetched by script, and why.
