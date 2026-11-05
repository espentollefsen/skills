# Intility Managed Azure – tjenestekatalog

Hva Intility leverer og tar driftsansvar for på Azure. Bruk dette til tilbudsarbeid, scoping av driftsansvar, kundemøter og spørsmål som "hva inkluderer tjenesten", "LZ vs. Application Management", "kan Intility drifte X". For teknisk plattform-/designdetalj (Management Groups, ESLZ-mønstre, kvalifisering), se `eslz-standarder.md`.

## Modell: to nivåer

Managed Azure aktiveres når Intility skal ta driftsansvar for løsninger i Azure, og leveres på to nivåer:

1. **Intility Landing Zone** – grunnkomponent for drift i Azure (plattform, nettverk, sikkerhetsbaseline, kostnadsrapport).
2. **Application Management** – utvidet ende-til-ende applikasjonsdrift. **Krever Landing Zone.**

Scoping-regel: kunden velger selv hvilke subscriptions som innrulles i Landing Zone; øvrige er `unmanaged`. Flere managed-tjenester (Firewall, VPN, ExpressRoute, ekstra Defender-planer) er **kun tilgjengelig på innrullerte subscriptions**.

---

## Nivå 1 – Intility Landing Zone

Basert på Azure Landing Zone-rammeverket og CAF. Alle kunder settes opp med Azure Enterprise Scale Landing Zone.

### Ressursorganisering
Management Group-struktur i to hovedgrupper: **Platform** (administrasjonsressurser – Event Hub, Storage for logging; standard konsum 500–1 000 kr/mnd) og **Landing Zone** (kundens applikasjonsressurser, delt i miljøene Corp / Online / Decommissioned / Sandbox). Detaljert MG-tabell i `eslz-standarder.md`.

### Nettverk og konnektivitet
| Tjeneste | Beskrivelse |
|---|---|
| Managed Azure Network \| VNet | Hub-and-spoke med VNet-peering, NSG/ASG etter zero trust. IP-adresser må følge Intilitys standarder. |
| Managed Azure Direct Link \| VPN | Standardløsning Intility↔Azure. Full kryptering, høy fleksibilitet, mot alle Azure-datasentre. |
| Managed Azure Direct Link \| ExpressRoute | Dedikert, privat forbindelse (inkl. Norway East og West Europe). Går ikke over offentlig internett. |
| Managed Azure Firewall | Sentral, skalerbar brannmur i hub-VNet, fokus øst–vest. Stateful inspeksjon, application/network rules, Threat Intelligence. |

**⚠️ Scoping:** VPN, ExpressRoute og Azure Firewall er kun tilgjengelig på subscriptions innrullert i en Intility Landing Zone.

### Identitet og tilgangsstyring
- To standard rollegrupper opprettes: **Reader** og **Contributor** (i AD og Azure AD).
- Brukere/grupper kartlegges i implementeringsprosjekt, deretter selvbetjening via Intility Portal.
- Anbefalte tilvalg: PIM + revisjon, MFA, betinget adgang og multinivå MFA, skreddersydd Azure AD-integrasjon.

### Sikkerhet (Security Baseline)
- **Microsoft Policies** – basert på MCSB, CAF og Intility best practices. Revisjon av non-compliant ressurser anbefales; gjennomgang tilbys som **fakturerbar** tjeneste.
- **Defender for Cloud** – MCSB + Defender CSPM som default. Ytterligere Defender-planer krever **Application Management**.
- **Sentralisert aktivitetslogging** – logger til Intility SOC. Egendefinerte alarmer er **ekstra** tjeneste.

### Automasjon og oppdateringer
Standardisert, reproduserbart basisoppsett til alle kunder. Løpende oppdateringer med varsling til superbrukere/systemeiere via APM. Sikker utrulling fra sikre arbeidsstasjoner i tråd med Intilitys sonemodell.

### Kostnadshåndtering
Azure-kostnadsrapport i Intility Insight (kun innrullerte subscriptions):

| Rapport | Formål |
|---|---|
| Totaloversikt | Kostnadsbilde over tid – topper, bunner, trender |
| Per subscription/ressursgruppe | Fordeling på miljøer, systemer, applikasjoner |
| Top 5 Usage Drivers | De 5 største kostnadene + utvikling |
| Drilldown-matrise | Dypt innsyn per kategori/tjeneste |
| Kartoversikt | Geografisk plassering av tjenester |
| Forecasting | Forventet forbruk neste 30 dager |

Utvidede rapporter (ved forespørsel): **Azure Anomalies** (uventede kostnadsendringer) og **Azure Orphaned** (ubrukte ressurser som fortsatt koster, f.eks. disker etter slettet VM).

---

## Nivå 2 – Application Management (krever Landing Zone)

Ende-til-ende ansvar for den underliggende applikasjonsplattformen. Inkluderer:
- Oppsett og/eller revisjon av eksisterende oppsett.
- Dokumentasjon i CMDB via Application Platform Manager (APM).
- Support, feilretting og endringshåndtering **24/7/365**.
- Koordinering med applikasjonsleverandører og tredjeparter.
- Privilegert tilgangsstyring (PAM) med self-service og just-in-time-tilgang.
- Applikasjonsovervåking og automatisk feilretting 24/7/365: kontinuerlige sjekker minimum hvert 5. min, auto-feilretting ved terskelbrudd, manuell feilretting/eskalering til spesialist ved behov.
- **Dynatrace** som kjernesystem: auto-varsling, AI-rotårsaksanalyse, konsolidering av relaterte avvik, alvorlighetsgrad (antall brukere/tjenester påvirket). Tilvalg: APM og Real User Monitoring (RUM) for utviklere.

**Intility som Single Point of Contact:** alle feil og endringer går via Intility. Flyt: kunnskapsartikler → spesialist → applikasjonsleverandør. Gjentakende feil: rotårsaksanalyse → forbedringstiltak → nye/forbedrede monitorer og kunnskapsartikler.

### Tjenester som krever Application Management
- **Managed Defender for Cloud** – aktivering + management av planer: Key Vault, App Services, Resource Manager, DNS, Storage, Databases (Azure SQL, SQL on machines, open-source DB, Cosmos DB), Containers (herding, sårbarhet, runtime), APIs. SOC responderer innenfor normal arbeidstid.
- **Defender for Resource Manager** – overvåker ressursstyringsoperasjoner; alarmer til Intility SOC.
- **PAM i APM** – Azure Connect med Privileged Access User (PAU), tidsbegrenset tilgang + PIM-elevasjon til spesifikke subscriptions/ressursgrupper. Støtter private endpoints uten unntak for public IP.
- **CMDB** – alle applikasjoner og Azure-ressurser dokumentert i egenutviklet CMDB i APM; tilgjengelig for kunde, Intility og tredjeparter.

---

## Managed-tilleggstjenester

### Managed Azure Kubernetes Service (AKS)
Sikker Kubernetes-plattform. Inkluderer: versjonsoppgradering, cluster-/node-administrasjon og autoskalering, alarmhåndtering (CPU/minne), automatisk secrets-/sertifikathåndtering, tilganger/policies, DNS, direkte kanal til Intilitys Kubernetes-eksperter (Teams/Slack). Fordeler: true PaaS (betal kun for app-noder), overvåking 24/7, Dynatrace-integrasjon, selvbetjent publisering med WAF/TLS, mikrosegmentert nettverk, geo-redundant infrastruktur med full DR, integrasjon med Intility Identity & Access.

### Managed Azure Disaster Recovery
Fullt administrert DR for alle produksjons-VMer, basert på Azure Site Recovery. Intility håndterer implementering, overvåking av sync-jobs, failover, DR-drills på forespørsel, best practices og oppdatering.
- Crash-consistent recovery points hvert 5. min (siste timen).
- Standardisert RPO: **1 time med 24 punkter (24 timer)**.
- Replikering mellom produksjons-SSD – lik ytelse etter failover.
- **Default: compute i Norway East, replikering til West Europe.** Replikering til Norway West på forespørsel (krever søknad til Microsoft per subscription).

### Andre relaterte tjenester
| Tjeneste | Beskrivelse |
|---|---|
| Intility Managed Encryption Keys (IMEK) | Kryptering av applikasjonsdata i Azure |
| Cloudflare Application Gateway | Sikker publisering av webapplikasjoner på tvers av skyplattformer |
| Dynatrace | Utvidet applikasjonsovervåking |

---

## Rask scoping-guide (advisory)

- **Kun Landing Zone:** kunden drifter ressursene selv; Intility leverer plattform, nettverk, sikkerhetsbaseline og kostnadsrapport. Velg når kunden vil ha ESLZ-rammeverket, men beholde driftsansvaret.
- **Landing Zone + Application Management:** Intility tar ende-til-ende driftsansvar (24/7/365, overvåking, auto-feilretting, CMDB, PAM, SPOC). Velg når kunden vil sette bort drift.
- **Krever Application Management:** ekstra Defender-planer, Defender for Resource Manager, PAM i APM, managed applikasjonsdrift.
- **Fakturerbart / ekstra:** policy-compliance-gjennomgang, egendefinerte alarmer, utvidede kostnadsrapporter (Anomalies/Orphaned).
- **Kun på innrullerte subscriptions:** VPN, ExpressRoute, Azure Firewall.
