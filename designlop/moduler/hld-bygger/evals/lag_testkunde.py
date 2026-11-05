#!/usr/bin/env python3
"""Lag den anonymiserte testkunden «Eksempel Kraft AS» (fiktiv) i en mappe. Brukes av alle fem skillenes evals.
  python lag_testkunde.py /sti/til/testkunde
Innholdet inneholder bevisst innlagte feil og konflikter som skillene skal finne:
  – tilbudstekst lover macOS og mikrosegmentering, mens prislisten har begge som opsjon med antall 0
  – etableringsplanen sier oppstartsdag 26.10.2026, mens HLD-utkastet sier 15.03.2027 med Bilag 4 som kilde
  – HLD-utkastet har foreldet henvisning «kap. 11», tall («40 servere»), ukjent verktøy («Ardoq») og «Dette er besluttet»"""
import os, sys, random, shutil
import openpyxl, docx
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'kommentarlop', 'scripts'))
from bruk_endringer import lukk_kommentarer
from docxlib import W15, w15, w14, w
from lxml import etree
import zipfile

ut = sys.argv[1]; os.makedirs(ut, exist_ok=True)
# ---------- prisliste (Bilag 7-lignende) ----------
wb = openpyxl.Workbook(); ws = wb.active; ws.title = '1. Månedlig drift'
ws.append(['Tjeneste', 'Beskrivelse', 'Enhet', 'Antall', 'Pris/mnd', 'Kommentar'])
for r in [['Managed Workforce Directory', 'Dedikert AD og Entra ID', 'fast', 1, 6000, ''], ['Managed Windows Client', 'Intune-forvaltet Windows-klient', 'bruker', 56, 210, ''],
          ['Managed Network Location', 'LAN, WiFi, SD-WAN per lokasjon', 'lokasjon', 3, 4200, ''], ['Application Management | SaaS', 'SaaS Management', 'applikasjon', 10, 45, 'Prisforutsetning; faktisk antall reguleres'],
          ['Azure Express Route (200 Mbps)', 'Privat forbindelse til Azure', 'link', 1, 3799, 'Erstatter Direct Link VPN som er flyttet til Opsjoner']]: ws.append(r)
ws2 = wb.create_sheet('4. Opsjoner'); ws2.append(['Tjeneste', 'Beskrivelse', 'Enhet', 'Antall', 'Pris/mnd', 'Kommentar'])
for r in [['Managed Mac Client', 'Mac-klient forvaltet av Intune', 'bruker', 0, 165, ''], ['Microsegmentation', 'Mikrosegmentering per applikasjon', 'EPG', 0, 221, 'Flyttet til opsjon etter revurdering av krav NVT10'],
          ['Managed Secure Print', 'Sikker utskrift (Uniflow)', 'printer', 0, 580, ''], ['Managed Azure Direct Link | VPN', 'VPN-reserve mot Azure', 'link', 0, 2044, 'Opsjon']]: ws2.append(r)
wb.save(os.path.join(ut, 'prisliste.xlsx'))
# ---------- tilbudstekst og etableringsplan ----------
open(os.path.join(ut, 'tilbud.txt'), 'w', encoding='utf-8').write("""Tilbudssvar Eksempel Kraft AS – utdrag

DA06 Klienter. Vi tilbyr likeverdig støtte for macOS-klienter og forvalter disse sammen med Windows i Intune.
NVT06 Nettverkssegmentering. Kundens nettverkstenant har støtte for mikrosegmentering ned på portnivå.
DA16 Print. Managed Print inkluderer sikker utskrift med autentisering ved printeren.
ST01 Identitet. Identity Manager er en inkludert del av tjenesten.
APP08 Lisens. Kontorbrukere lisensieres på Microsoft 365 Business Premium.
""")
open(os.path.join(ut, 'etableringsplan.txt'), 'w', encoding='utf-8').write("""Etableringsplan (Bilag 4 Vedlegg 4.1) – utdrag
Fase 1 Planlegging: milepæl «Endelig løsningsdesign godkjent» 28.08.2026.
Oppstartsdag: 26.10.2026. Fase 5 godkjenningsperiode: to måneder.
Dersom kartleggingen medfører endringer i løsningsdesignet og tilvalgene beskrevet i Bilag 2, dokumenteres dette i Bilag 9.
""")
# ---------- HLD-utkast med bevisste feil og fagteamkommentarer ----------
d = docx.Document()
d.add_heading('Løsningsdesign – Eksempel Kraft – HLD', 0)
d.add_heading('Innledning', 1)
d.add_paragraph('Dette dokumentet beskriver overordnet løsningsdesign. Endringer etter godkjenning håndteres iht. kap. 12 og Bilag 9.')
d.add_paragraph('Oppstartsdag er planlagt 15.03.2027 (Bilag 4 Vedlegg 4.1).')
d.add_heading('Identitet', 1)
d.add_heading('Identitetsplattform', 2)
p_trust = d.add_paragraph('Alle brukere forvaltes alltid hos Intility. Dette er besluttet. Det etableres ingen varig trust mot avgivende miljø.')
p_hrm = d.add_paragraph('Identitetslivssyklus styres fra HRM; automatisering via Identity Manager er en opsjon.')
d.add_heading('Forutsetninger', 2)
d.add_paragraph('Identitetsportefølje verifisert mot Ardoq-grunnlaget.')
d.add_heading('Arbeidsplass', 1)
d.add_heading('Klienter', 2)
p_mac = d.add_paragraph('Windows forvaltes i Intune. Mac forvaltes via Jamf Pro og inngår i klientleveransen.')
p_print = d.add_paragraph('Managed Print inkluderer sikker utskrift med autentisering ved printeren.')
d.add_heading('Forutsetninger', 2)
d.add_paragraph('Antall servere er 40, og det er 10 SaaS-applikasjoner under Application Management.')
d.add_heading('Nettverk', 1)
d.add_heading('Segmentering', 2)
p_seg = d.add_paragraph('Servernettet segmenteres med mikrosegmentering på portnivå, og tjenesten forutsettes bestilt.')
d.add_heading('Fremtidige opsjoner', 1)
d.add_paragraph('Opsjoner listes i kap. 11.')
tab = d.add_table(rows=2, cols=2); tab.rows[0].cells[0].text = 'Tjeneste'; tab.rows[0].cells[1].text = 'Status'; tab.rows[1].cells[0].text = 'Managed Print'; tab.rows[1].cells[1].text = 'Inngår'
def kom(p, tekst, forfatter, init):
    return d.add_comment(runs=[p.runs[0], p.runs[-1]], text=tekst, author=forfatter, initials=init)
kom(p_trust, 'Vær forsiktig med formuleringen «alltid hos Intility».', 'Monica Test / Eksempel IAM', 'MT')
k_hrm = kom(p_hrm, 'Fjern HRM inntil det er besluttet.', 'Monica Test / Eksempel IAM', 'MT')
k_svar = kom(p_hrm, 'Enig – formuleringen er foreslått fjernet.', 'Espen Test', 'ET')
kom(p_mac, 'Jamf avvikles. Mac administreres med Intune på lik linje med Windows.', 'Halvor Test / Eksempel Workplace', 'HT')
kom(p_print, 'Sikker utskrift er ikke et krav til grunnleveransen.', 'Jon Test / Eksempel Workplace', 'JT')
kom(p_seg, 'Dette er for detaljert og står ikke i vedlegget.', 'Ingrid Test / Eksempel Network', 'IT')
tmp = os.path.join(ut, '_tmp.docx'); d.save(tmp)
# normaliser (paraId + commentsExtended) og legg inn svar-tråd mellom k_hrm og k_svar
norm = os.path.join(ut, '_norm.docx'); lukk_kommentarer(tmp, norm, set())
z = zipfile.ZipFile(norm); files = {n: z.read(n) for n in z.namelist()}
cr = etree.fromstring(files['word/comments.xml']); ext = etree.fromstring(files['word/commentsExtended.xml'])
pid = {int(c.get(w('id'))): c.findall(w('p'))[-1].get(w14('paraId')) for c in cr.findall(w('comment'))}
for e in ext.findall(w15('commentEx')):
    if e.get(w15('paraId')) == pid[k_svar.comment_id]: e.set(w15('paraIdParent'), pid[k_hrm.comment_id])
files['word/commentsExtended.xml'] = etree.tostring(ext, xml_declaration=True, encoding='UTF-8', standalone=True)
with zipfile.ZipFile(os.path.join(ut, 'hld_utkast.docx'), 'w', zipfile.ZIP_DEFLATED) as zo:
    for n, b in files.items(): zo.writestr(n, b)
os.remove(tmp); os.remove(norm)
from docxlib import fiks_zoom; fiks_zoom(os.path.join(ut, 'hld_utkast.docx'))
print('Testkunde skrevet til', ut, sorted(os.listdir(ut)))
