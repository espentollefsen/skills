# Standard disposisjon for HLD

Tilpass antall fagkapitler til kundens omfang, men behold strukturen. Fagkapitlene har *identisk* oppbygning slik at fagteam og godkjennere vet hvor de skal lete.

## Hoveddisposisjon
1. **Innledning**
   1.1 Begreper (kun begreper som brukes; bruk prislistens varelinjenavn)
   1.2 Formål og forhold til detaljdesign (HLD = hva/hvorfor, fryses ved godkjenning; LLD/vedlegg = hvordan/verdier)
   1.3 Omfang og avgrensning (tabell: område → hva HLD fastsetter → kapittel)
   1.4 Vedlegg (liste: filnavn – hva det inneholder – eier – godkjenningspunkt)
2. **Overordnet arkitektur og topologi** (2.1 målbilde per område i en setning hver, 2.2 topologiskisse = Figur 1, 2.3 designprinsipper)
3. **Applikasjonsmiljø**
4. **Identitet og tilgang (IAM)**
5. **Lisensiering**
6. **Nettverk** (6.1 arkitektur + Figur 2, 6.2 segmentering og sikkerhet, 6.3 …)
7. **Workplace** (klienter, mobil, møterom, print, utstyr)
8. **Sikkerhet**
9. **Migrering og overgang** (strømmer, rekkefølge, avhengigheter til avgivende part)
10. **Roller, ansvar og drift** (RACI A/R separat; forvaltning etter overlevering)

Kapittel for områder som ligger utenfor omfang (f.eks. OT, dataplattform) skrives som avgrensning med henvisning – ikke som design.

## Mal per fagkapittel (x)
- **x.1 Formål** – hva kapitlet fastsetter, én–to setninger
- **x.2 Scope og avgrensning** – hva som inngår (grunnleveranse), hva som er opsjon (antall 0), hva som er utenfor
- **x.3 … designbeslutninger og prinsipper** – det som er valgt og hvorfor; henvis til standard
- **x.n Forutsetninger** – nummerert liste over påstander designet hviler på, hver med: hvem som bekrefter, i hvilket vedlegg. **Alle «Forutsetninger»-overskrifter skal ha samme overskriftsnivå** i hele dokumentet (feil nivå gir feil nummerering og brutte henvisninger – `hld_lint.py` sjekker dette).

## Fastlåste mønstre
- Hvert fagkapittel *sluttes* av forutsetninger; vedlegget kvitterer for dem (Bekreftes / Åpen / Avvik).
- Figurer: bildetekst på formen «Figur N: …», en kort figurbeskrivelse under, og figuren viser kun høyt nivå (se `topologifigurer`).
- Priser står aldri i HLD. Volum står aldri i HLD.
