# Live registre (MCP) som kilde

Når et register er koblet til via MCP (f.eks. IntIpaas: `list_apps`, `list_flows`, `list_flow_classifications`), er det en **prosjektunderlags**-kilde: sannere enn gamle dokumenter, men ikke ufeilbarlig.

## Slik bruker du det
1. **Hent hele registeret** (apper + flyter + klassifisering) før du skriver applikasjonskapittelet og vedlegget. Sammenlign med forrige uttak: nye, fjernede og endrede rader utgjør en endringsliste.
2. **Datamaster**: avgjør hvem som er master og hvem som er konsument ved å lese kilde/mål-feltene i flytdata – ikke ved å tolke applikasjonsnavn.
3. **Registeret kan avvike fra virkeligheten.** Eksempler: en leverandør har bekreftet SSO, men notatet i registeret er eldre; en applikasjon er merket SaaS, men hostes i avgivende parts Azure; kritikalitet er ikke satt. Noter avviket i vedlegget og si at registeret må oppdateres av eieren.
4. **Statuser og begreper** – livssyklus (Videreføres / Ny / Erstattes / Utgår / TBD), kritikalitet, teknologitype (IT/OT) – overføres til vedlegg slik de står, så oppsummeringsformler fortsatt stemmer. Legg ny informasjon (f.eks. «anskaffelse TBD») i egen kolonne i stedet for å endre en statuskolonne formler teller på.
5. **IT/OT-plassering** er ofte uavklart i registeret (applikasjon «definert som OT, men går gjennom IT/OT-switch»). Ikke avgjør; opprett åpent punkt.
6. **Datoer og TSA-frister** hentes fra registeret/planen, ikke fra hukommelsen.

## Det registeret ikke kan svare på
Hvem som eier applikasjonen hos kunden, SaaS Management-valg, leveransemodell for klientapplikasjoner. Disse blir kolonner kunden fyller ut («Fastsettes i Fase 1») og åpne punkter.
