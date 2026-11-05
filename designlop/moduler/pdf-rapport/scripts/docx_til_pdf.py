#!/usr/bin/env python3
"""Lag en designet PDF-rapport fra et vedlegg i docx. Overskrifter, avsnitt, punktlister og tabeller beholdes i rekkefølge.
Endringslogg og Godkjenning (kapitler) hoppes alltid over.

  python docx_til_pdf.py Vedlegg_D.docx Vedlegg_D.pdf --kunde "Lunera Energi" --versjon "v0.2 · 01.10.2026" \
      --kpi "Brukertyper|4|User, External, Email, Resource Account|blue" --kpi "..."
Første tabell i dokumentet tolkes som metadata, andre tabell som kvittering.
"""
import argparse, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from rapport_lib import *
import docx
from docx.table import Table as DT
from docx.text.paragraph import Paragraph as DP
from docx.oxml.ns import qn

SKIP_KAPITLER = {'endringslogg', 'godkjenning'}

def blokker(d):
    for ch in d.element.body.iterchildren():
        if ch.tag == qn('w:p'): yield DP(ch, d)
        elif ch.tag == qn('w:tbl'): yield DT(ch, d)

def stilnavn(p):
    if p._p.pPr is not None and p._p.pPr.pStyle is not None and p._p.pPr.pStyle.val: return p._p.pPr.pStyle.val.replace(' ', '').lower()
    return (p.style.name if p.style is not None else '').replace(' ', '').lower()

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('docx'); ap.add_argument('pdf')
    ap.add_argument('--kunde', default=''); ap.add_argument('--versjon', default=''); ap.add_argument('--kpi', action='append', default=[])
    ap.add_argument('--konfidensielt', default='', help='Valgfritt ledd i bunnteksten. Standard: ingen.'); a = ap.parse_args()
    d = docx.Document(a.docx); items = list(blokker(d))
    tekst = [p for p in items if isinstance(p, DP) and p.text.strip()]
    tittel = tekst[1].text if len(tekst) > 1 else tekst[0].text
    story = [Paragraph(esc(a.kunde or tekst[0].text), KICK), Paragraph(esc(tittel), H1)]
    if len(tekst) > 2: story.append(Paragraph(esc(tekst[2].text), P))
    cards = []
    for k in a.kpi:
        t, v, s, z = (k.split('|') + ['', '', 'neutral'])[:4]; cards.append((t, v, s, z or 'neutral'))
    if cards: story += [Spacer(1, 4), kpi_row(cards), Spacer(1, 6)]
    toppen = {tekst[0].text.strip(), tittel.strip(), tekst[2].text.strip() if len(tekst) > 2 else ''}
    tabeller = 0; skipping = False; pb = []
    def flush():
        nonlocal pb
        if pb: story.append(bullets(pb)); pb = []
    for it in items:
        if isinstance(it, DP):
            t = it.text.strip(); s = stilnavn(it)
            if not t or t in toppen: continue
            if s.startswith('heading1'):
                flush(); skipping = t.lower().lstrip('0123456789. ') in SKIP_KAPITLER
                if skipping: continue
                if not t.startswith('1 ') and not t.startswith('2 '): story.append(PageBreak())
                story.append(Paragraph(esc(t), H2)); continue
            if skipping: continue
            if s.startswith('heading2'): flush(); story.append(Paragraph(esc(t), H3))
            elif 'list' in s or (it._p.pPr is not None and it._p.pPr.numPr is not None): pb.append(t)
            else: flush(); story.append(Paragraph(esc(t), SM if t.startswith('Test for hva') else BODY))
        else:
            flush()
            if skipping: continue
            rows = [[c.text for c in r.cells] for r in it.rows]
            if len(rows) < 2: continue  # nøkkeltallskort (enrads tabell) vises ikke som tabell
            tabeller += 1; hdr, body = rows[0], rows[1:]
            sc = tuple(i for i, h in enumerate(hdr) if h.strip() in ('Status',))
            if len(hdr) == 2 and tabeller == 1: story += [table(['Felt', 'Verdi'], body[1:] if body and body[0][0] == 'Felt' else body, [0.15, 0.85], 'blue'), Spacer(1, 6)]
            else: story += [table(hdr, body, [0.46, 0.09, 0.45] if sc == (1,) and len(hdr) == 3 else autowidths(hdr, body), 'neutral', status_cols=sc), Spacer(1, 6)]
    flush()
    bygg(a.pdf, tittel, ' · '.join(x for x in [a.kunde, tittel, a.versjon, a.konfidensielt] if x), story); print('Skrev', a.pdf)

if __name__ == '__main__': main()
