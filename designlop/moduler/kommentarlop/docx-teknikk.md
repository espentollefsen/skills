# docx-teknikk

## Hvor ligger kommentarene
- `word/comments.xml`: selve kommentarene (`w:comment` med id, author, date, initials; innhold i `w:p`). Hvert kommentaravsnitt kan ha `w14:paraId`.
- `word/document.xml`: ankeret – `w:commentRangeStart`/`w:commentRangeEnd` rundt teksten og en `w:r` med `w:commentReference` på slutten.
- `word/commentsExtended.xml`: `w15:commentEx` per kommentar, nøklet på paraId til *siste* avsnitt i kommentaren. `w15:done="1"` = «ferdig» (Word viser «Task completed»); `w15:paraIdParent` peker på forelderens paraId (svar i tråd).

## Hva skriptene gjør
- `ekstraher.py`/`docxlib.py` leser alt over uten Word.
- `bruk_endringer.py` redigerer tekst (beholder første tekstløps formatering; løp som bærer kommentarreferanser bevares), legger nye kommentarer med python-docx (`add_comment`), lukker eksisterende (setter `done=1` for kommentaren og alle svar i tråden) og oppretter `commentsExtended.xml` (med relasjon og content-type) hvis den mangler. Retter også python-docx sin `w:zoom`-feil slik at fila validerer.

## Begrensninger å kjenne
- Inline-formatering inne i et avsnitt (fet/kursiv midt i setningen) går tapt når avsnittet erstattes; bruk `erstatt_tekst` for å røre så lite som mulig.
- Tekst i hyperlenker, felt og innholdsfortegnelse behandles ikke. Innholdsfortegnelsen må oppdateres i Word (eller LibreOffice) etter endringer.
- Lukking virker på kommentarer; endringslogg-kommentarer du legger til står åpne og lukkes av brukeren.
- Tabellrader slettes via `slett_tabellrad` + `anker`.

## Validering
`python /mnt/skills/public/docx/scripts/office/validate.py fil.docx [--original forrige.docx]` – kjør etter hver gjennomføring. Antall avsnitt skal endres bare med antall slettede/innsatte avsnitt.
