---
name: topologifigurer
description: Lager og reviderer topologi-/arkitekturfigurer (Figur 1 «topologiskisse» og Figur 2 «nettverkstopologi») for HLD i Intilitys Bifrost-inspirerte stil — SVG som master, på høyt nivå med soner, bokser og korte blokkpiler (ingen forbindelseslinjer), fargelag per plattform, overflow-sjekk, PNG til Word og A4-liggende PDF. Bruk når brukeren ber om en figur, tegning, skisse, topologi, arkitekturdiagram eller nettverksdiagram til et designdokument, vil «fiffe opp» eller modernisere en figur, skal rette tekst i en figur etter kommentarer, bytte figur i Word, eller spør om Lucid. Utløs også når figurtekst må avstemmes mot HLD-teksten.
---

# Topologifigurer

Lager figurene i HLD-en. Figurene er *dokumenter*: de må stemme med HLD-teksten og kontrakten like nøye som prosa. I praksis hang figurene tre–fire rettinger bak teksten (foreldede produktnavn, opsjoner tegnet som om de inngikk, kapitler som var fjernet).

## Prinsipper
1. **SVG er masteren.** PNG (til Word) og PDF (til deling) rendres fra SVG. Endre aldri bare PNG-en.
2. **Høyt nivå.** Soner → bokser med 1–5 korte tekstlinjer → **korte blokkpiler i mellomrommene mellom sonene**, kun mellom ytterste bokser/soner. **Ingen detaljerte forbindelseslinjer** (de blir uleselige og må vedlikeholdes). Etiketter på linjer droppes med linjene.
3. **Teksten følger HLD-teksten.** Samme navn, samme avgrensning. Står noe som opsjon (antall 0), tegnes det ikke som inngående – ta det ut eller merk «opsjon» (stiplet boks). Overgangsforhold (avgivende parts miljø, migreringslinje) hører normalt til migreringskapitlet, ikke målbildefiguren, hvis brukeren vil ha figuren på målbildenivå.
4. **Tekst kortes ned – skriftstørrelsen krympes ikke.** Når en linje går ut av boksen: forkort teksten eller utvid boksen. Skriftstørrelse kan reduseres bare for én-to lange linjer, via `skriftstr` på boksen.
5. **Ikke tilbakefør brukerens egne redigeringer.** Hvis brukeren har rettet i et verktøy (Lucid, PowerPoint) og laster opp bildet, er de rettelsene fasit for *hva som skal ut*; HLD-teksten er fasit for *ordlyd*. Avstem, og si hva du ikke fulgte og hvorfor.
6. **Avviksliste.** Etter hver figurrunde: list opp hva som ble endret, hva som bevisst ikke ble endret (venter på avklaring), og eventuelle produktvalg i figuren som ennå ikke står i teksten.

## Arbeidsflyt
1. **Les relevante HLD-kapitler** (og kommentarregistre hvis figuren skal revideres). Lag en liste over hva figuren skal vise og hva som er opsjon/utenfor.
2. **Skriv spec (JSON)** – start fra `assets/eksempel_spec.json`. Felt: `tittel, bredde, hoyde, soner[{tittel,x,y,b,h,farge,bokser[{x,y,b,h,tittel,linjer,type}]}], stripe, piler[{retning,x,y1,y2}], tegnforklaring`. Fargene: `blue` (kundens lokasjoner/InCloud), `purple` (Azure), `green` (Microsoft 365/SaaS), `navy` (Intilitys plattformlag), `neutral`, `amber`. Bokstyper: `box`, `ot`, `dmz`, `dark`, `dashed`, `tr`.
3. **Generer:** `python scripts/lag_figur.py spec.json figur.svg`
4. **Sjekk overflow – alltid:** `python scripts/sjekk_overflow.py figur.svg` (exit 1 ved funn). Rett til den sier OK.
5. **Se på resultatet.** Render PNG (`python scripts/render.py figur.svg --png-mappe ut/`) og se på bildet selv. Sjekk lesbarhet, at piler peker riktig, og at intet står i veien.
6. **Til Word:** `python scripts/bytt_bilde_i_docx.py dok.docx --liste` viser bildene med nærmeste tekst (mediefilnavn er *ikke* figurnummer). Bytt med `--media imageN.png --med figur.png --ut ny.docx` – bredden beholdes og høyden følger sideforholdet. Oppdater figurbeskrivelsen i teksten (se under) via kommentarløpet hvis dokumentet er under revisjon.
7. **Lesekopi:** `python scripts/render.py f1.svg f2.svg --pdf figurer_A4_liggende.pdf` (vektor, én figur per side).

## Figurtekst i dokumentet
Under hver figur: bildetekst «Figur N: …» og én figurbeskrivelse som sier hva figuren viser og at pilene angir hovedretning. Beskriv forbindelsene enten i figuren eller i teksten – ikke begge deler. Henvis til kapittel for overgangsforhold som ikke er tegnet.

## Stil, farger og typografi
Se `references/stil.md`. Kort: hvit bakgrunn, avrundede kort, fargelag per plattform, dempede blokkpiler (#9FB3CF), Liberation Sans/Arial, 11.5–13 px brødtekst i figuren.

## Lucid og andre verktøy
Import av SVG til Lucid gir redigerbare former, men Lucid gjør linjer om til connectors som rutes på nytt, og legger tegnforklaringslinjer oppå tekst. Bruk det derfor bare som speil for visning/kommentering – ikke som master – med mindre brukeren velger Lucid som master (da er SVG-kildene foreldet). Detaljer og alternativer: `references/lucid-og-word.md`.

## Referanser
- `references/stil.md` – palett, typografi, pilgeometri, layoutregler
- `references/lucid-og-word.md` – Lucid, Word-tillegg, eksport
- `assets/eksempel_spec.json` – anonymisert eksempel
- `scripts/lag_figur.py`, `sjekk_overflow.py`, `render.py`, `bytt_bilde_i_docx.py`
