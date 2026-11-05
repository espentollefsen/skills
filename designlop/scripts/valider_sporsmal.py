#!/usr/bin/env python3
"""Kontroller at spørsmålstreet overholder begrensningene til ask_user_input_v0: maks 3 spørsmål per kall, 2–4 alternativer per spørsmål, korte etiketter.
  python valider_sporsmal.py ../assets/sporsmalstre.json"""
import json, sys
feil = []
def sjekk(runde, navn):
    qs = runde['spørsmål']
    if not 1 <= len(qs) <= 3: feil.append(f'{navn}: {len(qs)} spørsmål (maks 3 per kall)')
    for q in qs:
        n = len(q['alternativer'])
        if not 2 <= n <= 4: feil.append(f'{navn}/{q["id"]}: {n} alternativer (må være 2–4)')
        if q['type'] not in ('single_select', 'multi_select'): feil.append(f'{navn}/{q["id"]}: ugyldig type {q["type"]}')
        for a in q['alternativer']:
            if len(a) > 60: feil.append(f'{navn}/{q["id"]}: etikett for lang ({len(a)} tegn): {a[:40]}…')
        if len(set(q['alternativer'])) != n: feil.append(f'{navn}/{q["id"]}: duplikate alternativer')
t = json.load(open(sys.argv[1], encoding='utf-8'))
sjekk(t['runde_0_start'], 'runde_0'); [sjekk(r, f'runde_1/{k}') for k, r in t['runde_1'].items()]; sjekk(t['runde_plan'], 'runde_plan'); sjekk(t['mal_konfliktvalg'], 'mal_konfliktvalg')
ids = [q['id'] for r in [t['runde_0_start'], t['runde_plan']] + list(t['runde_1'].values()) for q in r['spørsmål']]
if len(ids) != len(set(ids)): feil.append('Duplikate spørsmåls-ID-er')
for f in feil: print('FEIL', f)
print('OK – spørsmålstreet overholder verktøyets begrensninger.' if not feil else f'{len(feil)} feil.'); sys.exit(1 if feil else 0)
