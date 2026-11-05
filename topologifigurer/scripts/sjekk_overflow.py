#!/usr/bin/env python3
"""Finn tekst som går ut av boksen den ligger i, i en SVG. Kjør alltid før figuren leveres.
  python sjekk_overflow.py figur.svg [--slingring 6]
Måler tekstbredde med Liberation Sans (samme font som rendringen). Rettelse: kort ned teksten (ikke krymp fonten) eller utvid boksen."""
import re, sys, glob
from lxml import etree
from PIL import ImageFont

def font(bold, size):
    f = glob.glob('/usr/share/fonts/**/LiberationSans-%s.ttf' % ('Bold' if bold else 'Regular'), recursive=True)[0]
    return ImageFont.truetype(f, int(round(size * 4)))  # 4x for presisjon

def klasser(root):
    css = ''.join(e.text or '' for e in root.iter('{http://www.w3.org/2000/svg}style')); out = {}
    for m in re.finditer(r'\.(\w+)\{([^}]*)\}', css):
        d = dict(kv.split(':', 1) for kv in m.group(2).split(';') if ':' in kv); out[m.group(1)] = d
    return out

def main():
    path = sys.argv[1]; slingring = float(sys.argv[sys.argv.index('--slingring') + 1]) if '--slingring' in sys.argv else 6
    root = etree.parse(path).getroot(); ns = '{http://www.w3.org/2000/svg}'; kl = klasser(root)
    rects = [(float(r.get('x')), float(r.get('y')), float(r.get('width')), float(r.get('height'))) for r in root.iter(ns + 'rect') if r.get('width') not in (None,) and float(r.get('width')) < float(root.get('width')) - 5]
    funn = 0
    for t in root.iter(ns + 'text'):
        x, y = float(t.get('x')), float(t.get('y')); s = ''.join(t.itertext())
        d = dict(kl.get(t.get('class', '').split()[0] if t.get('class') else '', {}))
        for kv in (t.get('style') or '').split(';'):
            if ':' in kv: a, b = kv.split(':', 1); d[a.strip()] = b.strip()
        if t.get('font-size'): d['font-size'] = t.get('font-size') + 'px'
        if t.get('font-weight'): d['font-weight'] = t.get('font-weight')
        size = float(d.get('font-size', '12').replace('px', '')); bold = d.get('font-weight') == 'bold'
        w = font(bold, size).getlength(s) / 4
        if d.get('text-anchor') == 'middle': x0, x1 = x - w / 2, x + w / 2
        else: x0, x1 = x, x + w
        inn = [r for r in rects if r[0] <= x <= r[0] + r[2] and r[1] <= y <= r[1] + r[3]]
        if not inn: continue
        r = min(inn, key=lambda r: r[2] * r[3])  # minste omsluttende boks
        if x1 > r[0] + r[2] - slingring + 0 or x0 < r[0]:
            funn += 1; print(f'OVERFLOW  "{s[:70]}"  tekst slutter x={x1:.0f}, boksen slutter x={r[0]+r[2]:.0f}  (mangler {x1-(r[0]+r[2])+slingring:.0f}px)')
    print(f'{funn} tekstlinjer går ut av bokser.' if funn else 'OK – ingen tekst går ut av bokser.')
    sys.exit(1 if funn else 0)

if __name__ == '__main__': main()
