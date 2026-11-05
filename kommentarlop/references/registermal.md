# Registermal

## JSON til `lag_register.py`
```json
{"tittel": "Identitetskommentarer – HLD og Vedlegg D",
 "undertittel": "Gjennomgang av åpne kommentarer fra <fagteam> med forslag · Intility Advisory · <dato> · Ingen endringer gjennomført",
 "intro": "Hva registeret bygger på: dokumentversjoner, antall kommentarer, hva som er nytt siden sist.",
 "avklaringer": [["Tittel", "Hva må avklares før endring, og av hvem"]],
 "seksjoner": [
   {"overskrift": "Løsningsdesign – HLD", "fagperson": "Monica Fritzøe",
    "rader": [{"nr": "41", "sted": "2.1 Identitet", "original": "teksten i dokumentet", "kommentar": "kommentaren ordrett (inkl. svar i tråden)",
               "forslag": "ordrett ny tekst, eller «Ingen endring» + begrunnelse", "kilde": "henvisning + merknad", "revisjon": ""}]},
   {"overskrift": "Vedlegg D – Identitet", "fagperson": "kilde", "rader": [ ... ]}],
 "folgeendringer": ["Vedlegg E kap. 3: ...", "Figur 2: ..."]}
```

## Radinnhold – kvalitetskrav
- **nr**: kommentar-ID(er), f.eks. «89 / 90» for kommentar + svar. For rader uten kommentar (konsekvens): «–».
- **sted**: kapittelnummer + overskrift (fra `ekstraher.py`: feltet `sted`).
- **original**: avsnittet slik det står (feltet `avsnitt`) – så leseren ikke trenger å åpne dokumentet.
- **kommentar**: ordrett, inkl. svar («Svar: …»).
- **forslag**: ordrett tekst som kan limes inn. Ved flere endringer i samme rad, nummerer dem.
- **kilde**: henvisning (Bilag 7 Vedlegg 7.2 ark 4; Vedlegg 2.3 kap. 9.6.2) + eventuell kontraktsmerknad («Dette avviker fra tilbudet – PL må vite»).
- **revisjon**: tom for HLD-rader. For vedleggsrader kan «Godkjent – konsekvens av HLD #nn» forhåndsutfylles når raden er en ren konsekvens av en godkjent HLD-rad (se beslutningsmonstre.md).

## Avklaringer (øverst)
Kort liste over det brukeren må avgjøre eller få avklart *før* endring: kontraktskonflikter, ting bare kunden/PL kan svare, og ting du ikke vet. Ikke gjem dem i radene.

## Følgeendringer (nederst)
Kort liste per dokument: «Vedlegg A: Standard Online → SSO ja», «Figur 1: fjern boks X». Det er sjekklisten brukeren bruker for å se at ingenting blir glemt.

## Versjoner
Når kommentarene eller dokumentene endrer seg (nye kommentarer, renummerering), bygg registeret på nytt og kall det v2/v3 — behold brukerens tidligere revisjonskommentarer ved å lese dem tilbake med `les_register.py` og sette dem inn i `revisjon`.
