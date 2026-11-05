#!/usr/bin/env python3
"""Trekk ut kommentarer fra et Word-dokument til JSON (med anker, avsnitt, overskrift, trådstruktur og ferdig-status).

  python ekstraher.py HLD.docx kommentarer.json [--kun-apne] [--utelat-forfatter "Endringslogg"] [--forfatter Monica]

Kommentar-ID-er kan endres av Word mellom versjoner. Ekstraher derfor alltid på nytt fra filen du faktisk skal endre."""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from docxlib import les_kommentarer

ap = argparse.ArgumentParser(); ap.add_argument('docx'); ap.add_argument('ut')
ap.add_argument('--kun-apne', action='store_true'); ap.add_argument('--utelat-forfatter', action='append', default=[]); ap.add_argument('--forfatter', action='append', default=[])
a = ap.parse_args()
ks = les_kommentarer(a.docx)
if a.kun_apne: ks = [k for k in ks if not k['ferdig']]
for u in a.utelat_forfatter: ks = [k for k in ks if u.lower() not in k['forfatter'].lower()]
if a.forfatter: ks = [k for k in ks if any(f.lower() in k['forfatter'].lower() for f in a.forfatter)]
json.dump(ks, open(a.ut, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
fa = {}
for k in ks: fa[k['forfatter'].split(' /')[0]] = fa.get(k['forfatter'].split(' /')[0], 0) + 1
print(f'{len(ks)} kommentarer skrevet til {a.ut}'); [print(f'  {n:3d}  {f}') for f, n in sorted(fa.items(), key=lambda x: -x[1])]
