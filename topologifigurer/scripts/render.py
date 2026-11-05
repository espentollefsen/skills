#!/usr/bin/env python3
"""Render SVG-figurer til PNG (til Word) og/eller en A4-liggende PDF (én figur per side, vektor).
  python render.py figur1.svg figur2.svg --png-mappe ut/ --pdf ut/figurer_A4_liggende.pdf [--png-bredde 2700]"""
import argparse, io, os, re
import cairosvg
from pypdf import PdfWriter, PdfReader, Transformation

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('svg', nargs='+'); ap.add_argument('--png-mappe'); ap.add_argument('--pdf'); ap.add_argument('--png-bredde', type=int, default=2700)
    a = ap.parse_args()
    if a.png_mappe:
        os.makedirs(a.png_mappe, exist_ok=True)
        for s in a.svg:
            ut = os.path.join(a.png_mappe, os.path.splitext(os.path.basename(s))[0] + '.png'); cairosvg.svg2png(url=s, write_to=ut, output_width=a.png_bredde); print('PNG', ut)
    if a.pdf:
        PW, PH, M = 842, 595, 20; w = PdfWriter()
        for s in a.svg:
            txt = open(s, encoding='utf-8').read(); vb = re.search(r'viewBox="0 0 (\d+) (\d+)"', txt); bw, bh = int(vb.group(1)), int(vb.group(2))
            sc = min((PW - 2 * M) / bw, (PH - 2 * M) / bh)
            pdf = cairosvg.svg2pdf(bytestring=txt.encode('utf-8'), output_width=bw * sc / 0.75, output_height=bh * sc / 0.75)
            src = PdfReader(io.BytesIO(pdf)).pages[0]; sw, sh = float(src.mediabox.width), float(src.mediabox.height)
            pg = w.add_blank_page(width=PW, height=PH); pg.merge_transformed_page(src, Transformation().translate((PW - sw) / 2, (PH - sh) / 2))
        with open(a.pdf, 'wb') as fh: w.write(fh)
        print('PDF', a.pdf)

if __name__ == '__main__': main()
