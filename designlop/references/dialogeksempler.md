# Dialogeksempler

## A. Uklar start
Bruker: «Hjelp meg med designdokumentene for Nordlys.»
Du kjører skanningen, så: «Jeg ser en HLD med 6 åpne fagteamkommentarer, en prisliste og et tilbudssvar, og ingen vedlegg ennå. Hva vil du gjøre? (velg gjerne flere)» → `ask_user_input_v0`, runde 0, med alternativene fra treet.

## B. Tydelig forespørsel – ingen meny
Bruker: «Lag PDF av Vedlegg A.»
Du: kjør `vedlegg_lint` → `pdf-rapport` direkte. Ingen spørsmål, med mindre noe mangler (da ett spørsmål).

## C. Flere valg → plan
Bruker valgte «Gå gjennom kommentarer» + «Lage figurer eller PDF-rapporter».
Etter detaljrunde (fagområder: Nettverk; figurer: Figur 2; byttes inn i HLD: ja) viser du:

> **Plan**
> 1. *Nå* – `kommentarlop`: ekstraher, lag nettverksregister (HLD + Vedlegg C) → **stopp for din beslutning**
> 2. *Etter beslutning* – gjennomfør i HLD med endringslogg, lukk kommentarer
> 3. *Etter 2* – oppdater Vedlegg C etter HLD-beslutningene
> 4. *Etter 2* – `topologifigurer`: oppdater Figur 2, bytt inn i HLD, PDF
> Skal jeg starte på trinn 1?

→ bekreftelsesspørsmål: Kjør · Endre planen · Vis først hva som vil skje.

## D. Konfliktvalg som flervalg
Over knappene (tekst): «K-01 Mac: tilbudet lover macOS-støtte, prislisten har Managed Mac Client som opsjon (antall 0). A → «Mac forvaltes med Intune», krever Bilag 9. B → «Mac er opsjon og inngår ikke i grunnleveransen». K-02 Mikrosegmentering: …»
Spørsmål 1: «K-01 Mac – hva skal HLD-en si?» [A: følg tilbudet · B: følg prislisten · Hold åpen – avklares med PL]
Spørsmål 2: «K-02 Mikrosegmentering – hva skal HLD-en si?» [samme alternativer]

## E. Avslutning
«Trinn 1 er ferdig: tre registre ligger i … Jeg stopper her til du har fylt ut revisjonskolonnen. Hva nå?» → [Jeg har fylt ut registrene – gjennomfør · Lag PDF-lesekopi av registrene · Ferdig for nå]
