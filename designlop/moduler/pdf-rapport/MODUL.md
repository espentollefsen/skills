---
name: pdf-rapport
description: Lager designede, lesbare PDF-rapporter (A4 liggende) av vedlegg og registre i Excel eller Word — nøkkeltallskort, fargede statusmerker, grupperte tabeller, kvitteringstabell og åpne punkter — i stedet for en rå utskrift av regnearket. Bruk når brukeren ber om en PDF av et vedlegg, regneark eller Word-dokument, vil ha en «lesekopi», «mer inspirerende», «lettere å lese» eller «presentabel» versjon, skal dele et vedlegg med ARF/styringsgruppe/kunde, eller ber om PDF av vedlegg A–F. Utløs også for «gjør dette med de andre vedleggene også».
---

# PDF-rapport

Gjør vedleggsfiler (Excel-registre og Word-vedlegg) om til rapporter folk faktisk leser. Excel/Word forblir kildefilen kunden fyller ut; PDF-en er lesekopien. Den genereres fra kilden og kan kjøres på nytt når kilden endres – rediger aldri PDF-en.

Utskrift direkte fra Excel gir smale kolonner, tekst som brytes midt i ord og ingen hierarki. Rapportformen legger på det leseren trenger: oversikt først, grupperte tabeller, statusmerker.

## Hva rapporten inneholder (og ikke)
- **Side 1:** tittel, ingress, 3–5 nøkkeltallskort (antall, fordeling), metadata-tabell (Overordnet dokument · Eier · Kontraktsgrunnlag · Godkjenning), «Formål og innhold i forhold til HLD», kvitteringstabell med statusmerker (Bekreftes grønn · Åpen amber · Avvik rød), åpne punkter.
- **Deretter:** registrene/kapitlene i kildens rekkefølge. Tabeller i Excel-vedlegg kan **grupperes** etter en kolonne (f.eks. leveransemodell) med fargelag per gruppe. Kritikalitet og klassifisering vises som fargemerker.
- **Aldri med:** Endringslogg og Godkjenning (ark/kapitler hoppes alltid over – vedlegg skal ikke ha dem). Tekniske ark kan utelates med `--hopp-over`.

Bunnteksten viser kunde · tittel · versjon/dato og sidetall. Konfidensialitetstekst tas bare med hvis du eksplisitt ber om det (`--konfidensielt "Konfidensielt"`).

## Bruk
**Excel-vedlegg**
```
python scripts/xlsx_til_pdf.py Vedlegg_A.xlsx Vedlegg_A.pdf --tittel "Vedlegg A – Applikasjoner og integrasjoner" \
  --kunde "<Kunde>" --versjon "v0.5 · 01.10.2026" --ingress "Målporteføljen …" \
  --kpi "Applikasjoner|=ANTALL:Applikasjoner|videreføres · nye · overgang|blue" \
  --kpi "Multi-tenant SaaS|=ANTALL:Applikasjoner:Leveransemodell=Multi-tenant SaaS|SSO via Entra ID|green" \
  --gruppe-ark Applikasjoner --gruppe-kolonne "Leveransemodell" --hopp-over Definisjoner
```
KPI-verdi: tekst, `=ANTALL:<ark>` (antall datarader) eller `=ANTALL:<ark>:<kolonne>=<verdi>`. Sonefarge: `blue`, `purple`, `green`, `amber`, `neutral`.

**Word-vedlegg**
```
python scripts/docx_til_pdf.py Vedlegg_D.docx Vedlegg_D.pdf --kunde "<Kunde>" --versjon "v0.2 · 01.10.2026" \
  --kpi "Brukertyper|4|User, External, Email, Resource Account|blue" …
```
Første tabell tolkes som metadata, tabell med «Status»-kolonne som kvittering.

## Arbeidsflyt
1. Kjør vedlegg-linten først (`vedlegg-bygger/scripts/vedlegg_lint.py`) – rapporten skal ikke skjule regelbrudd.
2. Velg 3–5 nøkkeltall som sier noe (ikke bare «antall rader»): fordeling etter status, antall åpne punkter, antall som krever ny avtale.
3. Kjør skriptet. **Se på resultatet:** `pdftoppm -r 40 -png rapport.pdf side` og kikk på 2–3 sider. Sjekk at ingen tekst er avkuttet, at tabellene har fornuftige bredder, og at nøkkeltallene stemmer med kilden.
4. Ved mange vedlegg: bruk samme KPI-struktur og farger på tvers, så pakken ser enhetlig ut.
5. Husk å regenerere PDF-ene når kildefilene endres (og når vedleggene har fått nye felt).

## Tilpasning
Trenger du noe skriptene ikke gjør (f.eks. en figur i rapporten, egne kolonnebredder), importer `scripts/rapport_lib.py` og bygg en spesialrapport: `kpi_row`, `table`, `pill`, `bullets`, `bygg`. Se `references/tilpasning.md`.

## Samme look i Word
`scripts/rapport_docx_lib.py` lager Word-rapporter (A4 liggende) i samme stil som PDF-ene: nøkkeltallskort, navy tabellhoder med sebrastriper, statusmerker, fargelag per kapittel, bunntekst med sidetall. Ekte Word-struktur (Heading 1/2 i navigasjonsruten, topprad som gjentas ved sideskift, rader som ikke deles).
```python
import sys; sys.path.insert(0, '<skill>/scripts')
from rapport_docx_lib import *
R = Rapport('Vedlegg X – Tittel', 'Kunde · Vedlegg X · v0.1 · Intility – Konfidensielt')
R.kicker('Kunde'); R.tittel('Vedlegg X – Tittel'); R.ingress('…')
R.kpi([('Antall', 40, 'undertekst', 'blue'), …]); R.meta([('Eier', '…'), ('Godkjenning', '…')])
R.h1('Kvittering av HLD-forutsetninger'); R.tabell(['Forutsetning', 'Status', 'Merknad'], rader, [0.46, 0.09, 0.45], status_kol=(1,))
R.lagre('Vedlegg_X.docx')   # validér med docx-skillens validate.py og se på sidene
```
Celleverdier kan være tekst, `Pill(tekst, farge)` eller `Rich([...])` (flere linjer/stiler). `statuspill()` gjør statusord til merker og **beholder lang statustekst** (merke først, resten under). Hold tabelltekst ren – ikke legg inn skjulte tegn (f.eks. hardt mellomrom) for å polstre merker; andre skript leser statusene tilbake fra filen. Avstandsavsnitt rett før en overskrift med sideskift fjernes automatisk (unngår blanke sider). Når et Word-vedlegg skal bli PDF: `docx_til_pdf.py` hopper over nøkkeltallskortene (enrads tabeller).

## Beslektede skills
`vedlegg-bygger` (lager kildefilene), `topologifigurer` (figurer, inkl. PDF av figurer), `kommentarlop`.
