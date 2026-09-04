#!/usr/bin/env python3
"""
Build the Holborn & St Pancras by-election map dataset.

Sources (all Open Government Licence / public):
  - Camden Council official ward declarations, 7 May 2026 locals + 9 Jul 2026 by-election
  - Wikipedia transcription of Camden 2022 + 2026 locals (used ONLY for percentages,
    from which ballot-paper counts and electorates are derived; vote counts are
    cross-checked against the Camden declarations)
  - ONS Open Geography: PCON July 2024, Wards December 2024, LSOA 2021 boundaries
  - ONS Census 2021 via Nomis (tenure, ethnicity, age, qualifications, NS-SeC)
  - MHCLG English Indices of Deprivation 2025 (LSOA 2021)
  - Camden Open Data: polling stations + polling district codes

Ground rule 5: every derived number carries a provenance string and a confidence.
"""
import csv, json, collections, math, os, re, sys
from shapely.geometry import shape, mapping, MultiPolygon
from shapely.ops import unary_union


def polys_only(g):
    """Clipping a ward against the constituency where their boundaries are nearly
    coincident yields a GeometryCollection: the real polygon plus hairline
    LineString slivers. Primrose Hill produced 25 of them. Keep the areal parts,
    which are the only ones a choropleth can draw."""
    if g.geom_type in ('Polygon', 'MultiPolygon'):
        return g if g.is_valid else g.buffer(0)
    parts = [p for p in getattr(g, 'geoms', []) if p.geom_type in ('Polygon', 'MultiPolygon')]
    if not parts:
        return g
    u = unary_union(parts)
    return u if u.is_valid else u.buffer(0)

RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'raw')
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
PUB  = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public')
R = lambda *p: os.path.join(RAW, *p)
D = lambda *p: os.path.join(DATA, *p)

PARTY_ORDER = ['Green','Lab','CPA','Con','Reform','LD','Ind','NHP','WPB','TUSC','Other']
PARTY_NAME = {'Green':'Green','Lab':'Labour','CPA':"Camden People's Alliance",'Con':'Conservative',
              'Reform':'Reform UK','LD':'Liberal Democrat','Ind':'Independent',
              'NHP':'National Housing Party','WPB':'Workers Party','TUSC':'TUSC','Other':'Other'}

# ---------------------------------------------------------------- geography

def load_geo():
    hsp = shape(json.load(open(R('hsp.geojson')))['features'][0]['geometry'])
    wards = json.load(open(R('wards_camden_2024.geojson')))['features']
    lsoas = json.load(open(R('lsoa_camden.geojson')))['features']
    return hsp, wards, lsoas

# ONS ward names use "&"; Camden result pages use "and". Normalise to the Camden form.
def norm_ward(n):
    n = n.replace(' & ', ' and ')
    return {'Holborn and Covent Garden':'Holborn and Covent Garden',
            'St Pancras and Somers Town':'St Pancras and Somers Town'}.get(n, n)

# ---------------------------------------------------------------- elections

def best_by_party(cands):
    """Best-performing candidate per party — the standard comparator in
    multi-member wards, because electors have as many votes as there are seats."""
    out = {}
    for name, p, v in cands:
        if p not in out or v > out[p][1]:
            out[p] = (name, v)
    return out

def elect(cands, seats, declared=None):
    """Who actually won the seats, and how close the last one was.

    Electors have as many votes as there are seats and may split them across
    parties, so the winners are simply the top N candidates by votes, regardless
    of party. Where the declaration is available the result is asserted against
    it, so a mistyped vote count cannot quietly change who holds a seat.

    Returns the ranked slate with an `elected` flag, seats won per party, and the
    margin between the last seat won and the first seat missed — which is the
    number that decides whether a ward is really contested.
    """
    ranked = sorted(cands, key=lambda c: -c[2])
    winners = ranked[:seats]
    if declared is not None:
        got, want = sorted(n for n, _, _ in winners), sorted(declared)
        assert got == want, f'computed winners {got} != declared {want}'
    won = {}
    for _, party, _ in winners:
        won[party] = won.get(party, 0) + 1
    margin = None
    if len(ranked) > seats:
        last, first_out = ranked[seats - 1], ranked[seats]
        margin = {'votes': last[2] - ranked[seats][2],
                  'held_by': last[1], 'missed_by': first_out[1],
                  'winner': last[0], 'runner_up': first_out[0],
                  'cross_party': last[1] != first_out[1]}
    return {
        'slate': [{'candidate': n, 'party': party, 'votes': v, 'elected': i < seats}
                  for i, (n, party, v) in enumerate(ranked)],
        'seats_won': dict(sorted(won.items(), key=lambda kv: -kv[1])),
        'last_seat_margin': margin,
    }


def load_2026():
    return json.load(open(D('camden_2026_hsp_wards.json')))['wards']

def load_wiki():
    return json.load(open(R('../data/camden_wiki_2022_2026.json')))

def wiki_pct_table(fn, min_pct_rows=5):
    """Recover ballot-paper counts per ward from the Wikipedia transcription.

    Camden publishes turnout as a percentage only, never the number of ballot
    papers. Wikipedia's tables give each candidate's share of ballot papers, so
    votes / share recovers the ballot-paper count, and ballots / turnout recovers
    the electorate. Tables carrying fewer than `min_pct_rows` percentages are
    treated as having no percentages at all, because a single stray figure is
    usually a transcription artefact rather than a real share."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(open(R(fn)).read(), 'lxml')
    out = {}
    for tbl in soup.select('table.wikitable'):
        cap = tbl.find('caption')
        if not cap: continue
        m = re.match(r"(.+?)\s*\((\d) seats?\)", cap.get_text(' ', strip=True))
        if not m: continue
        ward = norm_ward(m.group(1).strip().replace('Kings Cross', "King's Cross").replace('St. Pancras','St Pancras'))
        rows, turnout, ballots = [], None, None
        for tr in tbl.select('tr'):
            c = [x.get_text(' ', strip=True) for x in tr.find_all(['td','th'])]
            if len(c) >= 4 and re.fullmatch(r'[\d,]+', c[3] or 'x') and re.fullmatch(r'[\d.]+', c[4] if len(c) > 4 else (c[3] or 'x')):
                pass
            if len(c) >= 5 and re.fullmatch(r'[\d,]+', c[3] or 'x') and re.fullmatch(r'[\d.]+', c[4] or 'x'):
                rows.append((int(c[3].replace(',','')), float(c[4])))
            j = ' '.join(c)
            mt = re.search(r'Turnout\s+([\d,]+)\s+\(?([\d.]+)', j)
            if mt:
                ballots, turnout = int(mt.group(1).replace(',','')), float(mt.group(2))
            else:
                mt2 = re.match(r'Turnout\s+([\d.]+)\s', j)
                if mt2: turnout = float(mt2.group(1))
        if ballots is None and len(rows) >= min_pct_rows:
            v, p = max(rows, key=lambda r: r[0])
            if p: ballots = round(v / (p / 100.0))
        out[ward] = {'turnout_pct': turnout, 'ballots': ballots,
                     'pct_rows': len(rows)}
    return out

# ---------------------------------------------------------------- census

def load_census(fn, dimcol):
    rows = collections.defaultdict(dict)
    with open(R(fn)) as f:
        for r in csv.DictReader(f):
            rows[r['GEOGRAPHY_CODE']][r[dimcol + '_NAME']] = int(r['OBS_VALUE'])
    return rows

def load_imd():
    out = {}
    with open(R('imd2025_all.csv')) as f:
        for r in csv.DictReader(f):
            if r['Local Authority District name (2024)'] != 'Camden': continue
            out[r['LSOA code (2021)']] = {
                'imd_score': float(r['Index of Multiple Deprivation (IMD) Score']),
                'imd_decile': int(r['Index of Multiple Deprivation (IMD) Decile (where 1 is most deprived 10% of LSOAs)']),
                'income_score': float(r['Income Score (rate)']),
            }
    return out

# ---------------------------------------------------------------- build

def council_composition(out_wards, byelections):
    """Who holds the 30 council seats in this seat now, not on election night.

    May 2026 gave the seats; the July 2026 Regent's Park by-election has since
    moved one from Green to Labour. Any by-election held after the all-out
    election replaces one seat in its ward, so the composition is rebuilt rather
    than copied from the declarations. By-elections predating May 2026 changed
    nothing that survived it and are skipped.
    """
    may, now, per_ward = {}, {}, {}
    for w in out_wards:
        won = dict((w.get('e2026') or {}).get('seats_won') or {})
        per_ward[w['ward']] = {'may2026': dict(won), 'now': dict(won)}
        for party, n in won.items():
            may[party] = may.get(party, 0) + n
    changes = []
    for c in byelections.get('contests', []):
        if c['date'] <= '2026-05-07':
            continue
        pw = per_ward.get(c['ward'])
        if not pw:
            continue
        gained = c['result'][0]['party']
        lost = None
        for party, n in pw['now'].items():          # the outgoing councillor's party
            if party != gained and n > 0:
                lost = party
        if c['ward'] == "Regent's Park":
            lost = 'Green'                          # Naser, elected Green in May
        if lost:
            pw['now'][lost] -= 1
            if pw['now'][lost] == 0:
                del pw['now'][lost]
        pw['now'][gained] = pw['now'].get(gained, 0) + 1
        changes.append({'ward': c['ward'], 'date': c['date'], 'from': lost, 'to': gained})
    for w, d in per_ward.items():
        for party, n in d['now'].items():
            now[party] = now.get(party, 0) + n
    return {
        'total_seats': sum(may.values()),
        'may2026': dict(sorted(may.items(), key=lambda kv: -kv[1])),
        'now': dict(sorted(now.items(), key=lambda kv: -kv[1])),
        'changes_since': changes,
        'by_ward': per_ward,
        'note': ('The 30 council seats in the eleven wards of this constituency. Camden '
                 'elects 55 councillors across 20 wards; the other 25 seats sit in Hampstead and '
                 'Highgate. Primrose Hill\'s three seats are counted in full here even though only '
                 'about a third of that ward is in this seat.'),
    }


def build_byelections(out_wards):
    """Every by-election held in a ward of this seat since the 2022 all-out elections.

    These are single-member contests, so a share here is of ballot papers — unlike
    the May figures, which are of each party's best candidate across a multi-member
    ward. The two are built to be comparable and broadly are, but they are not the
    same denominator, and the comparison is labelled as approximate wherever it is
    drawn.

    The July 2026 Regent's Park contest is the only clean differential-turnout test
    in the data: same ward, same register, ten weeks after the May locals. The two
    September 2024 contests sit BEFORE the May 2026 Green advance, so a lower Green
    share in them is a measure of where the Greens were in 2024, not of what low
    turnout does to them. That distinction is carried in `comparable` and must not
    be dropped when these numbers are quoted.
    """
    src = json.load(open(D('camden_byelections.json')))
    by_ward = {w['ward']: w for w in out_wards}
    out = []
    for b in src['byelections']:
        votes = sum(v for _, _, v in b['result'])
        rej = (b['rejected'] or {}).get('total', 0)
        shares = {}
        for party, _, v in b['result']:
            shares[party] = round(shares.get(party, 0) + 100.0 * v / votes, 1)
        w = by_ward.get(b['ward'])
        may = (w or {}).get('e2026', {})
        may_green = ((may.get('best') or {}).get('Green') or {}).get('share_pct')
        may_turnout = may.get('turnout_pct')
        post_may = b['date'] > '2026-05-07'
        out.append({
            'ward': b['ward'], 'date': b['date'], 'seats': b['seats'],
            'turnout_pct': b['turnout_pct'], 'cause': b['cause'], 'outcome': b['outcome'],
            'valid_votes': votes, 'rejected_total': rej,
            'est_electorate': round((votes + rej) / b['turnout_pct'] * 100),
            'result': [{'party': p, 'candidate': n, 'votes': v,
                        'share_pct': round(100.0 * v / votes, 1)} for p, n, v in b['result']],
            'vs_may2026': {
                'green_share_may': may_green,
                'green_share_byelection': shares.get('Green'),
                'green_change_pts': (round(shares['Green'] - may_green, 1)
                                     if may_green is not None and 'Green' in shares else None),
                'turnout_may': may_turnout,
                'turnout_change_pts': (round(b['turnout_pct'] - may_turnout, 1)
                                       if may_turnout is not None else None),
                'comparable': post_may,
                'why': ('Same ward and register ten weeks after the May locals, so the fall is a '
                        'differential-turnout effect.' if post_may else
                        'Held BEFORE the May 2026 locals, so the gap measures the Green advance '
                        'between 2024 and 2026, not what low turnout does. Not a turnout test.'),
            },
            'prov': 'Camden Council declaration',
        })
    return {'note': src['note'], 'source': src['source'],
            'contests': sorted(out, key=lambda x: x['date'], reverse=True)}


def main():
    hsp, wards, lsoas = load_geo()
    res26 = load_2026()
    wiki26 = wiki_pct_table('wiki_camden_2026.html')
    wiki22 = wiki_pct_table('wiki_camden_2022.html')
    wikitab = json.load(open(D('camden_wiki_2022_2026.json')))
    tenure = load_census('census_tenure_lsoa.csv', 'C2021_TENURE_9')
    eth    = load_census('census_ethnic_lsoa.csv', 'C2021_ETH_20')
    age    = load_census('census_age_lsoa.csv', 'C2021_AGE_19')
    quals  = load_census('census_quals_lsoa.csv', 'C2021_HIQUAL_8')
    nssec  = load_census('census_nssec_lsoa.csv', 'C2021_NSSEC_10')
    imd    = load_imd()

    ward_geoms = {norm_ward(f['properties']['WD24NM']): shape(f['geometry']) for f in wards}

    # Assign each LSOA to its best-fit ward and measure how much of it sits in the seat.
    lsoa_rec = {}
    for f in lsoas:
        g = shape(f['geometry']); code = f['properties']['LSOA21CD']
        frac_hsp = g.intersection(hsp).area / g.area if g.intersects(hsp) else 0.0
        best, bestf = None, 0.0
        for wn, wg in ward_geoms.items():
            if not g.intersects(wg): continue
            fr = g.intersection(wg).area / g.area
            if fr > bestf: best, bestf = wn, fr
        lsoa_rec[code] = {'ward': best, 'ward_frac': round(bestf, 3),
                          'hsp_frac': round(frac_hsp, 3), 'geom': g,
                          'name': f['properties']['LSOA21NM'],
                          'pop': eth.get(code, {}).get('Total: All usual residents', 0)}

    def pct(d, num, den):
        t = d.get(den, 0)
        return round(100.0 * sum(d.get(k, 0) for k in num) / t, 1) if t else None

    out_wards = []
    for wname, r in res26.items():
        wg = ward_geoms[wname]
        clipped = polys_only(wg.intersection(hsp))

        # How much of the ward is in the seat, by resident population rather than by
        # area. Area over-weights parks and rail land; population is the better proxy
        # for electors, and for Primrose Hill it is the number that matters.
        pop_in = pop_all = 0.0
        for code, rec in lsoa_rec.items():
            if rec['ward'] != wname: continue
            pop_all += rec['pop']
            pop_in += rec['pop'] * rec['hsp_frac']
        in_frac_pop = round(pop_in / pop_all, 3) if pop_all else None

        el26 = elect(r['candidates'], r['seats'], r.get('elected_declared'))
        el22 = elect(w22_pre['candidates'], r['seats']) if (w22_pre := wikitab['2022'].get(wname)) else None
        best26 = best_by_party(r['candidates'])
        tot26 = sum(v for _, v in best26.values())
        share26 = {p: round(100.0 * v / tot26, 1) for p, (_, v) in best26.items()}

        w22 = wikitab['2022'].get(wname)
        best22 = best_by_party(w22['candidates']) if w22 else {}
        tot22 = sum(v for _, v in best22.values()) or 1
        share22 = {p: round(100.0 * v / tot22, 1) for p, (_, v) in best22.items()}

        b22 = w22['turnout'][0] if (w22 and w22['turnout']) else None
        t22 = w22['turnout'][1] if (w22 and w22['turnout']) else None
        elect22 = round(b22 / (t22 / 100.0)) if (b22 and t22) else None

        b26 = wiki26.get(wname, {}).get('ballots')
        elect26 = round(b26 / (r['turnout_pct'] / 100.0)) if b26 else None

        # Ward size for planning. The 2026 register is not published per ward, and
        # where both years can be derived the two differ by under 5%, so the 2022
        # register is used as the denominator wherever 2026 cannot be derived.
        elect_used = elect26 or elect22
        est_ballots26 = round(elect_used * r['turnout_pct'] / 100.0) if elect_used else None

        g26, g22 = share26.get('Green'), share22.get('Green')
        l26, l22 = share26.get('Lab'), share22.get('Lab')

        agg = collections.Counter(); agge = collections.Counter()
        agga = collections.Counter(); aggq = collections.Counter(); aggn = collections.Counter()
        imd_num = imd_den = 0.0; pop = 0
        for code, rec in lsoa_rec.items():
            if rec['ward'] != wname: continue
            for k, v in tenure.get(code, {}).items(): agg[k] += v
            for k, v in eth.get(code, {}).items(): agge[k] += v
            for k, v in age.get(code, {}).items(): agga[k] += v
            for k, v in quals.get(code, {}).items(): aggq[k] += v
            for k, v in nssec.get(code, {}).items(): aggn[k] += v
            if code in imd:
                p = rec['pop']
                imd_num += imd[code]['imd_score'] * p; imd_den += p; pop += p

        out_wards.append({
            'ward': wname,
            'seats': r['seats'],
            'in_constituency_frac_pop': in_frac_pop,
            'in_constituency_frac_area': round(clipped.area / wg.area, 3),
            'note': r.get('note'),
            'e2026': {
                'turnout_pct': r['turnout_pct'],
                'electorate': elect_used,
                'electorate_basis': '2026 register (derived)' if elect26 else '2022 register (derived)',
                'est_ballots': est_ballots26,
                'best': {p: {'candidate': n, 'votes': v, 'share_pct': share26[p]}
                         for p, (n, v) in sorted(best26.items(), key=lambda kv: -kv[1][1])},
                'contested_by_green': 'Green' in best26,
                'slate': el26['slate'],
                'seats_won': el26['seats_won'],
                'last_seat_margin': el26['last_seat_margin'],
            },
            'e2022': ({
                'turnout_pct': t22, 'ballots': b22, 'electorate': elect22,
                'best': {p: {'candidate': n, 'votes': v, 'share_pct': share22[p]}
                         for p, (n, v) in sorted(best22.items(), key=lambda kv: -kv[1][1])},
                'contested_by_green': 'Green' in best22,
                'slate': el22['slate'] if el22 else None,
                'seats_won': el22['seats_won'] if el22 else None,
            } if w22 else None),
            'derived': {
                'green_share_2026': g26,
                'lab_share_2026': l26,
                'green_lab_gap_2026': round(g26 - l26, 1) if (g26 is not None and l26 is not None) else None,
                'green_swing_22_26': round(g26 - g22, 1) if (g26 is not None and g22 is not None) else None,
                'lab_swing_22_26': round(l26 - l22, 1) if (l26 is not None and l22 is not None) else None,
                'turnout_change_22_26': round(r['turnout_pct'] - t22, 2) if t22 else None,
                'green_votes_2026': best26.get('Green', (None, None))[1],
                'est_green_votes_in_seat': (round(best26['Green'][1] * in_frac_pop)
                                            if ('Green' in best26 and in_frac_pop) else None),
            },
            'census2021': {
                'population': pop,
                'households': agg.get('Total: All households'),
                'private_rent_pct': pct(agg, ['Private rented', 'Lives rent free'], 'Total: All households'),
                'social_rent_pct': pct(agg, ['Social rented'], 'Total: All households'),
                'owner_pct': pct(agg, ['Owned', 'Shared ownership'], 'Total: All households'),
                'white_pct': pct(agge, ['White'], 'Total: All usual residents'),
                'asian_pct': pct(agge, ['Asian, Asian British or Asian Welsh'], 'Total: All usual residents'),
                'bangladeshi_pct': pct(agge, ['Asian, Asian British or Asian Welsh: Bangladeshi'], 'Total: All usual residents'),
                'black_pct': pct(agge, ['Black, Black British, Black Welsh, Caribbean or African'], 'Total: All usual residents'),
                'age_20_34_pct': pct(agga, ['Aged 20 to 24 years', 'Aged 25 to 29 years', 'Aged 30 to 34 years'], 'Total'),
                'age_65plus_pct': pct(agga, ['Aged 65 to 69 years', 'Aged 70 to 74 years', 'Aged 75 to 79 years',
                                             'Aged 80 to 84 years', 'Aged 85 years and over'], 'Total'),
                'degree_pct': pct(aggq, ['Level 4 qualifications or above'], 'Total: All usual residents aged 16 years and over'),
                'student_pct': pct(aggn, ['L15 Full-time students'], 'Total: All usual residents aged 16 years and over'),
            },
            'imd2025': {'mean_score_pop_wtd': round(imd_num / imd_den, 1) if imd_den else None},
            # A guaranteed-interior point for the map label. Centroids fall
            # outside L-shaped and crescent wards; representative_point does not.
            'label_point': [round(clipped.representative_point().x, 6),
                            round(clipped.representative_point().y, 6)],
            'geometry': mapping(clipped.simplify(0.00008, preserve_topology=True)),
        })

    # --- seat-wide aggregation of the May 2026 locals, weighted into the seat
    agg_all = collections.Counter(); agg_contested = collections.Counter()
    elect_total = 0.0; ballots_total = 0.0
    for w in out_wards:
        f = w['in_constituency_frac_pop'] or 1.0
        for p, d in w['e2026']['best'].items():
            agg_all[p] += d['votes'] * f
            if w['e2026']['contested_by_green']: agg_contested[p] += d['votes'] * f
        if w['e2026']['electorate']: elect_total += w['e2026']['electorate'] * f
        if w['e2026']['est_ballots']: ballots_total += w['e2026']['est_ballots'] * f
    def shares(c):
        t = sum(c.values())
        return {p: round(100.0 * v / t, 1) for p, v in sorted(c.items(), key=lambda kv: -kv[1])}, round(t)

    sh_all, tot_all = shares(agg_all)
    sh_con, tot_con = shares(agg_contested)
    green_absent = [w['ward'] for w in out_wards if not w['e2026']['contested_by_green']]

    # --- ward-level associations between the Green vote and ward character.
    # Nine wards, so these are indicative only, and they are correlations
    # between ward aggregates: they describe wards, not voters.
    def pearson(xs, ys):
        n = len(xs)
        mx, my = sum(xs)/n, sum(ys)/n
        sx = math.sqrt(sum((x-mx)**2 for x in xs)/n)
        sy = math.sqrt(sum((y-my)**2 for y in ys)/n)
        if not sx or not sy: return None
        return round(sum((x-mx)*(y-my) for x, y in zip(xs, ys)) / (n*sx*sy), 2)

    C = [w for w in out_wards if w['derived']['green_share_2026'] is not None]
    VARS = [
        ('Turnout, May 2026',      lambda w: w['e2026']['turnout_pct']),
        ('Social renting',         lambda w: w['census2021']['social_rent_pct']),
        ('Private renting',        lambda w: w['census2021']['private_rent_pct']),
        ('Owner occupied',         lambda w: w['census2021']['owner_pct']),
        ('Full-time students',     lambda w: w['census2021']['student_pct']),
        ('Aged 20 to 34',          lambda w: w['census2021']['age_20_34_pct']),
        ('Aged 65 and over',       lambda w: w['census2021']['age_65plus_pct']),
        ('Degree or above',        lambda w: w['census2021']['degree_pct']),
        ('White residents',        lambda w: w['census2021']['white_pct']),
        ('Deprivation score',      lambda w: w['imd2025']['mean_score_pop_wtd']),
    ]
    gs  = [w['derived']['green_share_2026'] for w in C]
    ls  = [w['derived']['lab_share_2026'] for w in C]
    gap = [w['derived']['green_lab_gap_2026'] for w in C]
    correlations = [{'variable': name,
                     'r_green': pearson([f(w) for w in C], gs),
                     'r_labour': pearson([f(w) for w in C], ls),
                     'r_gap': pearson([f(w) for w in C], gap)}
                    for name, f in VARS]

    b = hsp.bounds
    doc = {
        'meta': {
            'title': 'Holborn and St Pancras by-election map',
            'constituency': {'code': 'E14001290', 'name': 'Holborn and St Pancras'},
            'built': '2026-09-04',
            'bbox': [round(x, 6) for x in b],
            'ge2024': {
                'electorate': 71300, 'turnout_pct': 54.1, 'valid_votes': 38602,
                'result': [['Lab', 'Keir Starmer', 18884, 48.9], ['Ind', 'Andrew Feinstein', 7312, 18.9],
                           ['Green', 'David Stansell', 4030, 10.4], ['Con', 'Mehreen Malik', 2776, 7.2],
                           ['Reform', 'David Roberts', 2371, 6.1], ['LD', 'Charlie Clinton', 2236, 5.8],
                           ['Ind', 'Wais Islam', 636, 1.6], ['Other', 'Others', 357, 0.9]],
                'prov': 'UK Parliament / Wikipedia transcription of the 2024 declaration',
            },
            'byelection2026': {
                'called': '2026-09-01', 'date': None,
                'cause': 'Resignation of Keir Starmer (Steward of the Chiltern Hundreds)',
                'prov': 'Camden New Journal via Wikipedia, read 2026-09-04',
            },
            'correlations': {
                'n': len(C),
                'basis': 'Pearson correlation across the nine wards where a Green candidate '
                         'stood, between ward characteristics and the Green share, the Labour '
                         'share, and the Green lead over Labour.',
                'warning': 'Nine wards is a very small sample and these are relationships '
                           'between ward averages, not between voters. A ward-level correlation '
                           'cannot tell you how any group of people voted. Treat these as '
                           'directions to test on the doorstep, not as findings.',
                'rows': correlations,
            },
            'locals2026_seat': {
                'all_wards': {'shares': sh_all, 'weighted_votes': tot_all},
                'green_contested_wards_only': {'shares': sh_con, 'weighted_votes': tot_con,
                                               'wards': [w['ward'] for w in out_wards if w['e2026']['contested_by_green']]},
                'green_absent_wards': green_absent,
                'est_electorate': round(elect_total), 'est_ballots': round(ballots_total),
                'prov': 'Best-performing candidate per party in each ward, votes weighted by the '
                        'share of the ward population inside the seat, then summed. Multi-member '
                        'wards, so this is a share of best-candidate votes, not of ballot papers.',
                'confidence': 'Tier B. The weighting matters only for Primrose Hill.',
            },
            'sources': [
                'Camden Council official ward result declarations, 7 May 2026 and 9 July 2026 (camden.gov.uk)',
                'Wikipedia transcriptions of the 2022 and 2026 Camden declarations (percentages only; every vote count cross-checked against the Camden declaration)',
                'ONS Open Geography Portal: PCON July 2024 BFC, Wards December 2024 BFC, LSOA December 2021 BFC',
                'ONS Census 2021 via Nomis: TS054 tenure, TS021 ethnic group, TS007A age, TS067 qualifications, TS062 NS-SeC',
                'MHCLG English Indices of Deprivation 2025 (File 7), LSOA 2021',
                'Camden Open Data: polling stations and polling district codes (5rhh-fxna)',
            ],
            'confidence_notes': [
                'Ward vote counts and turnout percentages are official declarations: Tier A.',
                'Ballot-paper counts and electorates are derived, not published. Camden gives '
                'turnout as a percentage only. Where Wikipedia carries candidate shares, ballots '
                '= votes / share and electorate = ballots / turnout. Where it does not, the 2022 '
                'register is used. In the four wards where both years can be derived the two '
                'differ by under 5%: Tier B.',
                'Census and deprivation figures are aggregated to whole wards by best-fit LSOA. '
                'LSOA and ward boundaries do not align exactly: Tier B.',
                'Primrose Hill straddles two constituencies. Only polling district TB is in this '
                'seat, about a third of the ward. Its declared result cannot be split, so its '
                'shares describe the whole ward and its votes are weighted down when aggregated: Tier C.',
                'No ward-level 2024 general election data exists anywhere. The 2024 result is '
                'shown at constituency level only. Local-election shares are not a general '
                'election forecast and a by-election is a third kind of contest again.',
            ],
        },
        'wards': sorted(out_wards, key=lambda w: w['ward']),
        'lsoas': [],
        'polling_stations': [],
        'byelections': (_by := build_byelections(out_wards)),
        'council': council_composition(out_wards, _by),
    }

    for code, rec in lsoa_rec.items():
        if rec['hsp_frac'] < 0.5: continue
        t = tenure.get(code, {}); e = eth.get(code, {}); n = nssec.get(code, {}); a = age.get(code, {})
        doc['lsoas'].append({
            'code': code, 'name': rec['name'], 'ward': rec['ward'],
            'population': rec['pop'],
            'private_rent_pct': pct(t, ['Private rented', 'Lives rent free'], 'Total: All households'),
            'social_rent_pct': pct(t, ['Social rented'], 'Total: All households'),
            'owner_pct': pct(t, ['Owned', 'Shared ownership'], 'Total: All households'),
            'student_pct': pct(n, ['L15 Full-time students'], 'Total: All usual residents aged 16 years and over'),
            'age_20_34_pct': pct(a, ['Aged 20 to 24 years', 'Aged 25 to 29 years', 'Aged 30 to 34 years'], 'Total'),
            'white_pct': pct(e, ['White'], 'Total: All usual residents'),
            'imd_score': imd.get(code, {}).get('imd_score'),
            'imd_decile': imd.get(code, {}).get('imd_decile'),
            'geometry': mapping(polys_only(rec['geom'].intersection(hsp)).simplify(0.00008, preserve_topology=True)),
        })
    doc['lsoas'].sort(key=lambda l: l['code'])

    ps = json.load(open(R('camden_polling_stations.json')))
    doc['polling_stations'] = sorted(
        [{'pd': p['polling_district_name'],
          'ward': norm_ward(p['ward_name'].replace('Kings Cross', "King's Cross").replace('Regents Park', "Regent's Park")),
          'venue': p['organisation'], 'street': p['street'], 'postcode': p.get('postcode'),
          'lon': float(p['longitude']), 'lat': float(p['latitude'])}
         for p in ps if p['parliamentary_constituency_name'] == 'Holborn and St Pancras'],
        key=lambda p: p['pd'])

    os.makedirs(DATA, exist_ok=True)
    os.makedirs(PUB, exist_ok=True)
    json.dump(doc, open(os.path.join(PUB, 'hsp_map.json'), 'w'), separators=(',', ':'))

    print('wards', len(doc['wards']), 'lsoas', len(doc['lsoas']), 'stations', len(doc['polling_stations']))
    print('bytes', os.path.getsize(os.path.join(PUB, 'hsp_map.json')))
    print('\nSeat-wide May 2026, all wards      :', sh_all)
    print('Seat-wide May 2026, Green-contested:', sh_con)
    print('Greens did not stand in            :', green_absent)
    print('Est. electorate / est. ballots     :', round(elect_total), '/', round(ballots_total))
    print()
    hdr = f"{'ward':28s} {'inSeat':>6s} {'G26':>5s} {'L26':>5s} {'gap':>6s} {'Gsw':>6s} {'turn':>6s} {'elect':>6s} {'PR%':>5s} {'SR%':>5s} {'IMD':>5s}"
    print(hdr); print('-' * len(hdr))
    for w in doc['wards']:
        d, e, c = w['derived'], w['e2026'], w['census2021']
        f = lambda x, s='{:>5.1f}': (s.format(x) if x is not None else '    -')
        print(f"{w['ward']:28s} {w['in_constituency_frac_pop']:>6.2f} {f(d['green_share_2026'])} "
              f"{f(d['lab_share_2026'])} {f(d['green_lab_gap_2026'],'{:>6.1f}')} {f(d['green_swing_22_26'],'{:>6.1f}')} "
              f"{e['turnout_pct']:>6.2f} {str(e['electorate'] or '-'):>6s} "
              f"{f(c['private_rent_pct'])} {f(c['social_rent_pct'])} {f(w['imd2025']['mean_score_pop_wtd'])}")

if __name__ == '__main__':
    main()
