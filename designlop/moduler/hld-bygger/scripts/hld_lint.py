#!/usr/bin/env python3
"""Kontroller et HLD-utkast (docx) mot reglene fra metoden. Kjør før hver leveranse.

  python hld_lint.py hld.docx [--kilde etableringsplan.txt --kilde ...] [--forbudt "Ardoq,Jamf"] [--volumord "servere,brukere,..."] [--ut rapport.md]

Sjekker (feil = exit 1):
  FEIL     kryssreferanse «kap. X.Y» til kapittel som ikke finnes
  FEIL     «Forutsetninger»-overskrifter på ulikt nivå (de skal alle ha samme nivå)
  FEIL     forbudte termer (prosjektets egne: verktøy/produkter/standarder uten kilde)
  ADVARSEL tall med volumord i brødtekst («40 servere») – tall hører hjemme i registre, ikke i HLD
  ADVARSEL «besluttet»/«Dette er besluttet» – bare med henvisning til beslutning
  ADVARSEL datoer som ikke finnes i oppgitte kildefiler (og står sammen med en bilagshenvisning)
  ADVARSEL «Bilag»-henvisning til dato/volum uten vedleggsnummer"""
import argparse, re, sys
import docx
from docx.oxml.ns import qn

VOLUM = 'servere|brukere|lisenser|subscriptions|applikasjoner|ressurser|møterom|printere|lokasjoner|klienter|enheter|aksesspunkter|switcher|rutere|linjer|SaaS|transaksjoner'

def stil(p):
    if p._p.pPr is not None and p._p.pPr.pStyle is not None and p._p.pPr.pStyle.val: return p._p.pPr.pStyle.val
    return p.style.name if p.style is not None else ''

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('docx'); ap.add_argument('--kilde', action='append', default=[]); ap.add_argument('--forbudt', default='')
    ap.add_argument('--volumord', default=VOLUM); ap.add_argument('--ut'); a = ap.parse_args()
    d = docx.Document(a.docx); feil, adv = [], []
    # nummerering av overskrifter
    nr = [0, 0, 0, 0]; overskrifter = {}; niv_forutsetninger = set(); avsn = []
    for p in d.element.body.iter(qn('w:p')):
        P = docx.text.paragraph.Paragraph(p, d); t = P.text.strip(); s = stil(P).replace(' ', '').lower()
        m = re.fullmatch(r'heading([1-4])', s)
        if m and t:
            n = int(m.group(1)); nr[n - 1] += 1
            for i in range(n, 4): nr[i] = 0
            overskrifter['.'.join(str(x) for x in nr[:n])] = t
            if t.lower().startswith('forutsetninger'): niv_forutsetninger.add(n)
            avsn.append((t, '.'.join(str(x) for x in nr[:n]), True))
        elif t: avsn.append((t, '.'.join(str(x) for x in nr if x), False))
    # 1) kryssreferanser
    for t, kap, er_h in avsn:
        if er_h: continue
        for m in re.finditer(r'kap(?:ittel)?\.?\s+(\d+(?:\.\d+)*)', t):
            if m.group(1) not in overskrifter and not re.search(r'(Vedlegg|Bilag|tjenestebeskrivelse|Byggehåndbok|Designgrunnlag|ISAE)', t[max(0, m.start() - 70):m.start()]):
                feil.append(f'Kryssreferanse til «kap. {m.group(1)}» som ikke finnes (i kap. {kap}: «{t[:80]}…»)')
    # 2) Forutsetninger-nivå
    if len(niv_forutsetninger) > 1: feil.append(f'«Forutsetninger»-overskrifter står på ulike nivåer: {sorted(niv_forutsetninger)}. De skal ha samme nivå.')
    # 3) forbudt
    for term in [x.strip() for x in a.forbudt.split(',') if x.strip()]:
        for t, kap, er_h in avsn:
            if re.search(re.escape(term), t, re.I): feil.append(f'Forbudt term «{term}» i kap. {kap}: «{t[:90]}…»')
    # 4) tall + volumord og besluttet
    for t, kap, er_h in avsn:
        if er_h: continue
        for m in re.finditer(r'\b(\d{1,4})\s+(' + a.volumord + r')\b', t, re.I):
            adv.append(f'Tall i HLD: «{m.group(0)}» (kap. {kap}) – bør stå i register/vedlegg, ikke i HLD')
        for m in re.finditer(r'\b(' + a.volumord + r')\s+(?:er|på|utgjør|=|:)\s+(\d{1,4})\b', t, re.I):
            adv.append(f'Tall i HLD: «{m.group(0)}» (kap. {kap}) – bør stå i register/vedlegg, ikke i HLD')
        if re.search(r'Dette er besluttet|er besluttet\b', t): adv.append(f'«besluttet» uten henvisning (kap. {kap}): «{t[:90]}…»')
    # 5) datoer mot kilder
    kt = ''
    for k in a.kilde: kt += open(k, encoding='utf-8', errors='ignore').read() + '\n'
    if a.kilde:
        for t, kap, er_h in avsn:
            for m in re.finditer(r'\b\d{2}\.\d{2}\.\d{4}\b', t):
                if m.group(0) not in kt and re.search(r'Bilag|Vedlegg', t): adv.append(f'Dato {m.group(0)} (kap. {kap}) står sammen med en bilagshenvisning, men finnes ikke i oppgitte kilder: «{t[:90]}…»')
    ut = ['# HLD-lint', f'Fil: `{a.docx}`', f'Kapitler funnet: {len(overskrifter)}', '']
    ut += [f'- **FEIL** {f}' for f in feil] + [f'- ADVARSEL {x}' for x in adv]
    ut.append('' if (feil or adv) else '✔ Ingen funn.'); ut.append(f'\n{len(feil)} feil, {len(adv)} advarsler.')
    rapport = '\n'.join(ut); print(rapport)
    if a.ut: open(a.ut, 'w', encoding='utf-8').write(rapport)
    sys.exit(1 if feil else 0)

if __name__ == '__main__': main()
