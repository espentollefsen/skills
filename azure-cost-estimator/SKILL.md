---
name: azure-cost-estimator
description: >
  Kalkulerer Azure-kostnader for arkitekturer med støtte for ESLZ/ALZ-modus.
  Bruk denne skillen når brukeren ønsker kostnadskalkulator, prisestimat, kostnadsanalyse eller budsjettering
  for Azure-ressurser – spesielt når det nevnes ESLZ, enterprise scale, landing zone, private endpoint,
  VNet-integrasjon, hub-spoke, eller Intility-arkitektur. Skillen henter offisielle priser fra Azure
  Retail Pricing API, verifiserer SKU-kapabiliteter mot Microsoft Learn MCP, håndterer NOK-konvertering,
  og produserer tre scenarier (Lav/Medium/Høy) basert på faktisk dokumentert SKU-støtte.
  Bruk alltid denne fremfor å gjette priser eller kapabiliteter fra treningsdatasettet.
  Trigger også når brukeren deler et arkitekturdiagram og spør om kostnader, eller ber om Excel-rapport
  over Azure-kostnader.
---

# Azure Cost Estimator

Denne skillen gir deg et strukturert rammeverk for å kalkulere Azure-kostnader korrekt, med
offisielle priser fra Azure Retail Pricing API og faktabasert SKU-veiledning hentet direkte
fra Microsoft Learn.

## Grunnprinsipper

**Fakta over hukommelse.** Stol aldri på innbakt kunnskap om SKU-kapabiliteter eller timepriser –
begge endres jevnlig. Slå alltid opp begge deler fra primærkildene (Azure Pricing API og Microsoft Learn MCP).

**Informer, ikke forby.** Skillen sin oppgave er å presentere *hva som er mulig* per SKU basert på
dokumentert fakta, slik at brukeren kan ta et informert valg. Kalkylen speiler det valgte scenariet.

---

## Arbeidsflyt steg for steg

### Steg 0 – Avklar ESLZ/ALZ-kvalifisering (alltid første spørsmål)

Still alltid dette spørsmålet før du gjør noe annet:

> "Skal løsningen kvalifisere til Enterprise Scale Landing Zone (ESLZ/ALZ)?"

Svaret bestemmer hvilke kapabiliteter som er relevante å undersøke i Steg 2:
- **Ja → ESLZ-modus**: Kapabilitetene Private Endpoint og VNet-integrasjon er avgjørende.
  Løsningen bør også vurdere zone-redundans og HA der det er tilgjengelig.
- **Nei → Standard-modus**: Velg SKU-er basert på funksjonelle behov og kostnad.
  Kapabilitetene er fortsatt nyttige å kjenne til, men er ikke styrende for valget.

### Steg 1 – Identifiser ressurser

Les arkitekturdiagrammet eller brukerbeskrivelsen og list opp alle ressurser.
Still avklarende spørsmål ved behov:
- Er VPN Gateway / Firewall Intility-delt (ekskluderes fra kundens kalkyle)?
- Hvilken region? (standard: **norwayeast**)
- Windows eller Linux for App Service / Functions?

Merk: Appout-subnet er et egress-subnet for utgående trafikk fra Web App og Functions –
ikke en egen appserver. Ikke regn det som en separat ressurs.

### Steg 2 – Slå opp kapabiliteter per SKU via Microsoft Learn

For **hver tjeneste** i kalkylen, fastslå hvilke SKU-er som støtter de kapabilitetene
som er relevante for scenariet. Dokumenter alltid kilden.

**Primær kilde: Microsoft Learn MCP**
Bruk Microsoft Learn MCP-verktøyet for oppslag. Eksempler på søk:
```
"Azure App Service VNet integration regional supported pricing tiers"
"Azure Database for PostgreSQL Flexible Server private endpoint tier requirements"
"Azure Functions Premium plan private endpoint VNet integration"
"Azure Front Door Premium private endpoint origin support"
"Azure Key Vault private endpoint support tiers"
```

**Dersom Microsoft Learn MCP er utilgjengelig:**
Bruk `web_fetch` direkte mot `https://learn.microsoft.com` – dette er den **eneste** tillatte
kilden for kapabilitetsinformasjon. Det er **ikke tillatt** å søke eller hente informasjon fra
andre nettsider, blogger, tredjepartskilder eller generell websøk.
Konstruer URL-en manuelt basert på tjenestenavn, f.eks.:
```
https://learn.microsoft.com/azure/app-service/overview-vnet-integration
https://learn.microsoft.com/azure/postgresql/flexible-server/concepts-networking-private
https://learn.microsoft.com/azure/azure-functions/functions-networking-options
https://learn.microsoft.com/azure/firewall/overview
```

Relevante kapabiliteter å undersøke (tilpass etter tjeneste og modus):
- **Private Endpoint** – støttes av hvilke tiers/SKU-er?
- **VNet-integrasjon** – støttes av hvilke tiers/SKU-er?
- **Zone-redundans** – støttes av hvilke tiers/SKU-er?
- **Høy tilgjengelighet / replika** – støttes av hvilke tiers/SKU-er?

Resultatet fra Microsoft Learn brukes til å bygge en kapabilitetstabell per tjeneste:

| SKU / Tier | Private Endpoint | VNet-integrasjon | Zone-redundans | Kilde |
|---|---|---|---|---|
| (fylles ut fra MS Learn) | | | | |

Denne tabellen er grunnlaget for scenario-byggingen i Steg 4.

### Steg 3 – Hent offisielle priser fra Azure Retail Pricing API

For hver aktuell SKU, hent pris via HTTP:

```
GET https://prices.azure.com/api/retail/prices?api-version=2023-01-01-preview
    &$filter=serviceName eq '<tjeneste>' and armRegionName eq '<region>' and currencyCode eq 'USD'
```

Standard region: **norwayeast**. Standard kalkulasjonsgrunnlag: **730 timer/mnd**.

Logg `meterName` og `retailPrice` (USD/time) for hver SKU du inkluderer.
Månedskostnad = `retailPrice × 730`.

Typiske filtre for vanlige tjenester:
```
serviceName eq 'Azure Firewall' and armRegionName eq 'norwayeast'
serviceName eq 'Azure App Service' and armRegionName eq 'norwayeast'
serviceName eq 'Azure Database for PostgreSQL' and armRegionName eq 'norwayeast'
serviceName eq 'Azure Functions' and armRegionName eq 'norwayeast'
serviceName eq 'Azure Front Door and CDN Profiles' and armRegionName eq 'norwayeast'
```

### Steg 4 – Bygg tre scenarier

Bruk kapabilitetstabellen fra Steg 2 til å velge SKU-er for hvert nivå.
I ESLZ-modus: velg laveste SKU som faktisk støtter Private Endpoint og VNet-integrasjon
(ifølge Microsoft Learn). I Standard-modus: velg laveste SKU som dekker funksjonelt behov.

**Lav:** Laveste kvalifiserende SKU per tjeneste, 1 instans, minimal trafikk
**Medium:** Produksjonskonfigurasjon med moderat last, HA på database
**Høy:** Full redundans, zone-redundant der støttet, høy gjennomstrømming

### Steg 5 – Konverter til NOK

Hent dagens USD/NOK-kurs via web_search. Oppgi alltid kurs, dato og kilde.

### Steg 6 – Presenter resultatene

Bygg alltid en interaktiv HTML-widget (via `show_widget`) og tilby Excel-eksport ved behov.

#### Widget-spesifikasjon

```
Layout:
┌─────────────────────────────────────────────────┐
│  [ESLZ-modus ✓]  eller  [Standard-modus]  badge │
│  Region: Norway East  |  Kurs: X,XX NOK/USD      │
├──────────────────────────────────────────────────┤
│  [ Lav ]  [ Medium ]  [ Høy ]   ← aktiv tab      │
├──────────────────────────────────────────────────┤
│  Månedlig NOK   Månedlig USD   Årlig NOK          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ XX XXX   │  │  X XXX   │  │ XXX XXX  │        │
│  └──────────┘  └──────────┘  └──────────┘        │
├──────────────────────────────────────────────────┤
│ Ressurs │ SKU │ Kapabiliteter │ USD/mnd │ NOK/mnd │
│ ...     │ ... │ PE ✓  VNet ✓  │   XX    │   XXX   │
│ (ekskl.)│ –   │ Delt hub      │    –    │    –    │
├──────────────────────────────────────────────────┤
│  ✓ API-pris  ✓ MS Learn-verifisert               │
│  Kurs: X,XX NOK/USD  |  Kilde: ...  |  Dato: ... │
└──────────────────────────────────────────────────┘
```

Tekniske krav til widgeten:
- Tre tab-knapper (Lav / Medium / Høy) som bytter innhold uten sidereload
- Sammendragskortene oppdateres automatisk ved tab-bytte
- Kapabilitet-kolonnen viser kompakte badges: `PE ✓` / `PE ✗`, `VNet ✓` / `VNet ✗`
- Rader med ekskluderte ressurser (f.eks. Firewall i delt hub) vises nedtonet med forklaring
- Badge "✓ API-pris" på rader der pris er hentet fra Azure Pricing API
- Badge "✓ MS Learn" der kapabilitet er bekreftet via Microsoft Learn
- ESLZ-modus-badge er grønn, Standard-modus-badge er grå
- Kursinfo, kilde og dato alltid synlig nederst

Tilby Excel-eksport ved behov (se under).

---

## Excel-eksport

Når brukeren ber om Excel, lag en `.xlsx` med:
- **Forutsetninger-fane**: USD/NOK-kurs, timer/mnd (730), MS Learn-kildereferanser
- **Scenario-faner** (én per nivå): Ressurser med SKU, kapabiliteter, USD og NOK per mnd og år
  - Blå tekst = hardkodede inputverdier (USD/mnd per ressurs)
  - Sort tekst = Excel-formler (NOK = USD × kurs, år = mnd × 12)
  - Grønn bakgrunn = API-verifisert pris
- **Sammenligning-fane**: Alle tre scenarier side om side med betinget fargeformatering
- Ingen formelfeil (#REF!, #DIV/0! etc.)
- Kjør alltid `recalc.py` etter generering

---

## Kostnadsfeller å informere om

**Azure Firewall** – Dersom løsningen inkluderer Azure Firewall, still følgende avklaringsspørsmål
før du kalkulerer eller slår opp SKU-er:
- Er Firewall delt i Intility sin connectivity-hub (og dermed ekskludert fra kundens kalkyle)?
- Hvilke features trengs? (f.eks. IDPS, TLS-inspeksjon, URL-filtrering, Web Categories)
  → Svarene avgjør om Basic, Standard eller Premium er riktig tier – slå opp kapabilitetene
  per tier via Microsoft Learn MCP før du anbefaler noe.

**Azure Functions** – Consumption-planen støtter ikke Private Endpoint eller VNet-integrasjon
ifølge Microsoft Learn. Verifiser alltid dette for aktuell tjeneste og region.

**Appout-subnet** er et egress-subnet, ikke en egen appserver.

---

## Referansefiler

- `references/common-resources.md` – Typiske ressurser i standard Intility ESLZ-arkitektur

Merk: Ingen hardkodet SKU-liste vedlikeholdes i denne skillen. Kapabiliteter hentes alltid
fra Microsoft Learn MCP for å sikre at informasjonen er oppdatert.
