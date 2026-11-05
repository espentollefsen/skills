---
name: "vedlegg-bygger"
description: Bygger detaljdesign-vedlegg (LLD) som realiserer et HLD — Excel-registre (applikasjoner, lisenser, nettverksenheter, IP-plan) og Word-vedlegg (identitet, workplace, migrering/cutover), med «Formål og innhold i forhold til HLD», kvitteringstabell mot HLD-forutsetninger, ÅP-nummererte åpne punkter og «Fastsettes i Fase 1»-plassholdere. Bruk når brukeren ber om vedlegg, detaljdesign, LLD, register, «Vedlegg A–F», kvitteringstabell, åpne punkter, å oppdatere et vedlegg mot et register (IntIpaas e.l.), å velge mellom ett vedlegg per fagområde og ett referansedokument med registre, eller å kontrollere at et vedlegg følger reglene. Utløs også når noen sier «lag et dokument med verdier for X» til et HLD.
---

# Vedlegg-bygger

Lager vedleggene som gir verdiene HLD-en ikke skal inneholde. Hvert vedlegg er kontraktsforankret, kvitterer for HLD-ens forutsetninger, og er bygget slik at det kan oppdateres og lastes inn i kundens CMDB/forvaltningsplattform senere.

## Reglene (og hvorfor)
1. **«Formål og innhold i forhold til HLD»** er første innhold i alle vedlegg: hvilket HLD-kapittel vedlegget detaljerer, hva HLD fastsetter som vedlegget realiserer, hva vedlegget inneholder, og hvor/hvordan det godkjennes. Uten det vet leseren ikke hva som er avtalt og hva som er detalj.
   **Metadata-tabellen øverst er lik i alle vedlegg**: nøyaktig fire felt i fast rekkefølge – **Overordnet dokument · Eier · Kontraktsgrunnlag · Godkjenning**. *Eier er alltid én relevant avdeling* («Intility Network», «Intility IAM», «Intility Workplace», «Intility Applications», «Intility FinOps & Licenses»), aldri en person eller rolle. Ikke ta med Kilde, Status eller Versjon i tabellen: versjon og dato står i bunnteksten, kilde hører hjemme i innholdsavsnittet, og status i kvitteringen og åpne punkter. Bunnteksten har ingen konfidensialitetstekst med mindre kunden ber om det.

2. **Kvitteringstabell** (HLD-forutsetning → Bekreftes / Åpen / Avvik → merknad). Dette er koblingen til HLD; en forutsetning uten kvittering er et hull.
3. **Åpne punkter** med ID `ÅP-<bokstav>-nn` (f.eks. ÅP-D-03), type (beslutning / kartlegging / Bilag 9 / avhengighet / parkert) og eier. Bruk prefiks som ikke kolliderer med andre ID-serier (flyt-ID F04 vs. åpent punkt F-01 skapte forveksling; derfor `ÅP-` foran). Generer ID-ene – ikke skriv dem for hånd og ikke prefiks to ganger.
4. **Aldri Endringslogg og Godkjenning** som ark eller kapitler. Endringslogg bæres av HLD-kommentarene; sporbarhet for vedlegg hører ikke hjemme i vedlegget. Metadatafeltet «Godkjenning» (hvem/når) er innhold og skal stå.
5. **«Fastsettes i Fase 1»** som ensartet plassholder for verdier kartleggingen skal gi. Ett vokabular i hele pakken (ikke blandet med «Fastsettes i detaljdesign»).
6. **Standard henvises, ikke skrives ut.** Dokumenter bare det som er kunde-spesifikt, med henvisning til tjenestebeskrivelsen for resten (se vurderingen i HLD-bygger: leverer Intility det likt til alle?).
7. **Ingen priser.** Priser står i prislisten. Volum fra prislisten føres som «prisgrunnlag»; faktisk antall som «bekreftet». Avvik over prisgrunnlaget er volumendring, ikke designendring.
8. **Prisliste før tilbudstekst.** Opsjon/antall 0 er ikke inkludert. Konflikter legges frem for brukeren (se `hld-bygger`: Stopp ved konflikt) – vedlegget skriver ikke en opsjon som om den var bestilt.
9. **Forslag er merket forslag.** Egen anbefaling (UPN-standard, go/no-go-kriterier, verktøyvalg) står som «Intility foreslår …» eller «forslag – bekreftes av [part]».

## Excel eller Word?
- **Excel** når innholdet er rader som vokser, filtreres, fylles ut av flere og senere lastes inn i et register: applikasjoner og flyter, lisenser og volumer, enheter og linjer, IP-plan.
- **Word** når innholdet er beslutninger med begrunnelse som kunden skal godkjenne: identitet (Conditional Access-valg, JML), workplace (klientvalg, innrullering), migrering (strømmer, cutover, go/no-go).
- Mange vedlegg er begge deler: registeret i Excel, beslutningene i Word. Splitt hellere enn å presse begrunnelser inn i celler ingen leser.

## Arbeidsflyt
1. **Les HLD-kapitlet og forutsetningene** vedlegget skal kvittere for. Hent kilder: prisliste (volum), tjenestebeskrivelse, kundens underlag, og live register via MCP hvis det finnes (hent hele registeret, sammenlign med forrige uttak).
2. **Bestem format** (over) og eventuelt **struktur** – ett vedlegg per fagområde eller et referansedokument med registre (`references/alternativ-a-b.md`). Spør ikke om dette er avgjort; legg frem begge nøytralt hvis det ikke er det.
3. **Skriv spec (JSON)** etter `references/vedlegg-mal.md`. Kjør:
   - Excel: `python scripts/bygg_vedlegg_xlsx.py spec.json Vedlegg_X.xlsx`, deretter `python /mnt/skills/public/xlsx/scripts/recalc.py Vedlegg_X.xlsx` hvis arket har formler.
   - Word: `python scripts/bygg_vedlegg_docx.py spec.json Vedlegg_X.docx`, valider med docx-skillens `validate.py`.
4. **Lint:** `python scripts/vedlegg_lint.py Vedlegg_X.xlsx|docx`. Må gi 0 feil.
5. **Oppdater, ikke bygg om**, når vedlegget finnes fra før og et register har endret seg: endre celler/avsnitt, behold struktur, og forklar endringene i svaret (ikke i vedlegget). Kolonner formler teller på endres ikke; ny informasjon får ny kolonne.
6. **Lesekopi:** lag PDF med skillen `pdf-rapport`.
7. **Lever** med: hva som er nytt, hvilke åpne punkter som oppsto, og hvilke registeravvik eieren må rette.

## Fra kommentarløpet
Når fagteamene har kommentert HLD-en, følger vedleggsforslagene HLD-beslutningene. Rader som er rene konsekvenser av en godkjent HLD-endring kan godkjennes samlet; rader der du må velge form (struktur på en tabell, formulering av et åpent punkt) legges frem. Se `kommentarlop`.

## Referanser
- `references/vedlegg-mal.md` – spec-felt, innhold i hvert vedleggstype, plassholdere
- `references/alternativ-a-b.md` – de to LLD-strukturene og hvordan de presenteres
- `scripts/bygg_vedlegg_xlsx.py`, `scripts/bygg_vedlegg_docx.py`, `scripts/vedlegg_lint.py`
- Testdata: `evals/files/vedlegg_a_spec.json`, `evals/files/vedlegg_d_spec.json`
