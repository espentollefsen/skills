# ESLZ-standarder (Intility Managed Azure)

Faglige standarder og plattformfakta for all arkitektur som skal kjøre i Intilitys ESLZ. Bruk dette både som faktagrunnlag (hva plattformen er) og som sjekkliste ved design og kvalifisering (hvordan kvalifisere en løsning).

> **Kildetype og verifisering:** **Del 1** er Intility-proprietære fakta – autoritativ kilde, verifiseres IKKE mot Microsoft. **Del 2** er Microsoft-/Azure-avhengige fakta – behandles som startverdi og **verifiseres mot Microsoft Learn MCP ved bruk** (se SKILL.md, seksjonen «ESLZ-faktasjekk»). Korriger denne filen ved avvik.

---

## Del 1 – Hva er Intility ESLZ

Intility Landing Zone er Intilitys implementering av Microsofts Cloud Adoption Framework (CAF) med Enterprise Scale Landing Zone (ESLZ). Det er en standardisert, modulær Azure-plattform som gir kunden et ferdig rammeverk for sikker og skalerbar drift. Alle kunder med Intility Landing Zone settes opp med en Azure ESLZ basert på CAF.

Kjerneprinsipper:
- **Standardisert og reproduserbar** – samme oppsett rulles ut til alle kunder; forenkler vedlikehold og oppdateringer.
- **Modulær** – alle starter med et "Core"-oppsett som kan utvides med standardiserte opsjoner.
- **Kundetilpasning** – kundens param-filer i GitHub styrer kundespesifikke tilpasninger uten eget utviklingsarbeid.

### Ressursorganisering (Management Groups)

| Management Group | ID | Forelder | Beskrivelse |
|---|---|---|---|
| Intility Landing Zone | `ima` | Tenant root | Begrenser LZ-tilgangen fra tenant root |
| [KundeKode] Intility Managed | `[KundeKode]` | `ima` | Toppnivå – policyer og innstillinger for hele LZ |
| Platform | `[KundeKode]-platform` | `[KundeKode]` | Plattformkomponenter for kjernefunksjonalitet |
| Connectivity | `[KundeKode]-connectivity` | `[KundeKode]-platform` | Private DNS Zones, VPN, DNS Resolver m.m. |
| Management | `[KundeKode]-management` | `[KundeKode]-platform` | Loggregistrering (Event Hub, Flow Logs) |
| Identity | `[KundeKode]-identity` | `[KundeKode]-platform` | Identitetsressurser (f.eks. Entra ID DS) |
| Landing Zones | `[KundeKode]-landing-zones` | `[KundeKode]` | Kundens applikasjonssubscriptions |
| Corp | `[KundeKode]-corp` | `[KundeKode]-landing-zones` | Interne ressurser – ikke direkte tilgjengelig fra internett |
| Online | `[KundeKode]-online` | `[KundeKode]-landing-zones` | Eksternt tilgjengelige ressurser (Front Door, AppGW m.m.) |
| Sandboxes | `[KundeKode]-sandboxes` | `[KundeKode]` | Prototyping, test/utvikling |
| [KundeKode] Unmanaged | `[KundeKode]-unmanaged` | `ima` | Subscriptions uten Intility-relasjon |

### Standard subscriptions

Tre subscriptions opprettes som standard: `[KundeKode]-Identity`, `[KundeKode]-Management`, `[KundeKode]-Connectivity`. Plattformkonsum ligger typisk på **500–1 000 kr/mnd** for standard enterprise scale.

### Online vs. Corp (viktig designvalg, følger Well-Architected Framework)

- **Corp** – ressurser som kun skal være internt tilgjengelige. Strenge policies for public networking. Alt som kan, skal ligge her med private endpoints.
- **Online** – ressurser som kan/må være eksternt tilgjengelige (Front Door, App Gateway, APIM). I prinsippet skal Online kun inneholde inngress-tjenester; alt annet bør ligge i Corp med private endpoints.

### Nettverksdesign

Intility leverer **ikke** en standard nettverkskonfigurasjon som del av LZ-deployet – nettverksbehov varierer for mye. Nettverkskartlegging skjer i en egen mapping- og designprosedyre. Typisk design: **hub-and-spoke med InCloud-integrasjon via Azure Direct Link**.

| Tjeneste | Beskrivelse |
|---|---|
| Managed Azure Network \| VNet | Hub-and-spoke, Zero Trust med NSG/ASG, VNet-peering |
| Managed Azure Direct Link \| VPN | Kryptert VPN mellom Intility og Azure – standardløsning |
| Managed Azure Direct Link \| ExpressRoute | Dedikert, privat forbindelse med høy kapasitet |
| Managed Azure Firewall | Sentral, skalerbar brannmur (stateful, app/network rules, Threat Intel) |

### Identitet og tilgang

- Hybrid identitet basert på InCloud Active Directory med Entra ID Connect.
- Tre tilgangsmetoder: Azure Lighthouse, AdminAgent (CSP), B2-brukere i kundens tenant.
- Custom RBAC-roller for minste nødvendige tilgang (f.eks. `KeyVault-ARMTemplate-Deployer`, `Network-Vnet-Peering-Contributor`).
- Enterprise Scale-roller: Subscription Owner, Application-Owners, Network-management, Network-Subnet-Contributor, Security-Operations.

### Logging og sikkerhet

- Diagnostiske logger → Event Hub i kundens tenant → replikert til sentral Event Hub → Splunk.
- Flow Logs → Storage Account i kundens tenant (standard fra Q1 2026).
- Policies basert på MCSB, CAF og Intilitys best practices.
- Defender for Cloud – CSPM og Defender for Resource Manager som standard. Sentralisert SOC-logging.

### Overvåking (Monitoring)

Dynatrace er kjernesystem for applikasjonsovervåkning. Krever at subscription er satt til **Application Management** i PCM og har tag `intilityManaged = True`.

### DevOps og kode

- Basert på Microsofts open source: `Azure/terraform-azurerm-caf-enterprise-scale`. Policies hentes fra `Azure/Enterprise-Scale`.
- Felles GitHub-repo for alle kunder; hver kunde har egen param-fil.
- Deploy via GitHub Actions med self-hosted network runners.

### Opsjonelle tjenester

| Kategori | Tjeneste |
|---|---|
| Connectivity | Hub & Spoke VPN, Hub & Spoke VPN med Azure Firewall, vWAN med Azure Firewall, Direct Link |
| DNS | DNS Resolver for dedikerte domener, DNS Resolver for multitenant DNS |
| Sikker tilgang | Azure Connect, PIM (Privileged Identity Management) |
| DevOps | Azure DevOps VMSS Build Agents, GitHub Runners Managed VNet |
| SOC | Managed Sentinel |
| Sertifikater | Azure ACME – Automatic Certificate Management |

### FinOps / Kostnadshåndtering

- Azure kostnadsrapport i Intility Insight (kun for LZ-enrolled subscriptions).
- Underrapporter: totaloversikt, kostnader per subscription/RG, Top 5 Usage Drivers, forecasting, geografisk kart.
- Utvidede rapporter (500 kr/mnd per rapport): Azure Anomalies og Azure Orphaned.

### Ansvarsfordeling

- **Kun Landing Zone:** kunden er ansvarlig for drift av ressurser; Intility bistår med oppsett og rammeverk.
- **Med Application Management:** Intility tar ende-til-ende-ansvar for infrastruktur, overvåkning, feilretting, dokumentasjon og endringshåndtering.

---

## Del 2 – Design- og kvalifiseringsstandarder

Bruk dette ved design og ESLZ-kvalifisering av en konkret løsning.

### Grunnmønster

- **Hub-spoke-topologi.** Kundens workloads ligger i spokes; hub (managed av Intility) inneholder Azure Firewall, gateways og delte tjenester. Spoke-VNets peeres mot hub, og all nord-sør- og øst-vest-trafikk rutes via hub-firewall (UDR med default route mot huben).
- **Privat tilkobling som standard.** PaaS-tjenester eksponeres via Private Endpoints i spoke (Corp). Offentlige endepunkter blokkeres eller flagges av Azure Policy. Private DNS-soner administreres sentralt – anta at kunden IKKE selv styrer Private DNS.
- **Azure Policy-håndheving.** Forvent deny/audit-policies på bl.a. offentlig nettverkstilgang, manglende diagnostikk, ikke-godkjente regioner og SKU-er. Design som bryter policy må enten endres eller behandles som formelt avvik.
- **Regioner.** Norway East er primær standardregion. Sweden Central og North/West Europe brukes når tjenesten ikke finnes i Norway East – verifiser alltid regiontilgjengelighet (Microsoft Learn MCP) før du anbefaler.

### ESLZ-kvalifisering: sjekkliste per tjeneste

Når en ny tjeneste/arkitektur skal kvalifiseres, vurder punktvis:

1. **Private Endpoint-støtte** – finnes det PE for alle dataplan-endepunkter tjenesten bruker? (Mange tjenester har PE for kontrollplan, men ikke alle under-endepunkter.)
2. **VNet-integrasjon utgående** – kan tjenesten sende trafikk via kundens VNet (VNet integration / VNet injection / delegert subnett)? Hvilken delegasjon kreves, og hvor stort subnett?
3. **DNS-avhengigheter** – hvilke private DNS-soner kreves? Kolliderer de med sentralstyrte soner?
4. **Tvungen ruting** – tåler tjenesten UDR/0.0.0.0-route mot firewall? Trengs unntak (f.eks. service tags i firewall)?
5. **Identitet** – støttes managed identity? Kreves Entra-roller/GDAP-tilpasning for managed drift?
6. **Regionstøtte** – tilgjengelig i Norway East? Hvis ikke, hva er nærmeste region og hva betyr det for latens/datalagring?
7. **Policy-konflikt** – kjente policies som blokkerer (offentlig tilgang, SKU-restriksjoner)?
8. **Driftbarhet** – diagnostikk til Log Analytics, alarmer, backup der relevant.

Konkluder eksplisitt: **ESLZ-kvalifisert / kvalifisert med avvik / ikke kvalifisert**, med avvikene listet.

### Kjente fallgruver (flagg disse proaktivt)

- App Service/Function VNet integration krever dedikert delegert subnett – dimensjoner for skalering (minimum /27, helst /26).
- Container Apps: workload profiles vs. consumption har ulik nettverksmodell; kun workload profiles gir full UDR-støtte.
- Fabric: kapasitet (F-SKU) er regionsbundet; private link for Fabric har begrensninger på enkelte opplevelser – verifiser per workload.
- Databricks: secure cluster connectivity + Private Link krever to PE-typer (front-end og back-end); IP access lists gjelder kun offentlig endepunkt.
- Azure OpenAI/AI Foundry: PE dekker dataplan, men enkelte studio-/portalopplevelser krever ekstra konfigurasjon.
- Service Bus/Event Hub: Private Endpoint krever Premium/dedikerte tier på enkelte funksjoner – sjekk tier-krav.
- GitHub Actions mot privat nett: krever VNet-injected runners eller self-hosted runners i spoke.

### Navnekonvensjoner

Følg CAF-baserte navnekonvensjoner: `<ressurstype>-<workload>-<miljø>-<region>-<løpenr>`, f.eks. `app-fakturaportal-prod-noe-001`. Miljøkoder: `dev`, `test`, `prod`. Regionkoder: `noe` (Norway East), `swc` (Sweden Central), `neu`/`weu`. Ressursgrupper: `rg-<workload>-<miljø>-<region>`. Avvik fra dette kun hvis kunden har egen etablert konvensjon.

### Avviksvurdering

Når et krav ikke kan oppfylles i ESLZ: beskriv (1) hva avviket er, (2) risiko, (3) kompenserende tiltak, (4) anbefaling. Aldri "stille avvik" – kunde og Intility-drift skal kunne ta et informert valg.
