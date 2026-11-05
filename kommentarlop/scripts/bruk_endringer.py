#!/usr/bin/env python3
"""Gjennomfør godkjente endringer i et Word-dokument OG dokumenter dem som endringslogg-kommentarer, i én operasjon.

  python bruk_endringer.py inn.docx spec.json ut.docx

spec.json:
{
  "logg_forfatter": "Endringslogg (ET)", "logg_initialer": "EL",
  "grunnlag_prefiks": "Grunnlag: Kommentargjennomgang v3 (ET 01.10.2026) – ",       # settes foran hver loggtekst hvis oppgitt
  "endringer": [
    {"finn": "unik tekstbit i avsnittet", "op": "erstatt_tekst", "fra": "gammel", "til": "ny",
     "logg": "Endret: ... Grunnlag: ...", "lukker": [41, "Monica|Vær forsiktig"]},
    {"finn": "...", "op": "sett_avsnitt", "til": "hele det nye avsnittet", "logg": "..."},
    {"finn": "...", "op": "sett_inn_etter", "til": "nytt avsnitt etter det funnede", "logg": "..."},
    {"finn": "...", "op": "slett_avsnitt", "anker": "avsnitt som får loggkommentaren", "logg": "..."},
    {"finn": "...", "op": "slett_tabellrad", "anker": "avsnitt som får loggkommentaren", "logg": "..."},
    {"finn": "...", "op": "kun_logg", "logg": "Ingen endring – teksten står fordi ...", "lukker": [89, 90]}
  ]
}
«lukker» tar kommentar-ID-er (fra ekstraher.py på DENNE filen) eller «Forfatter|første tegn av teksten». Alle lukkes («Task completed»),
inkludert svar i tråden, og teksten deres legges ordrett inn i loggkommentaren som «Opprinnelig kommentar Forfatter #id (dato): «…»».
Kjører tørt og avbryter FØR noe skrives hvis et «finn» ikke gir nøyaktig ett treff."""
import argparse, copy, json, os, random, re, shutil, sys, tempfile, zipfile
from lxml import etree
import docx
from docx.text.paragraph import Paragraph
sys.path.insert(0, os.path.dirname(__file__))
from docxlib import W, W14, W15, w, w14, w15, ptekst, les_kommentarer

XML_SPACE = '{http://www.w3.org/XML/1998/namespace}space'

def alle_avsnitt(d):
    return [p for p in d.element.body.iter(w('p'))]

def finn_avsnitt(d, tekstbit, ekskluder=()):
    treff = [p for p in alle_avsnitt(d) if tekstbit in ptekst(p) and p not in ekskluder]
    if len(treff) != 1:
        vis = '\n'.join('   · ' + ptekst(p)[:110] for p in treff[:5])
        sys.exit(f'FEIL: «{tekstbit[:70]}» ga {len(treff)} treff (forventet 1).' + (f'\n{vis}' if vis else ''))
    return treff[0]

def sett_tekst(p, ny):
    """Sett avsnittstekst. Beholder første tekstløpets formatering og alle løp som bærer kommentarreferanser."""
    tekstlop = [r for r in p.findall(w('r')) if r.find(w('t')) is not None]
    if not tekstlop:
        r = etree.SubElement(p, w('r')); t = etree.SubElement(r, w('t')); tekstlop = [r]
    første = tekstlop[0]
    for t in første.findall(w('t'))[1:]: første.remove(t)
    t = første.find(w('t')); t.text = ny; t.set(XML_SPACE, 'preserve')
    for r in tekstlop[1:]:
        if r.find(w('commentReference')) is None: p.remove(r)

def uten_ankere(p):
    p = copy.deepcopy(p)
    for a in list(p.iter(w('commentRangeStart'))) + list(p.iter(w('commentRangeEnd'))): a.getparent().remove(a)
    for r in list(p.findall(w('r'))):
        if r.find(w('commentReference')) is not None: p.remove(r)
    for k in list(p.attrib):
        if 'paraId' in k or 'textId' in k: del p.attrib[k]
    return p

def los_id(spec_id, kommentarer):
    if isinstance(spec_id, int): return spec_id
    fo, _, start = str(spec_id).partition('|')
    c = [k for k in kommentarer if fo.lower() in k['forfatter'].lower() and k['tekst'].startswith(start)]
    if len(c) != 1: sys.exit(f'FEIL: «lukker»-oppføringen «{spec_id}» ga {len(c)} treff i dokumentets kommentarer.')
    return c[0]['id']

def hovedlop(inn, spec_fil, ut):
    spec = json.load(open(spec_fil, encoding='utf-8'))
    kommentarer = les_kommentarer(inn); kid = {k['id']: k for k in kommentarer}
    d = docx.Document(inn)
    forfatter = spec.get('logg_forfatter', 'Endringslogg'); init = spec.get('logg_initialer', 'EL'); pre = spec.get('grunnlag_prefiks', '')
    # 1) valider alle «finn» før noe endres
    for e in spec['endringer']:
        finn_avsnitt(d, e['finn'])
        for l in e.get('lukker', []):
            i = los_id(l, kommentarer)
            if i not in kid: sys.exit(f'FEIL: kommentar {i} finnes ikke i {inn}')
        if e.get('anker'): finn_avsnitt(d, e['anker'])
    lukk = set(); logger = []
    for e in spec['endringer']:
        p = finn_avsnitt(d, e['finn']); op = e['op']; anker = p
        if op == 'erstatt_tekst':
            t = ptekst(p)
            if e['fra'] not in t: sys.exit(f'FEIL: «{e["fra"][:60]}» finnes ikke i avsnittet «{t[:60]}»')
            sett_tekst(p, t.replace(e['fra'], e['til']))
        elif op == 'sett_avsnitt': sett_tekst(p, e['til'])
        elif op == 'sett_inn_etter':
            ny = uten_ankere(p); sett_tekst(ny, e['til']); p.addnext(ny); anker = ny
        elif op in ('slett_avsnitt', 'slett_tabellrad'):
            anker = finn_avsnitt(d, e['anker']) if e.get('anker') else (p.getprevious() if p.getprevious() is not None and p.getprevious().tag == w('p') else None)
            if anker is None: sys.exit(f'FEIL: {op} for «{e["finn"][:50]}» trenger «anker» (avsnitt som får loggkommentaren)')
            if op == 'slett_tabellrad':
                tr = p
                while tr is not None and tr.tag != w('tr'): tr = tr.getparent()
                tr.getparent().remove(tr)
            else: p.getparent().remove(p)
        elif op == 'kun_logg': pass
        else: sys.exit(f'Ukjent op: {op}')
        ids = [los_id(l, kommentarer) for l in e.get('lukker', [])]; lukk.update(ids)
        logger.append((anker, pre + e['logg'], ids))
    # 2) loggkommentarer
    for anker, tekst, ids in logger:
        lop = [r for r in Paragraph(anker, d).runs]
        if not lop: print(f'ADVARSEL: avsnittet har ingen løp; loggkommentar utelatt: {tekst[:60]}'); continue
        c = d.add_comment(runs=[lop[0], lop[-1]], text=tekst, author=forfatter, initials=init)
        for i in ids:
            k = kid[i]; c.add_paragraph(f'Opprinnelig kommentar {k["forfatter"].split(" /")[0]} #{i} ({k["dato"]}): «{k["tekst"]}»')
    tmp = ut + '.tmp'; d.save(tmp)
    lukk_kommentarer(tmp, ut, lukk); os.remove(tmp)
    from docxlib import fiks_zoom; fiks_zoom(ut)
    print(f'{len(spec["endringer"])} endringer gjennomført, {len(logger)} loggkommentarer lagt til, {len(lukk)} opprinnelige kommentarer (med svar) lukket → {ut}')

def lukk_kommentarer(inn, ut, ids):
    """Sett done=1 i commentsExtended for gitte kommentar-ID-er og alle svar i tråden. Oppretter commentsExtended ved behov."""
    zin = zipfile.ZipFile(inn); files = {n: zin.read(n) for n in zin.namelist()}
    cr = etree.fromstring(files['word/comments.xml'])
    pid2id = {}; siste = {}
    for c in cr.findall(w('comment')):
        cid = int(c.get(w('id'))); ps = c.findall(w('p')); p = ps[-1]
        if not p.get(w14('paraId')): p.set(w14('paraId'), '%08X' % random.randint(0x10000000, 0x7FFFFFFF))
        siste[cid] = p.get(w14('paraId')); pid2id[siste[cid]] = cid
        for q in ps:
            if q.get(w14('paraId')): pid2id.setdefault(q.get(w14('paraId')), cid)
    ny_ext = 'word/commentsExtended.xml' not in files
    ext = etree.fromstring(files['word/commentsExtended.xml']) if not ny_ext else etree.Element(w15('commentsEx'), nsmap={'w15': W15})
    have = {e.get(w15('paraId')): e for e in ext.findall(w15('commentEx'))}
    for cid, pid in siste.items():
        if pid not in have:
            e = etree.SubElement(ext, w15('commentEx')); e.set(w15('paraId'), pid); e.set(w15('done'), '0'); have[pid] = e
    forelder = {}
    for pid, e in have.items():
        par = e.get(w15('paraIdParent'))
        if par and pid in pid2id and par in pid2id: forelder[pid2id[pid]] = pid2id[par]
    def rot(i):
        while i in forelder: i = forelder[i]
        return i
    mål = {rot(i) for i in ids}
    for cid, pid in siste.items():
        if rot(cid) in mål: have[pid].set(w15('done'), '1')
    files['word/comments.xml'] = etree.tostring(cr, xml_declaration=True, encoding='UTF-8', standalone=True)
    files['word/commentsExtended.xml'] = etree.tostring(ext, xml_declaration=True, encoding='UTF-8', standalone=True)
    if ny_ext:
        ct = files['[Content_Types].xml'].decode('utf-8')
        if 'commentsExtended' not in ct:
            ct = ct.replace('</Types>', '<Override PartName="/word/commentsExtended.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.commentsExtended+xml"/></Types>')
            files['[Content_Types].xml'] = ct.encode('utf-8')
        rels = files['word/_rels/document.xml.rels'].decode('utf-8')
        rels = rels.replace('</Relationships>', '<Relationship Id="rIdCommentsExt" Type="http://schemas.microsoft.com/office/2011/relationships/commentsExtended" Target="commentsExtended.xml"/></Relationships>')
        files['word/_rels/document.xml.rels'] = rels.encode('utf-8')
    with zipfile.ZipFile(ut, 'w', zipfile.ZIP_DEFLATED) as zo:
        for n, b in files.items(): zo.writestr(n, b)

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('inn'); ap.add_argument('spec'); ap.add_argument('ut'); a = ap.parse_args()
    hovedlop(a.inn, a.spec, a.ut)
