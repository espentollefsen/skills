# Ruting

## Oppgave → skill
| Brukerens ønske (stikkord) | Skill | Første handling | Stopper for brukeren når … |
|---|---|---|---|
| HLD, løsningsdesign, kapittel, «står dette i kontrakten», opsjon, scope | `hld-bygger` | Inventar av kilder → `opsjon_sjekk.py` | kontraktsdokumenter er i konflikt |
| vedlegg, register, detaljdesign, LLD, kvitteringstabell, ÅP, «oppdater mot IntIpaas», ett vedlegg per fagområde vs referansedokument | `vedlegg-bygger` | Les HLD-kapittel + forutsetninger → spec → bygg → `vedlegg_lint.py` | struktur (A/B) ikke er avgjort; kontraktskonflikt |
| kommentarer, fagteam har kommentert, register, endringslogg, lukk, gjennomfør | `kommentarlop` | `ekstraher.py` → registre | alltid etter registre (beslutning) |
| figur, topologi, tegning, skisse, SVG, Lucid, «fiffe opp», bytt figur | `topologifigurer` | Les HLD-tekst → spec → `sjekk_overflow.py` | figurinnhold avhenger av uavklart punkt (f.eks. fjerntilgang) |
| PDF, lesekopi, presentabel, «mer inspirerende», del med ARF | `pdf-rapport` | `vedlegg_lint.py` først → rapport | – |

Direkte ruting uten meny: hvis forespørselen inneholder stikkord fra bare én rad, gå rett til den skillen.

## Avhengigheter (rekkefølge ved flere oppgaver)
1. **Konfliktsjekk / kommentarregistre** – kan gjøres uten beslutning, men *avgjør* hva som skal skrives.
2. **HLD** (skriv/revider). Hvis HLD finnes med fagteamkommentarer: bruk `kommentarlop` for å endre – ikke rediger direkte.
3. **Vedlegg** følger HLD-beslutningene (forslag bygger på dem; rene konsekvenser kan forhåndsgodkjennes).
4. **Figurer** følger HLD-teksten og vedleggene (ikke omvendt).
5. **PDF-rapporter** sist, fra de ferdige kildefilene.

Hvert ledd med et menneskelig stopp setter resten i kø. Si tydelig i planen hva som kjøres nå og hva som kjøres etter beslutning.

## Typiske kombinasjoner
- **Ny kunde fra scratch:** konfliktsjekk → (valg) → HLD-disposisjon og kapitler → vedlegg → figurer → PDF.
- **Etter fagteamrunde:** registre (stopp) → gjennomfør + logg + lukk → vedlegg etter HLD-beslutninger → figurer → PDF.
- **Oppdatere mot register:** skann → `vedlegg-bygger` (oppdater) → lint → PDF.
- **Levere pakke:** lint alt → PDF-lesekopier → figur-PDF → oppsummering av åpne punkter.

## Kvalitetsport før levering (uansett rute)
`hld_lint.py` på HLD · `vedlegg_lint.py` på alle vedlegg · `sjekk_overflow.py` på figurer · docx-validering · se på 2–3 sider av hver PDF.
