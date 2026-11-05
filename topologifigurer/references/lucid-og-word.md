# Lucid, Word og eksport

## Lucid
- SVG kan importeres til Lucid (verktøy som konverterer SVG → Lucidchart). Formene kommer inn redigerbare og med samme innhold.
- Lucid gjør linjer til **connectors** som festes til former og rutes automatisk. Konsekvenser: tegnforklaringens linjeprøver havner over tekst, enkelte linjer rutes gjennom bokser, linjeetiketter flytter seg. Figurer med blokkpiler og uten linjer påvirkes mindre – men sjekk eksporten.
- Eksport fra Lucid til PNG/PDF gir ofte en bred hvit ramme rundt tegneflaten.
- **Anbefaling:** SVG forblir master, Lucid er speil (importer på nytt etter hver endring) – med mindre fagteamene skal redigere direkte; da blir Lucid master og SVG-kildene foreldet. Velg én, og si det.

## Lucid-tillegget for Word
Word-tillegget «Lucidchart Diagrams for Word» setter inn et diagram som bilde med kobling til Lucid-dokumentet; «Oppdater» henter ny versjon. Ikke en levende kobling. Krav: tillegget er tillatt i organisasjonens M365, og alle som oppdaterer har Lucid-tilgang. Risiko for frosne dokumenter: noen kan trykke Oppdater etter godkjenning. Når HLD fryses: konverter til vanlig bilde eller lås Lucid-dokumentet. Ikke bland tillegget med skript som bytter bilder i docx (koblingen går tapt uten at man merker det).

## Eksport av ferdige figurer
- PNG til Word: 2700 px bredde er nok til skarp visning på tekstbredde.
- PDF til deling: `render.py --pdf` (A4 liggende, vektor, 20 pt marg).
- Behold SVG-filene sammen med dokumentpakken – de er kilden.
