# Prising: én enkelt ressurs

Interaktivt, veiledende prisoppslag for én Azure-ressurs. For full arkitekturkalkyle (flere ressurser, tre scenarier, Excel), bruk `prising-arkitektur.md`.

## Grunnprinsipper

**Spør først – pris etterpå.** Still de veiledende spørsmålene *før* API-kall – feil svar på ett spørsmål (region, redundans) gir feil pris. Still alle relevante spørsmål samlet i én runde, ikke ett om gangen.

**Fakta over hukommelse.** Kall alltid Azure Pricing API og Microsoft Learn MCP.

## Steg 1 – Identifiser ressursen

- "hva koster X?" → direkte oppslag
- "er X dyrere enn Y?" → to oppslag, sammenlign side om side med differanse i NOK og %
- "hva er månedsprisen?" → timepris × 730

Avklar tjenesten hvis tvetydig ("SQL Database" → Azure SQL Database, Managed Instance, eller SQL på VM?).

## Steg 2 – Veiledende spørsmål

**Alltid:** Region (standard `norwayeast`) · Betalingsmodell (PAYG, 1-års eller 3-års reservasjon)

**Per tjeneste:**
- **VM:** OS (Windows/Linux) · Hybrid Benefit · Spot · disktype · serie/størrelse
- **App Service / Functions:** OS · tier (Free→Isolated) · antall instanser
- **Azure SQL:** deployment (Single/Elastic/MI) · Provisioned/Serverless · vCores/DTU · service tier (GP/BC/Hyperscale) · backup-redundans · Hybrid Benefit
- **PostgreSQL/MySQL Flexible:** compute tier (Burstable/GP/Memory Opt.) · vCores · storage GB · Zone Redundant HA
- **Storage:** Standard/Premium · LRS/ZRS/GRS/GZRS · Hot/Cool/Cold/Archive · datavolum
- **AKS:** Free/Uptime SLA control plane · node-VM-størrelse · antall noder
- **Redis:** tier · størrelse · zone redundancy
- **Front Door/CDN:** Standard/Premium · utgående trafikk GB/mnd
- **Key Vault:** Standard/Premium (HSM) · antall operasjoner
- **Private Endpoint:** antall
- **VPN GW / ExpressRoute:** SKU · dataoverføring GB/mnd

## Steg 3 – Verifiser kapabiliteter (Learn MCP)

Etter svar, før prisoppslag: bekreft at valgt SKU støtter det brukeren trenger (PE, zone redundancy, serverless). Hvis ikke – informer og foreslå laveste SKU som støtter kravet.

## Steg 4 – Hent pris

```
GET https://prices.azure.com/api/retail/prices?api-version=2023-01-01-preview&$filter=<filter>
```

Filtereksempler:
```
serviceName eq 'Virtual Machines' and armRegionName eq 'norwayeast' and skuName eq 'D4s v5' and priceType eq 'Consumption'
serviceName eq 'Azure App Service' and armRegionName eq 'norwayeast' and skuName eq 'P1 mv3' and operatingSystemFamily eq 'Linux'
serviceName eq 'SQL Database' and armRegionName eq 'norwayeast' and skuName eq 'General Purpose' and meterName eq '4 vCores'
serviceName eq 'Azure Cache for Redis' and armRegionName eq 'norwayeast' and skuName eq 'P1'
serviceName eq 'Storage' and armRegionName eq 'norwayeast' and skuName eq 'LRS'
```

API-et returnerer mange meters – filtrer på `meterName`/`skuName`. PAYG: `priceType eq 'Consumption'`. Reservasjon: `priceType eq 'Reservation'` + `reservationTerm`. 730 t/mnd; lagring ofte per GB/mnd direkte.

## Steg 5 – NOK-kurs

web_search for dagens USD/NOK. Oppgi kurs, dato, kilde – eller merket antagelse hvis kurs ikke kan hentes.

## Steg 6 – Presenter

```
Ressurs:         <tjeneste>
Konfigurasjon:   <tier, vCores, storage, HA, region>
SKU:             <sku>
Betalingsmodell: <PAYG/reservasjon>

Pris per time:   $X.XX
Pris per mnd:    $XXX (~X XXX NOK)
Pris per år:     $X XXX (~XX XXX NOK)

Reservasjon 1 år: $XXX/mnd (~X XXX NOK) → X% spart
Reservasjon 3 år: $XXX/mnd (~X XXX NOK) → X% spart

✓ Pris: Azure Retail Pricing API (dato)  ✓ Kapabiliteter: Microsoft Learn MCP
USD/NOK: X,XX (kilde, dato)
```

Inkluder reservasjonspriser hvis brukeren spurte, eller hvis innsparingen er vesentlig (>20 %).

## Vanlige feil å unngå

- Ikke anta region – spør, default `norwayeast`
- Ikke bland compute og storage – lagring er ofte separat meter
- Ikke glem Hybrid Benefit – 40–55 % rabatt på Windows/SQL
- Ikke presenter én pris uten kontekst – alltid SKU, tier og forutsetninger
- Ikke gjett kapabiliteter – verifiser mot Learn MCP
