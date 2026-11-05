# Kommentar-ID og mapping

Word renummererer kommentar-ID-er når dokumentet lagres eller flettes. Et register bygget på forrige versjon kan derfor referere til ID-er som i dagens fil peker på andre kommentarer.

## Regler
1. Ekstraher fra filen du skal endre, rett før du lager `spec.json`.
2. I `spec.json` kan `lukker` angis som `"Forfatter|første tegn av kommentaren"` i stedet for tall. Skriptet løser den mot dokumentets egne kommentarer og avbryter hvis den ikke gir nøyaktig ett treff. Foretrekk dette når registeret ble laget på en eldre versjon.
3. Når du mapper et eldre register til ny fil: match på forfatter + eksakt tekst. Tråder: finn forelderen først, svaret via `forelder`. Kommentarer med lik tekst fra samme forfatter (f.eks. «Se over») er tvetydige; bruk anker/avsnitt som tiebreaker, eller spør.
4. Behold registrenes nummer i endringsloggteksten (det er dem brukeren og fagteamet har forholdt seg til), men la skriptet slå dem opp i filens egne ID-er. Si fra i svaret at ID-ene i filen kan avvike.
5. Endringslogg-kommentarene du selv har lagt til har egne ID-er; utelat dem i nye uttrekk med `--utelat-forfatter "Endringslogg"`.
