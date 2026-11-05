#!/usr/bin/env python3
"""Bygg et kommentarregister (Word, A4 liggende) med sju kolonner, siste kolonne «Revisjonskommentar» er TOM og forbeholdt revisors egne notater.

  python lag_register.py register.json ut.docx

register.json:
{"tittel": "Identitetskommentarer – HLD og Vedlegg D", "undertittel": "Gjennomgang ... · Intility Advisory · dato · Ingen endringer gjennomført",
 "intro": "Hva registeret bygger på ...",
 "avklaringer": [["Tittel", "Tekst"], ...],
 "seksjoner": [{"overskrift": "Løsningsdesign – HLD", "fagperson": "Monica Fritzøe",
                "rader": [{"nr": "41", "sted": "2.1 Identitet", "original": "teksten i dokumentet", "kommentar": "kommentaren ordrett",
                           "forslag": "ny tekst / tiltak", "kilde": "kontrakt/vedlegg-henvisning og merknad", "revisjon": ""}]}],
 "folgeendringer": ["..."]}
«revisjon» fylles bare når revisor allerede har besluttet (da settes teksten inn; ellers blir cellen tom)."""
import json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from docxlib import fiks_zoom
from docx import Document
from docx.shared import Pt, Mm, RGBColor
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

KOL = [('#', 0.5), ('Sted', 1.3), ('Opprinnelig tekst i dokumentet', 3.0), ('Kommentar / innspill ({fp})', 2.5), ('Forslag til ny tekst / tiltak', 3.1), ('Kilde og merknad', 2.3), ('Revisjonskommentar', 1.9)]

def skygge(cell, hexfarge):
    tcPr = cell._tc.get_or_add_tcPr(); sh = OxmlElement('w:shd'); sh.set(qn('w:val'), 'clear'); sh.set(qn('w:color'), 'auto'); sh.set(qn('w:fill'), hexfarge); tcPr.append(sh)

def skriv(cell, tekst, fet=False, kursiv=False, farge=None, str_=7.5):
    cell.text = ''
    linjer = str(tekst or '').split('\n')
    for i, l in enumerate(linjer):
        p = cell.paragraphs[0] if i == 0 else cell.add_paragraph()
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(l); r.font.size = Pt(str_); r.font.name = 'Arial'; r.bold = fet; r.italic = kursiv
        if farge: r.font.color.rgb = RGBColor.from_string(farge)

def bygg(spec, ut):
    d = Document(); s = d.sections[0]; s.orientation = WD_ORIENT.LANDSCAPE; s.page_width, s.page_height = Mm(297), Mm(210)
    for m in ('left_margin', 'right_margin'): setattr(s, m, Mm(14))
    s.top_margin = s.bottom_margin = Mm(14)
    st = d.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(10)
    h = d.add_paragraph(); r = h.add_run(spec['tittel']); r.bold = True; r.font.size = Pt(18)
    p = d.add_paragraph(); r = p.add_run(spec.get('undertittel', '')); r.font.size = Pt(10); r.font.color.rgb = RGBColor(0x59, 0x59, 0x59)
    if spec.get('intro'):
        p = d.add_paragraph(); r = p.add_run(spec['intro']); r.italic = True; r.font.size = Pt(9)
    p = d.add_paragraph(); r = p.add_run('Kolonnen «Revisjonskommentar» er tom og er forbeholdt egne notater under gjennomgangen.'); r.italic = True; r.font.size = Pt(9)
    if spec.get('avklaringer'):
        d.add_heading('Avklaringer som må tas før endring', level=1)
        for t, tekst in spec['avklaringer']:
            p = d.add_paragraph(); a = p.add_run(t + ': '); a.bold = True; a.font.size = Pt(9); b = p.add_run(tekst); b.font.size = Pt(9)
    tot = sum(b for _, b in KOL); bredde = 297 - 28
    for sek in spec['seksjoner']:
        d.add_heading(sek['overskrift'], level=1)
        t = d.add_table(rows=1, cols=len(KOL)); t.style = 'Table Grid'; t.autofit = False
        for i, (navn, b) in enumerate(KOL):
            c = t.rows[0].cells[i]; c.width = Mm(bredde * b / tot); skriv(c, navn.format(fp=sek.get('fagperson', 'fagteam')), fet=True, farge='FFFFFF'); skygge(c, '7F7F7F' if i == 6 else '1F3864')
        for i, (_, b) in enumerate(KOL): t.columns[i].width = Mm(bredde * b / tot)
        tr = t.rows[0]._tr; trPr = tr.get_or_add_trPr(); th = OxmlElement('w:tblHeader'); th.set(qn('w:val'), 'true'); trPr.append(th)
        for r_ in sek['rader']:
            row = t.add_row().cells
            vals = [r_.get('nr'), r_.get('sted'), r_.get('original'), r_.get('kommentar'), r_.get('forslag'), r_.get('kilde'), r_.get('revisjon', '')]
            for i, v in enumerate(vals):
                row[i].width = Mm(bredde * KOL[i][1] / tot); skriv(row[i], v, fet=(i == 0), kursiv=(i == 2))
                if i == 6: skygge(row[i], 'F2F2F2')
        d.add_paragraph()
    if spec.get('folgeendringer'):
        d.add_heading('Følgeendringer i andre dokumenter', level=1)
        for f in spec['folgeendringer']:
            p = d.add_paragraph(f, style='List Bullet'); [setattr(r.font, 'size', Pt(9)) for r in p.runs]
    d.save(ut); fiks_zoom(ut); print('Skrev', ut)

if __name__ == '__main__':
    if len(sys.argv) != 3: sys.exit(__doc__)
    bygg(json.load(open(sys.argv[1], encoding='utf-8')), sys.argv[2])
