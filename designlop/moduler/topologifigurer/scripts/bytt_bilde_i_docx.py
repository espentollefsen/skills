#!/usr/bin/env python3
"""Bytt et innebygd bilde i en docx med ny PNG, og behold bredden (høyden justeres etter nytt sideforhold).

  python bytt_bilde_i_docx.py dok.docx --liste                 # vis hvilke bilder som er brukt, med størrelse og nærmeste tekst
  python bytt_bilde_i_docx.py dok.docx --media image3.png --med ny.png --ut dok_ny.docx

Viktig: mediefilnavn (image3.png) er IKKE figurnummer. Bruk --liste og se hvilken tekst bildet står ved før du bytter."""
import argparse, re, sys, zipfile
from lxml import etree
from PIL import Image
import io

NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main', 'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
      'a': 'http://schemas.openxmlformats.org/drawingml/2006/main', 'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
      'pic': 'http://schemas.openxmlformats.org/drawingml/2006/picture'}

def lesrels(z):
    rels = etree.fromstring(z.read('word/_rels/document.xml.rels'))
    return {r.get('Id'): r.get('Target') for r in rels}

def liste(path):
    z = zipfile.ZipFile(path); rels = lesrels(z); doc = etree.fromstring(z.read('word/document.xml'))
    for dr in doc.iter('{%s}drawing' % NS['w']):
        blip = dr.find('.//a:blip', NS)
        if blip is None: continue
        t = rels.get(blip.get('{%s}embed' % NS['r']), '?'); ext = dr.find('.//wp:extent', NS)
        p = dr.getparent()
        while p is not None and p.tag != '{%s}p' % NS['w']: p = p.getparent()
        før = ''
        if p is not None:
            prev = p.getprevious(); etter = p.getnext()
            før = ''.join(x.text or '' for x in (prev.iter('{%s}t' % NS['w']) if prev is not None else []))[:50]
            etter_t = ''.join(x.text or '' for x in (etter.iter('{%s}t' % NS['w']) if etter is not None else []))[:60]
        print(f'{t:22s} {int(ext.get("cx"))/360000:.1f}x{int(ext.get("cy"))/360000:.1f} cm   før: «{før}»  etter: «{etter_t}»')

def bytt(path, media, ny, ut):
    z = zipfile.ZipFile(path); files = {n: z.read(n) for n in z.namelist()}; rels = lesrels(z)
    mål = 'media/' + media
    rid = next((k for k, v in rels.items() if v == mål), None)
    if rid is None: sys.exit(f'Fant ikke {mål} i dokumentet. Bruk --liste.')
    w, h = Image.open(ny).size; data = open(ny, 'rb').read()
    files['word/' + mål] = data
    doc = etree.fromstring(files['word/document.xml']); endret = 0
    for dr in doc.iter('{%s}drawing' % NS['w']):
        blip = dr.find('.//a:blip', NS)
        if blip is not None and blip.get('{%s}embed' % NS['r']) == rid:
            ext = dr.find('.//wp:extent', NS); cx = int(ext.get('cx')); cy = int(cx * h / w); ext.set('cy', str(cy))
            for e in dr.iter('{%s}ext' % NS['a']):
                if e.get('cx'): e.set('cx', str(cx)); e.set('cy', str(cy))
            endret += 1
    files['word/document.xml'] = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', standalone=True)
    with zipfile.ZipFile(ut, 'w', zipfile.ZIP_DEFLATED) as zo:
        for n, b in files.items(): zo.writestr(n, b)
    print(f'Byttet {media} ({endret} forekomst(er)); størrelsesforhold {w}x{h} → {ut}')

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('docx'); ap.add_argument('--liste', action='store_true'); ap.add_argument('--media'); ap.add_argument('--med'); ap.add_argument('--ut'); a = ap.parse_args()
    if a.liste: liste(a.docx)
    else:
        if not (a.media and a.med and a.ut): sys.exit(__doc__)
        bytt(a.docx, a.media, a.med, a.ut)
