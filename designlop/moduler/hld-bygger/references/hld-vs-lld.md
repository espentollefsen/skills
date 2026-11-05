# HLD mot LLD/vedlegg

## Rollefordeling
| | HLD | Vedlegg / detaljdesign (LLD) |
|---|---|---|
| Svarer på | Hva og hvorfor | Hvordan og med hvilke verdier |
| Endres | Etter formell endring (frosset ved godkjenning) | Løpende frem til godkjenning, deretter registre |
| Innhold | Målbilde, prinsipper, plattformvalg, avgrensninger, begrunnelser mot kontrakt, forutsetninger | Konfigurasjonsverdier, lister, IP-planer, policyer, runbooks, volumer |
| Standard | Henviser til tjenestebeskrivelsen | Dokumenterer kun Lunera-spesifikke avvik og beslutninger |

**Testen:** Bytter jeg en verdi i vedlegget – er HLD fortsatt riktig? Ja → verdien lå riktig. Nei → løft den til HLD som prinsipp, eller behandle den som endring (Bilag 9).

**Standard-testen:** Leverer Intility dette likt til alle kunder? Ja → det beskrives ikke, bare henvisning til tjenestebeskrivelsen og kapittel.

## Forutsetninger og kvittering
Et frosset dokument kan ikke ha åpne spørsmål. Derfor:
1. HLD stiller **forutsetninger** (i eget kapittel per fagområde) – påstander designet hviler på, med angivelse av hvem som bekrefter dem og hvor.
2. Vedlegget **kvitterer** i en tabell på første ark/kapittel 2: forutsetning → **Bekreftes** / **Åpen** / **Avvik** → merknad/hvor bekreftes.
3. Det som ikke er avgjort blir et **åpent punkt** med ID (`ÅP-<vedleggsbokstav>-nn`), type (beslutning / kartlegging / Bilag 9 / avhengighet / parkert) og eier – i vedlegget, ikke som åpent spørsmål i HLD.
4. Alle forutsetningskapitler har samme overskriftsnivå (ellers feil nummerering).

## Bilag 9 og endringsregimet
Det som endrer avtalt leveranse, volum eller pris, er en endringssak – ikke en designendring i HLD. Typiske Bilag 9-kandidater: volum over prisgrunnlaget, opsjoner som bestilles, omfangsreduksjon (en annen part utfører noe som var Intilitys), omplanlagt milepæl. Skriv i HLD «etter avtalens prismodell/endringsregime» og la saken få spor utenfor HLD (referat eller Bilag 9). HLD kan aldri selv være kilden til en omfangsendring.

## Hva som aldri skal stå i HLD
- Priser og kroner
- Volumtall (servere, brukere, subscriptions, møterom …)
- IP-planer, VLAN, konkrete regelsett, produktversjoner
- Egne anbefalinger formulert som fakta
- Beskrivelse av standardtjenester som allerede står i tjenestebeskrivelsen
