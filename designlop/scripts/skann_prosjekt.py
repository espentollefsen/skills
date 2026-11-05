#!/usr/bin/env python3
"""Skann en mappe med prosjektfiler og si hva som finnes og hva som er naturlig neste steg, slik at du slipper å spørre om det filene allerede viser.

  python skann_prosjekt.py /sti/til/mappe [--json]

Gjenkjenner: HLD (docx, med antall kommentarer / åpne), vedlegg (xlsx/docx), kommentarregistre (docx med «Revisjonskommentar», og om noen rader er besluttet),
prisliste, tilbudssvar/kravsvar, etableringsplan, tjenestebeskrivelse, figurer (svg/png/pdf), PDF-lesekopier."""
import argparse, json, os, re, sys, zipfile
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'; W15 = 'http://schemas.microsoft.com/office/word/2012/wordml'
def w(t): return '{%s}%s' % (W, t)

def kommentarer(path):
    """Returnerer (totalt, åpne fagteamkommentarer, fagteamkommentarer). Endringslogg-kommentarer regnes ikke som fagteam."""
    try:
        z = zipfile.ZipFile(path)
        if 'word/comments.xml' not in z.namelist(): return 0, 0, 0
        cr = etree.fromstring(z.read('word/comments.xml')); forf = {}
        for c in cr.findall(w('comment')):
            ps = c.findall(w('p')); p = ps[-1].get('{http://schemas.microsoft.com/office/word/2010/wordml}paraId') or ('id' + c.get(w('id')))
            forf[p] = c.get(w('author')) or ''
        ferdig = set()
        if 'word/commentsExtended.xml' in z.namelist():
            ext = etree.fromstring(z.read('word/commentsExtended.xml'))
            ferdig = {e.get('{%s}paraId' % W15) for e in ext.findall('{%s}commentEx' % W15) if e.get('{%s}done' % W15) == '1'}
        fag = [p for p, a in forf.items() if 'endringslogg' not in a.lower()]
        return len(forf), sum(1 for p in fag if p not in ferdig), len(fag)
    except Exception:
        return 0, 0, 0

def docx_info(path):
    import docx
    d = docx.Document(path); tekst = ' '.join(p.text for p in d.paragraphs[:40])
    reg = None
    for t in d.tables:
        h = [c.text.strip() for c in t.rows[0].cells]
        if 'Revisjonskommentar' in h:
            i = h.index('Revisjonskommentar'); utfylt = sum(1 for r in t.rows[1:] if r.cells[i].text.strip()); rader = len(t.rows) - 1
            reg = (reg or [0, 0]); reg[0] += rader; reg[1] += utfylt
    return tekst, reg

def klassifiser(path):
    n = os.path.basename(path); nl = n.lower(); ext = os.path.splitext(nl)[1]
    k = dict(fil=n, sti=path, type='Annet', detalj='')
    if ext == '.docx':
        tekst, reg = docx_info(path); tot, apne, fag = kommentarer(path)
        if reg is not None: k.update(type='Kommentarregister', detalj=f'{reg[0]} rader, {reg[1]} med revisjonskommentar utfylt')
        elif nl.startswith('vedlegg'): k.update(type='Vedlegg (Word)', detalj=f'{tot} kommentarer' if tot else '')
        elif 'løsningsdesign' in nl or 'hld' in nl or 'Løsningsdesign' in tekst[:400]: k.update(type='HLD', detalj=f'{tot} kommentarer, {fag} fra fagteam, {apne} åpne fagteamkommentarer' if tot else 'ingen kommentarer')
        elif 'tjenestebeskrivelse' in nl or '2_3' in nl: k.update(type='Tjenestebeskrivelse')
        elif 'tilbud' in nl or 'kravsvar' in nl or '2_2' in nl: k.update(type='Tilbudssvar/kravsvar')
        elif 'etablering' in nl or '4_1' in nl: k.update(type='Etableringsplan')
        elif 'bilag' in nl: k.update(type='Kontraktsbilag')
    elif ext in ('.xlsx', '.xlsm'):
        import openpyxl
        try: ark = openpyxl.load_workbook(path, read_only=True).sheetnames
        except Exception: ark = []
        if any(a.lower().startswith('dokumentinfo') for a in ark): k.update(type='Vedlegg (Excel)', detalj=f'ark: {", ".join(ark[:5])}')
        elif any('opsj' in a.lower() or 'månedlig drift' in a.lower() for a in ark) or 'prisliste' in nl or '7_2' in nl: k.update(type='Prisliste', detalj=f'{len(ark)} ark')
        elif 'kravsvar' in nl or '2_1' in nl: k.update(type='Tilbudssvar/kravsvar')
        elif 'governance' in nl or 'raci' in nl or 'ansvar' in nl: k.update(type='Ansvarsmatrise (RBAC/RACI)')
        else: k.update(type='Excel (ukjent)', detalj=f'ark: {", ".join(ark[:4])}')
    elif ext in ('.txt', '.md'):
        if 'tilbud' in nl or 'kravsvar' in nl: k.update(type='Tilbudssvar/kravsvar')
        elif 'etablering' in nl or 'plan' in nl: k.update(type='Etableringsplan')
        elif 'tjenestebeskrivelse' in nl: k.update(type='Tjenestebeskrivelse')
        elif 'konflikt' in nl: k.update(type='Konfliktrapport')
    elif ext == '.pdf':
        if 'figur' in nl: k.update(type='Figur (PDF)')
        elif nl.startswith('vedlegg'): k.update(type='Vedlegg (PDF-lesekopi)')
        elif 'løsningsdesign' in nl or 'hld' in nl: k.update(type='HLD (PDF)')
        elif 'tilbud' in nl or 'bilag' in nl: k.update(type='Kontraktsbilag (PDF)')
    elif ext == '.svg': k.update(type='Figur (SVG-master)' if 'figur' in nl else 'SVG')
    elif ext in ('.png', '.jpg', '.jpeg'): k.update(type='Figur (bilde)' if 'figur' in nl else 'Bilde')
    elif ext == '.json' and 'spec' in nl: k.update(type='Spec (JSON)')
    return k

def familie(navn):
    """Fjern versjons-/datomerking slik at v2/v3 av samme register havner i samme familie."""
    n = os.path.splitext(navn)[0]
    n = re.sub(r'[_\- ]*v\d+(\.\d+)?', '', n, flags=re.I); n = re.sub(r'[_\- ]*\d{4}-\d{2}-\d{2}', '', n); n = re.sub(r'[_\- ]*(utkast|ny|final|kopi)\b', '', n, flags=re.I)
    return n.strip('_- ').lower()

def nyeste_per_familie(liste):
    ut = {}
    for f in liste:
        k = familie(f['fil'])
        if k not in ut or os.path.getmtime(f['sti']) > os.path.getmtime(ut[k]['sti']): ut[k] = f
    return list(ut.values())

def forslag(funn):
    typer = {}
    for f in funn: typer.setdefault(f['type'], []).append(f)
    s = []
    hld = typer.get('HLD', []); reg = nyeste_per_familie(typer.get('Kommentarregister', []))
    if any(re.search(r'(\d+) åpne fagteamkommentarer', f['detalj']) and int(re.search(r'(\d+) åpne fagteamkommentarer', f['detalj']).group(1)) > 0 for f in hld) and not reg: s.append(('kommentarlop', 'HLD har åpne kommentarer og det finnes ingen registre → lag kommentarregistre.'))
    bes = []; ubes = []
    for f in reg:
        m = re.search(r'(\d+) rader, (\d+) med', f['detalj'])
        if m and int(m.group(2)) > 0: bes.append((f['fil'], int(m.group(1)), int(m.group(2))))
        elif m: ubes.append(f['fil'])
    if bes: s.append(('kommentarlop', f'{len(bes)} register(e) har besluttede rader ({sum(b[2] for b in bes)} av {sum(b[1] for b in bes)}) → gjennomfør og lukk. Nyeste versjon: ' + '; '.join(b[0] for b in bes[:4]) + (' …' if len(bes) > 4 else '')))
    if ubes: s.append(('kommentarlop', f'{len(ubes)} register(e) venter på din beslutning (tom revisjonskolonne): ' + '; '.join(ubes[:4]) + (' …' if len(ubes) > 4 else '')))
    if len(typer.get('Kommentarregister', [])) > len(reg): s.append(('kommentarlop', f'{len(typer["Kommentarregister"]) - len(reg)} eldre registerversjon(er) ignorert – bare nyeste versjon per register vurderes.'))
    if typer.get('Prisliste') and (typer.get('Tilbudssvar/kravsvar') or typer.get('Tjenestebeskrivelse')): s.append(('hld-bygger', 'Prisliste og tilbud/tjenestebeskrivelse finnes → kjør konfliktsjekk (opsjon_sjekk) før HLD skrives eller revideres.'))
    if not hld and typer.get('Prisliste'): s.append(('hld-bygger', 'Ingen HLD funnet, men kontraktsfiler finnes → start med disposisjon og konfliktsjekk.'))
    ved = typer.get('Vedlegg (Excel)', []) + typer.get('Vedlegg (Word)', [])
    pdf = {f['fil'].rsplit('.', 1)[0] for f in typer.get('Vedlegg (PDF-lesekopi)', [])}
    mangler = [v['fil'] for v in ved if v['fil'].rsplit('.', 1)[0] not in pdf]
    if mangler: s.append(('pdf-rapport', f'{len(mangler)} vedlegg mangler PDF-lesekopi: ' + ', '.join(mangler[:4]) + (' …' if len(mangler) > 4 else '')))
    if ved: s.append(('vedlegg-bygger', f'{len(ved)} vedlegg finnes → kjør vedlegg_lint for å sjekke reglene (ingen Endringslogg/Godkjenning, Formål og innhold, ÅP-ID).'))
    if typer.get('Figur (SVG-master)') and not typer.get('Figur (PDF)'): s.append(('topologifigurer', 'SVG-figurer finnes uten PDF → render A4-liggende PDF.'))
    if typer.get('Figur (bilde)') and not typer.get('Figur (SVG-master)'): s.append(('topologifigurer', 'Figur finnes som bilde uten SVG-master → bygg SVG-master fra HLD-teksten.'))
    return s

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('mappe'); ap.add_argument('--json', action='store_true'); a = ap.parse_args()
    funn = []
    for rot, mapper, filer in os.walk(a.mappe):
        mapper[:] = [m for m in mapper if not m.startswith(('.', '__'))]
        for f in sorted(filer):
            if f.startswith(('.', '~$', '_')): continue
            try: funn.append(klassifiser(os.path.join(rot, f)))
            except Exception as e: funn.append(dict(fil=f, sti=os.path.join(rot, f), type='Ukjent', detalj=f'kunne ikke leses: {e}'))
    s = forslag(funn)
    if a.json: print(json.dumps(dict(filer=funn, forslag=s), ensure_ascii=False, indent=1)); return
    grupper = {}
    for f in funn: grupper.setdefault(f['type'], []).append(f)
    print(f'# Prosjektskanning: {a.mappe}  ({len(funn)} filer)\n')
    for t in sorted(grupper, key=lambda x: (x in ('Annet', 'Bilde', 'Ukjent'), x)):
        print(f'**{t}** ({len(grupper[t])})')
        for f in grupper[t][:8]: print(f'  - {f["fil"]}' + (f'  — {f["detalj"]}' if f['detalj'] else ''))
        if len(grupper[t]) > 8: print(f'  … og {len(grupper[t]) - 8} til')
    print('\n## Foreslått neste steg' if s else '\n## Ingen åpenbare neste steg utledet – spør brukeren.')
    for skill, tekst in s: print(f'- [{skill}] {tekst}')

if __name__ == '__main__': main()
