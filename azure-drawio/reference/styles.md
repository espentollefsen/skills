# Styles, Colours, Fonts & XML Escaping

`scripts/emit.py` generates all of this for you. Read this file when you are hand-editing a
diagram, debugging one, or adding a new element type to the emitter.

## XML escaping — read this before writing any `value=`

Labels are HTML *inside* an XML attribute, so every markup character is escaped **twice over**
relative to how it reads. Getting this wrong produces a file draw.io refuses to open, and is the
single most common failure in hand-written output.

| You want to render | Write in `value=` |
|---|---|
| `<b>` … `</b>` (bold) | `&lt;b&gt;` … `&lt;/b&gt;` |
| `<br>` (line break) | `&lt;br&gt;` |
| `<div>`, `<ul>`, `<li>` | `&lt;div&gt;`, `&lt;ul&gt;`, `&lt;li&gt;` |
| a literal `&` | `&amp;amp;` |
| a non-breaking space | `&amp;nbsp;` |
| a literal `"` | `&quot;` |
| `·` `→` `←` `↓` | literal UTF-8 — safe, no escaping |

Canonical pair — this label:

> **kv-invoicing-prod**
> Key Vault · Standard (Private Endpoint)

is written:

```xml
value="&lt;b&gt;kv-invoicing-prod&lt;/b&gt;&lt;br&gt;Key Vault · Standard (Private Endpoint)"
```

In a spec file for `emit.py`, write labels in plain readable form (`<b>name</b><br>text`) — the
emitter escapes them. Everywhere else in this skill, label formats are shown in readable source
form; escape them yourself before emitting, then run `scripts/validate_drawio.py`.

## Fonts

Bifrost uses **Satoshi** for headings and **Open Sans** for body text.

Both must be written as font *stacks*. Verified by render: a bare `fontFamily=Open Sans` and the
Google-Fonts `fontSource=` mechanism **both fall back to a serif** in draw.io when the font is
missing, which looks nothing like Bifrost. A stack falls back to a sane sans instead.

| Use | `fontFamily=` |
|---|---|
| Title / headings | `Satoshi Intility, Satoshi, Helvetica, Arial, sans-serif` |
| Everything else | `Open Sans, Helvetica, Arial, sans-serif` |

Text colour is `fontColor=#071627` (Bifrost `base-c`) rather than pure black.

Satoshi Intility and Open Sans are both installed on Intility machines (see the Bifrost
typography docs for the G:-drive paths). The stacks mean a diagram still looks right when shared
with someone who has neither.

## Palettes

Two themes. `bifrost` is the default; `classic` preserves the original hand-picked palette.

**Colour follows scope, nothing else.** There is one colour per scope —
`online` / `connectivity` / `management` / `corp` — and no second shade for a second
subscription in the same scope. Two corp subscriptions in one diagram (e.g. a shared-services
corp subscription and a workload corp subscription) both get the ordinary corp colour; their
MG/Sub/RG header segments are what tell them apart, not the fill. `emit.py` falls back to `corp`
and warns if a spec asks for a scope outside this list — there is no "secondary corp" palette to
fall back to instead.

Bifrost values come from the RGB-HEX table in the Bifrost colour docs, which is the sanctioned
source when CSS variables are not an option — a `.drawio` file is exactly that case. Light-mode
values only, since a diagram has no colour-scheme switch.

### Bifrost (default)

| Element | Fill | Stroke | Bifrost token |
|---|---|---|---|
| external clients | `#e3e3e8` | `#3d4c5c` | neutral-fade / neutral-fade-c |
| online | `#e7dcfe` | `#631cce` | chill-fade / chill |
| connectivity | `#fff5c7` | `#99620a` | warning-fade / warning-fade-c |
| corp | `#d8fdf8` | `#007375` | brand-fade / brand |
| InCloud | `#f3f3f6` | `#565776` | base / base-c-2 |
| notes header | `#007375` | `#007375` | brand (white text, `brand-hc`) |
| notes body | `#ffffff` | `#d3d3df` | base-3 / base-dimmed |
| Direct Link edge | — | `#565776` | base-c-2 |
| peering edge | — | `#888888` | neutral grey |

Corp gets Intility's brand teal because it holds the customer's own workload; connectivity gets
warning-amber because it is the shared Intility platform layer; online gets chill-purple to mark
internet exposure. VNet and subnet strokes reuse their band's stroke colour — the dash patterns
(`8 4` vs `3 3`) already distinguish the two levels, so no extra colours are needed.

### Classic

| Element | Fill | Stroke |
|---|---|---|
| external clients | `#FAEEDA` | `#854F0B` |
| online | `#F3EDF7` | `#7B1FA2` |
| connectivity | `#FAECE7` | `#993C1D` |
| corp | `#E6F1FB` | `#185FA5` |
| InCloud | `#F1EFE8` | `#444441` |
| notes (header and body) | `#b0e3e6` | `#0e8088` |

## Container styles

**Corner radius is fixed, not relative.** `rounded=1` alone scales the corner radius with the
box's own size, so the same style renders a subtle curve on a small subnet box and an
exaggerated, pill-like curve on a large band. Every container style below therefore also sets
`absoluteArcSize=1;arcSize=10;`, which fixes the radius at 10px regardless of box size — bands,
VNets, subnets and notes cards all get the same corner, no matter how tall or wide they are.

### Subscription / management-group bands — solid fill, `strokeWidth=2`

```xml
rounded=1;absoluteArcSize=1;arcSize=10;whiteSpace=wrap;html=1;fillColor={FILL};strokeColor={STROKE};strokeWidth=2;fontSize=12;verticalAlign=top;fontStyle=1;align=left;spacingLeft=15;spacingTop=10;fontColor=#071627;fontFamily=Open Sans, Helvetica, Arial, sans-serif;
```

Azure scope bands carry **`value=""`** — their label is three separate icon+text header segments
(see SKILL.md → *Band header*). Only the clients and InCloud bands put a label on the band cell.

### VNet boxes — dashed `8 4`, no fill, `spacingLeft=42`

```xml
rounded=1;absoluteArcSize=1;arcSize=10;whiteSpace=wrap;html=1;fillColor=none;strokeColor={STROKE};dashed=1;dashPattern=8 4;fontSize=11;verticalAlign=top;align=left;spacingLeft=42;spacingTop=8;fontStyle=1;
```

`spacingLeft=42` clears the 27px-wide VNet header icon at `vnet_x+8`.

### Subnet boxes — dashed `3 3`, no fill, `spacingLeft=38`

```xml
rounded=1;absoluteArcSize=1;arcSize=10;whiteSpace=wrap;html=1;fillColor=none;strokeColor={STROKE};dashed=1;dashPattern=3 3;fontSize=11;verticalAlign=top;align=left;spacingLeft=38;spacingTop=6;
```

`spacingLeft=38` clears the 18px-wide subnet header icon at `snet_x+15`.

### Text cells

```xml
text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;fontSize=11;fontColor=#071627;fontFamily=Open Sans, Helvetica, Arial, sans-serif;
```

`fontSize=10` for NSG labels and private-DNS-zone labels. `fontSize=16;fontStyle=1` plus the
heading stack for the title.

### Notes panel

Header (brand fill, white text, heading font):

```xml
rounded=1;absoluteArcSize=1;arcSize=10;whiteSpace=wrap;html=1;fillColor=#007375;strokeColor=#007375;strokeWidth=2;fontSize=13;verticalAlign=middle;align=left;spacingLeft=12;fontStyle=1;fontColor=#ffffff;
```

Category cards (white, dimmed border, height computed from content):

```xml
rounded=1;absoluteArcSize=1;arcSize=10;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d3d3df;strokeWidth=2;fontSize=10;verticalAlign=top;align=left;spacingLeft=8;spacingTop=6;
```

## Edge styles

```xml
<!-- HTTPS ingress: clients → AGW VNet -->
endArrow=classic;html=1;rounded=0;fontSize=11;edgeStyle=orthogonalEdgeStyle;

<!-- VNet peering: band → band, no arrowheads -->
endArrow=none;startArrow=none;html=1;rounded=0;dashed=1;dashPattern=6 3;strokeColor=#888888;strokeWidth=1.5;fontSize=10;exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;

<!-- Direct Link / S2S VPN: vpng icon ↔ InCloud band -->
endArrow=classic;startArrow=classic;html=1;rounded=0;strokeColor=#565776;strokeWidth=2;fontSize=10;
```
