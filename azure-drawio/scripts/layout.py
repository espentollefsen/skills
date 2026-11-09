#!/usr/bin/env python3
"""Compute the exact coordinate plan for an Azure draw.io diagram.

Removes all hand-arithmetic from diagram generation: describe the bands and how many
rows each subnet/column holds, and this prints every concrete integer coordinate to
drop into the XML.

Usage:
    python3 layout.py spec.json          # human-readable plan
    python3 layout.py spec.json --json   # machine-readable plan
    python3 layout.py --demo             # print an example spec and its plan

Spec format (all keys optional unless noted):

{
  "bands": [                                   # REQUIRED, top-to-bottom order
    {"id": "client_box", "kind": "clients"},
    {"id": "online_gw",  "kind": "azure", "scope": "online", "vnet_w": 700,
     "subnets": [{"id": "snet_agw", "rows": 2}]},
    {"id": "conn", "kind": "azure", "scope": "connectivity", "vnet_w": 580,
     "subnets": [{"id": "snet_gw", "rows": 1}, {"id": "snet_dnspr_in", "rows": 1}],
     "right_column": {"kind": "dns", "rows": 9}},
    {"id": "corp", "kind": "azure", "scope": "corp", "vnet_w": 680,
     "subnets": [{"id": "snet_pe", "rows": 5}],
     "right_column": {"kind": "paas", "rows": 7}},
    {"id": "incloud_box", "kind": "incloud", "rows": 3}
  ]
}

"rows" is the number of icon+text rows. right_column "kind" is "paas" (60px pitch,
outside the corp VNet) or "dns" (30px pitch, outside the hub VNet).
"""

# Windows consoles/pipes default to a legacy code page; force UTF-8 so labels and
# messages containing arrows, middots or Norwegian letters never raise UnicodeEncodeError.
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
import json
import sys

# ---------------------------------------------------------------- constants
LEFT = -750          # left edge of every band
BAND_W = 1100        # band width  -> right edge at 350
BAND_GAP = 50        # vertical gap between bands
TITLE_Y, TITLE_H = 100, 30
FIRST_BAND_Y = 180

SUB_HEAD = 50        # band top -> first inner box top
SUB_PAD_B = 20       # padding below tallest inner element

VNET_DX = 20         # VNet inset from band left   -> x = -730
VNET_HEAD = 35       # VNet top -> first subnet top
VNET_PAD_B = 20
VNET_MIN_H = 90      # a VNet with no subnets still needs a visible body

SNET_DX = 20         # subnet inset from VNet left -> x = -710
SNET_GAP = 20        # vertical gap between sibling subnets

ROW1_DY = 35         # subnet top -> first icon top
ROW_PITCH = 60       # icon-to-icon vertical pitch
ICON_NOM_H = 30      # nominal icon height used for height maths
SNET_PAD_B = 30

TEXT_DX = 38         # icon x -> text x
TEXT_DY = -8         # icon y -> text y
TEXT_W = 420         # in-subnet label width (stops clear of the NSG label)
TEXT_H = 45

NSG_DY = 8           # subnet top -> NSG icon top
NSG_INSET = 30       # subnet right edge -> NSG icon x
NSG_TEXT_DX = -120

CLIENTS_H = 80
# PaaS text sits 48px right of the icon so it clears the widest PaaS icon (LAW, 43px).
PAAS_ICON_X, PAAS_TEXT_X, PAAS_TEXT_W, PAAS_PITCH = -10, 38, 310, 60
DNS_ICON_X, DNS_TEXT_X, DNS_TEXT_W, DNS_PITCH = -120, -90, 280, 30

NOTES_X, NOTES_W, NOTES_Y = 400, 540, 180
LANE_PEER = -790     # left lane for peering edges that skip a band
LANE_INCLOUD = -900  # outer left lane for the Direct Link edge

# Azure scope bands carry no label of their own — the three header segments below
# supply it — so every band uses the same text inset.
BAND_SPACING_LEFT = {"azure": 15, "clients": 15, "incloud": 15}


# ---------------------------------------------------------------- geometry
def subnet_h(rows):
    """Height of a subnet box holding `rows` icon rows."""
    rows = max(1, int(rows))
    return ROW1_DY + ROW_PITCH * (rows - 1) + ICON_NOM_H + SNET_PAD_B  # = 60*rows + 35


def vnet_h(subnets):
    if not subnets:
        return VNET_MIN_H
    total = sum(subnet_h(s.get("rows", 1)) for s in subnets)
    total += SNET_GAP * (len(subnets) - 1)
    return max(VNET_MIN_H, VNET_HEAD + total + VNET_PAD_B)


def right_col_h(col):
    if not col:
        return 0
    pitch = DNS_PITCH if col.get("kind") == "dns" else PAAS_PITCH
    return pitch * int(col.get("rows", 0)) + 10


def band_h(band):
    kind = band.get("kind", "azure")
    if kind == "clients":
        return CLIENTS_H
    if kind == "incloud":
        return SUB_HEAD + ROW_PITCH * int(band.get("rows", 1)) + 10 + SUB_PAD_B
    body = max(vnet_h(band.get("subnets", [])), right_col_h(band.get("right_column")))
    return SUB_HEAD + body + SUB_PAD_B


def plan(spec):
    bands_in = spec.get("bands")
    if not bands_in:
        raise SystemExit("spec error: 'bands' is required and must be non-empty")

    out = {
        "title": {"id": "title", "x": LEFT, "y": TITLE_Y, "w": BAND_W, "h": TITLE_H},
        "notes": {"x": NOTES_X, "y": NOTES_Y, "w": NOTES_W},
        "lanes": {"peering": LANE_PEER, "incloud": LANE_INCLOUD},
        "bands": [],
    }

    y = FIRST_BAND_Y
    for band in bands_in:
        kind = band.get("kind", "azure")
        bid = band.get("id") or "band"
        h = band_h(band)
        entry = {
            "id": bid,
            # `id` is the prefix used to derive child ids; `cell_id` is the band cell itself.
            "cell_id": f"{bid}_sub" if kind == "azure" else bid,
            "kind": kind,
            "scope": band.get("scope"),
            "x": LEFT, "y": y, "w": BAND_W, "h": h,
            "spacing_left": BAND_SPACING_LEFT.get(kind, 15),
        }

        if kind == "azure":
            # Three header segments, each an icon + its own text cell at a fixed offset.
            # Deterministic: no character-width estimation, so names can never collide
            # with the icon that follows them.
            entry["header"] = {
                "mg": {
                    "icon": {"id": f"{bid}_mg_icon", "x": LEFT + 20, "y": y + 14,
                             "w": 20, "h": 19.39},
                    "text": {"id": f"{bid}_mg_text", "x": LEFT + 46, "y": y + 10,
                             "w": 150, "h": 20},
                },
                "sub": {
                    "icon": {"id": f"{bid}_sub_icon", "x": LEFT + 200, "y": y + 12,
                             "w": 14, "h": 22.59},
                    "text": {"id": f"{bid}_sub_text", "x": LEFT + 220, "y": y + 10,
                             "w": 210, "h": 20},
                },
                "rg": {
                    "icon": {"id": f"{bid}_rg_icon", "x": LEFT + 440, "y": y + 14,
                             "w": 20, "h": 16},
                    "text": {"id": f"{bid}_rg_text", "x": LEFT + 466, "y": y + 10,
                             "w": 170, "h": 20},
                },
            }
            vw = int(band.get("vnet_w", 680))
            vx, vy = LEFT + VNET_DX, y + SUB_HEAD
            vh = vnet_h(band.get("subnets", []))
            entry["vnet"] = {
                "id": f"{bid}_vnet", "x": vx, "y": vy, "w": vw, "h": vh,
                "spacing_left": 42,
                "header_icon": {"id": f"{bid}_vnet_icon", "x": vx + 8, "y": vy + 10,
                                "w": 27, "h": 16.12},
            }

            sx, sw = vx + SNET_DX, vw - 2 * SNET_DX
            sy = vy + VNET_HEAD
            subnets = []
            for snet in band.get("subnets", []):
                rows = max(1, int(snet.get("rows", 1)))
                sid = snet.get("id") or "snet"
                sh = subnet_h(rows)
                icon_x = sx + 20
                nsg_x = sx + sw - NSG_INSET
                # The subnet label and the NSG label share the subnet's header row.
                # Narrow subnets (the hub is only 540px) leave little room, so report
                # the budget rather than letting the two strings silently overlap.
                label_room = (nsg_x + NSG_TEXT_DX) - (sx + 38) - 10
                subnets.append({
                    "id": sid, "x": sx, "y": sy, "w": sw, "h": sh,
                    "spacing_left": 38,
                    "label_max_chars": max(0, int(label_room / 5.8)),
                    "header_icon": {"id": f"{sid}_subnet_icon", "x": sx + 15, "y": sy + 6,
                                    "w": 18, "h": 10.78},
                    "nsg": {
                        "icon": {"id": f"icon_nsg_{sid.replace('snet_', '')}",
                                 "x": nsg_x, "y": sy + NSG_DY, "w": 16, "h": 19.43},
                        "text": {"id": f"text_nsg_{sid.replace('snet_', '')}",
                                 "x": nsg_x + NSG_TEXT_DX, "y": sy + NSG_DY,
                                 "w": 110, "h": 20, "font_size": 10},
                    },
                    "rows": [
                        {
                            "index": i,
                            "icon": {"x": icon_x, "y": sy + ROW1_DY + ROW_PITCH * i},
                            "text": {"x": icon_x + TEXT_DX,
                                     "y": sy + ROW1_DY + ROW_PITCH * i + TEXT_DY,
                                     "w": TEXT_W, "h": TEXT_H},
                        }
                        for i in range(rows)
                    ],
                })
                sy += sh + SNET_GAP
            entry["subnets"] = subnets

            col = band.get("right_column")
            if col:
                is_dns = col.get("kind") == "dns"
                ix = DNS_ICON_X if is_dns else PAAS_ICON_X
                tx = DNS_TEXT_X if is_dns else PAAS_TEXT_X
                tw = DNS_TEXT_W if is_dns else PAAS_TEXT_W
                pitch = DNS_PITCH if is_dns else PAAS_PITCH
                base = y + SUB_HEAD
                entry["right_column"] = {
                    "kind": col.get("kind", "paas"),
                    "rows": [
                        {"index": i,
                         "icon": {"x": ix, "y": base + pitch * i},
                         "text": {"x": tx, "y": base + pitch * i - (4 if is_dns else 8),
                                  "w": tw, "h": 20 if is_dns else 45,
                                  "font_size": 10 if is_dns else 11}}
                        for i in range(int(col.get("rows", 0)))
                    ],
                }

        if kind == "azure" and band.get("no_vnet"):
            rows = max(1, int(band.get("rows", 0) or 0))
            icon_x = LEFT + 20
            entry["rows"] = [
                {"index": i,
                 "icon": {"x": icon_x, "y": y + SUB_HEAD + ROW_PITCH * i},
                 "text": {"x": icon_x + TEXT_DX,
                          "y": y + SUB_HEAD + ROW_PITCH * i + TEXT_DY,
                          "w": 900, "h": TEXT_H}}
                for i in range(rows)
            ]

        elif kind == "incloud":
            rows = max(1, int(band.get("rows", 1)))
            icon_x = LEFT + 20
            entry["rows"] = [
                {"index": i,
                 "icon": {"x": icon_x, "y": y + SUB_HEAD + ROW_PITCH * i},
                 "text": {"x": icon_x + TEXT_DX,
                          "y": y + SUB_HEAD + ROW_PITCH * i + TEXT_DY,
                          "w": 600, "h": TEXT_H}}
                for i in range(rows)
            ]

        out["bands"].append(entry)
        y += h + BAND_GAP

    out["content_bottom"] = y - BAND_GAP
    out["page"] = {"width": 1700, "height": max(1200, out["content_bottom"] + 200)}
    return out


# ---------------------------------------------------------------- rendering
def render(p):
    L = []
    t = p["title"]
    L.append(f"title            x={t['x']:>5} y={t['y']:>5} w={t['w']} h={t['h']}")
    L.append(f"notes panel      x={p['notes']['x']:>5} y={p['notes']['y']:>5} w={p['notes']['w']}")
    L.append(f"edge lanes       peering x={p['lanes']['peering']}   incloud x={p['lanes']['incloud']}")
    L.append(f"page             {p['page']['width']} x {p['page']['height']}"
             f"   (content ends y={p['content_bottom']})")
    L.append("")

    for b in p["bands"]:
        scope = f" [{b['scope']}]" if b.get("scope") else ""
        L.append(f"== {b['id']}{scope}  kind={b['kind']}")
        L.append(f"   band          x={b['x']:>5} y={b['y']:>5} w={b['w']} h={b['h']}"
                 f"   spacingLeft={b['spacing_left']}  id={b['cell_id']}")
        if b.get("header"):
            for name, seg in b["header"].items():
                ic, tx = seg["icon"], seg["text"]
                L.append(f"   hdr {name:<4}      icon x={ic['x']:>5} y={ic['y']:>5} "
                         f"w={ic['w']} h={ic['h']}   text x={tx['x']} y={tx['y']} "
                         f"w={tx['w']}   ids={ic['id']}/{tx['id']}")
        if b.get("vnet"):
            v = b["vnet"]
            L.append(f"   vnet          x={v['x']:>5} y={v['y']:>5} w={v['w']} h={v['h']}"
                     f"   spacingLeft={v['spacing_left']}  id={v['id']}")
            hi = v["header_icon"]
            L.append(f"   vnet icon     x={hi['x']:>5} y={hi['y']:>5} w={hi['w']} h={hi['h']}")
        for s in b.get("subnets", []):
            L.append(f"   -- {s['id']}   x={s['x']:>5} y={s['y']:>5} w={s['w']} h={s['h']}"
                     f"   spacingLeft={s['spacing_left']}"
                     f"   LABEL MAX {s['label_max_chars']} CHARS")
            hi = s["header_icon"]
            L.append(f"      snet icon  x={hi['x']:>5} y={hi['y']:>5} w={hi['w']} h={hi['h']}")
            n = s["nsg"]
            L.append(f"      nsg icon   x={n['icon']['x']:>5} y={n['icon']['y']:>5} "
                     f"w=16 h=19.43   text x={n['text']['x']} y={n['text']['y']} (fontSize=10)")
            for r in s["rows"]:
                L.append(f"      row {r['index']}      icon x={r['icon']['x']:>5} "
                         f"y={r['icon']['y']:>5}   text x={r['text']['x']} y={r['text']['y']} "
                         f"w={r['text']['w']} h={r['text']['h']}")
        if b.get("right_column"):
            c = b["right_column"]
            L.append(f"   -- right column ({c['kind']})")
            for r in c["rows"]:
                L.append(f"      row {r['index']}      icon x={r['icon']['x']:>5} "
                         f"y={r['icon']['y']:>5}   text x={r['text']['x']} y={r['text']['y']} "
                         f"w={r['text']['w']} fontSize={r['text']['font_size']}")
        for r in b.get("rows", []):
            L.append(f"   row {r['index']}         icon x={r['icon']['x']:>5} "
                     f"y={r['icon']['y']:>5}   text x={r['text']['x']} y={r['text']['y']} "
                     f"w={r['text']['w']}")
        L.append("")
    return "\n".join(L)


DEMO = {
    "bands": [
        {"id": "client_box", "kind": "clients"},
        {"id": "online_gw", "kind": "azure", "scope": "online", "vnet_w": 700,
         "subnets": [{"id": "snet_agw", "rows": 2}]},
        {"id": "online_wl", "kind": "azure", "scope": "online", "vnet_w": 680,
         "subnets": [{"id": "snet_app", "rows": 1}]},
        {"id": "conn", "kind": "azure", "scope": "connectivity", "vnet_w": 580,
         "subnets": [{"id": "snet_gw", "rows": 1},
                     {"id": "snet_dnspr_in", "rows": 1},
                     {"id": "snet_dnspr_out", "rows": 1}],
         "right_column": {"kind": "dns", "rows": 9}},
        {"id": "corp", "kind": "azure", "scope": "corp", "vnet_w": 680,
         "subnets": [{"id": "snet_pe", "rows": 5}],
         "right_column": {"kind": "paas", "rows": 7}},
        {"id": "incloud_box", "kind": "incloud", "rows": 3},
    ]
}


def main(argv):
    args = [a for a in argv[1:]]
    as_json = "--json" in args
    args = [a for a in args if not a.startswith("--")]

    if "--demo" in argv[1:]:
        spec = DEMO
        if not as_json:
            print("# demo spec\n" + json.dumps(spec, indent=2) + "\n\n# plan")
    elif args:
        with open(args[0], encoding="utf-8") as fh:
            spec = json.load(fh)
    else:
        spec = json.load(sys.stdin)

    p = plan(spec)
    print(json.dumps(p, indent=2) if as_json else render(p))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
