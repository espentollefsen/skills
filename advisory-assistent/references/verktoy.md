# Verktøyvalg

Hvilket verktøy/skill som brukes til hva. Hensikten er konsistens og at fakta verifiseres ved kilden.

## Microsoft Learn MCP – teknisk sannhetskilde

Bruk `microsoft_docs_search` / `microsoft_docs_fetch` (last via tool_search først) til å verifisere:
- SKU-kapabiliteter (støtter tier X Private Endpoint? VNet integration? zone redundancy?)
- Regionstilgjengelighet
- Tjenestegrenser (limits/quotas)
- Konfigurasjonskrav (subnett-delegering, DNS-soner, nødvendige roller)

Regel: påstander om Azure-kapabiliteter i en kundeleveranse skal være verifisert mot Learn eller merket som antagelse. Treningsdata er utgangspunkt for hypoteser, ikke kilde.

## Azure Retail Pricing API – prissannhetskilde

Aldri oppgi priser fra hukommelsen. For kostnadsarbeid:
- **Hel arkitektur / flere ressurser** → følg `prising-arkitektur.md` (tre scenarier Lav/Medium/Høy, NOK+USD, widget + Excel ved behov).
- **Én enkelt ressurs** → følg `prising-enkeltressurs.md` (veiledende avklaring av region/SKU/redundans, deretter API-oppslag).
- API-et nås direkte på `prices.azure.com` fra bash.
- Oppgi alltid prisdato og valutakurs som forutsetning.

## Lucid MCP – diagrammer

- Finnes en SVG av diagrammet allerede i samtalen → `lucid_convert_svg_to_diagram` med SVG-en uendret.
- Trengs Lucid-native former (BPMN, swimlanes, UML-klasser, navngitte Azure-shapes) → `lucid_create_diagram_from_specification` (les `lucid://diagram-specification` først).
- Tankekart → `lucid_create_mind_map`. Orgkart → `lucid_create_org_chart`. Sekvensdiagram → `lucid_create_sequence_diagram`.
- Arkitekturdiagrammer følger hub-spoke-konvensjonen: hub til venstre/øverst, spokes gruppert per workload, Private Endpoints tegnet eksplisitt i spoke-subnett, trafikkflyt med retning.
- Raske skisser i chat kan gjøres som inline SVG (Visualizer) – tilby Lucid-versjon hvis brukeren skal jobbe videre med diagrammet.

## Bifrost – visuell profil for HTML/frontend

Alle HTML-artifacts og interne verktøy bruker Intilitys Bifrost-designsystem. Bruk Bifrost MCP (`getRequiredUsage`, `listComponents`, `fetchReactDoc`, `fetchCssDoc`, `fetchDesignDoc`) for korrekte komponenter, farger og typografi. Standard: mørkt tema, norsk UI-tekst.

## Andre skills i verktøykassen

- **intility-powerpoint-instructions** – ALLE presentasjoner. Aldri generisk deck-design.
- **docx-skillen** – formelle Word-leveranser.
- **xlsx-skillen** – arbeidsbøker utover kostnadsestimater.
- **iso27001** – sikkerhets-/compliance-rådgivning når kunden spør om ISO 27001.

## Rekkefølge ved sammensatte oppgaver

1. Avklar/anta scope (én eksplisitt antagelsesliste hvis input er knapp)
2. Verifiser kapabiliteter (Learn MCP)
3. Design (eslz-standarder.md som sjekkliste)
4. Estimer (pricing-skills)
5. Produser leveranse (leveransemaler.md + riktig format-skill)
6. Diagram til slutt eller parallelt (Lucid)
