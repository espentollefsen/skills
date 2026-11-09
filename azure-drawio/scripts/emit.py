#!/usr/bin/env python3
"""Emit a complete .drawio file from a content spec.

layout.py answers "where does everything go"; this answers "write the file".
Together they remove hand-assembly of XML entirely — which is where these
diagrams historically went wrong, because one miscounted row shifts every
coordinate below it and nothing catches it until a human squints at a render.

Usage:
    python3 emit.py spec.json -o diagram.drawio
    python3 emit.py --demo -o demo.drawio      # emit the bundled example spec
    python3 emit.py --print-demo-spec          # show that spec to copy and edit

Spec shape — see examples/full-diagram.spec.json for a complete one:

{
  "meta":  {"title": "...", "diagram_name": "...", "region": "norwayeast"},
  "theme": "bifrost" | "classic",
  "bands": [ ... ],
  "notes": [{"title": "1. Nettverk", "items": ["...", "..."]}]
}

Edges are generated automatically: HTTPS from the clients band, VNet peering from
every Azure band to the connectivity band (routed down the left lane when a band
sits in between), and the Direct Link when an InCloud band is present.
"""

# Windows consoles/pipes default to a legacy code page; force UTF-8 so labels and
# messages containing arrows, middots or Norwegian letters never raise UnicodeEncodeError.
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)

_spec = importlib.util.spec_from_file_location("layout", os.path.join(HERE, "layout.py"))
layout = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(layout)


# ---------------------------------------------------------------- themes
# Bifrost values come from the RGB-HEX table in the Bifrost design docs, which is
# the sanctioned source when CSS variables are not an option — exactly our case.
# Light-mode values only; a .drawio has no colour-scheme switch.
THEMES = {
    "bifrost": {
        "clients":   ("#e3e3e8", "#3d4c5c"),   # neutral-fade / neutral-fade-c
        "online":    ("#e7dcfe", "#631cce"),   # chill-fade / chill
        "connectivity": ("#fff5c7", "#99620a"),  # warning-fade / warning-fade-c
        "corp":      ("#d8fdf8", "#007375"),   # brand-fade / brand
        "management": ("#ffd1ed", "#bd006e"),  # attn-fade / attn
        "incloud":   ("#f3f3f6", "#565776"),   # base / base-c-2
        "notes_head": ("#007375", "#007375"),  # brand
        "notes_body": ("#ffffff", "#d3d3df"),  # base-3 / base-dimmed
        "notes_head_font": "#ffffff",          # brand-hc
        "font": "#071627",                     # base-c
        # Bifrost specifies Satoshi for headings and Open Sans for body. Both must be
        # font *stacks*: draw.io falls back to a SERIF when a named family is missing,
        # which looks nothing like Bifrost. Verified by render — a bare "Open Sans"
        # and the Google-Fonts fontSource both came out serif; these stacks come out
        # sans, and use the real fonts on machines that have them.
        "heading_family": "Satoshi Intility, Satoshi, Helvetica, Arial, sans-serif",
        "body_family": "Open Sans, Helvetica, Arial, sans-serif",
        "body_source": None,
    },
    "classic": {
        "clients": ("#FAEEDA", "#854F0B"),
        "online": ("#F3EDF7", "#7B1FA2"),
        "connectivity": ("#FAECE7", "#993C1D"),
        "corp": ("#E6F1FB", "#185FA5"),
        "management": ("#f8cecc", "#b85450"),
        "incloud": ("#F1EFE8", "#444441"),
        "notes_head": ("#b0e3e6", "#0e8088"),
        "notes_body": ("#b0e3e6", "#0e8088"),
        "notes_head_font": "#000000",
        "font": "#000000",
        "heading_family": None,
        "body_family": None,
        "body_source": None,
    },
}

# Short aliases so specs stay readable. Sizes match reference/icons.md.
ICONS = {
    "mg":      ("img/lib/azure2/general/Management_Groups.svg", 20, 19.39),
    "sub":     ("img/lib/azure2/general/Subscriptions.svg", 14, 22.59),
    "rg":      ("img/lib/mscae/ResourceGroup.svg", 20, 16),
    "vnet":    ("img/lib/azure2/networking/Virtual_Networks.svg", 27, 16.12),
    "snet":    ("img/lib/azure2/networking/Subnet.svg", 18, 10.78),
    "nsg":     ("img/lib/azure2/networking/Network_Security_Groups.svg", 16, 19.43),
    "agw":     ("img/lib/azure2/networking/Application_Gateways.svg", 30, 30),
    "pip":     ("img/lib/azure2/networking/Public_IP_Addresses.svg", 30, 30),
    "pe":      ("img/lib/azure2/networking/Private_Endpoint.svg", 30, 27.5),
    "vpng":    ("img/lib/azure2/networking/Virtual_Network_Gateways.svg", 24, 31.85),
    "dnspr":   ("img/lib/azure2/networking/DNS_Private_Resolver.svg", 30, 30),
    "pdns":    ("img/lib/mscae/DNS_Private_Zones.svg", 22, 22),
    "dns":     ("img/lib/mscae/DNS.svg", 30, 30),
    "fw":      ("img/lib/azure2/networking/Firewalls.svg", 30, 30),
    "waf":     ("img/lib/azure2/networking/Web_Application_Firewall_Policies_WAF.svg", 30, 30),
    "app":     ("img/lib/azure2/app_services/App_Services.svg", 30, 30),
    "func":    ("img/lib/azure2/compute/Function_Apps.svg", 30, 30),
    "ca":      ("img/lib/azure2/other/Worker_Container_App.svg", 30, 30),
    "cae":     ("img/lib/azure2/other/Container_App_Environments.svg", 30, 30),
    "cr":      ("img/lib/azure2/containers/Container_Registries.svg", 38, 38),
    "aks":     ("img/lib/azure2/compute/Kubernetes_Services.svg", 38, 38),
    "vm":      ("img/lib/azure2/compute/Virtual_Machine.svg", 30, 30),
    "sqldb":   ("img/lib/azure2/databases/SQL_Database.svg", 38, 38),
    "sql":     ("img/lib/azure2/databases/SQL_Server.svg", 38, 38),
    "cosmos":  ("img/lib/azure2/databases/Azure_Cosmos_DB.svg", 38, 38),
    "psql":    ("img/lib/azure2/databases/Azure_Database_PostgreSQL_Server.svg", 38, 38),
    "redis":   ("img/lib/azure2/databases/Cache_Redis.svg", 38, 38),
    "st":      ("img/lib/azure2/storage/Storage_Accounts.svg", 38, 38),
    "kv":      ("img/lib/azure2/security/Key_Vaults.svg", 38, 38),
    "cert":    ("img/lib/mscae/Certificate.svg", 38, 38),
    "id":      ("img/lib/azure2/identity/Managed_Identities.svg", 30, 30),
    "sb":      ("img/lib/azure2/integration/Service_Bus.svg", 38, 38),
    "evh":     ("img/lib/azure2/analytics/Event_Hubs.svg", 38, 38),
    "evg":     ("img/lib/azure2/integration/Event_Grid_Topics.svg", 38, 38),
    "apim":    ("img/lib/azure2/integration/API_Management_Services.svg", 38, 38),
    "appcs":   ("img/lib/azure2/integration/App_Configuration.svg", 38, 38),
    "appi":    ("img/lib/azure2/management_governance/Application_Insights.svg", 30, 42.95),
    "log":     ("img/lib/azure2/management_governance/Log_Analytics_Workspaces.svg", 43, 43),
    "monitor": ("img/lib/azure2/management_governance/Monitor.svg", 38, 38),
}


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def num(v):
    """Emit 38 rather than 38.0, but keep 19.39."""
    f = float(v)
    return str(int(f)) if f == int(f) else str(f)


class Emitter:
    # Colour follows scope, nothing else. Two subscriptions in the same scope (e.g.
    # two corp workloads) share the same colour — the band headers (MG/Sub/RG) are
    # what tells them apart, not a second shade invented for the occasion.
    SCOPES = ("online", "connectivity", "management", "corp")

    def __init__(self, spec):
        self.spec = spec
        self.t = THEMES[spec.get("theme", "bifrost")]
        self.cells = []
        self.warnings = []

    # ---------------------------------------------------------- primitives
    def _font(self, heading=False):
        fam = self.t["heading_family"] if heading else self.t["body_family"]
        if not fam:
            return f"fontColor={self.t['font']};"
        out = f"fontColor={self.t['font']};fontFamily={fam};"
        if not heading and self.t["body_source"]:
            out += f"fontSource={self.t['body_source']};"
        return out

    def box(self, cid, value, style, x, y, w, h):
        self.cells.append(
            f'<mxCell id="{cid}" value="{esc(value)}" style="{style}" vertex="1" parent="1">'
            f'<mxGeometry x="{num(x)}" y="{num(y)}" width="{num(w)}" height="{num(h)}" '
            f'as="geometry" /></mxCell>')

    def icon(self, cid, alias, x, y, w=None, h=None):
        path, iw, ih = ICONS[alias]
        sketch = "sketch=0;" if alias == "rg" else ""
        self.cells.append(
            f'<mxCell id="{cid}" value="" style="image;{sketch}aspect=fixed;html=1;points=[];'
            f'align=center;fontSize=12;image={path};" vertex="1" parent="1">'
            f'<mxGeometry x="{num(x)}" y="{num(y)}" width="{num(w or iw)}" '
            f'height="{num(h or ih)}" as="geometry" /></mxCell>')

    def text(self, cid, value, x, y, w, h, fs=11, heading=False):
        style = (f"text;html=1;strokeColor=none;fillColor=none;align=left;"
                 f"verticalAlign=middle;fontSize={fs};{self._font(heading)}")
        self.box(cid, value, style, x, y, w, h)

    def edge(self, cid, value, style, src, tgt, points=None):
        geo = '<mxGeometry relative="1" as="geometry" />'
        if points:
            pts = "".join(f'<mxPoint x="{num(px)}" y="{num(py)}" />' for px, py in points)
            geo = (f'<mxGeometry relative="1" as="geometry"><Array as="points">{pts}'
                   f'</Array></mxGeometry>')
        self.cells.append(
            f'<mxCell id="{cid}" value="{esc(value)}" style="{style}{self._font()}" '
            f'edge="1" parent="1" source="{src}" target="{tgt}">{geo}</mxCell>')

    # ---------------------------------------------------------- build
    def build(self):
        plan = layout.plan({"bands": [self._layout_band(b) for b in self.spec["bands"]]})
        byid = {b["id"]: b for b in plan["bands"]}

        meta = self.spec.get("meta", {})
        t = plan["title"]
        title = meta.get("title", "")
        if meta.get("region"):
            title = f"{title} · {meta['region']}" if title else meta["region"]
        self.box("title", title,
                 f"text;html=1;strokeColor=none;fillColor=none;align=center;"
                 f"verticalAlign=middle;whiteSpace=wrap;fontSize=16;fontStyle=1;"
                 f"{self._font(heading=True)}", t["x"], t["y"], t["w"], t["h"])

        for band in self.spec["bands"]:
            p = byid[band["id"]]
            kind = p["kind"]
            if kind == "clients":
                self._clients(band, p)
            elif kind == "incloud":
                self._incloud(band, p)
            else:
                self._azure(band, p)

        self._edges(plan, byid)
        self._notes(plan)
        return plan

    def _layout_band(self, b):
        """Strip content down to the shape layout.py needs."""
        out = {"id": b["id"], "kind": b.get("kind", "azure")}
        if out["kind"] == "azure":
            out["scope"] = b.get("scope")
            out["vnet_w"] = (b.get("vnet") or {}).get("w", 680)
            out["no_vnet"] = b.get("vnet") is None
            if out["no_vnet"]:
                out["rows"] = len(b.get("rows", []))
            out["subnets"] = [{"id": s["id"], "rows": len(s.get("rows", []))}
                              for s in b.get("subnets", [])]
            col = b.get("right_column")
            if col:
                out["right_column"] = {"kind": col.get("kind", "paas"),
                                       "rows": len(col.get("rows", []))}
        elif out["kind"] == "incloud":
            out["rows"] = len(b.get("rows", []))
        return out

    def _band_style(self, scope, spacing_left):
        fill, stroke = self.t[scope]
        return (f"rounded=1;absoluteArcSize=1;arcSize=10;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};"
                f"strokeWidth=2;fontSize=12;verticalAlign=top;fontStyle=1;align=left;"
                f"spacingLeft={spacing_left};spacingTop=10;{self._font()}")

    def _clients(self, band, p):
        self.box(p["cell_id"], band.get("label", ""),
                 self._band_style("clients", p["spacing_left"]),
                 p["x"], p["y"], p["w"], p["h"])

    def _incloud(self, band, p):
        self.box(p["cell_id"], band.get("label", "Intility InCloud"),
                 self._band_style("incloud", p["spacing_left"]),
                 p["x"], p["y"], p["w"], p["h"])
        for spec_row, pr in zip(band.get("rows", []), p["rows"]):
            rid = spec_row["id"]
            self.icon(f"icon_{rid}", spec_row.get("icon", "vm"),
                      pr["icon"]["x"], pr["icon"]["y"])
            self.text(f"text_{rid}", spec_row["label"], pr["text"]["x"], pr["text"]["y"],
                      pr["text"]["w"], pr["text"]["h"])

    def _azure(self, band, p):
        scope = band.get("scope", "corp")
        if scope not in self.SCOPES:
            self.warnings.append(
                f"band '{band['id']}' uses scope '{scope}', which is not one of "
                f"{self.SCOPES} — falling back to 'corp'. Colour follows scope, "
                f"nothing else: a second subscription in the same scope reuses "
                f"the same colour, distinguished by its MG/Sub/RG header instead.")
            scope = "corp"
        fill, stroke = self.t[scope]
        self.box(p["cell_id"], "", self._band_style(scope, p["spacing_left"]),
                 p["x"], p["y"], p["w"], p["h"])

        for key, alias in (("mg", "mg"), ("sub", "sub"), ("rg", "rg")):
            seg, val = p["header"][key], band.get(key)
            if not val:
                continue
            self.icon(seg["icon"]["id"], alias, seg["icon"]["x"], seg["icon"]["y"],
                      seg["icon"]["w"], seg["icon"]["h"])
            self.text(seg["text"]["id"], f"<b>{val}</b>", seg["text"]["x"],
                      seg["text"]["y"], seg["text"]["w"], seg["text"]["h"])

        vspec = band.get("vnet")
        if vspec is None:
            # No network: lay the resources out across the band instead of squeezing
            # them into the narrow right-hand column.
            for rspec, rp in zip(band.get("rows", []), p.get("rows", [])):
                rid = rspec["id"]
                self.icon(f"icon_{rid}", rspec.get("icon", "kv"),
                          rp["icon"]["x"], rp["icon"]["y"])
                self.text(f"text_{rid}", rspec["label"], rp["text"]["x"], rp["text"]["y"],
                          rp["text"]["w"], rp["text"]["h"])
            self._right_column(band, p)
            return
        v = p["vnet"]
        self.box(v["id"], vspec.get("label", ""),
                 f"rounded=1;absoluteArcSize=1;arcSize=10;whiteSpace=wrap;html=1;fillColor=none;strokeColor={stroke};"
                 f"dashed=1;dashPattern=8 4;fontSize=11;verticalAlign=top;align=left;"
                 f"spacingLeft={v['spacing_left']};spacingTop=8;fontStyle=1;{self._font()}",
                 v["x"], v["y"], v["w"], v["h"])
        hi = v["header_icon"]
        self.icon(hi["id"], "vnet", hi["x"], hi["y"], hi["w"], hi["h"])

        for sspec, sp in zip(band.get("subnets", []), p["subnets"]):
            label = sspec.get("label", "")
            if len(label) > sp["label_max_chars"]:
                self.warnings.append(
                    f"subnet '{sspec['id']}' label is {len(label)} chars but only "
                    f"{sp['label_max_chars']} fit beside the NSG label — shorten it "
                    f"and move the detail into a resource row")
            self.box(sp["id"], label,
                     f"rounded=1;absoluteArcSize=1;arcSize=10;whiteSpace=wrap;html=1;fillColor=none;strokeColor={stroke};"
                     f"dashed=1;dashPattern=3 3;fontSize=11;verticalAlign=top;align=left;"
                     f"spacingLeft={sp['spacing_left']};spacingTop=6;{self._font()}",
                     sp["x"], sp["y"], sp["w"], sp["h"])
            shi = sp["header_icon"]
            self.icon(shi["id"], "snet", shi["x"], shi["y"], shi["w"], shi["h"])

            if sspec.get("nsg"):
                n = sp["nsg"]
                self.icon(n["icon"]["id"], "nsg", n["icon"]["x"], n["icon"]["y"],
                          n["icon"]["w"], n["icon"]["h"])
                self.text(n["text"]["id"], f"<b>{sspec['nsg']}</b>", n["text"]["x"],
                          n["text"]["y"], n["text"]["w"], n["text"]["h"],
                          n["text"]["font_size"])

            for rspec, rp in zip(sspec.get("rows", []), sp["rows"]):
                rid = rspec["id"]
                self.icon(f"icon_{rid}", rspec["icon"], rp["icon"]["x"], rp["icon"]["y"])
                self.text(f"text_{rid}", rspec["label"], rp["text"]["x"], rp["text"]["y"],
                          rp["text"]["w"], rp["text"]["h"])

        self._right_column(band, p)

    def _right_column(self, band, p):
        col = band.get("right_column")
        if not col:
            return
        for rspec, rp in zip(col.get("rows", []), p["right_column"]["rows"]):
            rid = rspec["id"]
            self.icon(f"icon_{rid}", rspec.get("icon", "pdns"),
                      rp["icon"]["x"], rp["icon"]["y"])
            self.text(f"text_{rid}", rspec["label"], rp["text"]["x"], rp["text"]["y"],
                      rp["text"]["w"], rp["text"]["h"], rp["text"]["font_size"])

    # ---------------------------------------------------------- edges
    def _edges(self, plan, byid):
        bands = plan["bands"]
        order = [b["id"] for b in bands]
        conn = next((b for b in bands if b.get("scope") == "connectivity"), None)
        lane = plan["lanes"]["peering"]

        peer = ("endArrow=none;startArrow=none;html=1;rounded=0;dashed=1;dashPattern=6 3;"
                "strokeColor=#888888;strokeWidth=1.5;fontSize=10;")
        lane_n = 0

        clients = next((b for b in bands if b["kind"] == "clients"), None)
        if clients:
            first_az = next((b for b in bands if b["kind"] == "azure"), None)
            if first_az:
                self.edge("arr_client_agw", "HTTPS",
                          "endArrow=classic;html=1;rounded=0;fontSize=11;"
                          "edgeStyle=orthogonalEdgeStyle;",
                          clients["cell_id"], first_az["vnet"]["id"])

        def draw_peer(eid, up, down, label):
            """Adjacent bands get a straight centre line; anything else goes down its
            own left lane. Never route right — the notes panel lives there."""
            nonlocal lane_n
            if abs(order.index(up["id"]) - order.index(down["id"])) == 1:
                self.edge(eid, label,
                          peer + "exitX=0.5;exitY=1;exitDx=0;exitDy=0;"
                                 "entryX=0.5;entryY=0;entryDx=0;entryDy=0;",
                          up["cell_id"], down["cell_id"])
            else:
                this_lane = lane - 30 * lane_n
                lane_n += 1
                self.edge(eid, label,
                          peer + "exitX=0;exitY=1;exitDx=0;exitDy=0;"
                                 "entryX=0;entryY=0;entryDx=0;entryDy=0;",
                          up["cell_id"], down["cell_id"],
                          points=[(this_lane, up["y"] + up["h"] + 10),
                                  (this_lane, down["y"] - 15)])

        # Direct spoke-to-spoke peering. VNet peering is non-transitive, so an AGW
        # peered only to the hub cannot reach a backend in another spoke — the link
        # has to be drawn because it has to exist.
        for spec_band in self.spec["bands"]:
            for peer_spec in spec_band.get("peers", []):
                if isinstance(peer_spec, str):
                    peer_spec = {"to": peer_spec}
                target = byid.get(peer_spec["to"])
                src = byid.get(spec_band["id"])
                if not target or not src:
                    self.warnings.append(
                        f"band '{spec_band['id']}' declares a peering to "
                        f"'{peer_spec['to']}', which is not a band in this diagram")
                    continue
                a, b2 = ((src, target) if order.index(src["id"]) < order.index(target["id"])
                         else (target, src))
                draw_peer(f"arr_peer_{src['id']}_{target['id']}", a, b2,
                          peer_spec.get("label", "VNet peering (direkte)"))

        if conn:
            ci = order.index(conn["id"])
            for b in bands:
                if b["kind"] != "azure" or b["id"] == conn["id"]:
                    continue
                spec_b = next((x for x in self.spec["bands"] if x["id"] == b["id"]), {})
                if spec_b.get("peers_hub") is False:
                    continue
                bi = order.index(b["id"])
                up, down = (b, conn) if bi < ci else (conn, b)
                draw_peer(f"arr_peer_{b['id']}_conn", up, down, "VNet peering")

        incloud = next((b for b in bands if b["kind"] == "incloud"), None)
        if incloud and conn:
            vpng = self.spec.get("meta", {}).get("vpng_icon_id", "icon_vpng")
            if any(f'id="{vpng}"' in c for c in self.cells):
                self.edge("arr_vpng_incloud", "Direct Link / S2S VPN",
                          "endArrow=classic;startArrow=classic;html=1;rounded=0;"
                          "strokeColor=#565776;strokeWidth=2;fontSize=10;"
                          "exitX=0;exitY=0.5;exitDx=0;exitDy=0;"
                          "entryX=0;entryY=0.3;entryDx=0;entryDy=0;",
                          vpng, incloud["cell_id"],
                          points=[(plan["lanes"]["incloud"], conn["y"] + 140),
                                  (plan["lanes"]["incloud"], incloud["y"] + 78)])

    # ---------------------------------------------------------- notes
    def _notes(self, plan):
        notes = self.spec.get("notes", [])
        if not notes:
            return
        nx, nw = plan["notes"]["x"], plan["notes"]["w"]
        y = plan["notes"]["y"]
        hfill, hstroke = self.t["notes_head"]
        bfill, bstroke = self.t["notes_body"]

        self.box("notes_header", self.spec.get("meta", {}).get("notes_title", "Notater"),
                 f"rounded=1;absoluteArcSize=1;arcSize=10;whiteSpace=wrap;html=1;fillColor={hfill};strokeColor={hstroke};"
                 f"strokeWidth=2;fontSize=13;verticalAlign=middle;align=left;spacingLeft=12;"
                 f"fontStyle=1;fontColor={self.t['notes_head_font']};"
                 + (f"fontFamily={self.t['heading_family']};" if self.t["heading_family"] else ""),
                 nx, y, nw, 40)
        y += 45

        # Height from content, so a short category does not leave dead space.
        chars_per_line = int((nw - 20) / (10 * 0.53))
        for i, cat in enumerate(notes):
            lines = 0
            for item in cat["items"]:
                lines += max(1, -(-len(item) // chars_per_line))
            h = 24 + lines * 15 + 12
            body = "".join(f"<li>{it}</li>" for it in cat["items"])
            val = f"<b>{cat['title']}</b><div><ul>{body}</ul></div>"
            self.box(f"notes_{i}", val,
                     f"rounded=1;absoluteArcSize=1;arcSize=10;whiteSpace=wrap;html=1;fillColor={bfill};"
                     f"strokeColor={bstroke};strokeWidth=2;fontSize=10;verticalAlign=top;"
                     f"align=left;spacingLeft=8;spacingTop=6;{self._font()}",
                     nx, y, nw, h)
            y += h + 5
        self.notes_bottom = y

    # ---------------------------------------------------------- output
    def render(self, plan):
        meta = self.spec.get("meta", {})
        name = meta.get("diagram_name", "azure-architecture")
        page_h = max(plan["page"]["height"], getattr(self, "notes_bottom", 0) + 100)
        return (
            '<mxfile host="app.diagrams.net">\n'
            f'  <diagram name="{esc(name)}" id="{esc(name)}-v1">\n'
            '    <mxGraphModel dx="2000" dy="600" grid="1" gridSize="10" guides="1" '
            'tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" '
            f'pageWidth="{plan["page"]["width"]}" pageHeight="{int(page_h)}" '
            'math="0" shadow="0">\n'
            '      <root>\n        <mxCell id="0" />\n        <mxCell id="1" parent="0" />\n'
            '        ' + "\n        ".join(self.cells) +
            '\n      </root>\n    </mxGraphModel>\n  </diagram>\n</mxfile>\n')


def main(argv):
    out = None
    if "-o" in argv:
        out = argv[argv.index("-o") + 1]

    demo_path = os.path.join(SKILL, "examples", "full-diagram.spec.json")
    if "--print-demo-spec" in argv:
        print(open(demo_path, encoding="utf-8").read())
        return 0
    if "--demo" in argv:
        spec = json.load(open(demo_path, encoding="utf-8"))
    else:
        args = [a for a in argv[1:] if not a.startswith("-")
                and (out is None or a != out)]
        if not args:
            print(__doc__)
            return 2
        spec = json.load(open(args[0], encoding="utf-8"))

    em = Emitter(spec)
    plan = em.build()
    xml = em.render(plan)

    for w in em.warnings:
        print(f"  warn    {w}", file=sys.stderr)

    if out:
        open(out, "w", encoding="utf-8").write(xml)
        print(f"wrote {out}  ({len(em.cells)} cells, page "
              f"{plan['page']['width']}x{plan['page']['height']})")
    else:
        print(xml)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
