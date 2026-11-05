# Vedleggsmal

## Felles blokker (alle vedlegg, i denne rekkefølgen)
1. **Tittel + metadata-tabell** (lik i alle vedlegg, nøyaktig disse fire feltene i denne rekkefølgen): **Overordnet dokument** (HLD-kapittel), **Eier** (én avdeling, ikke person: «Intility Network»), **Kontraktsgrunnlag** (bilag/vedlegg/kravkoder), **Godkjenning** (hvem og når). Ingen Kilde/Status/Versjon i tabellen; ingen egen endringslogg.
2. **Formål og innhold i forhold til HLD** – to avsnitt:
   - *Formål*: «Vedlegget detaljerer HLD kap. N (…) og …. HLD-en fastsetter [prinsipper/valg]; dette vedlegget gir [verdier/lister/beslutninger]».
   - *Innhold*: «Innhold: kvittering av forutsetningene i HLD N.n; …(opplist); …. [Priser gjentas ikke.] Godkjennes av Kunden [når].»
3. **Kvittering av HLD-forutsetninger** – tabell med tre kolonner.
4. (Fagkapitler/ark)
5. **Åpne punkter og Bilag 9-kandidater** – ID, punkt, type, eier.
(Definisjoner som siste ark i Excel-vedlegg der begrepene trenger forklaring.)

## Spec – Excel (`bygg_vedlegg_xlsx.py`)
Se skriptets docstring og `evals/files/vedlegg_a_spec.json`. Feltene: `tittel, meta[[nøkkel,verdi]], formal[2 avsnitt], kvittering[[forutsetning,status,merknad]], apne_punkter{prefiks,rader[[punkt,type,eier]]}, registre[{navn,kolonner,rader,bredder,frys}], definisjoner, oppsummering[[etikett,verdi/formel]]`.
- Ark 1 = «Dokumentinfo og forutsetninger» (genereres). Deretter oppsummering (valgfritt, med formler), registre, definisjoner.
- Formler i oppsummeringen skal telle på kolonner som ikke endrer vokabular senere (livssyklus, leveransemodell). Ny info → ny kolonne.

## Spec – Word (`bygg_vedlegg_docx.py`)
Se skriptets docstring og `evals/files/vedlegg_d_spec.json`. Kapitler nummereres automatisk fra 3 (1 = Formål, 2 = Kvittering, siste = Åpne punkter). Blokktyper: `avsnitt`, `tabell`, `punkter`, `underkapittel`.

## Innhold per vanlig vedleggstype (som utgangspunkt – tilpass til HLD)
**Applikasjoner og integrasjoner (Excel)** – ark: Applikasjoner (livssyklusstatus, anskaffelsesstatus, leveransemodell, plassering, SaaS Management, kritikalitet, identitet/tilgang, forvaltningsnivå, systemeier, merknad, avtaleeier), Integrasjoner (kilde, mål, innhold, type, klassifisering, kritikalitet, realisering på plattformen, merknad), Oppsummering (formler), Definisjoner. Kilde: register. Systemeier fylles av kunden – blokkerer ofte andre vedlegg (SSO-godkjenning, funksjonstest) og bør løftes som åpent punkt.
**Lisens (Excel)** – ark: Oppsummering (lisensmodell), Volumer (prisgrunnlag | bekreftet | kilde), Microsoft-lisenser, tjenester med lisensavhengighet (opsjoner som ikke er lisenser), Tredjepartslisenser (avtaleeier, ny avtale for kunden?, registrert i forvaltningsplattformen). 
**Nettverk (Excel)** – ark: Lokasjoner (enheter og linjer per lokasjon – ikke priser), Topologi/VRF og Servernett som *henvisning* til standard, IP-plan (leveres av Network), Tilknytning (Azure, avgivende part, OT, tredjeparter), Designbeslutninger (ID, beslutning, begrunnelse, status, kilde). Utstyrstilbud med priser er et eget kommersielt dokument.
**Identitet (Word)** – tenant/domener (standard henvises), brukertyper og brukermatrise, Conditional Access som kundevalg mot standard, roller i identitetsplattformen, SSO per SaaS, livssyklus (JML).
**Workplace (Word)** – klientplattform, klientapplikasjoner/pakker, mobil, møterom, print, utstyr og maskinparkanalyse, innrulleringsrutine for utstyr fra tredjepart, løpende forvaltning.
**Migrering og cutover (Word)** – rammer og milepæler, strømmer (omfang, metode/verktøy som forslag, forutsetninger, ansvarlig, testkriterium), testplan, cutover-plan med go/no-go (forslag), runbook-struktur, godkjenningsperiode. Hvem som utfører hver strøm må stå eksplisitt (avgivende part kan utføre deler).

## Kolonne- og statusvokabular (hold det lik i hele pakken)
- Kvitteringsstatus: **Bekreftes · Åpen · Avvik**
- Plassholder: **Fastsettes i Fase 1**
- Prisgrunnlag vs bekreftet antall
- Åpne punkter: type ∈ {Beslutning, Kartlegging, Bilag 9, Avhengighet, Parkert, Lukket}
