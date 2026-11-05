#!/usr/bin/env python3
"""Bygg et vedlegg som Excel-register (listebaserte vedlegg: applikasjoner, lisenser, nettverksenheter ...).

  python bygg_vedlegg_xlsx.py spec.json Vedlegg_X.xlsx

Spec (alle felt er på norsk, se ../references/vedlegg-mal.md):
{
 "tittel": "Vedlegg A – Applikasjoner og integrasjoner",
 "meta": [["Overordnet dokument","Løsningsdesign – <Kunde> – HLD, kap. 3"],["Eier","..."],["Godkjenning","..."],["Kontraktsgrunnlag","..."],["Status","Utkast ..."],["Versjon","0.1 – dd.mm.åååå – ..."]],
 "formal": ["Vedlegget detaljerer HLD kap. N ... HLD-en fastsetter ...; dette vedlegget gir ...", "Innhold: ... Godkjennes av Kunden ..."],
 "kvittering": [["Forutsetning i HLD x.y", "Bekreftes", "Hvor/hvordan bekreftes"]],
 "apne_punkter": {"prefiks": "ÅP-A", "rader": [["Punkt","Type","Eier"]]},
 "registre": [{"navn":"Applikasjoner","kolonner":["..."],"rader":[["..."]],"bredder":[30,20],"frys":"B2"}],
 "definisjoner": [["Begrep","Forklaring"]],
 "oppsummering": [["Etikett","verdi eller =formel"]]
}
Regler som håndheves: ingen ark kalt Endringslogg eller Godkjenning. ÅP-IDer genereres (ÅP-A-01, ...). Status i kvitteringen må være Bekreftes/Åpen/Avvik.
Celler som begynner med «Fastsettes i» får grå bakgrunn (utfylles senere)."""
import json, sys
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

NAVY = '17325C'; GRID = Side(style='thin', color='C9D3E0')
STATUS = {'Bekreftes': 'D5EFDF', 'Åpen': 'FFF0C9', 'Avvik': 'F8D4CF'}
VERBUDT = {'endringslogg', 'godkjenning'}

def hode(ws, rad, verdier, farge=NAVY):
    for i, v in enumerate(verdier, 1):
        c = ws.cell(rad, i, v); c.font = Font(bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor=farge)
        c.alignment = Alignment(wrap_text=True, vertical='center'); c.border = Border(bottom=GRID)

def rad(ws, r, verdier, status_kol=None):
    for i, v in enumerate(verdier, 1):
        c = ws.cell(r, i, v); c.alignment = Alignment(wrap_text=True, vertical='top'); c.border = Border(bottom=GRID)
        if isinstance(v, str) and v.startswith('Fastsettes i'): c.fill = PatternFill('solid', fgColor='F2F2F2')
        if status_kol is not None and i - 1 == status_kol and v in STATUS: c.fill = PatternFill('solid', fgColor=STATUS[v]); c.font = Font(bold=True)

STANDARD_META = ['Overordnet dokument', 'Eier', 'Kontraktsgrunnlag', 'Godkjenning']

def bygg(spec, ut):
    if [k for k, _ in spec['meta']] != STANDARD_META: sys.exit(f'FEIL: metadata-tabellen skal ha nøyaktig feltene {STANDARD_META} i denne rekkefølgen (Eier = avdeling, ikke person)')
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = 'Dokumentinfo og forutsetninger'
    ws['A1'] = spec['tittel']; ws['A1'].font = Font(bold=True, size=16, color=NAVY)
    r = 3
    for k, v in spec['meta']:
        ws.cell(r, 1, k).font = Font(bold=True); c = ws.cell(r, 2, v); c.alignment = Alignment(wrap_text=True, vertical='top'); ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=4); ws.row_dimensions[r].height = max(18, 15 * (len(str(v)) // 90 + 1)); r += 1
    r += 1; ws.cell(r, 1, 'Formål og innhold i forhold til HLD').font = Font(bold=True, size=12, color=NAVY); r += 1
    for t in spec['formal']:
        c = ws.cell(r, 1, t); c.alignment = Alignment(wrap_text=True, vertical='top'); ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=4); ws.row_dimensions[r].height = 15 * (len(t) // 120 + 1); r += 1
    r += 1; ws.cell(r, 1, 'Kvittering av HLD-forutsetninger').font = Font(bold=True, size=12, color=NAVY); r += 1
    hode(ws, r, ['Forutsetning (HLD)', 'Status', 'Merknad / hvor bekreftes']); r += 1
    for f in spec['kvittering']:
        if f[1] not in STATUS: sys.exit(f'FEIL: ugyldig status «{f[1]}» (tillatt: Bekreftes, Åpen, Avvik)')
        rad(ws, r, f, status_kol=1); ws.row_dimensions[r].height = 15 * (max(len(str(f[0])), len(str(f[2]))) // 60 + 1); r += 1
    r += 1; ws.cell(r, 1, 'Åpne punkter').font = Font(bold=True, size=12, color=NAVY); r += 1
    hode(ws, r, ['ID', 'Punkt', 'Type', 'Eier']); r += 1
    for i, (punkt, type_, eier) in enumerate(spec['apne_punkter']['rader'], 1):
        rad(ws, r, [f"{spec['apne_punkter']['prefiks']}-{i:02d}", punkt, type_, eier]); ws.row_dimensions[r].height = 15 * (len(punkt) // 60 + 1); r += 1
    for col, b in zip('ABCD', [34, 70, 26, 26]): ws.column_dimensions[col].width = b
    if spec.get('oppsummering'):
        o = wb.create_sheet('Oppsummering'); o['A1'] = spec['tittel']; o['A1'].font = Font(bold=True, size=14, color=NAVY)
        for i, (k, v) in enumerate(spec['oppsummering'], 3): o.cell(i, 1, k); o.cell(i, 2, v)
        o.column_dimensions['A'].width = 44; o.column_dimensions['B'].width = 24
    for reg in spec.get('registre', []):
        if reg['navn'].lower() in VERBUDT: sys.exit(f'FEIL: vedlegg skal ikke ha ark «{reg["navn"]}»')
        s = wb.create_sheet(reg['navn']); hode(s, 1, reg['kolonner'])
        for i, rr in enumerate(reg['rader'], 2): rad(s, i, rr)
        for i, b in enumerate(reg.get('bredder') or [24] * len(reg['kolonner']), 1): s.column_dimensions[openpyxl.utils.get_column_letter(i)].width = b
        s.freeze_panes = reg.get('frys', 'A2'); s.auto_filter.ref = f"A1:{openpyxl.utils.get_column_letter(len(reg['kolonner']))}{len(reg['rader']) + 1}"; s.row_dimensions[1].height = 32
    if spec.get('definisjoner'):
        d = wb.create_sheet('Definisjoner'); hode(d, 1, ['Begrep', 'Forklaring'])
        for i, rr in enumerate(spec['definisjoner'], 2): rad(d, i, rr)
        d.column_dimensions['A'].width = 30; d.column_dimensions['B'].width = 110
    for s in wb.worksheets:
        s.page_setup.orientation = 'landscape'; s.page_setup.fitToWidth = 1; s.page_setup.fitToHeight = 0; s.sheet_properties.pageSetUpPr = openpyxl.worksheet.properties.PageSetupProperties(fitToPage=True)
    wb.save(ut); print('Skrev', ut)

if __name__ == '__main__':
    if len(sys.argv) != 3: sys.exit(__doc__)
    bygg(json.load(open(sys.argv[1], encoding='utf-8')), sys.argv[2])
