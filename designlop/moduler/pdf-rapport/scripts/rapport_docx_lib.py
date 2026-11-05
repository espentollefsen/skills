"""Word-rapporter (A4 liggende) i samme visuelle språk som PDF-rapportene: nøkkeltallskort, statusmerker, navy tabellhoder, sebrastriper, bunntekst med sidetall.
Brukes av xlsx_til_docx.py og kan importeres for spesialrapporter. Alt er ekte Word: overskrifter (Heading 1/2) for navigasjonsrute, tabeller med gjentatt topprad."""
import re, zipfile
from docx import Document
from docx.shared import Pt, Mm, RGBColor
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

NAVY = '17325C'; GREY = '4F6079'; LINE = 'C9D3E0'; WHITE = 'FFFFFF'
GREEN = '2EAD63'; AMBER = 'D9941E'; RED = 'E2574C'; GRAYPILL = '6B7A90'
ZONES = {'blue': 'EAF0FB', 'purple': 'F1EDFB', 'green': 'EAF7F0', 'amber': 'FFF6E3', 'neutral': 'EEF3FA'}
STATUS_FARGER = {'Bekreftes': GREEN, 'Bekreftet': GREEN, 'Åpen': AMBER, 'Avvik': RED, 'Lukket': GRAYPILL, 'TBD': AMBER,
                 'Critical': RED, 'High': AMBER, 'Normal': GREEN, 'Re-etablering': GREEN, 'Uavklart': AMBER, 'Avvikling': GRAYPILL, 'Utgår': GRAYPILL}
FONT = 'Arial'
BREDDE_MM = 269  # A4 liggende 297 − 2×14

class Pill:
    def __init__(self, tekst, farge): self.tekst, self.farge = tekst, farge
class Rich:
    """Cellinnhold med flere linjer/stiler: Rich([('tekst', {'bold': True}), '\\n', ('liten tekst', {'color': 'D9941E'})])"""
    def __init__(self, deler): self.deler = deler

def S(x): return '' if x is None else str(x)

def statuspill(verdi):
    """Statusord → merke. Lang tekst som starter med et statusord beholdes: merket på første linje, resten under (ingenting forkastes)."""
    s = S(verdi)
    for k, f in STATUS_FARGER.items():
        if s == k or s.startswith(k + ' ') or s.startswith(k + '.'):
            if len(s) <= 20: return Pill(s, f)
            rest = s[len(k):].lstrip(' .–-')
            return Rich([Pill(k, f), '\n', rest])
    return s

# ---------- XML-hjelpere ----------
ORDEN = {
 'tcPr': ['cnfStyle','tcW','gridSpan','hMerge','vMerge','tcBorders','shd','noWrap','tcMar','textDirection','tcFitText','vAlign','hideMark'],
 'tblPr': ['tblStyle','tblpPr','tblOverlap','bidiVisual','tblStyleRowBandSize','tblStyleColBandSize','tblW','jc','tblCellSpacing','tblInd','tblBorders','shd','tblLayout','tblCellMar','tblLook','tblCaption','tblDescription'],
 'pPr': ['pStyle','keepNext','keepLines','pageBreakBefore','framePr','widowControl','numPr','suppressLineNumbers','pBdr','shd','tabs','suppressAutoHyphens','kinsoku','wordWrap','overflowPunct','topLinePunct','autoSpaceDE','autoSpaceDN','bidi','adjustRightInd','snapToGrid','spacing','ind','contextualSpacing','mirrorIndents','suppressOverlap','jc','textDirection','textAlignment','textboxTightWrap','outlineLvl','divId','cnfStyle','rPr','sectPr','pPrChange'],
 'rPr': ['rStyle','rFonts','b','bCs','i','iCs','caps','smallCaps','strike','dstrike','outline','shadow','emboss','imprint','noProof','snapToGrid','vanish','webHidden','color','spacing','w','kern','position','sz','szCs','highlight','u','effect','bdr','shd','fitText','vertAlign','rtl','cs','em','lang','eastAsianLayout','specVanish','oMath'],
}
def _lokal(el): return el.tag.split('}')[1]
def sett_inn(forelder, barn):
    """Sett inn barn i forelder i rekkefølgen OOXML-skjemaet krever (erstatter eksisterende element med samme navn)."""
    orden = ORDEN[_lokal(forelder)]; navn = _lokal(barn)
    for e in forelder.findall(barn.tag): forelder.remove(e)
    idx = orden.index(navn)
    for e in list(forelder):
        n = _lokal(e)
        if n in orden and orden.index(n) > idx: e.addprevious(barn); return barn
    forelder.append(barn); return barn

def _shd(el_pr, fill):
    sh = OxmlElement('w:shd'); sh.set(qn('w:val'), 'clear'); sh.set(qn('w:color'), 'auto'); sh.set(qn('w:fill'), fill); sett_inn(el_pr, sh)

def celle_skygge(c, fill): _shd(c._tc.get_or_add_tcPr(), fill)

def celle_marg(c, top=50, bottom=50, left=80, right=80):
    tcPr = c._tc.get_or_add_tcPr(); m = OxmlElement('w:tcMar')
    for k, v in (('top', top), ('left', left), ('bottom', bottom), ('right', right)):
        e = OxmlElement(f'w:{k}'); e.set(qn('w:w'), str(v)); e.set(qn('w:type'), 'dxa'); m.append(e)
    sett_inn(tcPr, m)

def celle_kant(c, **kanter):
    """kanter: top/bottom/left/right = (størrelse_åttedels_pt, farge) eller None for ingen."""
    tcPr = c._tc.get_or_add_tcPr(); b = OxmlElement('w:tcBorders')
    for side in ('top', 'left', 'bottom', 'right'):
        v = kanter.get(side); e = OxmlElement(f'w:{side}')
        if v is None: e.set(qn('w:val'), 'nil')
        else: e.set(qn('w:val'), 'single'); e.set(qn('w:sz'), str(v[0])); e.set(qn('w:space'), '0'); e.set(qn('w:color'), v[1])
        b.append(e)
    sett_inn(tcPr, b)

def tabell_fast(t, bredder_mm):
    t.autofit = False; t.alignment = WD_TABLE_ALIGNMENT.LEFT
    tblPr = t._tbl.tblPr
    lay = OxmlElement('w:tblLayout'); lay.set(qn('w:type'), 'fixed'); sett_inn(tblPr, lay)
    tw = OxmlElement('w:tblW'); tw.set(qn('w:type'), 'dxa'); tw.set(qn('w:w'), str(int(sum(bredder_mm) * 56.7))); sett_inn(tblPr, tw)
    grid = t._tbl.tblGrid
    for gc, b in zip(grid.findall(qn('w:gridCol')), bredder_mm): gc.set(qn('w:w'), str(int(b * 56.7)))
    for r in t.rows:
        for c, b in zip(r.cells, bredder_mm): c.width = Mm(b)

def rad_regler(row, topp=False):
    trPr = row._tr.get_or_add_trPr()
    cs = OxmlElement('w:cantSplit'); cs.set(qn('w:val'), 'true'); trPr.append(cs)
    if topp: h = OxmlElement('w:tblHeader'); h.set(qn('w:val'), 'true'); trPr.append(h)

def kjor(p, tekst, str_=7.6, fet=False, farge=NAVY, kursiv=False, skygge=None, kant=None):
    r = p.add_run(tekst); r.font.size = Pt(str_); r.font.name = FONT; r.bold = fet; r.italic = kursiv
    r._r.get_or_add_rPr().rFonts.set(qn('w:eastAsia'), FONT)
    r.font.color.rgb = RGBColor.from_string(farge)
    if skygge: _shd(r._r.get_or_add_rPr(), skygge)
    if kant:  # tegnkant i samme farge som fyllet gir luft rundt merket uten å endre teksten
        b = OxmlElement('w:bdr'); b.set(qn('w:val'), 'single'); b.set(qn('w:sz'), '4'); b.set(qn('w:space'), '2'); b.set(qn('w:color'), kant); sett_inn(r._r.get_or_add_rPr(), b)
    return r

def avsnitt_format(p, etter=0, for_=0, linje=1.0):
    pf = p.paragraph_format; pf.space_after = Pt(etter); pf.space_before = Pt(for_); pf.line_spacing = linje

def fyll_celle(c, verdi, str_=7.6, fet=False, farge=NAVY):
    c.text = ''; p = c.paragraphs[0]; avsnitt_format(p)
    if isinstance(verdi, Pill):
        kjor(p, verdi.tekst, 7, True, WHITE, skygge=verdi.farge, kant=verdi.farge)
    elif isinstance(verdi, Rich):
        for d in verdi.deler:
            if d == '\n': p = c.add_paragraph(); avsnitt_format(p); continue
            if isinstance(d, Pill): kjor(p, d.tekst, 7, True, WHITE, skygge=d.farge, kant=d.farge); continue
            t, st = d if isinstance(d, tuple) else (d, {})
            kjor(p, t, st.get('str', str_), st.get('bold', fet), st.get('color', farge))
    else:
        kjor(p, S(verdi), str_, fet, farge)

# ---------- Dokument ----------
class Rapport:
    def __init__(self, tittel, bunntekst, forfatter='Intility Advisory'):
        self.d = Document(); d = self.d; s = d.sections[0]
        s.orientation = WD_ORIENT.LANDSCAPE; s.page_width, s.page_height = Mm(297), Mm(210)
        s.left_margin = s.right_margin = Mm(14); s.top_margin = Mm(12); s.bottom_margin = Mm(14); s.footer_distance = Mm(6)
        n = d.styles['Normal']; n.font.name = FONT; n.font.size = Pt(9); n.element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
        for navn, sz, for_, etter in (('Heading 1', 14, 8, 6), ('Heading 2', 10.5, 6, 3)):
            h = d.styles[navn]; h.font.name = FONT; h.font.size = Pt(sz); h.font.bold = True; h.font.italic = False
            h.font.color.rgb = RGBColor.from_string(NAVY); h.element.rPr.rFonts.set(qn('w:eastAsia'), FONT); h.element.rPr.rFonts.set(qn('w:ascii'), FONT); h.element.rPr.rFonts.set(qn('w:hAnsi'), FONT)
            h.paragraph_format.space_before = Pt(for_); h.paragraph_format.space_after = Pt(etter); h.paragraph_format.keep_with_next = True
        d.core_properties.title = tittel; d.core_properties.author = forfatter
        # bunntekst
        f = s.footer; p = f.paragraphs[0]; p.text = ''; avsnitt_format(p)
        pPr = p._p.get_or_add_pPr(); b = OxmlElement('w:pBdr'); top = OxmlElement('w:top')
        for k, v in (('val', 'single'), ('sz', '4'), ('space', '4'), ('color', LINE)): top.set(qn(f'w:{k}'), v)
        b.append(top); sett_inn(pPr, b)
        tabs = OxmlElement('w:tabs')
        for val, pos in (('clear', 4680), ('clear', 9360), ('right', int(BREDDE_MM * 56.7))):
            tb = OxmlElement('w:tab'); tb.set(qn('w:val'), val); tb.set(qn('w:pos'), str(pos)); tabs.append(tb)
        sett_inn(pPr, tabs)
        kjor(p, bunntekst + '\t', 7.5, False, GREY); kjor(p, 'Side ', 7.5, False, GREY)
        def feltrun(**kw):
            r = kjor(p, '', 7.5, False, GREY); return r
        r = feltrun(); fc = OxmlElement('w:fldChar'); fc.set(qn('w:fldCharType'), 'begin'); r._r.append(fc)
        r = feltrun(); it = OxmlElement('w:instrText'); it.set(qn('xml:space'), 'preserve'); it.text = ' PAGE '; r._r.append(it)
        r = feltrun(); fc = OxmlElement('w:fldChar'); fc.set(qn('w:fldCharType'), 'separate'); r._r.append(fc)
        kjor(p, '1', 7.5, False, GREY)
        r = feltrun(); fc = OxmlElement('w:fldChar'); fc.set(qn('w:fldCharType'), 'end'); r._r.append(fc)
        self._forste = True

    def kicker(self, tekst):
        p = self.d.paragraphs[0] if (self._forste and len(self.d.paragraphs) == 1 and not self.d.paragraphs[0].text) else self.d.add_paragraph()
        self._forste = False; avsnitt_format(p); kjor(p, tekst, 10, False, GREY)

    def tittel(self, tekst):
        p = self.d.add_paragraph(); avsnitt_format(p, 4); kjor(p, tekst, 22, True, NAVY)
        p.style = self.d.styles['Title']; [setattr(r.font, 'size', Pt(22)) for r in p.runs]
        pPr = p._p.get_or_add_pPr()
        for e in pPr.findall(qn('w:pBdr')): pPr.remove(e)

    def ingress(self, tekst):
        p = self.d.add_paragraph(); avsnitt_format(p, 6); kjor(p, tekst, 9, False, GREY)

    def avsnitt(self, tekst, farge=GREY, str_=9, hold_med_neste=False):
        p = self.d.add_paragraph(); avsnitt_format(p, 4); kjor(p, tekst, str_, False, farge)
        if hold_med_neste: p.paragraph_format.keep_with_next = True
        return p

    def h1(self, tekst, ny_side=False):
        if ny_side:  # unngå blank side: fjern avstandsavsnittet rett før et tvunget sideskift
            blokker = list(self.d.element.body)
            if len(blokker) >= 2 and blokker[-2] is getattr(self, '_sp', None): self.d.element.body.remove(blokker[-2])
        p = self.d.add_heading(tekst, level=1); p.paragraph_format.page_break_before = ny_side; return p

    def h2(self, tekst): return self.d.add_heading(tekst, level=2)

    def mellomrom(self, pt=6):
        p = self.d.add_paragraph(); avsnitt_format(p, 0); p.paragraph_format.line_spacing = Pt(pt)
        for r in p.runs: r.font.size = Pt(2)
        self._sp = p._p

    def punkter(self, liste):
        for x in liste:
            p = self.d.add_paragraph(style='List Bullet'); avsnitt_format(p, 3); kjor(p, x, 9, False, NAVY)

    def kpi(self, kort):
        """kort: liste av (tittel, verdi, undertekst, sone)"""
        n = len(kort); t = self.d.add_table(rows=1, cols=n); b = [BREDDE_MM / n] * n; tabell_fast(t, b)
        for c, (tit, val, sub, sone) in zip(t.rows[0].cells, kort):
            celle_skygge(c, ZONES.get(sone, ZONES['neutral'])); celle_marg(c, 150, 150, 180, 180)
            celle_kant(c, top=(48, WHITE), bottom=(48, WHITE), left=(48, WHITE), right=(48, WHITE))
            c.text = ''; p = c.paragraphs[0]; avsnitt_format(p, 1); kjor(p, tit, 8, True, GREY)
            p = c.add_paragraph(); avsnitt_format(p, 1); kjor(p, S(val), 22, True, NAVY)
            p = c.add_paragraph(); avsnitt_format(p, 0); kjor(p, sub, 8, False, GREY)
        rad_regler(t.rows[0]); self.mellomrom(8)

    def tabell(self, hode, rader, bredder, sone='neutral', status_kol=(), fet_forste=True, nede=True):
        """bredder: andeler (sum ≈ 1). Celleverdier: str | Pill | Rich. status_kol: kolonner som gjøres om til statusmerker."""
        n = len(hode); tot = sum(bredder); mm = [BREDDE_MM * b / tot for b in bredder]
        t = self.d.add_table(rows=1, cols=n); tabell_fast(t, mm)
        for i, h in enumerate(hode):
            c = t.rows[0].cells[i]; fyll_celle(c, h, 7.8, True, WHITE); celle_skygge(c, NAVY); celle_marg(c, 60, 60, 80, 80); c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            celle_kant(c, top=None, left=None, right=None, bottom=None)
        rad_regler(t.rows[0], topp=True)
        for ri, r in enumerate(rader):
            row = t.add_row(); rad_regler(row); fill = WHITE if ri % 2 == 0 else ZONES.get(sone, ZONES['neutral'])
            for i in range(n):
                v = r[i] if i < len(r) else ''
                if i in status_kol and not isinstance(v, (Pill, Rich)): v = statuspill(v)
                c = row.cells[i]; fyll_celle(c, v, 7.6, fet=(i == 0 and fet_forste)); celle_skygge(c, fill); celle_marg(c, 50, 50, 80, 80)
                celle_kant(c, top=None, left=None, right=None, bottom=(4, LINE)); c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
        tabell_fast(t, mm)  # sett bredder på nye rader
        self.mellomrom(8); return t

    def meta(self, rader):
        """Metadata-tabell (Felt/Verdi): Overordnet dokument, Eier, Godkjenning, Kontraktsgrunnlag, Kilde, Status, Versjon."""
        self.tabell(['Felt', 'Verdi'], rader, [0.15, 0.85], 'blue')

    def lagre(self, sti):
        self.d.save(sti); fiks_zoom(sti)

def fiks_zoom(path):
    z = zipfile.ZipFile(path); files = {n: z.read(n) for n in z.namelist()}; z.close()
    s = files['word/settings.xml'].decode('utf-8'); s2 = re.sub(r'<w:zoom w:val="[^"]*"\s*/>', '<w:zoom w:percent="100"/>', s)
    if s2 != s:
        files['word/settings.xml'] = s2.encode('utf-8')
        with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as zo:
            for n, b in files.items(): zo.writestr(n, b)


def meta_fra_dokumentinfo(di_rader):
    """Hent metadata (nøkkel/verdi) fra toppen av arket «Dokumentinfo og forutsetninger», frem til «Formål og innhold…»."""
    ut = []
    for r in di_rader[1:]:
        a, b = (list(r) + [None, None])[:2]
        if a and str(a).startswith('Formål'): break
        if a and b: ut.append((str(a), str(b)))
    return ut


def autowidths(hode, rader, minw=0.06):
    """Fordel kolonnebredde etter innholdslengde (ca. 90. persentil per kolonne), med gulv og tak.
    Ingen kolonne blir smalere enn det lengste ordet i overskriften (unngår at «Brukertype» brytes midt i ordet)."""
    n = len(hode); lens = []
    for i in range(n):
        ls = sorted(len(S(r[i])) if i < len(r) else 0 for r in rader) or [0]
        lengste_ord = max((len(w) for w in S(hode[i]).split()), default=0)
        lens.append(max(len(S(hode[i])), ls[max(int(len(ls) * 0.9) - 1, 0)], lengste_ord + 4))
    lens = [min(max(l, 8), 60) for l in lens]; tot = sum(lens); w = [max(minw, l / tot) for l in lens]; sm = sum(w)
    return [x / sm for x in w]
