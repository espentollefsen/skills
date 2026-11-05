#!/usr/bin/env python3
"""Kontroller at et vedlegg (xlsx eller docx) følger reglene. Kjør før levering.
  python vedlegg_lint.py Vedlegg_X.xlsx|docx
Feil (exit 1): Endringslogg/Godkjenning-ark eller -kapittel · metadata-tabellen avviker fra de fire standardfeltene (Overordnet dokument · Eier · Kontraktsgrunnlag · Godkjenning) · mangler «Formål og innhold i forhold til HLD» · ugyldig kvitteringsstatus · ÅP-ID med feil format, dobbelt prefiks eller duplikat.
Advarsler: priser i vedlegg · blandet «Fastsettes i …»-vokabular · Eier som ser ut som rolle/person/flere parter."""
import re, sys
feil, advarsler = [], []

def sjekk_tekster(tekster, overskrifter, statuser, ap_ids, meta_nokler):
    if any(re.sub(r'^[\d. ]+', '', o).strip().lower() in ('endringslogg', 'godkjenning') for o in overskrifter): feil.append('Inneholder Endringslogg/Godkjenning (skal ikke finnes i vedlegg).')
    if not any('Formål og innhold i forhold til HLD' in t for t in list(tekster) + list(overskrifter)): feil.append('Mangler «Formål og innhold i forhold til HLD».')
    for s in statuser:
        if s not in ('Bekreftes', 'Åpen', 'Avvik'): feil.append(f'Ugyldig kvitteringsstatus: «{s}» (tillatt: Bekreftes, Åpen, Avvik).')
    seen = set()
    for i in ap_ids:
        if 'ÅP-ÅP' in i: feil.append(f'Dobbelt prefiks i ÅP-ID: {i}')
        elif not re.fullmatch(r'ÅP-[A-Z]-\d{2}', i): feil.append(f'ÅP-ID har feil format: {i} (forventet ÅP-<vedleggsbokstav>-nn)')
        if i in seen: feil.append(f'Duplisert ÅP-ID: {i}')
        seen.add(i)
    alt = ' '.join(tekster)
    if re.search(r'\d[\d ]*\s?kr\s?/', alt): advarsler.append('Pris funnet (kr/…). Priser hører hjemme i prislisten (Bilag 7) og gjentas ikke i vedlegg.')
    if 'Fastsettes i detaljdesign' in alt and 'Fastsettes i Fase 1' in alt: advarsler.append('Blandet vokabular: både «Fastsettes i detaljdesign» og «Fastsettes i Fase 1». Bruk ett.')
    nokler = [k for k, _ in meta_nokler]
    if nokler != ['Overordnet dokument', 'Eier', 'Kontraktsgrunnlag', 'Godkjenning']: feil.append(f'Metadata-tabellen skal ha nøyaktig feltene Overordnet dokument · Eier · Kontraktsgrunnlag · Godkjenning (i den rekkefølgen). Fant: {nokler}')
    eier = dict(meta_nokler).get('Eier', '')
    if eier and (re.search(r'\b(arkitekt|prosjektleder|leder|rådgiver|konsulent)\b', eier, re.I) or re.search(r'[()/]', eier)): advarsler.append(f'Eier «{eier}» ser ut som en rolle eller flere parter. Eier skal være én relevant avdeling, ikke person eller rolle (f.eks. «Intility Network»).')

def xlsx(path):
    import openpyxl
    wb = openpyxl.load_workbook(path, data_only=True); tekster, ov, st, ap, meta = [], list(wb.sheetnames), [], [], []
    for ws in wb.worksheets:
        for r in ws.iter_rows(values_only=True):
            for c in r:
                if isinstance(c, str): tekster.append(c)
    di = wb[[n for n in wb.sheetnames if n.lower().startswith('dokumentinfo')][0]] if any(n.lower().startswith('dokumentinfo') for n in wb.sheetnames) else None
    if di is None: feil.append('Mangler arket «Dokumentinfo og forutsetninger».'); return tekster, ov, st, ap, meta
    mode = 'meta'
    for r in di.iter_rows(values_only=True):
        a, b = (list(r) + [None, None])[:2]
        if a is None: continue
        if str(a).startswith('Kvittering'): mode = 'k'; continue
        if str(a).startswith('Åpne punkter'): mode = 'a'; continue
        if str(a).startswith('Formål'): mode = 'f'; continue
        if mode == 'meta' and b is not None: meta.append((str(a), str(b)))
        if mode == 'k' and b is not None and a != 'Forutsetning (HLD)' and not str(a).startswith('Forutsetning (HLD'): st.append(str(b))
        if mode == 'a' and a != 'ID': ap.append(str(a))
    return tekster, ov, st, ap, meta

def docx_(path):
    import docx
    d = docx.Document(path); tekster = [p.text for p in d.paragraphs]; ov = [p.text for p in d.paragraphs if (p.style.name or '').startswith('Heading') or (p._p.pPr is not None and p._p.pPr.pStyle is not None and 'eading' in (p._p.pPr.pStyle.val or ''))]
    st, ap, meta = [], [], []
    for t in d.tables:
        h = [c.text.strip() for c in t.rows[0].cells]
        for r in t.rows: tekster += [c.text for c in r.cells]
        if h[:2] == ['Felt', 'Verdi']: meta = [(r.cells[0].text.strip(), r.cells[1].text.strip()) for r in t.rows[1:]]
        if h[:2] == ['Forutsetning (HLD)', 'Status']: st = [r.cells[1].text.strip() for r in t.rows[1:]]
        if h and h[0] == 'ID': ap = [r.cells[0].text.strip() for r in t.rows[1:]]
    return tekster, ov, st, ap, meta

if __name__ == '__main__':
    if len(sys.argv) != 2: sys.exit(__doc__)
    p = sys.argv[1]; res = xlsx(p) if p.lower().endswith('.xlsx') else docx_(p)
    sjekk_tekster(*res)
    for f in feil: print('FEIL     ', f)
    for a in advarsler: print('ADVARSEL ', a)
    print('OK – ingen regelbrudd.' if not feil and not advarsler else f'{len(feil)} feil, {len(advarsler)} advarsler.')
    sys.exit(1 if feil else 0)
