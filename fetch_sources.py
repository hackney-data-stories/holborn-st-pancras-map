#!/usr/bin/env python3
"""
Download every machine-fetchable source into raw/, so that build_hsp_data.py can
be run from a clean checkout.

One source is NOT fetched here. Camden's ward result pages sit behind Cloudflare
bot protection and refuse a scripted user agent, so the 7 May 2026 declarations
were read from the rendered pages by hand and are committed as
data/camden_2026_hsp_wards.json. That file is the only hand-transcribed input;
every vote in it was checked twice against camden.gov.uk, and independently
against the Wikipedia transcription, which agrees on all eleven wards.

Usage:  python3 fetch_sources.py
"""
import json, os, sys, urllib.request, urllib.parse

RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'raw')
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 ' \
     '(KHTML, like Gecko) Chrome/126.0 Safari/537.36'
ONS = 'https://services1.arcgis.com/ESMARspQHYMw9BZ9/ArcGIS/rest/services'
NOMIS = 'https://www.nomisweb.co.uk/api/v01/dataset'
CAMDEN_LAD = 'E09000007'      # London Borough of Camden
NOMIS_CAMDEN = '645922999'    # Nomis internal id for Camden

def get(url, dest, note=''):
    path = os.path.join(RAW, dest)
    if os.path.exists(path) and os.path.getsize(path) > 0:
        print(f'  have  {dest}')
        return
    print(f'  fetch {dest} {note}')
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=180) as r, open(path, 'wb') as f:
        f.write(r.read())

def arcgis(service, where, fields, dest, offset=None):
    q = {'where': where, 'outFields': fields, 'outSR': '4326', 'f': 'geojson'}
    if offset is not None:
        q['resultOffset'] = str(offset)
    get(f'{ONS}/{service}/FeatureServer/0/query?' + urllib.parse.urlencode(q), dest)

def main():
    os.makedirs(RAW, exist_ok=True)

    print('Boundaries — ONS Open Geography Portal (OGL v3, contains OS data © Crown copyright):')
    arcgis('Westminster_Parliamentary_Constituencies_July_2024_Boundaries_UK_BFC',
           "PCON24CD='E14001290'", '*', 'hsp.geojson', )
    arcgis('Westminster_Parliamentary_Constituencies_July_2024_Boundaries_UK_BFC',
           "PCON24NM IN ('Holborn and St Pancras','Hampstead and Highgate')", '*', 'pcon_2024.geojson')
    arcgis('Wards_December_2024_Boundaries_UK_BFC',
           f"LAD24CD='{CAMDEN_LAD}'", '*', 'wards_camden_2024.geojson')
    arcgis('Lower_layer_Super_Output_Areas_December_2021_Boundaries_EW_BFC_V10',
           "LSOA21NM LIKE 'Camden%'", 'LSOA21CD,LSOA21NM', 'lsoa_camden.geojson')
    for off in (0, 2000):
        arcgis('Output_Areas_2021_EW_BFC_V8', "LSOA21NM LIKE 'Camden%'",
               'OA21CD,LSOA21CD,LSOA21NM,LAT,LONG', f'oa_camden_{off}.geojson', offset=off)

    print('Census 2021 — ONS via Nomis (OGL v3):')
    for ds, name in [('NM_2072_1', 'tenure'), ('NM_2041_1', 'ethnic'), ('NM_2020_1', 'age'),
                     ('NM_2084_1', 'quals'), ('NM_2079_1', 'nssec')]:
        get(f'{NOMIS}/{ds}.data.csv?geography={NOMIS_CAMDEN}TYPE151&measures=20100&RecordLimit=20000',
            f'census_{name}_lsoa.csv', f'({name}, LSOA 2021)')

    print('Deprivation — MHCLG English Indices of Deprivation 2025, File 7 (OGL v3), 9.4 MB:')
    get('https://assets.publishing.service.gov.uk/media/691ded56d140bbbaa59a2a7d/'
        'File_7_IoD2025_All_Ranks_Scores_Deciles_Population_Denominators.csv', 'imd2025_all.csv')

    print('Polling districts — Camden Open Data (OGL v3):')
    get('https://opendata.camden.gov.uk/resource/5rhh-fxna.json?$limit=500',
        'camden_polling_stations.json')

    print('Prior results — Wikipedia (CC BY-SA 4.0), percentages only:')
    for yr in (2022, 2026):
        get(f'https://en.wikipedia.org/wiki/{yr}_Camden_London_Borough_Council_election',
            f'wiki_camden_{yr}.html')

    print('\nDone. Camden\'s own 2026 declarations are already committed at '
          'data/camden_2026_hsp_wards.json — see the note at the top of this file.')
    print('Next: python3 build_hsp_data.py')

if __name__ == '__main__':
    main()
