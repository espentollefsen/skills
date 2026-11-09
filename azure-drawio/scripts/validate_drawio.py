#!/usr/bin/env python3
"""Validate a generated Azure .drawio file before handing it to the user.

Catches the failure modes that are invisible in raw XML but obvious the moment
draw.io opens the file: malformed escaping, missing parents, dangling edges,
broken icon paths, boxes that overlap or overflow their band.

Usage:
    python3 validate_drawio.py diagram.drawio
    python3 validate_drawio.py diagram.drawio --quiet   # errors only

Exit code 0 = no errors (warnings allowed), 1 = at least one error.
"""

# Windows consoles/pipes default to a legacy code page; force UTF-8 so labels and
# messages containing arrows, middots or Norwegian letters never raise UnicodeEncodeError.
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
import re
import sys
import xml.etree.ElementTree as ET

ERRORS, WARNINGS = [], []


def err(msg):
    ERRORS.append(msg)


def warn(msg):
    WARNINGS.append(msg)


# Paths shipped in reference/icons.md. Anything outside this set is flagged as a
# warning, not an error — draw.io has far more shapes than the skill enumerates.
KNOWN_ICONS = {
    "img/lib/azure2/general/Management_Groups.svg",
    "img/lib/azure2/general/Subscriptions.svg",
    "img/lib/mscae/ResourceGroup.svg",
    "img/lib/azure2/networking/Virtual_Networks.svg",
    "img/lib/azure2/networking/Subnet.svg",
    "img/lib/azure2/networking/Application_Gateways.svg",
    "img/lib/azure2/networking/Public_IP_Addresses.svg",
    "img/lib/azure2/networking/Private_Endpoint.svg",
    "img/lib/azure2/networking/Virtual_Network_Gateways.svg",
    "img/lib/azure2/networking/Network_Security_Groups.svg",
    "img/lib/azure2/networking/Route_Tables.svg",
    "img/lib/azure2/networking/Firewalls.svg",
    "img/lib/azure2/networking/Load_Balancers.svg",
    "img/lib/azure2/networking/Front_Doors.svg",
    "img/lib/azure2/networking/DNS_Private_Resolver.svg",
    "img/lib/mscae/DNS_Private_Zones.svg",
    "img/lib/mscae/DNS.svg",
    "img/lib/azure2/app_services/App_Services.svg",
    "img/lib/azure2/app_services/App_Service_Plans.svg",
    "img/lib/azure2/compute/Function_Apps.svg",
    "img/lib/azure2/other/Worker_Container_App.svg",
    "img/lib/azure2/other/Container_App_Environments.svg",
    "img/lib/azure2/integration/App_Configuration.svg",
    "img/lib/azure2/networking/Web_Application_Firewall_Policies_WAF.svg",
    "img/lib/azure2/containers/Container_Registries.svg",
    "img/lib/azure2/compute/Kubernetes_Services.svg",
    "img/lib/azure2/compute/Virtual_Machine.svg",
    "img/lib/azure2/databases/SQL_Database.svg",
    "img/lib/azure2/databases/SQL_Server.svg",
    "img/lib/azure2/databases/Azure_Cosmos_DB.svg",
    "img/lib/azure2/databases/Azure_Database_PostgreSQL_Server.svg",
    "img/lib/azure2/databases/Cache_Redis.svg",
    "img/lib/azure2/storage/Storage_Accounts.svg",
    "img/lib/azure2/security/Key_Vaults.svg",
    "img/lib/mscae/Certificate.svg",
    "img/lib/azure2/identity/Managed_Identities.svg",
    "img/lib/azure2/integration/Service_Bus.svg",
    "img/lib/azure2/analytics/Event_Hubs.svg",
    "img/lib/azure2/integration/Event_Grid_Topics.svg",
    "img/lib/azure2/integration/API_Management_Services.svg",
    "img/lib/azure2/management_governance/Application_Insights.svg",
    "img/lib/azure2/management_governance/Log_Analytics_Workspaces.svg",
    "img/lib/azure2/management_governance/Monitor.svg",
}

# Paths that look plausible but do not exist in draw.io's libraries.
BAD_ICONS = {
    "img/lib/azure2/networking/DNS_Private_Resolvers.svg":
        "plural form does not exist — use DNS_Private_Resolver.svg",
    "img/lib/azure2/networking/Private_Endpoints.svg":
        "plural form does not exist — use Private_Endpoint.svg",
    "img/lib/azure2/general/Resource_Groups.svg":
        "Resource Group lives under mscae — use img/lib/mscae/ResourceGroup.svg",
    "img/lib/azure2/compute/Virtual_Machines.svg":
        "plural form does not exist — use Virtual_Machine.svg",
    # Confirmed absent from the bundled library — these are the "obvious" folder
    # guesses that do not match how draw.io actually organises the Azure set.
    "img/lib/azure2/app_services/Function_Apps.svg":
        "Function Apps live under compute/ — use img/lib/azure2/compute/Function_Apps.svg",
    "img/lib/azure2/integration/Event_Hubs.svg":
        "Event Hubs live under analytics/ — use img/lib/azure2/analytics/Event_Hubs.svg",
    "img/lib/azure2/databases/Azure_Cache_Redis.svg":
        "does not exist — use img/lib/azure2/databases/Cache_Redis.svg",
    "img/lib/azure2/general/Managed_Desktop.svg":
        "wrong library and wrong resource — App Configuration is "
        "img/lib/azure2/integration/App_Configuration.svg",
}

BAND_W = 1100
BAND_X = -750


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def geom(cell):
    g = cell.find("mxGeometry")
    if g is None:
        return None
    x, y = num(g.get("x", 0)), num(g.get("y", 0))
    w, h = num(g.get("width")), num(g.get("height"))
    if None in (x, y, w, h):
        return None
    return x, y, w, h


def rects_overlap(a, b, tol=1.0):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return (ax < bx + bw - tol and bx < ax + aw - tol
            and ay < by + bh - tol and by < ay + ah - tol)


def contains(outer, inner, tol=1.0):
    ox, oy, ow, oh = outer
    ix, iy, iw, ih = inner
    return (ix >= ox - tol and iy >= oy - tol
            and ix + iw <= ox + ow + tol and iy + ih <= oy + oh + tol)


def validate(path):
    raw = open(path, encoding="utf-8").read()

    try:
        root_el = ET.fromstring(raw)
    except ET.ParseError as e:
        err(f"XML is malformed: {e}")
        err("  most likely an unescaped <, > or & inside a value= attribute "
            "(see reference/styles.md)")
        return

    if root_el.tag != "mxfile":
        err(f"root element is <{root_el.tag}>, expected <mxfile>")

    diagrams = root_el.findall("diagram")
    if not diagrams:
        err("no <diagram> element found")
        return

    for diagram in diagrams:
        model = diagram.find("mxGraphModel")
        if model is None:
            err(f"diagram '{diagram.get('name')}' has no <mxGraphModel>")
            continue
        rt = model.find("root")
        if rt is None:
            err(f"diagram '{diagram.get('name')}' has no <root>")
            continue
        check_root(rt)

    if "&nbsp;" in raw and "&amp;nbsp;" not in raw:
        warn("found raw &nbsp; — inside value= it must be written &amp;nbsp;")


def check_root(rt):
    cells = rt.findall("mxCell")
    if len(cells) < 2:
        err("<root> must contain at least the two base cells")
        return

    if cells[0].get("id") != "0":
        err(f"first cell must be id=\"0\", found id=\"{cells[0].get('id')}\"")
    if cells[1].get("id") != "1" or cells[1].get("parent") != "0":
        err("second cell must be id=\"1\" parent=\"0\"")

    seen, ids = set(), set()
    for c in cells:
        cid = c.get("id")
        if cid is None:
            err("found an mxCell with no id")
            continue
        if cid in seen:
            err(f"duplicate cell id: {cid}")
        seen.add(cid)
        ids.add(cid)

    vertices, edges, bands = {}, [], {}

    for c in cells[2:]:
        cid = c.get("id") or "?"
        parent = c.get("parent")
        if parent is None:
            err(f"cell '{cid}' has no parent attribute (must be parent=\"1\")")
        elif parent != "1":
            if parent not in ids:
                err(f"cell '{cid}' has parent=\"{parent}\" which does not exist")
            else:
                warn(f"cell '{cid}' has parent=\"{parent}\"; this skill expects a flat "
                     "model with parent=\"1\" on every cell")

        style = c.get("style") or ""

        if c.get("edge") == "1":
            edges.append(c)
            for end in ("source", "target"):
                ref = c.get(end)
                if ref is None:
                    warn(f"edge '{cid}' has no {end}; it will float unless the geometry "
                         "pins both ends")
                elif ref not in ids:
                    err(f"edge '{cid}' has {end}=\"{ref}\" which is not a cell in this diagram")
            continue

        if c.get("vertex") != "1":
            warn(f"cell '{cid}' is neither vertex=\"1\" nor edge=\"1\"")
            continue

        g = geom(c)
        if g is None:
            err(f"vertex '{cid}' has a missing or non-numeric mxGeometry")
            continue
        vertices[cid] = g

        gel = c.find("mxGeometry")
        for attr in ("x", "y", "width", "height"):
            v = gel.get(attr)
            if v is None:
                continue
            if not re.fullmatch(r"-?\d+(\.\d+)?", v):
                err(f"vertex '{cid}' has non-literal {attr}=\"{v}\"; "
                    "coordinates must be concrete numbers, never expressions")

        if "image=" in style:
            m = re.search(r"image=([^;]+)", style)
            if m:
                p = m.group(1).strip()
                if p in BAD_ICONS:
                    err(f"cell '{cid}' uses a non-existent icon path '{p}' — {BAD_ICONS[p]}")
                elif p not in KNOWN_ICONS:
                    warn(f"cell '{cid}' uses icon path '{p}' which is not in "
                         "reference/icons.md; verify it renders")
            if (c.get("value") or "") != "":
                err(f"icon cell '{cid}' has a non-empty value; labels belong in a "
                    "separate text cell (icon+text two-cell pattern)")

        x, y, w, h = g
        if abs(w - BAND_W) < 1 and abs(x - BAND_X) < 1:
            bands[cid] = g

    check_bands(bands, vertices)
    check_icon_collisions(vertices, cells)
    check_label_collisions(cells, vertices)


def check_bands(bands, vertices):
    ordered = sorted(bands.items(), key=lambda kv: kv[1][1])
    for (ida, a), (idb, b) in zip(ordered, ordered[1:]):
        a_bottom, b_top = a[1] + a[3], b[1]
        if b_top < a_bottom - 1:
            err(f"bands '{ida}' and '{idb}' overlap vertically "
                f"('{ida}' ends y={a_bottom:g}, '{idb}' starts y={b_top:g})")
        elif b_top - a_bottom < 20:
            warn(f"only {b_top - a_bottom:g}px between bands '{ida}' and '{idb}'; "
                 "peering labels need ~50px")

    for cid, v in vertices.items():
        if cid in bands:
            continue
        # Anchor on the top-left corner, not the centre: a box that overflows badly
        # enough has its centre outside the band, and a centre-based lookup would
        # find no host and silently skip exactly the worst cases.
        host = None
        for bid, b in bands.items():
            if b[0] <= v[0] <= b[0] + b[2] and b[1] <= v[1] <= b[1] + b[3]:
                host = (bid, b)
                break
        if host and not contains(host[1], v, tol=2):
            err(f"cell '{cid}' (x={v[0]:g} y={v[1]:g} w={v[2]:g} h={v[3]:g}) overflows "
                f"its band '{host[0]}'")


def style_num(style, key, default=0.0):
    m = re.search(rf"(?:^|;){key}=(-?\d+(?:\.\d+)?)", style or "")
    return float(m.group(1)) if m else default


def label_extent(cell, g):
    """Estimate where a label actually renders, which is not where its box is.

    Text cells do not clip, and a box label starts at spacingLeft — so two labels
    can overlap on screen while both cells' geometries look fine. This is the
    failure mode that produced 'dnsResolvnsg-dnspr-in-prod' in a diagram that
    otherwise validated clean, so it is worth estimating rather than ignoring.
    """
    value = (cell.get("value") or "").strip()
    if not value:
        return None
    style = cell.get("style") or ""

    plain = re.sub(r"<[^>]+>", "", value.replace("&lt;", "<").replace("&gt;", ">"))
    plain = plain.replace("&amp;nbsp;", " ").replace("&nbsp;", " ").replace("&amp;", "&")
    lines = [ln for ln in re.split(r"<br\s*/?>", value.replace("&lt;br&gt;", "<br>")) if ln]
    widest = max((len(re.sub(r"<[^>]+>", "", ln)) for ln in lines), default=len(plain))

    size = style_num(style, "fontSize", 12.0)
    per_char = size * (0.58 if ("&lt;b&gt;" in value or "<b>" in value) else 0.53)
    width = widest * per_char

    x, y, w, h = g
    if style.startswith("text;"):
        # align=left text cells grow rightwards from x; centred ones from the middle
        left = x if "align=left" in style else x + w / 2 - width / 2
        top, bottom = y, y + h
    else:
        # a container's label sits on its first line, inset by spacingLeft
        left = x + style_num(style, "spacingLeft")
        top = y + style_num(style, "spacingTop")
        bottom = top + size + 6
    return left, left + width, top, bottom


def check_label_collisions(cells, vertices):
    labels = []
    for c in cells:
        cid = c.get("id")
        if cid not in vertices or "image=" in (c.get("style") or ""):
            continue
        ext = label_extent(c, vertices[cid])
        if ext:
            labels.append((cid, ext))

    right_edge = BAND_X + BAND_W
    for cid, ext in labels:
        # only judge labels that live inside the band column, not the notes panel
        if ext[0] < right_edge and ext[1] > right_edge + 4:
            err(f"label '{cid}' renders ~{ext[1] - right_edge:.0f}px past the right edge "
                f"of the band column — shorten it or widen the cell")

    for i, (ida, a) in enumerate(labels):
        for idb, b in labels[i + 1:]:
            # same visual row?
            if a[3] <= b[2] + 2 or b[3] <= a[2] + 2:
                continue
            overlap = min(a[1], b[1]) - max(a[0], b[0])
            if overlap > 10:
                err(f"labels '{ida}' and '{idb}' overlap by ~{overlap:.0f}px on screen; "
                    "shorten one (subnet labels share their row with the NSG label)")


def check_icon_collisions(vertices, cells):
    icons = {}
    for c in cells:
        cid = c.get("id")
        if cid in vertices and "image=" in (c.get("style") or ""):
            icons[cid] = vertices[cid]
    items = list(icons.items())
    for i, (ida, a) in enumerate(items):
        for idb, b in items[i + 1:]:
            if rects_overlap(a, b, tol=2):
                err(f"icons '{ida}' and '{idb}' overlap")


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    quiet = "--quiet" in argv
    targets = [a for a in argv[1:] if not a.startswith("--")]

    for path in targets:
        ERRORS.clear()
        WARNINGS.clear()
        try:
            validate(path)
        except OSError as e:
            print(f"cannot read {path}: {e}")
            return 1

        print(f"== {path}")
        for m in ERRORS:
            print(f"  ERROR   {m}")
        if not quiet:
            for m in WARNINGS:
                print(f"  warn    {m}")
        if not ERRORS:
            print(f"  OK      no errors"
                  + (f", {len(WARNINGS)} warning(s)" if WARNINGS and quiet else ""))
        if ERRORS:
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
