# Prising: hel arkitektur (tre scenarier)

Strukturert rammeverk for å kalkulere Azure-kostnader for en arkitektur, med offisielle priser fra Azure Retail Pricing API og faktabasert SKU-veiledning fra Microsoft Learn. For enkeltoppslag på én ressurs, bruk `prising-enkeltressurs.md` i stedet.

## Grunnprinsipper

**Fakta over hukommelse.** Stol aldri på innbakt kunnskap om SKU-kapabiliteter eller timepriser – begge endres jevnlig. Slå alltid opp begge deler fra primærkildene (Azure Pricing API og Microsoft Learn MCP).

**Informer, ikke forby.** Oppgaven er å presentere *hva som er mulig* per SKU basert på dokumentert fakta, slik at brukeren kan ta et informert valg. Kalkylen speiler det valgte scenariet.

## Arbeidsflyt steg for steg

### Steg 0 – Avklar ESLZ/ALZ-kvalifisering (alltid første spørsmål)

Still alltid dette spørsmålet før du gjør noe annet, med mindre konteksten allerede gjør svaret åpenbart (f.eks. at oppgaven eksplisitt gjelder ESLZ):

> "Skal løsningen kvalifisere til Enterprise Scale Landing Zone (ESLZ/ALZ)?"

- **Ja → ESLZ-modus**: Private Endpoint og VNet-integrasjon er avgjørende kapabiliteter. Vurder også zone-redundans og HA der tilgjengelig. Bruk sjekklisten i `eslz-standarder.md`.
- **Nei → Standard-modus**: Velg SKU-er basert på funksjonelle behov og kostnad.

### Steg 1 – Identifiser ressurser

Les arkitekturdiagrammet eller brukerbeskrivelsen og list opp alle ressurser. Avklar ved behov:
- Er VPN Gateway / Firewall Intility-delt (ekskluderes fra kundens kalkyle)?
- Hvilken region? (standard: **norwayeast**)
- Windows eller Linux for App Service / Functions?

Merk: Appout-subnet er et egress-subnet for utgående trafikk fra Web App og Functions – ikke en egen appserver. Ikke regn det som en separat ressurs.

### Steg 2 – Slå opp kapabiliteter per SKU via Microsoft Learn

For **hver tjeneste**, fastslå hvilke SKU-er som støtter de relevante kapabilitetene. Dokumenter kilden. Eksempler på søk i Microsoft Learn MCP:
```
"Azure App Service VNet integration regional supported pricing tiers"
"Azure Database for PostgreSQL Flexible Server private endpoint tier requirements"
"Azure Functions Premium plan private endpoint VNet integration"
"Azure Front Door Premium private endpoint origin support"
```

Dersom Learn MCP er utilgjengelig: bruk `web_fetch` direkte mot `https://learn.microsoft.com` – dette er den **eneste** tillatte kilden for kapabilitetsinformasjon. Ikke bruk blogger, tredjepartskilder eller generelt websøk.

Bygg en kapabilitetstabell per tjeneste:

| SKU / Tier | Private Endpoint | VNet-integrasjon | Zone-redundans | Kilde |
|---|---|---|---|---|

### Steg 3 – Hent offisielle priser fra Azure Retail Pricing API

```
GET https://prices.azure.com/api/retail/prices?api-version=2023-01-01-preview
    &$filter=serviceName eq '<tjeneste>' and armRegionName eq '<region>' and currencyCode eq 'USD'
```

Standard region: **norwayeast**. Kalkulasjonsgrunnlag: **730 timer/mnd**. Logg `meterName` og `retailPrice` per SKU. Månedskostnad = `retailPrice × 730`. Lagringspriser er ofte per GB/mnd direkte – ikke gang med 730.

### Steg 4 – Bygg tre scenarier

I ESLZ-modus: velg laveste SKU som faktisk støtter Private Endpoint og VNet-integrasjon (iht. Learn). I Standard-modus: laveste SKU som dekker funksjonelt behov.

- **Lav:** Laveste kvalifiserende SKU per tjeneste, 1 instans, minimal trafikk
- **Medium:** Produksjonskonfigurasjon med moderat last, HA på database
- **Høy:** Full redundans, zone-redundant der støttet, høy gjennomstrømming

### Steg 5 – Konverter til NOK

Hent dagens USD/NOK-kurs via web_search. Oppgi alltid kurs, dato og kilde. Hvis kurs ikke kan hentes (f.eks. nettverksrestriksjoner), bruk en eksplisitt merket antagelse.

### Steg 6 – Presenter resultatene

Bygg en interaktiv HTML-widget (via `show_widget`) og tilby Excel-eksport ved behov.

Widget-krav:
- Tre tab-knapper (Lav / Medium / Høy) som bytter innhold uten sidereload; sammendragskort (mnd NOK, mnd USD, år NOK) oppdateres ved tab-bytte
- Kapabilitets-badges per rad: `PE ✓/✗`, `VNet ✓/✗`
- Ekskluderte ressurser (f.eks. Firewall i delt hub) vises nedtonet med forklaring
- Badge "✓ API-pris" og "✓ MS Learn" der verifisert
- ESLZ-modus-badge grønn, Standard-modus grå
- Kurs, kilde og dato alltid synlig nederst

## Excel-eksport

Når brukeren ber om Excel, lag `.xlsx` (bruk xlsx-skillen) med:
- **Forutsetninger-fane**: USD/NOK-kurs, timer/mnd (730), Learn-kildereferanser
- **Scenario-faner** (én per nivå): ressurser med SKU, kapabiliteter, USD og NOK per mnd og år. Blå tekst = hardkodede inputverdier, sort tekst = formler (NOK = USD × kurs, år = mnd × 12), grønn bakgrunn = API-verifisert pris
- **Sammenligning-fane**: tre scenarier side om side med betinget formatering
- Ingen formelfeil; kjør alltid recalc-scriptet fra xlsx-skillen etter generering

## Kostnadsfeller å informere om

**Azure Firewall** – still avklaringsspørsmål før kalkyle: Er Firewall delt i Intilitys connectivity-hub (ekskludert fra kundens kalkyle)? Hvilke features trengs (IDPS, TLS-inspeksjon, URL-filtrering)? Svarene avgjør Basic/Standard/Premium – verifiser tier-kapabiliteter via Learn før anbefaling.

**Azure Functions** – Consumption-planen støtter ikke Private Endpoint eller VNet-integrasjon. Verifiser for aktuell tjeneste og region.

**Appout-subnet** er et egress-subnet, ikke en egen appserver.
