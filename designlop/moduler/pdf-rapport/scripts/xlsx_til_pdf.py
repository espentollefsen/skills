#!/usr/bin/env python3
"""Lag en designet PDF-rapport fra en vedlegg-arbeidsbok (xlsx).

Eksempel:
  python xlsx_til_pdf.py Vedlegg_A.xlsx Vedlegg_A.pdf --tittel "Vedlegg A – Applikasjoner" --kunde "Lunera Energi" \
      --versjon "v0.5 · 01.10.2026" --ingress "Målporteføljen ..." \
      --kpi "Applikasjoner|=ANTALL:Applikasjoner|videreføres, nye, overgang|blue" \
      --gruppe-ark Applikasjoner --gruppe-kolonne "Leveransemodell" --hopp-over Endringslogg --hopp-over Definisjoner

KPI-verdi kan være tekst, eller =ANTALL:<ark> (antall datarader) / =ANTALL:<ark>:<kolonne>=<verdi>.
Ark som heter «Dokumentinfo…» rendres spesielt (metadata, formål/innhold, kvittering, åpne punkter).
Ark som heter Endringslogg og Godkjenning hoppes alltid over: vedlegg skal ikke inneholde dem.
"""
import argparse, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from rapport_lib import *
import openpyxl

ALLTID_SKIP = {'endringslogg', 'godkjenning'}

def datarader(ws, header_row=1):
    rows = [r for r in ws.iter_rows(min_row=header_row + 1, values_only=True) if any(c not in (None, '') for c in r)]
    return rows

def finn_header(ws):
    for i, r in enumerate(ws.iter_rows(min_row=1, max_row=8, values_only=True), 1):
        filled = [c for c in r if c not in (None, '')]
        if len(filled) >= 3: return i
    return 1

def kpi_verdi(wb, spec):
    if not spec.startswith('='): return spec
    _, arg = spec.split(':', 1) if ':' in spec else (spec, '')
    parts = arg.split(':')
    ws = wb[parts[0]]; h = finn_header(ws); rows = datarader(ws, h)
    if len(parts) == 1: return str(len(rows))
    kol, val = parts[1].split('=', 1)
    hdr = [S(c) for c in next(ws.iter_rows(min_row=h, max_row=h, values_only=True))]
    idx = next(i for i, c in enumerate(hdr) if c.startswith(kol))
    return str(sum(1 for r in rows if S(r[idx]) == val))

def dokumentinfo(ws):
    meta, formal, kvitt, ap = [], [], [], []
    rows = [r for r in ws.iter_rows(values_only=True)]
    mode = 'meta'
    for r in rows:
        a, b, c, d = (list(r) + [None] * 4)[:4]
        if a is None and b is None: continue
        sa = S(a)
        if sa.startswith('Formål og innhold'): mode = 'formal'; continue
        if sa.startswith('Kvittering'): mode = 'kvitt'; continue
        if sa.startswith('Åpne punkter'): mode = 'ap'; continue
        if sa.startswith('Forutsetning') and mode == 'kvitt': continue
        if sa == 'ID' and mode == 'ap': continue
        if mode == 'meta' and b is not None and not sa.startswith('Vedlegg'): meta.append((sa, S(b)))
        elif mode == 'formal': formal.append(sa)
        elif mode == 'kvitt' and b is not None: kvitt.append((sa, S(b), S(c)))
        elif mode == 'ap' and b is not None: ap.append((sa, S(b), S(c), S(d)))
    return meta, formal, kvitt, ap

def main():
    ap_ = argparse.ArgumentParser()
    ap_.add_argument('xlsx'); ap_.add_argument('pdf')
    ap_.add_argument('--tittel', required=True); ap_.add_argument('--kunde', default=''); ap_.add_argument('--versjon', default='')
    ap_.add_argument('--ingress', default=''); ap_.add_argument('--kpi', action='append', default=[])
    ap_.add_argument('--gruppe-ark'); ap_.add_argument('--gruppe-kolonne'); ap_.add_argument('--hopp-over', action='append', default=[])
    ap_.add_argument('--konfidensielt', default='', help='Valgfritt ledd i bunnteksten (f.eks. «Konfidensielt»). Standard: ingen.')
    a = ap_.parse_args()
    wb = openpyxl.load_workbook(a.xlsx, data_only=True)
    skip = {s.lower() for s in a.hopp_over} | ALLTID_SKIP
    story = [Paragraph(esc(a.kunde), KICK), Paragraph(esc(a.tittel), H1)]
    if a.ingress: story.append(Paragraph(esc(a.ingress), P))
    story.append(Spacer(1, 6))
    cards = []
    for k in a.kpi:
        t, v, s, z = (k.split('|') + ['', '', 'neutral'])[:4]
        cards.append((t, kpi_verdi(wb, v), s, z or 'neutral'))
    if cards: story.append(kpi_row(cards)); story.append(Spacer(1, 8))
    for ws in wb.worksheets:
        if ws.title.lower() in skip: continue
        if ws.title.lower().startswith('dokumentinfo'):
            meta, formal, kvitt, ap = dokumentinfo(ws)
            if meta: story += [table(['Felt', 'Verdi'], meta, [0.15, 0.85], 'blue'), Spacer(1, 8)]
            if formal:
                story.append(Paragraph('Formål og innhold i forhold til HLD', H2))
                for t in formal: story.append(Paragraph(esc(t), P))
            if kvitt:
                story += [Paragraph('Kvittering av HLD-forutsetninger', H2), table(['Forutsetning (HLD)', 'Status', 'Merknad'], kvitt, [0.46, 0.09, 0.45], status_cols=(1,)), Spacer(1, 6)]
            if ap:
                story += [Paragraph('Åpne punkter', H2), table(['ID', 'Punkt', 'Type', 'Eier'], ap, [0.08, 0.6, 0.14, 0.18], 'amber')]
            story.append(PageBreak()); continue
        if ws.max_column <= 2:  # nøkkel/verdi-ark (f.eks. Oppsummering, Definisjoner)
            kv = [r for r in ws.iter_rows(min_row=1, values_only=True) if r[0] not in (None, '') and (len(r) < 2 or r[1] is not None)]
            if kv and len(kv[0]) >= 2 and kv[0][1] is None: kv = kv[1:]
            if kv and S(kv[0][0]).strip() in ('Begrep', 'Nøkkel', 'Etikett', 'Felt'): kv = kv[1:]
            if not kv: continue
            story += [Paragraph(esc(ws.title), H2), table(['Begrep' if 'defin' in ws.title.lower() else ws.title, 'Verdi' if 'defin' not in ws.title.lower() else 'Forklaring'], [(S(r[0]).strip(), S(r[1])) for r in kv], [0.3, 0.7], 'neutral'), PageBreak()]
            continue
        h = finn_header(ws); hdr = [S(c) for c in next(ws.iter_rows(min_row=h, max_row=h, values_only=True))]
        rows = datarader(ws, h)
        if not rows: continue
        while hdr and not hdr[-1]: hdr.pop()
        title_row = [S(c) for c in next(ws.iter_rows(min_row=1, max_row=1, values_only=True)) if c]
        story.append(Paragraph(esc(title_row[0] if h > 1 and title_row else ws.title), H2))
        if a.gruppe_ark == ws.title and a.gruppe_kolonne:
            gi = next(i for i, c in enumerate(hdr) if c.startswith(a.gruppe_kolonne))
            grupper = {}
            for r in rows: grupper.setdefault(S(r[gi]) or '–', []).append(r)
            for g, rs in grupper.items():
                story.append(Paragraph(f'{esc(g)} ({len(rs)})', H3))
                story += [table(hdr, rs, autowidths(hdr, rs), 'blue', status_cols=tuple(i for i, c in enumerate(hdr) if c.startswith(('Forretningskritikalitet', 'Kritikalitet')))), Spacer(1, 8)]
        else:
            sc = tuple(i for i, c in enumerate(hdr) if c.startswith(('Status', 'Klassifisering')))
            story += [table(hdr, rows, autowidths(hdr, rows), 'neutral', status_cols=sc)]
        story.append(PageBreak())
    if isinstance(story[-1], PageBreak): story.pop()
    bygg(a.pdf, a.tittel, ' · '.join(x for x in [a.kunde, a.tittel, a.versjon, a.konfidensielt] if x), story)
    print('Skrev', a.pdf)

if __name__ == '__main__': main()
