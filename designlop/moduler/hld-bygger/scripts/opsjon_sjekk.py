#!/usr/bin/env python3
"""Tre-veis-kontroll: finn tjenester som står som opsjon / antall 0 i prislisten, og sjekk om tilbudstekst eller tjenestebeskrivelse lover dem.
Resultatet er en KANDIDATLISTE for konflikter. Skriptet avgjør ingenting: du legger funnene frem for brukeren med begge alternativer (se ../references/konfliktrapport.md).

  python opsjon_sjekk.py prisliste.xlsx --tilbud tilbud.txt --tilbud tjenestebeskrivelse.docx [--synonymer syn.json] [--ut konflikter.md]

Støttede kildeformater: .txt .md .docx .pdf (krever pdftotext) .xlsx.
Prislisten: alle rader der kolonnen «Antall» er 0, samt alle rader på ark med «opsj» i navnet. Kolonner gjenkjennes på overskrift (Antall/Kommentar/Beskrivelse)."""
import argparse, json, re, subprocess, sys
import openpyxl

INNEBYGD_SYN = {  # engelsk prislistenavn -> norske/alternative søkeord i tilbudstekst
    'microsegmentation': ['mikrosegment'], 'secure print': ['sikker utskrift', 'secure print'], 'mac': ['macos', 'mac-klient', 'mac '],
    'client hardening': ['herding', 'applocker', 'bitlocker'], 'direct link': ['direct link', 'vpn-reserve'], 'resource account': ['ressurskonto', 'resource account'],
    'external user': ['ekstern bruker', 'b2b'], 'privileged access': ['privilegert tilgang', 'pam'], 'cloud backup': ['backup av microsoft 365', 'm365-backup', 'keepit'],
    'network integration hub': ['integration hub', 'ekstern partner'], 'wan': ['sd-wan'], 'sentinel': ['sentinel', 'siem'], 'purview': ['purview', 'informasjonsbeskyttelse', 'etikett'],
}
STOPP = {'managed', 'intility', 'service', 'services', 'tjeneste', 'client', 'user', 'microsoft', 'azure', 'online', 'security', 'platform', 'for', 'and', 'og', 'per', 'the', 'full', 'suite', 'standard'}

def les_tekst(sti):
    s = sti.lower()
    if s.endswith(('.txt', '.md')): return open(sti, encoding='utf-8', errors='ignore').read()
    if s.endswith('.docx'):
        import docx; d = docx.Document(sti); t = [p.text for p in d.paragraphs]
        for tb in d.tables:
            for r in tb.rows: t.append(' | '.join(c.text for c in r.cells))
        return '\n'.join(t)
    if s.endswith('.pdf'): return subprocess.run(['pdftotext', '-layout', sti, '-'], capture_output=True, text=True).stdout
    if s.endswith('.xlsx'):
        wb = openpyxl.load_workbook(sti, data_only=True); return '\n'.join(' | '.join(str(c) for c in r if c is not None) for ws in wb.worksheets for r in ws.iter_rows(values_only=True))
    sys.exit(f'Ukjent kildeformat: {sti}')

def opsjoner(xlsx):
    wb = openpyxl.load_workbook(xlsx, data_only=True); ut = []
    for ws in wb.worksheets:
        rows = list(ws.iter_rows(values_only=True)); hi = next((i for i, r in enumerate(rows[:10]) if sum(1 for c in r if c not in (None, '')) >= 3), None)
        if hi is None: continue
        h = [str(c or '').lower() for c in rows[hi]]
        col = lambda pat: next((i for i, c in enumerate(h) if re.search(pat, c)), None)
        ia, ik, ib = col(r'antall|qty|volum'), col(r'kommentar|merknad|comment'), col(r'beskrivelse|description')
        for i, r in enumerate(rows[hi + 1:], hi + 2):
            if not r or r[0] in (None, ''): continue
            antall = r[ia] if ia is not None else None
            er_opsjonsark = 'opsj' in ws.title.lower()
            if (isinstance(antall, (int, float)) and antall == 0) or er_opsjonsark:
                ut.append(dict(ark=ws.title, rad=i, navn=str(r[0]).strip(), antall=antall, kommentar=str(r[ik]).strip() if ik is not None and r[ik] else '', beskrivelse=str(r[ib]).strip() if ib is not None and r[ib] else ''))
    return ut

def soketermer(navn, syn):
    n = navn.lower(); termer = set()
    for nokkel, liste in {**INNEBYGD_SYN, **syn}.items():
        if nokkel in n: termer.update(x.lower() for x in liste)
    for tok in re.findall(r'[a-zæøå]{5,}', n):
        if tok not in STOPP: termer.add(tok)
    return termer

def setninger(tekst):
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+|\n+', tekst) if len(s.strip()) > 15]

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('prisliste'); ap.add_argument('--tilbud', action='append', default=[]); ap.add_argument('--synonymer'); ap.add_argument('--ut')
    a = ap.parse_args(); syn = json.load(open(a.synonymer, encoding='utf-8')) if a.synonymer else {}
    ops = opsjoner(a.prisliste); kilder = {k: setninger(les_tekst(k)) for k in a.tilbud}
    ut = [f'# Kandidater til kontraktskonflikt\n', f'Prisliste: `{a.prisliste}` – {len(ops)} opsjons-/antall-0-rader. Kilder: {", ".join(f"`{k}`" for k in kilder)}.\n',
          '> Dette er kandidater, ikke avgjørelser. Vurder hver for seg og legg konfliktene frem for brukeren med begge alternativer og konsekvens.\n',
          '| Prislinje (ark, rad) | Antall | Prislistens kommentar | Mulig løfte i tilbud/tjenestebeskrivelse |', '|---|---|---|---|']
    ant = 0
    for o in ops:
        termer = soketermer(o['navn'], syn); treff = []
        for k, ss in kilder.items():
            for s in ss:
                if any(t in s.lower() for t in termer): treff.append(f'«{s[:200]}» ({k})')
        if treff: ant += 1
        ut.append(f"| **{o['navn'].replace('|', '/')}** ({o['ark']}, rad {o['rad']}) | {o['antall'] if o['antall'] is not None else 'opsjon'} | {o['kommentar'] or '–'} | " + ('<br>'.join(treff[:3]) if treff else '*ingen treff*') + ' |')
    ut.append(f'\n**{ant} av {len(ops)} opsjoner har treff i tilbud/tjenestebeskrivelse – sjekk disse først.**')
    rapport = '\n'.join(ut)
    if a.ut: open(a.ut, 'w', encoding='utf-8').write(rapport); print('Skrev', a.ut)
    print(rapport)

if __name__ == '__main__': main()
