---
name: "designlop"
description: Startmeny og orkestrering for hele designmetoden (HLD, vedlegg, kommentarløp, topologifigurer, PDF-rapporter). Stiller flervalgsspørsmål om hva brukeren vil gjøre, skanner prosjektfilene først så den ikke spør om det filene allerede viser, setter opp en plan i riktig rekkefølge, og ruter til skillene hld-bygger, vedlegg-bygger, kommentarlop, topologifigurer og pdf-rapport. Bruk når brukeren sier «hjelp meg med designdokumentene», «hva kan du gjøre», «start designløpet», «hva er neste steg», «meny», åpner en kunde/et prosjekt med kontraktsfiler uten å si hva som skal gjøres, ber om flere av oppgavene samtidig (f.eks. HLD + vedlegg + figurer), eller når det er uklart hvilken av de fem skillene som passer. Når brukeren allerede sier tydelig hva som skal gjøres, hopp over menyen og rut direkte.
---

# Designløpet – startmeny

Samler de fem skillene bak én inngang. Du stiller korte flervalgsspørsmål, bygger en plan, og kjører så den eller de skillene som passer. Denne skillen **erstatter ikke** de andre: den bestemmer *hva* som skal gjøres og i hvilken rekkefølge, så leser du instruksjonene til hver skill du ruter til (se «Moduler») og følger dem fullt ut – inkludert stoppreglene.

| Skill | Gjør |
|---|---|
| `hld-bygger` | Skriver/sjekker HLD mot kontrakten, finner konflikter |
| `vedlegg-bygger` | Bygger og kontrollerer vedlegg (Excel/Word) |
| `kommentarlop` | Kommentarregistre → beslutning → endringer med logg |
| `topologifigurer` | Figurer (SVG → PNG/PDF) og bytte i Word |
| `pdf-rapport` | Designede PDF-lesekopier av vedlegg |

## Moduler (skillen er selvstendig)
De fem skillene ligger inne i denne skillen som moduler: `moduler/hld-bygger/`, `moduler/vedlegg-bygger/`, `moduler/kommentarlop/`, `moduler/topologifigurer/`, `moduler/pdf-rapport/`. Hver modul har sin egen `MODUL.md` (= den frittstående skillens SKILL.md), `references/` og `scripts/`. Er skillene i tillegg installert hver for seg, bruk dem; ellers les `moduler/<navn>/MODUL.md`. **Stier i en modul sin MODUL.md er relative til modulens egen mappe** (kjør f.eks. `python moduler/hld-bygger/scripts/opsjon_sjekk.py …`), og henvisninger mellom moduler («`hld-bygger/scripts/hld_lint.py`») peker på søsken-mappene i `moduler/`.

## Når du skal bruke menyen – og når ikke
- **Uklar forespørsel** («hjelp meg med designdokumentene», «hva nå?», nye kontraktsfiler uten instruks) → kjør menyen.
- **Tydelig forespørsel** («lag PDF av Vedlegg A», «gjennomfør registrene») → *ikke* vis menyen. Rut direkte til skillen. Menyen skal spare tid, ikke bremse.
- **Delvis tydelig** («lag figurene og vedleggene») → hopp over runde 0, ta bare de detaljspørsmålene som mangler.

## Flyten
```
0 Skann filer → 1 Meny (hva skal gjøres?) → 2 Detaljspørsmål per valg → 3 Plan + bekreft → 4 Kjør (les underliggende skill)
        → 5 Stopp-punkter som flervalg → 6 Oppsummer + neste-steg-meny
```

### 0. Skann (alltid først, hvis du har filer)
`python scripts/skann_prosjekt.py <mappe>` (typisk `/mnt/user-data/uploads` eller prosjektmappen). Den klassifiserer HLD, vedlegg, kommentarregistre (og om de er besluttet), prisliste, tilbud, etableringsplan, figurer og PDF-er, og foreslår neste steg. Bruk funnene til å **utelate spørsmål** og til å gi menyen en kort forhåndsoppsummering («Jeg ser HLD med 6 åpne fagteamkommentarer, en prisliste og et tilbudssvar»). Spør aldri om noe filene eller samtalen allerede har svart på.

### 1–3. Spørsmål med flervalg
Bruk verktøyet `ask_user_input_v0`. Spørsmålstreet ligger i `assets/sporsmalstre.json` (runde 0, én detaljrunde per valg, planbekreftelse, mal for konfliktvalg). Regler som verktøyet krever:
- **Maks 3 spørsmål per kall, 2–4 alternativer per spørsmål**, korte etiketter. Treet er validert mot dette (`python scripts/valider_sporsmal.py assets/sporsmalstre.json`); hvis du endrer det, kjør valideringen.
- Skriv en kort setning (1–2) *før* kallet – aldri vis knapper uten ord rundt.
- **Etter kallet er turen din over.** Svaret kommer som neste melding. Ikke skriv videre eller svar for brukeren.
- `multi_select` der flere valg gir mening (oppgaver, fagområder, vedleggstyper, figurer); `single_select` for alt som utelukker hverandre.
- Fritekst er alltid velkommen: «Skriv hvis det er noe annet». Hvis brukeren svarer med tekst i stedet for knapper, bruk teksten.
- Hopp over et spørsmål hvis `hopp_over_hvis` er oppfylt eller skanningen allerede besvarer det.
- **Verktøyet mangler** (annet miljø)? Presenter samme spørsmål som nummerert liste i tekst og be om «svar med tallene, flere er ok».

**Runde 0** er ett flervalgsspørsmål: Skrive/sjekke HLD · Bygge/oppdatere vedlegg · Gå gjennom kommentarer · Lage figurer eller PDF-rapporter. Brukeren kan velge flere.
**Runde 1** er detaljrunden for hvert valg, i tur og orden (en runde per valgt oppgave – ikke slå dem sammen til mer enn 3 spørsmål).
**Plan** (runde 3) viser du som kort nummerert liste *før* bekreftelsesspørsmålet: trinn · skill · hva som leveres · hvor jeg stopper for din beslutning. Alternativer: Kjør · Endre planen · Vis først hva som vil skje.

### Rekkefølge når flere oppgaver er valgt
Fast avhengighetsrekkefølge (se `references/ruting.md`): **kommentarregistre/konfliktsjekk → HLD → vedlegg → figurer → PDF**. Beslutninger flyter nedstrøms (HLD-beslutninger styrer vedleggene, teksten styrer figurene, ferdige filer styrer PDF-ene). Fordi kommentarløpet og konfliktsjekken har *menneskelige stopp*, gjør du først det som kan gjøres uten beslutning (lag registre, kjør konfliktsjekk, kjør lint) og setter resten i kø: «Etter at du har besluttet: gjennomfør → oppdater vedlegg → oppdater figurer → lag PDF».

### 4. Kjør
For hvert trinn: les skillens instruksjoner (`moduler/<navn>/MODUL.md`, eller SKILL.md hvis installert separat), følg dem fullt ut, og bruk skillens skript. Hold brukeren oppdatert med én linje per trinn («Trinn 2/4 – kommentarregistre: ferdig, ligger i …»).

### 5. Stopp-punkter som flervalg
Skillene stopper med vilje (kontraktskonflikt, registre som venter på beslutning). Presenter stoppen som flervalg der det passer:
- **Kontraktskonflikt:** ett `single_select`-spørsmål per konflikt (maks 3 per kall) etter `mal_konfliktvalg`: «A: følg tilbudet · B: følg prislisten · Hold åpen – avklares med PL». Legg alltid de konkrete konsekvensene i teksten *over* knappene (fra konfliktrapporten), slik at valget er informert. Skriv valget inn i konfliktrapporten som «besluttet av [bruker] [dato]». Er det mer enn 3 konflikter, ta dem i flere runder.
- **Kommentarregistre:** beslutningen tas i registrenes «Revisjonskommentar»-kolonne (stor tekstmengde passer ikke i knapper). Be brukeren laste dem opp igjen. Du kan tilby flervalg for *avklaringene* øverst i registrene.
- Ta aldri et stoppvalg for brukeren, og gjenbruk ikke et tidligere valg på et nytt punkt.

### 6. Avslutt
Gi en kort status (hva er gjort, hva venter på hvem) og vis menyen igjen med bare de valgene som nå gir mening (f.eks. etter registre: «Jeg har fylt ut registrene – gjennomfør» · «Lag PDF-lesekopi» · «Ferdig for nå»).

## Det du husker gjennom økten
Kunde og prosjekt · hvilke filer som finnes og hvor · valgte oppgaver og plan · beslutninger tatt (konflikter, kommentarregistre) · åpne punkter · språk (norsk som standard). Spør bare etter kundenavn hvis det ikke fremgår av filene.

## Referanser
- `references/ruting.md` – oppgave → skill, avhengigheter, stopp, nøkkelord for direkte ruting
- `references/dialogeksempler.md` – eksempler på innledning, spørsmål og plan
- `assets/sporsmalstre.json` – alle spørsmål og alternativer (rediger her, valider etterpå)
- `scripts/skann_prosjekt.py`, `scripts/valider_sporsmal.py`
- `moduler/` – de fem underskillene (komplette)
