"""Hjelpefunksjoner for å lese Word-kommentarer med anker, overskriftskontekst og trådstruktur (uten Word)."""
import re, zipfile
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
W14 = 'http://schemas.microsoft.com/office/word/2010/wordml'
W15 = 'http://schemas.microsoft.com/office/word/2012/wordml'
def w(t): return '{%s}%s' % (W, t)
def w14(t): return '{%s}%s' % (W14, t)
def w15(t): return '{%s}%s' % (W15, t)

def ptekst(p):
    return ''.join(t.text or '' for t in p.iter(w('t')))

def les_kommentarer(path):
    """Returnerer liste med dicts: id, forfatter, dato, tekst, paraId, ferdig, forelder (id eller None), anker, avsnitt, sted."""
    z = zipfile.ZipFile(path)
    if 'word/comments.xml' not in z.namelist(): return []
    cr = etree.fromstring(z.read('word/comments.xml'))
    ext = etree.fromstring(z.read('word/commentsExtended.xml')) if 'word/commentsExtended.xml' in z.namelist() else None
    doc = etree.fromstring(z.read('word/document.xml'))
    # kommentarer
    k = {}; pid2id = {}
    for c in cr.findall(w('comment')):
        cid = int(c.get(w('id'))); paras = c.findall(w('p'))
        tekst = '\n'.join(t for t in (ptekst(p).strip() for p in paras) if t)
        pids = [p.get(w14('paraId')) for p in paras if p.get(w14('paraId'))]
        for pid in pids: pid2id[pid] = cid
        k[cid] = dict(id=cid, forfatter=c.get(w('author')) or '', dato=(c.get(w('date')) or '')[:10], tekst=tekst, paraId=pids[-1] if pids else None,
                      ferdig=False, forelder=None, anker='', avsnitt='', sted='')
    if ext is not None:
        for e in ext.findall(w15('commentEx')):
            pid = e.get(w15('paraId')); cid = pid2id.get(pid)
            if cid is None: continue
            if e.get(w15('done')) == '1': k[cid]['ferdig'] = True
            par = e.get(w15('paraIdParent'))
            if par and par in pid2id: k[cid]['forelder'] = pid2id[par]
    # anker + overskriftskontekst (nummerering av Heading1-3 i dokumentrekkefølge)
    nr = [0, 0, 0]; overskrift = ''; apne = {}; tekster = {}
    for el in doc.iter():
        if el.tag == w('p'):
            ps = el.find(w('pPr')); st = ps.find(w('pStyle')).get(w('val')) if ps is not None and ps.find(w('pStyle')) is not None else ''
            m = re.fullmatch(r'(?i)heading\s*([1-3])', st or '')
            if m:
                n = int(m.group(1)); nr[n - 1] += 1
                for i in range(n, 3): nr[i] = 0
                overskrift = '.'.join(str(x) for x in nr[:n] if x) + ' ' + ptekst(el).strip()
        elif el.tag == w('commentRangeStart'):
            cid = int(el.get(w('id'))); apne[cid] = True; tekster[cid] = []
            if cid in k:
                p = el.getparent()
                while p is not None and p.tag != w('p'): p = p.getparent()
                k[cid]['avsnitt'] = ptekst(p).strip() if p is not None else ''; k[cid]['sted'] = overskrift
        elif el.tag == w('commentRangeEnd'):
            apne.pop(int(el.get(w('id'))), None)
        elif el.tag == w('t'):
            for cid in list(apne): tekster[cid].append(el.text or '')
    for cid, ts in tekster.items():
        if cid in k: k[cid]['anker'] = ''.join(ts).strip()
    return [k[i] for i in sorted(k)]

def fiks_zoom(path):
    """python-docx sin standardmal har <w:zoom w:val="bestFit"/> uten w:percent, som feiler skjemavalidering. Rett opp i fila."""
    import shutil, tempfile, os
    z = zipfile.ZipFile(path); files = {n: z.read(n) for n in z.namelist()}; z.close()
    if 'word/settings.xml' in files:
        s = files['word/settings.xml'].decode('utf-8')
        s2 = re.sub(r'<w:zoom w:val="[^"]*"\s*/>', '<w:zoom w:percent="100"/>', s)
        if s2 != s:
            files['word/settings.xml'] = s2.encode('utf-8')
            with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as zo:
                for n, b in files.items(): zo.writestr(n, b)
