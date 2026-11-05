---
name: kommentarlop
description: Kommentarløpet for HLD og vedlegg — trekker ut Word-kommentarer fra fagteam, lager kommentarregistre per fagområde (original tekst, kommentar, forslag, kilde og en tom «Revisjonskommentar»-kolonne), leser brukerens beslutninger tilbake, gjennomfører godkjente endringer i dokumentene med endringslogg-kommentarer som inneholder den opprinnelige kommentaren ordrett, og lukker de opprinnelige kommentarene (inkl. svartråder). Bruk når brukeren nevner kommentarer fra fagteam/kunde, kommentargjennomgang, kommentarregister, endringslogg, «lukk kommentarer», «gjennomfør endringene», «oppdater dokumentet etter kommentarene», eller laster opp et docx med kommentarer. Stopper alltid for brukerens beslutning før noe endres.
---

# Kommentarløpet

Gjør fagteamenes Word-kommentarer om til sporbare endringer i HLD og vedlegg. Løpet har en hard stoppregel: **ingenting i HLD eller vedlegg endres før brukeren har besluttet** (registeret er beslutningsunderlaget). Uten den regelen havner endringer i dokumentet som brukeren ikke ville hatt – og endringsloggen mister verdi.

Løpet har seks trinn. Trinn 1–3 og 5–6 gjør du; trinn 4 gjør brukeren.

```
1 Ekstraher → 2 Forslag per fagområde → 3 Registre (tom revisjonskolonne)
      → 4 BRUKEREN beslutter (stopp) → 5 Gjennomfør + logg + lukk → 6 Verifiser og oppdater vedlegg
```

## 1. Ekstraher
`python scripts/ekstraher.py HLD.docx kommentarer.json --kun-apne --utelat-forfatter "Endringslogg"`
- Gir id, forfatter, dato, tekst, anker (markert tekst), hele avsnittet, nærmeste overskrift med nummer, ferdig-status og trådstruktur (svar peker på forelder).
- **ID-ene kan endres av Word mellom versjoner.** Ekstraher alltid på nytt fra den filen du faktisk skal endre, og ikke gjenbruk ID-er fra et gammelt register uten å matche på forfatter + tekst (se `references/id-og-mapping.md`).
- Svar i tråd leses sammen med forelderen; en kommentar som er svar vises ikke som egen rad.

## 2. Forslag per fagområde
Gruppér etter fagperson/fagområde (identitet, workplace, nettverk, lisens, sikkerhet, applikasjon, migrering). For hver kommentar:
- Hva sier kommentaren? Er det en rettelse, et spørsmål, en kildeutfordring, eller noe som krever en kontraktsavgjørelse?
- Sjekk mot kilder (kontrakt, tjenestebeskrivelse, register). Svar på kildespørsmål med konkret henvisning – fagteam spør ofte «hvor er dette hentet fra?» og fortjener et presist svar.
- Foreslå ny tekst *ordrett*, ikke «omformuler». Foreslå «ingen endring» med begrunnelse når kontrakten går foran standarden eller kommentaren bygger på en misforståelse.
- Finner du en kontraktskonflikt eller et behov for omfangsendring: **flagg til brukeren som avklaring, ikke løs den i forslaget** (se `hld-bygger`).
- Samme problem i flere dokumenter: foreslå følgeendringer i vedleggene (tabell nederst i registeret).
Gode beslutningsmønstre og hvordan kommentarer sorteres: `references/beslutningsmonstre.md`.

## 3. Registre
Lag ett register per fagområde: `python scripts/lag_register.py register.json register.docx`.
Syv kolonner: **# · Sted · Opprinnelig tekst i dokumentet · Kommentar · Forslag til ny tekst/tiltak · Kilde og merknad · Revisjonskommentar**. Siste kolonne er **tom** og forbeholdt brukerens egne notater/beslutninger (grå bakgrunn). Øverst: avklaringer som må tas før endring. Nederst: følgeendringer i andre dokumenter. Format: A4 liggende, ikke endre kolonnenavn (`les_register.py` leter etter dem). Mal og felt: `references/registermal.md`.

Hvis dokumentet har vedlegg (A–F), bygg også vedleggstabellen i samme register: én rad per endring i vedlegget, med «HLD-beslutning» som grunnlag. Ikke endre vedleggsfilene i dette trinnet.

## 4. Brukeren beslutter (STOPP)
Lever registrene og vent. Brukeren fyller «Revisjonskommentar» (Godkjent / Underkjent / Avventer / egen tekst). Ikke fyll ut kolonnen selv for HLD-radene. Spør heller enn å anta når en rad er tom.

## 5. Gjennomfør, logg og lukk
Når brukeren melder tilbake med registre (evt. opplastet på nytt): `python scripts/les_register.py register.docx beslutninger.json` gir radene med revisjonskommentar.
Lag deretter `spec.json` for `scripts/bruk_endringer.py` og kjør:
`python scripts/bruk_endringer.py HLD.docx spec.json HLD_ny.docx`
- **Godkjent** → gjennomfør som foreslått (eller med brukerens justering).
- **Underkjent** → gjennomfør ikke; bruk `kun_logg` bare hvis kommentaren skal besvares.
- **Avventer** → ingen tekstendring, `kun_logg` med statusnotat, og *ikke* i «lukker» (kommentaren holdes åpen med vilje).
- **«Teksten står»** (svar til fagteamet) → `kun_logg` med forklaringen, kommentaren lukkes.
Skriptet validerer alle «finn» først og avbryter uten å skrive hvis ett ikke gir nøyaktig ett treff. Hver endring får en **endringslogg-kommentar** forankret i det endrede avsnittet, med: *hva ble endret* + *grunnlag* + *opprinnelig kommentar ordrett* («Opprinnelig kommentar Forfatter #id (dato): «…»»). De opprinnelige kommentarene (og svartråder) settes til ferdig. Detaljer og spec-format: `scripts/bruk_endringer.py` (docstring) og `references/docx-teknikk.md`.

## 6. Verifiser og oppdater vedlegg
1. Ekstraher på nytt fra utfilen: alle behandlede originalkommentarer skal være ferdig; de bevisst åpne skal være åpne; antall loggkommentarer skal tilsvare antall endringer.
2. Kjør `hld-bygger/scripts/hld_lint.py` på utfilen (kryssreferanser, forutsetningsnivå, forbudte termer).
3. Valider docx (`/mnt/skills/public/docx/scripts/office/validate.py`).
4. Så oppdater vedleggene etter registrenes vedleggstabeller (egen forespørsel: se `vedlegg-bygger`). Vedlegg har **ikke** endringslogg – sporbarheten ligger i HLD-kommentarene.
5. Er det figurer som berøres? Se `topologifigurer`.
6. Lever med en kort status: antall endret, antall lukket, hva som holdes åpen og hvorfor.

## Regler som ikke kan brytes
- Endre aldri HLD/vedlegg før trinn 4 er gjort. Bare registrene endres i trinn 1–3.
- Hold endringene kirurgiske: bare det registeret godkjenner. Omskriving av avsnitt utover det skaper nye feil andre steder.
- Skriv endringslogg ordrett etter malen; ikke parafraser opprinnelig kommentar.
- Én loggkommentar per endring; samme endring som lukker flere kommentarer (forfatter + svar) samles i én loggkommentar.
- Rapporter alltid det du ikke fikk til (en kommentar uten anker, en rad som ikke ble funnet).

## Referanser
- `references/registermal.md` – JSON-format og innhold i registeret
- `references/beslutningsmonstre.md` – godkjent/underkjent/avventer, rene konsekvenser vs. formvalg, kontraktsflagg
- `references/id-og-mapping.md` – Words ID-renummerering og hvordan du matcher
- `references/docx-teknikk.md` – hvordan kommentarer, tråder og «ferdig»-status ligger i docx
- `scripts/` – `ekstraher.py`, `lag_register.py`, `les_register.py`, `bruk_endringer.py`, `docxlib.py`
