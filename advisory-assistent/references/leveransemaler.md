# Leveransemaler

Faste strukturer for Advisory-leveranser. Bruk malen som ramme – tilpass omfang til oppgaven, men behold rekkefølgen og seksjonsnavnene slik at leveranser blir gjenkjennelige.

## Valg av format

- **Chat-svar**: avklaringer, raske vurderinger, idéutkast.
- **HTML-artifact (Bifrost-stil)**: interaktive verktøy, trackere, kalkulatorer, beslutningsguider.
- **Word (.docx)**: formelle kundeleveranser – løsningsdesign, rådgivningsnotat, tilbudsunderlag. Bruk docx-skillen.
- **PowerPoint (.pptx)**: kundemøter og styringsgrupper. Bruk skillen intility-powerpoint-instructions.
- **Excel (.xlsx)**: kostnadsestimater og ressurslister. Bruk azure-cost-estimator-skillen for kostnadsarbeidsbøker.

## Mal: Løsningsdesign (kunderettet)

```
# Løsningsdesign – [workload/system] for [kunde]
## 1. Sammendrag og anbefaling        (maks ½ side, konklusjon først)
## 2. Bakgrunn og behov
## 3. Målarkitektur                   (diagram + beskrivelse per komponent)
## 4. Nettverk og sikkerhet           (PE, DNS, ruting, identitet – eksplisitt per tjeneste)
## 5. ESLZ-kvalifisering              (kvalifisert / med avvik / ikke – jf. eslz-standarder.md)
## 6. Drift og forvaltning            (overvåkning, backup, ansvarsdeling Intility/kunde)
## 7. Kostnadsestimat                 (Lav/Medium/Høy, NOK + USD, referer forutsetninger)
## 8. Neste steg                      (konkrete, tidfestede punkter med ansvarlig)
Vedlegg: ressursliste, antagelser, avvik
```

## Mal: Rådgivningsnotat (kort kunderettet vurdering)

```
# [Tema] – vurdering og anbefaling
**Til:** [kunde/rolle]  **Fra:** Intility Advisory  **Dato:** [dato]
## Anbefaling                         (1–3 setninger, først)
## Vurdering                          (alternativer med fordeler/ulemper)
## Konsekvenser                       (kost, drift, sikkerhet, tid)
## Neste steg
```
Maks 2 sider. Alternativvurderinger som tabell: Alternativ | Fordeler | Ulemper | Kostnadsbilde | Anbefalt.

## Mal: Workshopoppsummering

```
# Oppsummering – [workshop] [dato]
## Deltakere
## Beslutninger                       (nummerert – kun reelle beslutninger)
## Åpne punkter                       (punkt | ansvarlig | frist)
## Hovedpunkter fra diskusjonen       (kort, tematisk)
## Neste steg
```

## Mal: Statusrapport (engasjement)

```
# Status – [engasjement] uke [nr]
## Overordnet status: 🟢/🟡/🔴 + én setning
## Fremdrift siden sist
## Risiko og blokkere                 (med tiltak)
## Beslutninger som trengs fra kunden
## Plan neste periode
```

## Mal: Tilbudsunderlag / pre-salg

```
# [Tjeneste/leveranse] for [kunde]
## Forstått behov                     (vis at vi har forstått – speil kundens språk)
## Foreslått løsning                  (arkitektur på konseptnivå, ikke detaljdesign)
## Leveransemodell                    (faser, roller, Intility/kunde-ansvar)
## Estimat                            (timer/kost med forutsetninger, tre scenarier ved usikkerhet)
## Forutsetninger og avgrensninger
```

## Mal: Møteforberedelse (internt til brukeren)

```
## Mål med møtet                      (hva skal vi oppnå / få besluttet)
## Status og kontekst                 (3–5 kulepunkter)
## Sannsynlige spørsmål fra kunden    (med foreslåtte svar)
## Det vi trenger fra dem
## Fallgruver / ting å unngå
```
Dette er internt – vær direkte og ærlig, inkludert om svakheter i eget forslag.

## Generelle regler for leveranser

- Konklusjon/anbefaling alltid først.
- Tall har alltid kilde og forutsetninger (pricing-API-dato, valutakurs, SKU).
- Diagrammer refereres i teksten og har komponentnummer som matcher beskrivelsen.
- Åpne punkter har alltid ansvarlig og frist – ellers er de ikke åpne punkter, men støy.
