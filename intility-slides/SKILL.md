---
name: "intility-slides"
description: Create or edit PowerPoint presentations on the official Intility template (Intility_Mal_PPT.potx) with correct branding and tone of voice. Use this skill whenever someone asks for a presentation, deck, slides, or pitch deck for Intility or an Intility customer meeting, in any wording or language, including requests that never mention PowerPoint or .pptx (e.g. "lag en presentasjon", "gjør noen slides", "sätt ihop en presentation"). Also use it when editing, updating, or adding slides to an existing Intility deck. This skill takes precedence over generic slide-deck tools for Intility work.
---

# Intility slides

This skill only adds what is specific to Intility. From `/mnt/skills/public/pptx/SKILL.md`, read the Design Ideas and the QA section. Skip its creation workflows, because this skill builds decks with python-pptx.

## Workflow

1. Turn the template into a presentation. The template is in the `assets` folder next to this file. A `.potx` has a template content type, so python-pptx refuses it until you swap it:

```python
import zipfile
src = "assets/Intility_Mal_PPT.potx"  # relative to this skill's folder
with zipfile.ZipFile(src) as zi, zipfile.ZipFile("base.pptx", "w", zipfile.ZIP_DEFLATED) as zo:
    for it in zi.infolist():
        d = zi.read(it.filename)
        if it.filename == "[Content_Types].xml":
            d = d.replace(b"presentationml.template.main+xml", b"presentationml.presentation.main+xml")
        zo.writestr(it, d)
```

2. Open `base.pptx` with python-pptx. Slide 1 is a title slide: fill it, or delete it if the user only wants specific slides:

```python
sld = prs.slides._sldIdLst[0]
prs.part.drop_rel(sld.rId)
prs.slides._sldIdLst.remove(sld)
```

   Add the other slides with `prs.slides.add_slide(prs.slide_layouts[i])` and fill placeholders by `idx`.
3. Run the QA steps from the pptx skill (content, validate, visual) and deliver a `.pptx`.

To edit an existing Intility deck, skip step 1 and open the deck directly. Add slides from its own layouts and follow the same branding rules.

## Layouts

| i | Name | Placeholders (idx) | Use for |
|---|---|---|---|
| 0 | Title_page | 12 badge (one or two words), 10 header, 11 subheading | Opening slide only |
| 1 | Normal_title_bullets | 0 title, 10 body | Short lists, one message |
| 2 | Plain_w_title_image | 0 title, 10 picture | Screenshot, diagram, large visual |
| 3 | 2_column_w_title | 0 title, 1 left heading, 2 left body, 3 right heading, 4 right body | Comparisons, before/after, two options |
| 4 | 2_column | 0 title, 10 left, 11 right | Two parallel texts without headings |
| 5 | Text_left_image_right | 0 title, 10 body, 1 picture | Text with a photo |
| 6 | Text_right_image_left | 0 title, 12 body, 1 picture | Same, mirrored |
| 7, 8, 9 | 5 / 10 / 12 Participants | 0 title, picture and name pairs | Team and contact slides |
| 10 | Empty-slide | none (dark) | Custom content, charts, section breaks |
| 11 | Empty-slide-white | none (white) | Customer logo slides only. Brand guidelines call for dark backgrounds everywhere else |

Picture placeholders must get an image or the slide must use a different layout; never leave an empty picture frame. On participant slides, delete unused picture and name pairs.

## Branding

The template carries the brand: keep the theme fonts and the logo on the layouts, don't restyle placeholders (the title slide badge is the one exception, see Accent colors), and don't add your own logo, footers, or stripes. Within those limits, design boldly. The Design Ideas in the pptx skill still apply, using the colors below.

- Background is dark navy `071627`. Text is light `F3F3F6`; muted text `8A98A8`.
- Cards and other surfaces on dark slides use `0F2133`.
- The theme's hyperlink color is near-black navy and disappears on dark slides. Set link text explicitly to the slide's accent color.
- Don't introduce colors outside the palette in this section.
- Fonts are the theme fonts (Satoshi Intility). When you add your own text boxes, leave the font unset so it inherits the theme. The font is not installed in the sandbox, so QA previews are approximate: leave about 10% slack in text boxes.
- Never use PowerPoint's built-in bold (`font.bold = True`, `b="1"`, or bold in table headers, chart labels, and text runs). When emphasis is needed, set the run's font to the theme heading font, Satoshi Intility Medium (shown as "Satoshi Intility Medium (Heading)" in PowerPoint). Reference it through the theme so it stays linked, and don't type the name:

```python
run.font.bold = False
run.font.name = "+mj-lt"  # theme heading font
```

  Apply the same rule to table header cells, chart text, and big numbers. Titles already inherit the heading font from the layouts, so leave them alone. One exception: the column headings (idx 1 and 3) on layout 3, `2_column_w_title`, are bold in the template. On every run you fill there, set `font.bold = False` and `font.name = "+mj-lt"`, so they show as Medium instead of bold. Before delivering, check that no run in the deck has `b="1"`.
- Charts: native charts with accent colors, light axis labels (`8A98A8`), no gridline clutter.
- Tables: python-pptx's default table style is a light Office style that clashes with the template. Set the table style to "No Style, No Grid" (`{2D5ABB26-0587-4C30-8999-92F81FD0307C}`), then fill the header with the accent and navy text, and alternate body rows between `0F2133` and no fill.

### Accent colors

Choose accent colors like this:

Each slide uses exactly one accent color. Never mix accent colors on the same slide: not in panels, cards, icons, big numbers, highlighted text, or tables. The only exceptions are status, overview slides, and charts with several series, described below.

- If the deck clearly belongs to one department or subject area in the table below, use that area's color as the only accent throughout.
- If the deck covers several areas from the table, give each slide the color of the area it is about. If a slide touches several areas, don't split it into several colors. Use the color of the area the deck is mainly about. If no area dominates the deck, use the color of the area the slide spends most of its content on, or of the first area presented if that is equal.
- Slides that aren't about one area (title, agenda, summary, closing) use the color of the first area presented. Overview slides that list several areas show each area in its own color. This is an exception to the one-color rule.
- Otherwise, cycle through the accents in this order, moving to the next color on each new slide: teal, green, purple, red, pink, yellow. After yellow, start again at teal.
- If it's unclear which area the deck belongs to, or the area isn't listed, ask before choosing.

Status is an exception. Use red `FF624D`, green `00F597`, and yellow `FFE482` on a slide with a different accent only when the color shows a status, such as failed, ok, and warning in a status table, traffic light, or health indicator. Don't use them for decoration, and don't use a status color to mark a category. Use the same meaning for each color throughout the deck (red for failed or critical, green for ok, yellow for warning).

Charts with several series always use the cycle order, starting with the deck's accent. This is an exception to the one-color rule.

Give the title slide color by filling the badge (idx 12) with the accent and keeping its navy text. Don't add decorative graphics to the title slide.

The badge must fit its text with even padding. The layout resizes it to the text only when someone edits it in PowerPoint, so a badge filled by python-pptx keeps the layout's fixed width of about 2.2": a short word like "Seminar" sits in a mostly empty pill. Left-aligned text also ends up with more padding on the left than on the right in PowerPoint. After filling the badge text and color, run this helper. It sizes the width from the text, centers the text so the padding is equal on both sides, and keeps the left position, top, and height from the layout:

```python
from pptx.util import Emu
from pptx.enum.text import PP_ALIGN

def fit_badge(shape, em=0.58, side_in=0.3, min_in=1.0):
    """Size the title slide badge (idx 12) to its text, with side_in padding each side."""
    text = shape.text_frame.text
    size_pt = 18
    for r in shape.text_frame.paragraphs[0].runs:
        if r.font.size:
            size_pt = r.font.size.pt
    text_in = len(text) * size_pt * em / 72 * 1.05  # 5% slack on the estimated text width
    width_in = max(min_in, text_in + 2 * side_in)
    left, top, height = shape.left, shape.top, shape.height  # read inherited values before overriding
    shape.left, shape.top, shape.height = left, top, height
    shape.width = Emu(int(width_in * 914400))
    shape.text_frame.word_wrap = False  # some viewers don't inherit wrap="none" from the layout
    shape.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    return width_in
```

Keep the badge to one or two words, as the layout intends. The width estimate matches Satoshi in PowerPoint closely, and the sandbox preview font is wider, so the preview shows slightly tighter padding than the real file. In the preview, check that the text sits on one line and is centered in the pill.

| Accent | Departments and subject areas |
|---|---|
| Teal `0DF2D7` | Operations, Support Platform, Ticketing, Onboarding, My Intility, Intility GPT, Transcribe |
| Green `00F597` | Sustainability Manager |
| Purple `AD8AFF` | Application Services, Applications, Cloud Infrastructure, Workloads, Network, Edge, Operational Technology (OT), Finance and Financial Manager |
| Red `FF624D` | Security, Compliance, Monitoring |
| Pink `FF6CC5` | Workplace, Device, Webshop, Procurement, Collaboration and Audiovisuals, Developer Infrastructure, DADP (Data, AI and Developer Platform), Data Science, Artificial Intelligence |
| Yellow `FFE482` | Consulting, Identity and Digital Work, License |

## Make it visual

The layouts are a starting point, not a limit. A deck built only from title-and-bullet layouts and identical card grids looks flat.

- Every slide has the navy `071627` background, except customer logo slides, which use `Empty-slide-white`. Create variation freely with `0F2133` surfaces such as panels, cards, and large blocks. Shapes sit on top of the layout's logo, so keep them clear of it.
- Use the accent as a surface, not only as a highlight: half-slide panels, filled cards, and large blocks with navy text and navy icons. Accent-colored text works for short highlights on dark backgrounds.
- Font sizes follow the placeholders. Go larger only where a slide carries one key message: statement text, big numbers, and titles on custom slides, as described below.
- Give the key message room. Statement slides on `Empty-slide` carry one large message at 40 to 54pt, optionally supported by big numbers or a background visual.
- Draw the idea (layers, flows, before and after, a foundation that carries applications) instead of another grid of equal cards. Use at most two card-grid slides per deck.
- Show numbers as big numbers (60 to 72pt in the accent) when the content has them.
- On custom slides built on `Empty-slide`, set the title yourself at 24 to 40pt, placed where the template title sits (0.92", 0.4").
- Keep titles on one line for as long as possible. This rule does not apply to the title slide (layout 1, `Title_page`): leave its header (idx 10) at the template's 40pt and let it wrap to a second line. Layout titles are 24pt already. Where a custom title is set above 24pt and doesn't fit on one line, lower the font size in steps of 2pt, down to a minimum of 24pt, instead of letting it wrap. If it still needs two lines at 24pt, that is fine. Never go below 24pt, and don't shorten or reword the title to make it fit. Set the size explicitly on every run rather than relying on autofit, because the preview font is only approximate.
- Titles on slides that use the same layout must have the same font size across the deck. This applies to every group of slides on one layout, such as all custom slides on `Empty-slide`. Work out the size each title needs, then give every title in the group the smallest of those sizes, so one long title lowers the size for the whole group. Do this once, after all slides in the group are built. The title slide is not part of any group.

```python
def fit_titles(shapes, start_pt=40, min_pt=24, em=0.55, slack=0.9):
    """Titles that share a layout: find the largest size at which each fits on one line,
    then give every title in the group the smallest of those sizes."""
    sizes = []
    for shape in shapes:
        text = shape.text_frame.text
        avail = shape.width / 914400 - 0.2  # inches, minus the 0.1" insets on each side
        pt = start_pt
        while pt > min_pt and len(text) * pt * em / 72 > avail * slack:
            pt -= 2
        sizes.append(max(pt, min_pt))
    common = min(sizes)
    for shape in shapes:
        for p in shape.text_frame.paragraphs:
            for r in p.runs:
                r.font.size = Pt(common)
    return common
```

  Collect the title shapes of each layout group in a list while building, then call `fit_titles(group, start_pt=40)` once at the end. Use `start_pt=40` for custom slide titles, or the size you chose for the deck. The estimate is deliberately conservative (`em` is the average character width as a fraction of the font size), so check the rendered preview: if every title in the group visibly fits on one line at a larger size, bump the group up a step, and if one wraps, take the whole group down a step. Layout placeholder titles that you leave at the template size (24pt) already match.

## Tone of voice

- Write in Norwegian by default. Switch only if the user writes in another language or asks for one, and keep one language across slides and speaker notes.
- Clear, professional, understated business language. Say what the customer gets, not how impressive Intility is.
- No sales language, slogans, marketing superlatives, or generic AI phrases such as "sømløs", "banebrytende", "skreddersydd", "i dagens digitale landskap", or "ta det til neste nivå".
- Sentence case for all titles and headings, never all caps. Titles state the point of the slide ("Sikkerhetsoppdateringer skjer nå fortløpende"), not a topic label ("Sikkerhet").
- Short bullets, at most five per slide, no full stops on fragments. Put detail in speaker notes.
- Keep product names as they are (Minato, Intility Inference, Public Cloud). Don't translate them.
- Do not invent facts, numbers, customer examples, internal claims, or descriptions of products the user hasn't described.
- Use placeholders when information is missing: `[sett inn tall]`, `[sett inn kunde]`, `[avklar]`.
- Keep names and figures from the user's files exactly as given. Point out gaps, duplicates, or inconsistencies in your reply instead of fixing them silently.
- End your reply with a short list of every placeholder, assumption, and unverified statement in the deck, so the user can check them before use.
