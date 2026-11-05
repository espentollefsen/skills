---
name: hld-bygger
description: Bygger og reviderer High-Level Design (HLD / overordnet løsningsdesign) for Intility Advisory-kunder, forankret i kontrakten. Bruk denne skillen når brukeren ber om HLD, løsningsdesign, overordnet design, arkitekturdokument, å skrive eller revidere et fagkapittel (applikasjon, identitet, lisens, nettverk, workplace, sikkerhet, migrering), å sjekke et design mot tilbudssvar/prisliste/Bilag 7, å lage forutsetningskapitler, eller når kontraktsbilag (Bilag 2/4/7, tilbudssvar, etableringsplan, prisliste, tjenestebeskrivelse) skal brukes som kilde for et designdokument. Bruk den også ved spørsmål som «står dette i kontrakten?», «hva er scope?» eller «er dette opsjon?», selv om ordet HLD ikke nevnes. Stopper og legger frem begge alternativer når kontraktsdokumentene er i konflikt.
---

# HLD-bygger

Skriver og kvalitetssikrer overordnet løsningsdesign (HLD) slik Intility Advisory jobber: kontraktsforankret, med tydelig skille mellom det som er avtalt og det som er Intilitys egne forslag, og uten detaljer som endrer seg etter godkjenning.

Metoden bygger på en lang praksisrunde der de fleste feilene kom fra tre kilder: påstander uten kilde fremstilt som besluttet, tilbudstekst som lovet mer enn prislisten dekket, og tall/detaljer i HLD som egentlig hørte hjemme i vedlegg. Reglene under finnes for å hindre akkurat det.

## Slik fordeler arbeidet seg
Omtrent 60–70 % av et HLD er standardisert: kapittelstruktur, forutsetnings- og kvitteringsmekanikk, henvisninger til tjenestebeskrivelsen, begrepsliste. Det kan du skrive effektivt. De siste 30–40 % er **konfliktavgjørelser**: tilbud mot prisliste, kundens forventning mot priset volum, fagteamets praksis mot avtaletekst. Der skal du *ikke* velge selv. Du legger frem alternativene, og et menneske velger (se «Stopp ved konflikt»).

## Parametre du må kjenne før du skriver
Spør hvis noe ikke er gitt:
- **Kunde** og kundens egne arkitekturkrav/rammeverk (kan være under revisjon – si det i teksten, ikke anta).
- **Kontraktsstruktur.** I SSA-D-avtaler er normalt Bilag 2 = løsning/tjenester (Vedlegg 2.1 kravsvar, 2.2 utfyllende svar, 2.3 tjenestebeskrivelse), Bilag 4 = gjennomføring/etablering, Bilag 7 = pris (Vedlegg 7.1 volumforutsetninger, 7.2 prisliste), Bilag 9 = endringer. Verifiser mot de faktiske filene; ikke bruk nummereringen blindt.
- **Fagteam og eiere** (hvem eier hvilket kapittel/vedlegg).
- **Vedleggsstruktur** (ett vedlegg per fagområde, eller ett referansedokument med registre – se vedlegg-bygger).
- **Språk** (norsk som standard).

## Arbeidsflyt
1. **Inventar av kilder.** List alt du har: tilbudssvar/kravsvar, utfyllende svar, etableringsplan, prisliste, tjenestebeskrivelse, kundens underlag, og live registre via MCP (f.eks. IntIpaas – se `references/registre-mcp.md`). Les dem *før* du skriver. Når du sier at noe «ikke står i kontrakten», si hvilke kilder du faktisk har lest og hvilke du ikke har (typisk hovedavtalens løpende tekst).
2. **Kjør konfliktsjekken.** `python scripts/opsjon_sjekk.py prisliste.xlsx --tilbud <tilbudstekst> --tilbud <tjenestebeskrivelse>` lister tjenester som er opsjon/antall 0 i prislisten og finner steder der tilbud eller tjenestebeskrivelse likevel lover dem. Les hver treff selv og avgjør hva som er reell konflikt.
3. **Stopp ved konflikt** (under). Fortsett gjerne med kapitler som ikke berøres, men skriv ikke konfliktpunktene før brukeren har valgt.
4. **Disposisjon.** Bruk `references/kapittelstruktur.md`.
5. **Skriv kapittel for kapittel** etter reglene under og `references/formuleringer.md`. Gi hvert fagkapittel et eget forutsetningskapittel (se `references/hld-vs-lld.md`).
6. **Lint.** `python scripts/hld_lint.py hld.docx --kilde etableringsplan.txt --forbudt "<ord prosjektet har strøket>"` fanger kryssreferanser til kapitler som ikke finnes, forutsetningskapitler på ulikt nivå, tall med volumord, «besluttet» uten kilde, og datoer som ikke finnes i kildene. Rett funnene eller forklar hvorfor de er riktige.
7. **Lever** med en kort oppsummering: hva som er kontraktsforankret, hva som er egen vurdering, og hvilke konflikter som venter på valg.

Skal et *eksisterende* HLD endres etter fagteamenes kommentarer, bruk skillen `kommentarlop` – den gjennomfører endringer med sporbar endringslogg.

## Kildeklasser – det viktigste
Hver påstand tilhører nøyaktig én klasse. Avgjør klassen *før* du formulerer setningen:

| Klasse | Eksempel på kilde | Slik skrives den |
|---|---|---|
| **Kontrakt** | Bilag/vedlegg med henvisning | Fakta, med henvisning (Bilag 7 Vedlegg 7.2; Vedlegg 2.2 kap. 6) |
| **Tjenestestandard** | Tjenestebeskrivelsen | Henvis; ikke skriv ut standarden på nytt |
| **Prosjektunderlag** | Kundens dokumenter, fagteamenes input, registre | Fakta med kilde, merk dato/versjon |
| **Egen vurdering** | Din anbefaling | Alltid «Intility foreslår/anbefaler …» eller «fastsettes av Kunden i Vedlegg X» – aldri som fakta |

Dikt aldri kilder. Verktøy, standarder og produktnavn du ikke finner i en kilde (i denne metoden ble «Ardoq» og «IEC 62443» funnet som oppdiktede referanser) fjernes eller merkes som usikre. Fullstendig veiledning og feilmønstre: `references/kildedisiplin.md`.

## Prislisten er scope
Når tilbudstekst, tjenestebeskrivelse og prisliste er uenige, er prislisten med «antall 0 = opsjon» scope-bestemmende. Kapabiliteter tilbudsteksten lover (likeverdig macOS-støtte, mikrosegmentering, sikker utskrift) betyr ikke at de er bestilt. Skriv aldri en opsjon som om den inngår. Der prislisten er stille om noe tilbudet lover, er det en konflikt – ikke en feil du løser selv.

## HLD sier hva og hvorfor – ikke verdier
Test på hver setning: *bytter vi verdien i vedlegget, er HLD fortsatt riktig?* Hvis ja, lå verdien riktig. Hvis ikke, løft den til HLD (som prinsipp) eller til endringsregimet (Bilag 9). Konsekvenser:
- **Ingen volumtall i HLD** (40 servere, 10 SaaS, 5 møterom). Skriv «etter avtalens prismodell» og la registeret bære tallet. Tall er prisgrunnlag, ikke design.
- **Standard henvises, ikke beskrives.** Leverer Intility det likt til alle kunder, står bare henvisningen til tjenestebeskrivelsen. Bare det Lunera-spesifikke dokumenteres.
- HLD fryses ved godkjenning. Det som kan endre seg etterpå, hører hjemme i vedlegg.

## Stopp ved konflikt
Finner du en konflikt mellom kontraktsdokumentene (typisk tilbudstekst vs. prisliste, tjenestekatalog vs. tilbud, plan vs. dokumentert dato, volum i ulike ark):
1. **Stopp** skrivingen av det punktet.
2. Lag en konfliktrapport etter `references/konfliktrapport.md`: hva hvert dokument sier (med henvisning), alternativ A og B, konsekvens av hvert (kontrakt, pris, hvem må involveres), og hva du anbefaler hvis brukeren ber om det.
3. **Vent på brukerens valg.** Gjenbruk aldri et tidligere valg på et nytt punkt, og løs det ikke «forsiktig» i teksten med mindre brukeren ber om det.
4. Dokumenter valget (kilde: brukerens svar) i teksten som «avtalt/besluttet av [rolle] [dato]», ikke som egen vurdering.

## Skrivestil (kortversjon)
- Norsk, saklig, presens. Ingen «alltid», «aldri», «besluttet» uten henvisning til beslutningen.
- Ansvar skrives med A og R adskilt (Accountable/Responsible). «Forvaltes hos Intility» sier ingenting uten hva. Bruk navngitte parter, ikke «tredjepart» uten å si hvem.
- Bruk prislistens varelinjenavn for tjenester (Managed Network Location, Managed Workforce …). Egne betegnelser defineres i begrepslisten eller utgår.
- Skille mellom «inngår» (grunnleveranse), «opsjon» (antall 0) og «foreslått» (egen vurdering).
- Oppgi eksplisitt det som er uavklart: ÅP-numrert åpent punkt med eier – ikke et åpent spørsmål i brødteksten.

## Referanser (les ved behov)
- `references/kapittelstruktur.md` – standard disposisjon og mal per fagkapittel
- `references/kildedisiplin.md` – kildeklasser, feilmønstre, eksempler på riktig/feil
- `references/hld-vs-lld.md` – grensen mot vedlegg, forutsetninger og kvittering, Bilag 9
- `references/konfliktrapport.md` – mal og konflikttyper
- `references/formuleringer.md` – før/etter-eksempler, ansvarsspråk, terminologi
- `references/registre-mcp.md` – bruk av live registre (IntIpaas e.l.) som kilde
- `scripts/opsjon_sjekk.py`, `scripts/hld_lint.py`

Beslektede skills: `vedlegg-bygger` (vedleggene som realiserer HLD), `kommentarlop` (endre HLD etter kommentarer), `topologifigurer` (figurene i HLD), `pdf-rapport` (lesekopier).
