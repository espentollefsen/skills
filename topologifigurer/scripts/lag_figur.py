#!/usr/bin/env python3
"""Generer en topologifigur (SVG) i Bifrost-inspirert stil fra en JSON-spec.

  python lag_figur.py spec.json figur.svg

Figurene er på HØYT NIVÅ: soner, bokser med korte tekstlinjer og korte blokkpiler i mellomrommene mellom sonene.
Ingen detaljerte forbindelseslinjer. Se ../references/stil.md og ../assets/eksempel_spec.json.
"""
import json, sys
from xml.sax.saxutils import escape as esc

CSS = """
  .zt{font-size:17px;font-weight:bold;fill:#17325C}
  .t{font-size:13px;font-weight:bold;fill:#17325C}
  .s{font-size:11.5px;fill:#4F6079}
  .tw{font-size:13px;font-weight:bold;fill:#FFFFFF}
  .sw{font-size:11.5px;fill:#DCE6F2}
  .ba{fill:#9FB3CF;stroke:none}
"""
ZONER = {  # fyll, kant, tittelfarge
    'blue': ('#EAF0FB', '#2F6FED', '#17325C'), 'purple': ('#F1EDFB', '#7B5BE6', '#17325C'), 'green': ('#EAF7F0', '#2EAD63', '#17325C'),
    'navy': ('#17325C', 'none', '#FFFFFF'), 'neutral': ('#F3F6FA', '#B9C7DE', '#17325C'), 'amber': ('#FFF6E3', '#D9941E', '#17325C')}
BOKSER = {  # fyll, kant, dash, mørk tekst?
    'box': ('#FFFFFF', '#C9D3E0', None, False), 'ot': ('#EAF8EF', '#2EAD63', None, False), 'dmz': ('#FFF6E3', '#D9941E', None, False),
    'dark': ('#0F2A47', '#8FB0F2', None, True), 'dashed': ('#FFFFFF', '#8FA3BF', '5 4', False), 'tr': ('#FFF2F0', '#E2574C', '6 4', False)}

def rect(x, y, b, h, fill, stroke, rx=10, dash=None, sw=1.2):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<rect x="{x}" y="{y}" width="{b}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'

def blokkpil(retning, x, y1, y2, skaft=12, hode=28, hh=14):
    """Kort blokkpil. ned/opp: x er senterlinje, y1 start, y2 spiss. hoyre/venstre: y er senterlinje (parameter x=y), y1=x start, y2=x spiss."""
    s, h = skaft / 2, hode / 2
    if retning == 'ned':
        yb = y2 - hh; return f'<path class="ba" d="M{x-s},{y1} L{x+s},{y1} L{x+s},{yb} L{x+h},{yb} L{x},{y2} L{x-h},{yb} L{x-s},{yb} Z"/>'
    if retning == 'opp':
        yb = y2 + hh; return f'<path class="ba" d="M{x-s},{y1} L{x+s},{y1} L{x+s},{yb} L{x+h},{yb} L{x},{y2} L{x-h},{yb} L{x-s},{yb} Z"/>'
    y = x; xs, xe = y1, y2
    if retning == 'hoyre':
        xb = xe - hh; return f'<path class="ba" d="M{xs},{y-s} L{xb},{y-s} L{xb},{y-h} L{xe},{y} L{xb},{y+h} L{xb},{y+s} L{xs},{y+s} Z"/>'
    xb = xe + hh; return f'<path class="ba" d="M{xs},{y-s} L{xb},{y-s} L{xb},{y-h} L{xe},{y} L{xb},{y+h} L{xb},{y+s} L{xs},{y+s} Z"/>'

def tekst(x, y, s, klasse, stil=''):
    st = f' style="{stil}"' if stil else ''
    return f'<text x="{x}" y="{y}" class="{klasse}"{st}>{esc(s)}</text>'

def boks(b):
    fyll, kant, dash, mork = BOKSER[b.get('type', 'box')]
    out = [rect(b['x'], b['y'], b['b'], b['h'], fyll, kant, 10, dash)]
    tk, lk = ('tw', 'sw') if mork else ('t', 's')
    fs = b.get('skriftstr'); stil = f'font-size:{fs}px' if fs else ''
    if b.get('tittel'): out.append(tekst(b['x'] + 12, b['y'] + 19, b['tittel'], tk))
    y0 = b['y'] + (36 if b.get('tittel') else 20)
    for i, l in enumerate(b.get('linjer', [])):
        out.append(tekst(b['x'] + 12, y0 + 16 * i, l, lk, stil))
    return out

def sone(z):
    fyll, kant, tfarge = ZONER[z.get('farge', 'neutral')]
    out = [rect(z['x'], z['y'], z['b'], z['h'], fyll, kant, 14, None, 1.2)]
    if z.get('tittel'): out.append(tekst(z['x'] + 12, z['y'] + 22, z['tittel'], 'zt', f'fill:{tfarge}'))
    for b in z.get('bokser', []): out += boks(b)
    for n in z.get('notater', []): out.append(tekst(n['x'], n['y'], n['tekst'], 's', 'font-weight:bold' if n.get('fet') else ''))
    return out

def stripe(s):
    out = [rect(s['x'], s['y'], s['b'], s['h'], '#0F2A47', '#8FB0F2', 10, None, 1)]
    cx = s['x'] + s['b'] / 2
    out.append(tekst(cx, s['y'] + 25, s['tittel'], 'tw', 'text-anchor:middle'))
    out.append(f'<line x1="{s["x"]+14}" y1="{s["y"]+37}" x2="{s["x"]+s["b"]-14}" y2="{s["y"]+37}" stroke="#8FB0F2" stroke-opacity="0.6"/>')
    y = s['y'] + 62
    for sek in s.get('seksjoner', []):
        out.append(tekst(s['x'] + 14, y, sek['overskrift'], 'tw', 'font-size:12.5px')); y += 17
        for l in sek['linjer']: out.append(tekst(s['x'] + 14, y, l, 'sw')); y += 16
        y += 14
    return out

def tegnforklaring(t):
    out = [rect(t['x'], t['y'], t['b'], t['h'], '#F3F6FA', '#B9C7DE', 14, None, 1.2)]
    out.append(tekst(t['x'] + 12, t['y'] + 22, t.get('tittel', 'Tegnforklaring'), 'zt'))
    y = t['y'] + 46
    for f in t.get('farger', []):
        fyll, kant, dash, _ = BOKSER[f['type']]
        out.append(rect(t['x'] + 14, y - 11, 16, 14, fyll, kant, 4, dash)); out.append(tekst(t['x'] + 38, y, f['tekst'], 's')); y += 20
    for l in t.get('linjer', []):
        out.append(tekst(t['x'] + 14, y, '• ' + l, 's')); y += 20
    return out

def bygg(spec):
    B, H = spec.get('bredde', 1800), spec.get('hoyde', 1000)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {B} {H}" width="{B}" height="{H}" font-family="Liberation Sans, Arial, sans-serif">',
         f'<style>{CSS}</style>', f'<rect width="{B}" height="{H}" fill="#FFFFFF"/>',
         f'<text x="30" y="34" font-size="20" font-weight="bold" fill="#17325C">{esc(spec["tittel"])}</text>']
    for z in spec.get('soner', []): o += sone(z)
    if spec.get('stripe'): o += stripe(spec['stripe'])
    for p in spec.get('piler', []): o.append(blokkpil(p['retning'], p['x'], p['y1'], p['y2']))
    if spec.get('tegnforklaring'): o += tegnforklaring(spec['tegnforklaring'])
    o.append('</svg>')
    return '\n'.join(o)

if __name__ == '__main__':
    if len(sys.argv) != 3: sys.exit(__doc__)
    spec = json.load(open(sys.argv[1], encoding='utf-8'))
    open(sys.argv[2], 'w', encoding='utf-8').write(bygg(spec)); print('Skrev', sys.argv[2])
