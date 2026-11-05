#!/usr/bin/env python3
"""Bygg et vedlegg som Word-dokument (tekst- og beslutningstunge vedlegg: identitet, workplace, migrering ...).

  python bygg_vedlegg_docx.py spec.json Vedlegg_X.docx

Spec:
{
 "tittel": "Vedlegg D – Identitet", "undertittel": "Detaljdesign for ... · Utkast 0.1", "kunde": "<Kunde>",
 "meta": [["Overordnet dokument","..."],["Eier","Intility <Avdeling>"],["Kontraktsgrunnlag","..."],["Godkjenning","..."]],
 "formal": ["Vedlegget detaljerer ...", "Innhold: ..."],
 "kvittering": [["Forutsetning (HLD)","Bekreftes|Åpen|Avvik","Merknad"]],
 "kapitler": [{"overskrift": "Tenant, domener og katalog",
               "blokker": [{"type":"avsnitt","tekst":"..."}, {"type":"tabell","kolonner":[...],"rader":[[...]]},
                           {"type":"punkter","punkter":["..."]}, {"type":"underkapittel","tekst":"..."}]}],
 "apne_punkter": {"prefiks":"ÅP-D","rader":[["Punkt","Type","Eier"]]}
}
Kapittelnummer settes automatisk: 1 Formål og innhold i forhold til HLD, 2 Kvittering, så dine kapitler fra 3, til slutt Åpne punkter.
Det lages ALDRI kapitler for Endringslogg eller Godkjenning."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from docx import Document
from docx.shared import Pt, Mm, RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import re, zipfile

STATUS = {'Bekreftes': 'D5EFDF', 'Åpen': 'FFF0C9', 'Avvik': 'F8D4CF'}

def skygge(cell, farge):
    tcPr = cell._tc.get_or_add_tcPr(); sh = OxmlElement('w:shd'); sh.set(qn('w:val'), 'clear'); sh.set(qn('w:color'), 'auto'); sh.set(qn('w:fill'), farge); tcPr.append(sh)

def celle(c, tekst, fet=False, farge=None, hvit=False, str_=8.5):
    c.text = ''; p = c.paragraphs[0]; p.paragraph_format.space_after = Pt(2)
    r = p.add_run(str(tekst if tekst is not None else '')); r.font.size = Pt(str_); r.bold = fet
    if hvit: r.font.color.rgb = RGBColor(255, 255, 255)
    if farge: skygge(c, farge)

def tabell(d, kolonner, rader, bredder=None, status_kol=None):
    t = d.add_table(rows=1, cols=len(kolonner)); t.style = 'Table Grid'
    for i, k in enumerate(kolonner): celle(t.rows[0].cells[i], k, True, '17325C', True)
    trPr = t.rows[0]._tr.get_or_add_trPr(); h = OxmlElement('w:tblHeader'); h.set(qn('w:val'), 'true'); trPr.append(h)
    for r in rader:
        cs = t.add_row().cells
        for i, v in enumerate(r[:len(kolonner)]):
            celle(cs[i], v, fet=(i == 0), farge=STATUS.get(v) if status_kol == i else None)
    if bredder:
        t.autofit = False
        for i, b in enumerate(bredder): t.columns[i].width = Mm(b)
        for row in t.rows:
            for i, b in enumerate(bredder): row.cells[i].width = Mm(b)
    d.add_paragraph(); return t

STANDARD_META = ['Overordnet dokument', 'Eier', 'Kontraktsgrunnlag', 'Godkjenning']

def bygg(spec, ut):
    if [k for k, _ in spec['meta']] != STANDARD_META: sys.exit(f'FEIL: metadata-tabellen skal ha nøyaktig feltene {STANDARD_META} i denne rekkefølgen (Eier = avdeling, ikke person)')
    d = Document(); s = d.sections[0]; s.page_width, s.page_height = Mm(210), Mm(297)
    for m in ('left_margin', 'right_margin', 'top_margin', 'bottom_margin'): setattr(s, m, Mm(20))
    st = d.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(10)
    for n, sz in (('Heading 1', 14), ('Heading 2', 11.5)):
        h = d.styles[n]; h.font.name = 'Arial'; h.font.size = Pt(sz); h.font.bold = True; h.font.color.rgb = RGBColor(0x17, 0x32, 0x5C)
    p = d.add_paragraph(); r = p.add_run(spec.get('kunde', '')); r.font.size = Pt(11); r.font.color.rgb = RGBColor(0x59, 0x59, 0x59)
    p = d.add_paragraph(); r = p.add_run(spec['tittel']); r.bold = True; r.font.size = Pt(20)
    p = d.add_paragraph(); r = p.add_run(spec.get('undertittel', '')); r.font.size = Pt(11); r.font.color.rgb = RGBColor(0x59, 0x59, 0x59)
    tabell(d, ['Felt', 'Verdi'], spec['meta'], [45, 125])
    d.add_heading('1 Formål og innhold i forhold til HLD', 1)
    for t in spec['formal']: d.add_paragraph(t)
    d.add_heading('2 Kvittering av HLD-forutsetninger', 1)
    d.add_paragraph('Forutsetningene HLD-en stiller på dette området, og status ved denne versjonen.')
    for f in spec['kvittering']:
        if f[1] not in STATUS: sys.exit(f'FEIL: ugyldig status «{f[1]}» (tillatt: Bekreftes, Åpen, Avvik)')
    tabell(d, ['Forutsetning (HLD)', 'Status', 'Merknad'], spec['kvittering'], [78, 22, 70], status_kol=1)
    n = 3
    for kap in spec['kapitler']:
        if re.sub(r'^[\d. ]+', '', kap['overskrift']).strip().lower() in ('endringslogg', 'godkjenning'): sys.exit('FEIL: vedlegg skal ikke ha kapitlene Endringslogg/Godkjenning')
        d.add_heading(f'{n} {kap["overskrift"]}', 1); n += 1
        for b in kap.get('blokker', []):
            if b['type'] == 'avsnitt': d.add_paragraph(b['tekst'])
            elif b['type'] == 'tabell': tabell(d, b['kolonner'], b['rader'], b.get('bredder'))
            elif b['type'] == 'punkter': [d.add_paragraph(x, style='List Bullet') for x in b['punkter']]
            elif b['type'] == 'underkapittel': d.add_heading(b['tekst'], 2)
    d.add_heading(f'{n} Åpne punkter og Bilag 9-kandidater', 1)
    rader = [[f"{spec['apne_punkter']['prefiks']}-{i:02d}", *r] for i, r in enumerate(spec['apne_punkter']['rader'], 1)]
    tabell(d, ['ID', 'Punkt', 'Type', 'Eier'], rader, [20, 90, 30, 30])
    d.save(ut)
    # rett opp python-docx sin zoom-feil
    z = zipfile.ZipFile(ut); files = {k: z.read(k) for k in z.namelist()}; z.close()
    files['word/settings.xml'] = re.sub(rb'<w:zoom w:val="[^"]*"\s*/>', b'<w:zoom w:percent="100"/>', files['word/settings.xml'])
    with zipfile.ZipFile(ut, 'w', zipfile.ZIP_DEFLATED) as zo:
        for k, b in files.items(): zo.writestr(k, b)
    print('Skrev', ut)

if __name__ == '__main__':
    if len(sys.argv) != 3: sys.exit(__doc__)
    bygg(json.load(open(sys.argv[1], encoding='utf-8')), sys.argv[2])
