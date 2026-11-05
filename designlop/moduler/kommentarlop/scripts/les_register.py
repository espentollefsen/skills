#!/usr/bin/env python3
"""Les brukerens beslutninger tilbake fra et kommentarregister: alle rader der kolonnen «Revisjonskommentar» er utfylt.
  python les_register.py register.docx beslutninger.json
Utdata: [{"tabell": 0, "nr": "41", "sted": "...", "forslag": "...", "revisjon": "Godkjent"}, ...]
Bruk resultatet til å bygge spec for bruk_endringer.py: rader med «Godkjent» (evt. med justert tekst) gjennomføres, «Underkjent»/«Avventer» gjennomføres IKKE
(Avventer får en statusnotat-kommentar og holdes åpen). Rader med tom revisjonskolonne er ikke vurdert ennå – spør, ikke anta."""
import json, sys
import docx

def main():
    if len(sys.argv) != 3: sys.exit(__doc__)
    d = docx.Document(sys.argv[1]); ut = []
    for ti, t in enumerate(d.tables):
        h = [c.text.strip() for c in t.rows[0].cells]
        if 'Revisjonskommentar' not in h: continue
        iR = h.index('Revisjonskommentar'); iN = 0; iS = h.index('Sted'); iF = next(i for i, x in enumerate(h) if x.startswith('Forslag'))
        for r in t.rows[1:]:
            c = [x.text.strip() for x in r.cells]
            ut.append(dict(tabell=ti, nr=c[iN], sted=c[iS], forslag=c[iF], revisjon=c[iR]))
    json.dump(ut, open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    v = [x for x in ut if x['revisjon']]
    print(f'{len(ut)} rader totalt, {len(v)} med revisjonskommentar, {len(ut) - len(v)} ikke vurdert ennå → {sys.argv[2]}')

if __name__ == '__main__': main()
