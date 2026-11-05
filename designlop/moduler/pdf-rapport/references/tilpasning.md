# Tilpasning av rapporter

## Bibliotek (`scripts/rapport_lib.py`)
- `kpi_row([(tittel, verdi, undertekst, sone), …])` – rad med nøkkeltallskort (3–5 stk.)
- `table(header, rows, widths=None, zone='neutral', status_cols=(i,))` – tabell med navy hode, sebrastriper i sonefarge, valgfri statuskolonne med merker
- `autowidths(header, rows)` – fordeler bredde etter innholdslengde
- `pill(tekst, farge)` – statusmerke; `STATUS_COLORS` styrer hvilke ord som får hvilken farge (utvid ved behov)
- `bullets([...])`, `H1/H2/H3/P/BODY/SM/CELL` – stiler, `esc()` – XML-escape
- `bygg(sti, tittel, bunntekst, story)` – skriver PDF (A4 liggende, marg 14 mm, side-nummer, bunntekst)

## Eksempel på spesialrapport
```python
import sys; sys.path.insert(0, '<skill>/scripts')
from rapport_lib import *
story = [Paragraph('Kunde', KICK), Paragraph('Tittel', H1), kpi_row([('Antall', '40', 'underlag', 'blue')]),
         Paragraph('Tabell', H2), table(['Navn','Status'], [('A','Bekreftes')], [0.7,0.3], status_cols=(1,))]
bygg('ut.pdf', 'Tittel', 'Kunde · Tittel · v1 · Konfidensielt', story)
```

## Lesbarhet
- Maks 9 kolonner på A4 liggende. Flere → del tabellen eller utelat kolonner som er interne.
- Lange merknader hører i siste kolonne; gi den størst bredde.
- Gruppér når en kolonne har få distinkte verdier (leveransemodell, plattform, status); ellers sorter.
- Ikke gjenta kvittering og åpne punkter i flere tabeller.

## Feil å se etter ved gjennomlesing
Avkuttet tekst i smale kolonner · statusmerker som ikke ble gjenkjent (vises som ren tekst) · feil nøkkeltall pga. endret kolonnenavn · sider med nesten tomme tabeller (flytt sideskift) · tegn som mangler i fonten.
