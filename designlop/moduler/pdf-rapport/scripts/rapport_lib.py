"""Felles bibliotek for lesbare PDF-rapporter (A4 liggende) i Intilitys Bifrost-inspirerte stil.
Brukes av xlsx_til_pdf.py og docx_til_pdf.py, og kan importeres direkte for spesialrapporter."""
import glob
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, ListFlowable, ListItem
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def _font(name):
    hits = glob.glob(f'/usr/share/fonts/**/{name}', recursive=True)
    if not hits:
        raise SystemExit(f'Fant ikke fonten {name}. Installer fonts-liberation eller tilpass _font().')
    return hits[0]
pdfmetrics.registerFont(TTFont('LS', _font('LiberationSans-Regular.ttf')))
pdfmetrics.registerFont(TTFont('LSB', _font('LiberationSans-Bold.ttf')))

# Palett (Bifrost-inspirert, "C-stilen"): fargelag per plattform
NAVY = colors.HexColor('#17325C'); BLUE = colors.HexColor('#2F6FED'); PURPLE = colors.HexColor('#7B5BE6')
GREEN = colors.HexColor('#2EAD63'); AMBER = colors.HexColor('#D9941E'); RED = colors.HexColor('#E2574C')
GREY = colors.HexColor('#4F6079'); LIGHT = colors.HexColor('#EEF3FA'); LINE = colors.HexColor('#C9D3E0')
Z_BLUE = colors.HexColor('#EAF0FB'); Z_PURPLE = colors.HexColor('#F1EDFB'); Z_GREEN = colors.HexColor('#EAF7F0'); Z_AMBER = colors.HexColor('#FFF6E3')
ZONES = {'blue': Z_BLUE, 'purple': Z_PURPLE, 'green': Z_GREEN, 'amber': Z_AMBER, 'neutral': LIGHT}

W = landscape(A4)[0] - 28 * mm

def style(name, font='LS', size=8.5, lead=None, color=NAVY, after=0, before=0):
    return ParagraphStyle(name, fontName=font, fontSize=size, leading=lead or size * 1.25, textColor=color, spaceAfter=after, spaceBefore=before)

H1 = style('h1', 'LSB', 22, 26, after=4); H2 = style('h2', 'LSB', 14, 18, before=6, after=6); H3 = style('h3', 'LSB', 10.5, 13, before=4, after=3)
P = style('p', size=9, lead=12, color=GREY, after=4); BODY = style('body', size=9, lead=12.5, after=5)
SM = style('sm', size=8, lead=10, color=GREY); CELL = style('cell', size=7.6, lead=9.4)
WH = style('wh', 'LSB', 7.8, 9.6, color=colors.white)
KICK = style('kick', size=10, color=GREY)

def S(x):
    return '' if x is None else str(x)

def esc(s):
    return S(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

STATUS_COLORS = {'Bekreftes': GREEN, 'Bekreftet': GREEN, 'Åpen': AMBER, 'Avvik': RED, 'Lukket': GREY, 'TBD': AMBER,
                 'Critical': RED, 'High': AMBER, 'Normal': GREEN, 'Re-etablering': GREEN, 'Uavklart': AMBER}

def pill(text, bg, fg=colors.white):
    t = Table([[Paragraph(esc(text), ParagraphStyle('pl', fontName='LSB', fontSize=7, leading=8.5, textColor=fg, alignment=1))]])
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), bg), ('ROUNDEDCORNERS', [4, 4, 4, 4]), ('LEFTPADDING', (0, 0), (-1, -1), 4),
                           ('RIGHTPADDING', (0, 0), (-1, -1), 4), ('TOPPADDING', (0, 0), (-1, -1), 1.5), ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5)]))
    return t

def smal_pill(tekst, farge):
    t = Table([[Paragraph(esc(tekst), ParagraphStyle('pls', fontName='LSB', fontSize=7, leading=8.5, textColor=colors.white, alignment=1))]], colWidths=[(len(S(tekst)) * 1.5 + 5) * mm], hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), farge), ('ROUNDEDCORNERS', [4, 4, 4, 4]), ('LEFTPADDING', (0, 0), (-1, -1), 3), ('RIGHTPADDING', (0, 0), (-1, -1), 3), ('TOPPADDING', (0, 0), (-1, -1), 1.5), ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5)]))
    return t

def status_cell(value):
    """Statusord → merke. Lang tekst beholdes: merket øverst, resten av teksten under (ingenting forkastes)."""
    s = S(value)
    for key, col in STATUS_COLORS.items():
        if s == key or s.startswith(key + ' ') or s.startswith(key + '.'):
            if len(s) <= 20: return pill(s, col)
            rest = s[len(key):].lstrip(' .–-')
            t = Table([[smal_pill(key, col)], [Paragraph(esc(rest), CELL)]], hAlign='LEFT')
            t.setStyle(TableStyle([('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (-1, -1), 0), ('TOPPADDING', (0, 0), (-1, -1), 1), ('BOTTOMPADDING', (0, 0), (-1, -1), 1)]))
            return t
    return Paragraph(esc(s), CELL)

def kpi(title, value, sub, bg=Z_BLUE, n=5):
    t = Table([[Paragraph(esc(title), style('kt', 'LSB', 8, color=GREY))],
               [Paragraph(esc(value), style('kv', 'LSB', 22, 24))],
               [Paragraph(esc(sub), SM)]], colWidths=[W / n - 6])
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), bg), ('ROUNDEDCORNERS', [8, 8, 8, 8]), ('LEFTPADDING', (0, 0), (-1, -1), 9),
                           ('RIGHTPADDING', (0, 0), (-1, -1), 9), ('TOPPADDING', (0, 0), (-1, 0), 8), ('BOTTOMPADDING', (0, -1), (-1, -1), 8)]))
    return t

def kpi_row(cards):
    """cards: liste av (tittel, verdi, undertekst, sonefarge). Returnerer en Table."""
    n = len(cards)
    row = [kpi(t, v, s, ZONES.get(z, LIGHT), n) for t, v, s, z in cards]
    return Table([row], colWidths=[W / n] * n, style=TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (-1, -1), 3), ('RIGHTPADDING', (0, 0), (-1, -1), 3)]))

def table(header, rows, widths=None, zone='neutral', bold_first=True, status_cols=()):
    n = len(header)
    widths = widths or [1 / n] * n
    data = [[Paragraph(esc(h), WH) for h in header]]
    for r in rows:
        cells = []
        for i in range(n):
            v = r[i] if i < len(r) else ''
            if i in status_cols: cells.append(status_cell(v))
            elif i == 0 and bold_first: cells.append(Paragraph(f'<b>{esc(v)}</b>', CELL))
            else: cells.append(Paragraph(esc(v), CELL))
        data.append(cells)
    t = Table(data, colWidths=[W * w for w in widths], repeatRows=1)
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), NAVY), ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, ZONES.get(zone, LIGHT)]),
                           ('LINEBELOW', (0, 0), (-1, -1), 0.4, LINE), ('VALIGN', (0, 0), (-1, -1), 'TOP'), ('TOPPADDING', (0, 0), (-1, -1), 3.5),
                           ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5), ('LEFTPADDING', (0, 0), (-1, -1), 4), ('RIGHTPADDING', (0, 0), (-1, -1), 4)]))
    return t

def bullets(items):
    return ListFlowable([ListItem(Paragraph(esc(b), BODY), leftIndent=10) for b in items], bulletType='bullet', start='•', leftIndent=12, bulletFontSize=8)

def autowidths(header, rows, minw=0.05):
    """Fordel bredde etter innholdslengde (ca. 90. persentil per kolonne), med gulv og tak."""
    n = len(header); lens = []
    for i in range(n):
        ls = sorted(len(S(r[i])) if i < len(r) else 0 for r in rows) or [0]
        lens.append(max(len(S(header[i])), ls[max(int(len(ls) * 0.9) - 1, 0)]))
    lens = [min(max(l, 6), 60) for l in lens]; tot = sum(lens)
    w = [max(minw, l / tot) for l in lens]; s = sum(w)
    return [x / s for x in w]

def bygg(path, tittel, bunntekst, story, forfatter='Intility Advisory'):
    def footer(c, d):
        c.saveState(); c.setFont('LS', 7.5); c.setFillColor(GREY)
        c.drawString(14 * mm, 7 * mm, bunntekst); c.drawRightString(landscape(A4)[0] - 14 * mm, 7 * mm, f'Side {d.page}')
        c.setStrokeColor(LINE); c.line(14 * mm, 10 * mm, landscape(A4)[0] - 14 * mm, 10 * mm); c.restoreState()
    doc = SimpleDocTemplate(path, pagesize=landscape(A4), leftMargin=14 * mm, rightMargin=14 * mm, topMargin=12 * mm, bottomMargin=12 * mm,
                            title=tittel, author=forfatter)
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
