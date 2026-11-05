---
name: azure-resource-pricer
description: >
  Henter nøyaktig pris for én enkelt Azure-ressurs via interaktiv veiledning og Azure Retail
  Pricing API. Bruk denne skillen når brukeren spør om pris på én bestemt Azure-tjeneste eller
  ressurs – f.eks. "hva koster en Azure SQL Database?", "hva er prisen på P2-nivå for App Service?",
  "hva koster en B4ms VM?", "hva koster Redis Cache i Norway East?", eller lignende enkeltoppslag.
  Stillingen stiller veiledende spørsmål for å avdekke region, SKU, redundans, lisensmodell og
  andre prisrelevante valg, og verifiserer kapabiliteter via Microsoft Learn MCP. Presenter
  alltid sluttprisen i NOK (dagens kurs) og USD. Bruk denne fremfor å gjette priser fra
  treningsdatasettet, og i stedet for azure-cost-estimator når det gjelder én enkelt ressurs
  og ikke en hel arkitektur.
---

# Azure Resource Pricer

Interaktiv, veiledende prisoppslag for én enkelt Azure-ressurs.

## Grunnprinsipper

**Én ressurs om gangen.** Denne skillen er optimert for dybdeoppslag på én tjeneste.
For full arkitekturkalkyle, bruk `azure-cost-estimator`-skillen.

**Spør først – pris etterpå.** Still de veiledende spørsmålene (se under) *før* du
kaller APIet. Feil svar på ett spørsmål (f.eks. region eller redundans) gir feil pris.

**Fakta over hukommelse.** Kall alltid Azure Pricing API og Microsoft Learn MCP.
Stol ikke på innbakt kunnskap om priser eller SKU-kapabiliteter.

---

## Arbeidsflyt

### Steg 1 – Identifiser ressursen

Forstå hvilken tjeneste brukeren spør om. Typiske formuleringer:
- "hva koster X?" → direkte oppslag
- "er X dyrere enn Y?" → to oppslag, sammenlign
- "hva er månedsprisen for ..." → beregn fra timepris × 730

Avklar tjenesten hvis uklart (f.eks. "SQL Database" → Azure SQL Database, SQL Managed Instance, eller SQL Server på VM?).

### Steg 2 – Still veiledende spørsmål

Still alle relevante spørsmål *samlet i én runde* (ikke ett om gangen). Velg spørsmål fra listen under basert på hva som er relevant for den aktuelle tjenesten.

#### Alltid relevante spørsmål:
- **Region:** Hvilken Azure-region? (standard: `norwayeast`)
- **Betalingsmodell:** Pay-as-you-go, 1-år reservasjon, eller 3-år reservasjon?

#### Avhengig av tjeneste:

**Virtuelle maskiner (VM):**
- OS: Windows eller Linux?
- Hybrid Benefit (eksisterende Windows Server/SQL-lisens)?
- Spot-instans?
- Disktype inkludert? (Premium SSD, Standard SSD, HDD)
- Ønsket størrelse/serie (f.eks. D-series, E-series, B-series)?

**App Service / Functions:**
- OS: Windows eller Linux?
- Tier: Free, Shared, Basic, Standard, Premium, Isolated?
- Antall instanser?

**Azure SQL Database / Managed Instance:**
- Deployment: Single Database, Elastic Pool, Managed Instance?
- Compute-modell: Provisioned eller Serverless?
- vCores eller DTU-modell?
- Service tier: General Purpose, Business Critical, Hyperscale?
- Backup-redundans: Locally Redundant, Zone Redundant, Geo Redundant?
- Hybrid Benefit (eksisterende SQL Server-lisens)?

**Azure Database for PostgreSQL / MySQL:**
- Flexible Server?
- Compute tier: Burstable, General Purpose, Memory Optimized?
- vCores?
- Storage (GB)?
- Høy tilgjengelighet (Zone Redundant HA)?

**Storage Account / Blob Storage:**
- Performance: Standard eller Premium?
- Redundans: LRS, ZRS, GRS, GZRS?
- Access tier: Hot, Cool, Cold, Archive?
- Forventet datavolum (GB)?

**Azure Kubernetes Service (AKS):**
- Gratis control plane (standard) eller betalt Uptime SLA?
- Node VM-størrelse?
- Antall noder?

**Azure Cache for Redis:**
- Tier: Basic, Standard, Premium, Enterprise?
- Cache-størrelse (GB)?
- Zone Redundancy?

**Azure Front Door / CDN:**
- Tier: Standard eller Premium?
- Forventet utgående trafikk (GB/mnd)?

**Key Vault:**
- Tier: Standard eller Premium (HSM)?
- Forventet antall operasjoner?

**Private Endpoint:**
- Antall Private Endpoints?

**VPN Gateway / ExpressRoute:**
- Gateway SKU?
- Dataoverføring (GB/mnd)?

### Steg 3 – Verifiser kapabiliteter via Microsoft Learn MCP

For tjenester der SKU/tier-valg har kapabilitetsimplikasjoner, søk i Microsoft Learn MCP
*etter* at brukeren har svart på spørsmålene, men *før* prisoppslaget:

```
"Azure <tjeneste> <feature> supported tiers"
"Azure <tjeneste> private endpoint requirements"
"Azure <tjeneste> zone redundancy supported SKU"
```

Formål: Bekreft at valgt SKU faktisk støtter det brukeren ønsker (f.eks. Private Endpoint,
Zone Redundancy, Serverless). Hvis ikke – informer brukeren og foreslå laveste SKU som støtter
kravet.

### Steg 4 – Hent pris fra Azure Retail Pricing API

```
GET https://prices.azure.com/api/retail/prices?api-version=2023-01-01-preview
    &$filter=<filter>
```

#### Nyttige filtereksempler:

```
# VM (Linux, Pay-as-you-go)
serviceName eq 'Virtual Machines' and armRegionName eq 'norwayeast' and skuName eq 'D4s v5' and priceType eq 'Consumption'

# App Service (Linux, Premium v3)
serviceName eq 'Azure App Service' and armRegionName eq 'norwayeast' and skuName eq 'P1 mv3' and operatingSystemFamily eq 'Linux'

# Azure SQL Database (General Purpose, 4 vCores)
serviceName eq 'SQL Database' and armRegionName eq 'norwayeast' and skuName eq 'General Purpose' and meterName eq '4 vCores'

# PostgreSQL Flexible Server
serviceName eq 'Azure Database for PostgreSQL' and armRegionName eq 'norwayeast'

# Redis Cache (Premium P1)
serviceName eq 'Azure Cache for Redis' and armRegionName eq 'norwayeast' and skuName eq 'P1'

# Storage (LRS, Hot)
serviceName eq 'Storage' and armRegionName eq 'norwayeast' and skuName eq 'LRS'
```

**Viktig:** API-responsen inneholder mange meters. Filtrer på `meterName` og `skuName` for
å finne riktig linje. Se etter `priceType eq 'Consumption'` for pay-as-you-go.
For reservasjoner, bruk `priceType eq 'Reservation'` og filtrer på `reservationTerm`.

**Kalkulasjonsgrunnlag:** 730 timer/mnd (standard). Månedspris = `retailPrice × 730`.

**Lagringspriser** er ofte per GB/mnd direkte – ikke gang med 730.

### Steg 5 – Hent NOK-kurs

Bruk web_search til å hente dagens USD/NOK-kurs. Oppgi alltid:
- Kurs brukt
- Dato
- Kilde

### Steg 6 – Presenter resultatet

Vis resultatet som en ryddig inline-tabell eller kort:

```
Ressurs:        Azure Database for PostgreSQL – Flexible Server
Konfigurasjon:  General Purpose, 4 vCores, 512 GB storage, ZRS HA, norwayeast
SKU:            GP_Standard_D4s_v3
Betalingsmodell: Pay-as-you-go

Pris per time:   $X.XX USD
Pris per mnd:    $XXX.XX USD  (~X XXX NOK)
Pris per år:     $X XXX.XX USD (~XX XXX NOK)

Reservasjon 1 år: $XXX.XX USD/mnd (~X XXX NOK)  → X% spart
Reservasjon 3 år: $XXX.XX USD/mnd (~X XXX NOK)  → X% spart

✓ Pris: Azure Retail Pricing API (YYYY-MM-DD)
✓ Kapabiliteter: Microsoft Learn MCP
USD/NOK: X.XX (kilde, YYYY-MM-DD)
```

Inkluder reservasjonspriser hvis brukeren spurte om det, eller hvis de gir vesentlig innsparing (>20%).

### Tillegg: Sammenligning av to SKU-er

Hvis brukeren ønsker å sammenligne (f.eks. "D4s v5 vs E4s v5"), gjør to oppslag og
presenter side om side med differanse i NOK og %.

---

## Vanlige feil å unngå

- **Ikke anta region** – spør alltid, default `norwayeast`
- **Ikke bland compute og storage** – lagring er ofte separat meter
- **Ikke glem Hybrid Benefit** – kan gi 40–55% rabatt på Windows/SQL
- **Ikke presenter én pris uten kontekst** – oppgi alltid SKU, tier, og forutsetninger
- **Ikke gjett på kapabiliteter** – verifiser alltid mot Microsoft Learn MCP

---

## Relasjon til andre skills

- **azure-cost-estimator**: Bruk den for full arkitekturkalkyle (flere ressurser, tre scenarier, ESLZ-modus, Excel-eksport)
- **azure-resource-pricer** (denne): Bruk for enkeltoppslag, hurtigsjekk av én ressurs, SKU-sammenligning
