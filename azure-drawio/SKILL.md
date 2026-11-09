---
name: azure-drawio
compatibility: opencode
metadata:
  domain: azure-architecture
  output: drawio
description: >
  Use this skill whenever the user wants to create, generate, or update an Azure architecture diagram in draw.io (.drawio / .xml) format.
  Triggers include: any request to diagram Azure resources, create a draw.io file for an Azure solution, visualize an Azure Landing Zone, draw infrastructure for a customer workload, or produce an architecture overview. Also triggers when the user provides a list of Azure resources and wants a diagram, even if they don't explicitly mention draw.io.
  Always use this skill when producing draw.io XML output involving Azure resources — it encodes all required conventions, icon paths, color schemes, naming standards, and design rules.
---

# Azure Architecture Diagrams in draw.io

Produces `.drawio` files for Azure architectures aligned with Microsoft Enterprise-Scale Landing
Zone (ESLZ) and Cloud Adoption Framework (CAF), using the official Azure SVG icons built into
draw.io, on Intility's hub-and-spoke conventions.

## Files in this skill

Read a reference file when you reach the step that needs it — don't read them all up front.

| File | Read it when |
|---|---|
| `reference/styles.md` | **Before writing any `value=`.** XML escaping rules, container styles, colours, edge styles |
| `reference/icons.md` | Choosing icon paths and sizes |
| `reference/naming.md` | Naming resources and resource groups |
| `reference/dns-zones.md` | Picking `privatelink.*` zones or sizing a dedicated subnet |
| `reference/verified-claims.md` | Asserting a SKU or product constraint; record new verifications here |
| `scripts/emit.py` | **Step 5 — the normal way to build a diagram.** Spec in, `.drawio` out |
| `scripts/layout.py` | Only if hand-assembling XML: computes every coordinate |
| `scripts/validate_drawio.py` | Step 7 — mandatory check before you show the user anything |
| `scripts/verify_facts.py` | Step 8 — mandatory. Checks the architecture's claims, not the file |
| `scripts/check_icons.py` | An icon renders as a grey placeholder, or after a draw.io upgrade |
| `examples/full-diagram.spec.json` | The spec to copy and adapt — a complete six-band diagram |
| `examples/full-diagram.drawio` | What that spec produces, validated and rendered |
| `examples/canonical-band.drawio` | A minimal hand-written two-band file showing the raw XML patterns |

---

## Running in opencode

Two things differ from other agent runtimes:

1. **Script paths and interpreter.** Every `scripts/…`, `reference/…` and `examples/…` path in
   this document is relative to the directory containing this `SKILL.md` (opencode reports that
   directory when the skill loads). The shell's working directory is the *user's project*, so
   call scripts by their full path and keep output in the project.

   The Python command depends on the platform — pick the one that works, don't assume:

   | Platform | Command |
   |---|---|
   | macOS / Linux / WSL / Git Bash | `python3` |
   | Windows (PowerShell / cmd) | `python` — or `py -3` if `python` is missing. `python3` on Windows is often a Microsoft Store stub that prints nothing; do not use it |

   bash / Git Bash / WSL:

   ```bash
   SKILL_DIR="<directory containing this SKILL.md>"
   python3 "$SKILL_DIR/scripts/emit.py" spec.json -o <cc>-<proj>-<env>.drawio
   python3 "$SKILL_DIR/scripts/validate_drawio.py" <cc>-<proj>-<env>.drawio
   python3 "$SKILL_DIR/scripts/verify_facts.py"    <cc>-<proj>-<env>.drawio
   ```

   PowerShell:

   ```powershell
   $SkillDir = "<directory containing this SKILL.md>"
   python "$SkillDir\scripts\emit.py" spec.json -o <cc>-<proj>-<env>.drawio
   python "$SkillDir\scripts\validate_drawio.py" <cc>-<proj>-<env>.drawio
   python "$SkillDir\scripts\verify_facts.py"    <cc>-<proj>-<env>.drawio
   ```

   Read and edit files under `reference/` (Steps 4 and 8 add verified facts there) by that same
   full path. Python 3 standard library only — nothing to `pip install`. All files are UTF-8; the
   scripts force UTF-8 console output, so Norwegian text and `→` are safe on Windows.

   The Step 9 preview command `drawio -x …` needs the draw.io desktop app's CLI. On Windows it is
   usually **not** on PATH; try `& "$env:LOCALAPPDATA\Programs\draw.io\draw.io.exe" -x -f png …`
   or `& "C:\Program Files\draw.io\draw.io.exe" …`, and if neither exists say so rather than
   skipping the step silently.

2. **MCP tool names.** opencode registers MCP tools as `<server-name>_<tool-name>`. Wherever this
   document says `microsoft_docs_search`, call the tool matching `*microsoft_docs_search` — with
   the recommended config (server named `microsoft-learn`) that is
   `microsoft-learn_microsoft_docs_search`. If no such tool is listed, treat the MCP as
   unavailable and follow the "MCP is unavailable" rules in Steps 4 and 8.

---

## Step 0: Gather required inputs

Ask for anything missing. Each of these seven changes the diagram's structure, so do not start
generating until they are all settled.

| Input | Purpose | Example |
|---|---|---|
| `customercode` | Short customer identifier, prefixes every scope | `contoso` |
| `projectname` | Workload / project name | `invoicing` |
| `environment` | Deployment environment | `prod`, `dev`, `test`, `stg` |
| `region` | Azure region — appears in the title, the notes, and every region-scoped DNS zone | `norwayeast` |
| `internet_facing` | Does any service need to be reachable from the internet? | Yes / No |
| `custom_domain` | Only if `internet_facing=Yes`: the public domain | `invoice.contoso.com` |
| `incloud` | Does the workload need to reach Intility InCloud? | Yes / No |

**If `internet_facing=Yes`**, also confirm the custom domain. It appears on the AGW label, on each
internet-facing resource's label, and as a DNS A-record note (`<custom_domain>` →
`pip-agw-shared-<env>`) in the notes panel.

**If `incloud=Yes`**, also ask:

1. **Domain type** — `i04.local` or a custom customer domain?
   - `i04.local` → DNS resolved via **Azure InCloud DNS Integration** (no DNS Private Resolver;
     DNS rides the Direct Link). Draw it as an icon+text row inside the hub VNet.
   - `Cust Domain` → DNS resolved via **DNS Private Resolver**. Ask which direction(s):
     **inbound** (on-prem → Azure), **outbound** (Azure → on-prem), or **both**.
2. **InCloud services** — for each server to be reached: name (`sql01.i04.local`) and
   port/protocol (`TCP 1433`). Each becomes a row inside the InCloud band.

**Language.** Match the user's language for all prose — labels, notes, section headings. Intility
work is usually Norwegian; if the user writes Norwegian, write Norwegian. Resource names, SKU
names, and DNS zones are always literal and never translated. Be consistent: don't mix Norwegian
and English section headings in the notes panel.

---

## Step 1: Design rules

### Core architecture

1. **Private by default.** Every PaaS service gets a Private Endpoint. Service Endpoints are
   legacy — never propose them. VNet Integration handles outbound from App Services/Container Apps.
   The single exception is the Intility ACME certificate vault — see rule 7b.
2. **AGW + WAF as reverse proxy.** All internet-facing services sit behind an Application Gateway
   (WAF_v2) in `<cc>-online`. Only draw the AGW band when `internet_facing=Yes`.
3. **DNS in the connectivity hub.** All `privatelink.*` zones live in `<cc>-connectivity`, linked
   to every spoke VNet. Never place them in a workload subscription.
4. **Management-group split.** Corp workloads → `<cc>-corp`. Internet-facing → `<cc>-online`.
   Shared services (VPN/ER, DNS, Firewall) → `<cc>-connectivity`.
5. **Naming.** `<type>-<projectname>-<environment>`; hub/shared resources use `hub` or `shared`.
   See `reference/naming.md`.
6. **Resource group per logical layer.** See the RG table in `reference/naming.md`.
7. **Subnet sizing and delegation.** See the table in `reference/dns-zones.md`. The ones people
   get wrong: AGW v2 wants **/24**, `GatewaySubnet` wants **/27**, and DNS Private Resolver needs
   **two** /28 subnets — one for inbound, one for outbound, each delegated to
   `Microsoft.Network/dnsResolvers`, neither shared with anything else.

7b. **Certificates come from Intility ACME, stored in `<cc>-management`.** Any service that
   needs a custom domain — the Application Gateway, and any *private* service with its own custom
   domain — gets its certificate issued through **Intility ACME** and stored in a shared Key Vault
   under the `<cc>-management` management group. **Always draw this when a custom domain is in
   play:** add a `management` band with the certificate Key Vault, and name the vault on every
   consumer's label (`sertifikat: kv-cert-<env>`). Never show a certificate uploaded directly to
   the AGW, and never put the certificate vault in a workload subscription — it is shared platform
   infrastructure, like DNS.

   **Intility ACME does not use private networking — `kv-cert` is the one documented exception to
   rules 1 and 15.** ACME reaches the vault over its public endpoint, so the management band has
   **no VNet, no subnet and no private endpoint**. Omit `vnet` from the band entirely and set
   `"peers_hub": false` — there is nothing to peer. Drawing a private endpoint here would be
   drawing something that does not exist. State the exception in the notes panel rather than
   letting it look like an oversight, and record which network restrictions guard the vault
   instead (Key Vault firewall, RBAC) — ask if you do not know.

### Networking and topology

8. **Hub-and-spoke, with direct peering where traffic actually needs it.** Workload VNets peer
   to the hub; they do not peer to each other by default. But **VNet peering is non-transitive** —
   two spokes both peered to the hub still cannot reach each other unless you route through a
   firewall/NVA with UDRs, or peer them directly. Microsoft documents "hub-and-spoke with direct
   peering" as a supported variant for exactly this.
   **The AGW VNet therefore peers directly to the VNet holding its backend pool.** An Application
   Gateway peered only to the hub cannot reach an App Service, Container App or AKS in a spoke, so
   a diagram that shows only the hub peering is drawing something that does not work. Declare it
   in the spec with `"peers": ["<band-id>"]` on the AGW band.
   Note the trade-off in the notes panel: directly peered traffic bypasses central firewall
   inspection.
9. **NSG on every subnet — except the reserved platform subnets.** Icon + label, even in dev.
   Do **not** draw an NSG on `AzureFirewallSubnet` (unsupported) or `GatewaySubnet` (unsupported
   for ExpressRoute, and discouraged for VPN).
10. **Draw the VPN gateway only when it does something.** `vpng-hub-<env>` and `GatewaySubnet`
    exist to reach InCloud/on-prem. If `incloud=No` and there is no other hybrid requirement, omit
    both — the hub VNet still exists to host the private DNS zones.
11. **IP planning in the notes.** Always document proposed CIDR ranges.

### Security and identity

12. **Managed Identity over secrets.** Always prefer it; flag any service principal or secret in
    the notes panel.
13. **Key Vault per workload.** One KV per project/subscription, never shared.
14. **Diagnostics on everything.** All resources send diagnostics to the workload LAW.
15. **No public endpoints on PaaS.** Private Endpoints only — except `kv-cert` (rule 7b), where
    the public endpoint is required by ACME and must be shown as such.

### Availability and operations

16. **Availability Zones for prod.** AGW, Container Apps, SQL, Redis must have AZ enabled in prod.
17. **Backup and retention in the notes.** Key Vault MUST have soft-delete + purge protection.

### Observability

18. **Application Insights is always workspace-based**, linked to `log-<projectname>-<env>`.
19. **One LAW per workload** — do not share across workloads in prod.
20. **Private monitoring needs AMPLS.** If monitoring must stay private, draw one
    `ampls-<proj>-<env>` private endpoint and list all five zones from `reference/dns-zones.md`.
    Listing only `privatelink.monitor.azure.com` breaks agent ingestion.

---

## Step 2: Split the workload by internet exposure

Classify **every** resource. Both bands appear whenever the workload has both kinds.

| Resource | Scope | Band colour (Bifrost) |
|---|---|---|
| Internet-facing, or needs outbound internet | `<cc>-online` | chill-purple `#e7dcfe` / `#631cce` |
| Purely internal | `<cc>-corp` | brand-teal `#d8fdf8` / `#007375` |

AKS/App Service exposed via AGW → online. KV/SQL/Storage/CR/LAW/App Insights → corp.

### Colour follows scope, nothing else

There are exactly four valid `scope` values: `online`, `connectivity`, `management`, `corp`. Each
gets one colour — there is no second shade for a second subscription that happens to share a
scope. If the workload has, say, a shared-services corp subscription and a workload corp
subscription, **both bands are `scope: "corp"` and both render in the same brand-teal.** What
tells them apart is the band header (MG · Subscription · RG), not the fill colour — invent a
distinguishing subscription or RG name, never a new colour. `emit.py` warns and falls back to
`corp` if a spec uses a scope outside this list.

---

## Step 3: Band order

The diagram is a vertical stack of full-width **bands**. Include only the bands that apply, in
this order — the layout script assigns every y-coordinate from this list:

| # | Band `id` | `kind` | Present when |
|---|---|---|---|
| 1 | `client_box` | `clients` | `internet_facing=Yes` |
| 2 | `online_gw` | `azure` (online) | `internet_facing=Yes` — the AGW + public IP |
| 3 | `online_wl` | `azure` (online) | there are internet-facing workload resources |
| 4 | `conn` | `azure` (connectivity) | **always** — hub VNet + private DNS zones |
| 5 | `management` | `azure` (management) | **any custom domain is used** — holds the Intility ACME certificate Key Vault |
| 6 | `corp` | `azure` (corp) | there are internal resources |
| 7 | `incloud_box` | `incloud` | `incloud=Yes` |

Each Azure band contains: three header segments (MG · Subscription · RG), one VNet, its subnets,
and optionally a right-hand column — private DNS zones in `conn`, PaaS resources in `corp`.

---

## Step 4: Infer the missing infrastructure

From the user's resource list, add what they didn't mention:

- App Service / Function → `snet-app` (delegated `Microsoft.Web/serverFarms`) + PE
- Container App Env → `snet-cae` (delegated `Microsoft.App/environments`) + PE
- SQL / Cosmos / Storage / Redis / SB / ACR / KV → PE **and** the matching zone in `conn`
- Every workload → KV + LAW + workspace-based App Insights
- Managed Identity when MI auth is used → PaaS column, not a subnet
- `internet_facing=Yes` → AGW WAF_v2 + `pip-agw-shared-<env>`; custom domain on the AGW label and
  on every internet-facing resource label; A-record note in the notes panel
- `incloud=Yes` → Direct Link edge from `icon_vpng` to `incloud_box`; `i04.local` needs **no**
  separate DNS edge (DNS rides the Direct Link); `Cust Domain` needs the resolver subnets
- Every subnet → NSG icon + label

**Never omit the private DNS zones**, even for a two-resource workload — a PE without its zone is
the most common real-world breakage this diagram is meant to prevent.

### Verify, don't infer

`reference/dns-zones.md` is a dated snapshot, not a complete list, and Azure moves. Zone names do
**not** follow a guessable pattern: Container Apps and AKS are region-scoped while Key Vault is
not, Event Hub shares Service Bus's zone, and Container Registry's regional data endpoint is a
record *inside* the main zone rather than a zone of its own.

Before you put a zone name, a subnet delegation, or a minimum subnet size in a diagram:

1. If it is in `reference/dns-zones.md`, use it verbatim.
2. If it is **not** there, look it up with the `microsoft-learn` MCP —
   `microsoft_docs_search` with "private endpoint DNS zone <service>" or "<service> subnet
   delegation requirements" — then add the result to the reference file so the next diagram gets
   it for free.
3. If the MCP is unavailable, say so and mark the value as unverified in the notes panel rather
   than presenting a guess as fact.

The same applies to any SKU constraint you are about to assert (which SKUs support Private
Endpoint, which need a dedicated subnet). A wrong zone name produces a diagram that looks correct
and silently resolves to a public IP.

---

## Step 5: Build the diagram with the emitter

Write a content spec and emit the file. The emitter owns layout, styling, escaping, edge routing
and notes sizing, so a miscounted row can no longer shift everything below it:

```bash
python3 scripts/emit.py spec.json -o <customercode>-<projectname>-<env>.drawio
```

Start from `examples/full-diagram.spec.json` — it is a complete six-band diagram. See its shape
with `python3 scripts/emit.py --print-demo-spec`. Structure:

```json
{
  "meta":  {"title": "nordly-kundeportal-prod", "diagram_name": "nordly-kundeportal-prod",
            "region": "norwayeast", "notes_title": "Notater"},
  "theme": "bifrost",
  "bands": [
    {"id": "client_box", "kind": "clients", "label": "Eksterne brukere · https://..."},
    {"id": "corp", "kind": "azure", "scope": "corp",
     "mg": "nordly-corp", "sub": "nordly-kundeportal-prod", "rg": "rg-network-prod",
     "vnet": {"label": "vnet-kundeportal-corp-prod (10.20.0.0/22)", "w": 680},
     "subnets": [{"id": "snet_pe", "label": "snet-pe-... (10.20.1.0/27)", "nsg": "nsg-pe-prod",
                  "rows": [{"id": "pe_kv", "icon": "pe", "label": "<b>pe-kv-...</b><br>PE → kv-..."}]}],
     "right_column": {"kind": "paas", "rows": [{"id": "kv", "icon": "kv", "label": "..."}]}}
  ],
  "notes": [{"title": "1. Nettverk", "items": ["...", "..."]}]
}
```

- **Labels go in plain readable form** (`<b>name</b><br>text`) — the emitter escapes them.
- **`icon`** is a short alias (`kv`, `pe`, `agw`, `sqldb`, `vpng`, `pdns`, …). The alias table at
  the top of `emit.py` maps each to a verified path and size; add new ones there, not inline.
- **`vnet.w`**: 700 for the AGW VNet, 580 for the hub (leaves room for the DNS-zone column),
  680 for workload VNets.
- **Edges are automatic**: HTTPS from the clients band, VNet peering from every Azure band to the
  connectivity band — routed down its own left lane when a band sits in between — and the Direct
  Link when an InCloud band is present.
- **A band with no network**: omit `vnet` entirely and the band draws only its headers and
  resource column — used for the ACME certificate vault, which has no private networking.
- **Direct spoke-to-spoke peering**: add `"peers": ["corp_fe"]` to a band (or
  `[{"to": "corp_fe", "label": "..."}]`). Required on the AGW band so it can reach its backend.
  Set `"peers_hub": false` to suppress the automatic hub peering for a band.
- **Notes heights are computed from content**, so a short category leaves no dead space.
- **`theme`**: `bifrost` (default, Intility's design system) or `classic` (the original palette).

The emitter warns when a subnet label is too long to sit beside its NSG label. Fix those warnings
— they render as overlapping text.

If a diagram needs a shape the emitter cannot express, extend `emit.py` rather than hand-writing
XML. Hand assembly is where these diagrams historically went wrong.

### Hand-assembly fallback

Only if the emitter genuinely cannot express the diagram. Run `python3 scripts/layout.py spec.json`
for the coordinates (`--demo` shows a full example), then follow Step 6. Never compute coordinates
yourself: every box below a change has to move too.

## Step 6: The raw XML (hand-assembly reference)

### File skeleton (required)

```xml
<mxfile host="app.diagrams.net">
  <diagram name="<cc>-<proj>-<env>" id="<cc>-<proj>-<env>-v1">
    <mxGraphModel dx="2000" dy="600" grid="1" gridSize="10" guides="1" tooltips="1" connect="1"
                  arrows="1" fold="1" page="1" pageScale="1" pageWidth="1700" pageHeight="2400"
                  math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <!-- every other mxCell here, each with parent="1" -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

- `id="0"` and `id="1" parent="0"` must be the first two cells.
- Every other cell needs `parent="1"`. The model is flat — nesting is not used; containment is
  purely geometric.
- All coordinates are concrete numbers. Never emit an arithmetic expression.
- Use the `pageHeight` the planner reports.

### Escaping

Read `reference/styles.md` first. Labels are HTML inside an XML attribute: bold is
`&lt;b&gt;…&lt;/b&gt;`, a line break is `&lt;br&gt;`, a literal ampersand is `&amp;amp;`, and a
non-breaking space is `&amp;nbsp;`. **All label formats below are written in readable source
form — escape them before emitting.**

### Icon + text is always two cells

Icons never carry labels. Every resource is an icon cell with `value=""` plus a text cell to its
right at the coordinates the planner gave you.

```xml
<mxCell id="icon_kv" style="image;aspect=fixed;html=1;points=[];align=center;fontSize=12;image=img/lib/azure2/security/Key_Vaults.svg;" value="" vertex="1" parent="1">
  <mxGeometry x="-10" y="1460" width="38" height="38" as="geometry" />
</mxCell>
<mxCell id="text_kv" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;fontSize=11;" value="&lt;b&gt;kv-invoicing-prod&lt;/b&gt;&lt;br&gt;Key Vault · Standard (Private Endpoint)" vertex="1" parent="1">
  <mxGeometry x="28" y="1452" width="320" height="45" as="geometry" />
</mxCell>
```

### Band header — three segments

Azure scope bands have `value=""`. Their label is three icon+text pairs at the fixed offsets the
planner reports: Management Group, then Subscription, then Resource Group.

| Segment | Icon | Text (source form) |
|---|---|---|
| MG | `Management_Groups.svg` | `<b>contoso-corp</b>` |
| Subscription | `Subscriptions.svg` | `<b>contoso-invoicing-prod</b>` |
| RG | `ResourceGroup.svg` (+`sketch=0`) | `<b>rg-app-prod</b>` |

VNet and subnet boxes keep their label on the box itself; the planner places their small header
icon so it clears the text (`spacingLeft=42` for VNets, `38` for subnets).

### Label formats (source form — escape before emitting)

| Resource | Label |
|---|---|
| App Service | `<b>app-proj-prod</b> · App Service<br>Custom domain: <domain> · VNet integrated` |
| Function App | `<b>func-proj-prod</b> · Function App<br>VNet integrated` |
| Container App | `<b>ca-proj-prod</b> · Container App<br>cae-proj-prod · VNet integrated` |
| Container App Env | `<b>cae-proj-prod</b> · Container App Environment<br>delegated · Microsoft.App/environments` |
| AGW | `<b>agw-shared-prod</b> · Application Gateway (WAF_v2)<br>Custom domain: <domain> → pip-agw-shared-prod` |
| Public IP | `<b>pip-agw-shared-prod</b><br>Public IP · Standard · Static` |
| Private Endpoint | `<b>pe-kv-proj-prod</b><br>PE → kv-proj-prod` |
| Key Vault | `<b>kv-proj-prod</b><br>Key Vault · Standard (Private Endpoint)` |
| Container Registry | `<b>crprojprod</b><br>Container Registry · Premium (Private Endpoint)` |
| SQL Database | `<b>sqldb-proj-prod</b><br>SQL Database · General Purpose (Private Endpoint)` |
| Storage | `<b>stprojprod</b><br>Storage Account · Standard_LRS (Private Endpoint)` |
| Service Bus | `<b>sb-proj-prod</b><br>Service Bus · Premium (Private Endpoint)` |
| App Insights | `<b>appi-proj-prod</b><br>Application Insights → log-proj-prod` |
| Log Analytics | `<b>log-proj-prod</b><br>Log Analytics Workspace` |
| Managed Identity | `<b>id-proj-prod</b><br>User-Assigned Managed Identity` |
| VPN Gateway | `<b>vpng-hub-prod</b><br>VPN Gateway · VpnGw2AZ` |
| DNS Private Resolver | `<b>dnspr-hub-prod</b><br>DNS Private Resolver · Inbound endpoint` (or `Outbound endpoint`) |
| Private DNS zone | `<b>privatelink.vaultcore.azure.net</b>` (fontSize 10) |
| NSG | `<b>nsg-app-prod</b>` (fontSize 10) |
| InCloud server | `<b>sql01.i04.local</b><br>TCP 1433` |
| Subnet box | `snet-app-prod (10.1.0.0/26)` — see the length limit below |

**Label width budgets.** Text cells do not clip — an over-long label renders straight past its
box and off the edge of the band. `validate_drawio.py` catches both cases, but aim for:

| Where | Budget per line |
|---|---|
| Subnet box label (shares its row with the NSG label) | the `LABEL MAX n CHARS` the planner reports — ~60 on the narrow hub, ~77 elsewhere |
| Right-hand PaaS column (310px wide) | **~46 characters** |
| Right-hand DNS zone column (280px) | ~48 characters |
| Resource row inside a subnet (420px) | ~70 characters |
| Full-width row in a VNet-less or InCloud band (900px / 600px) | plenty — put the detail here |

Keep subnet labels to `name (CIDR)` and move delegation and purpose into the resource row
underneath, where there is room.

### Cell IDs

| Element | Pattern | Example |
|---|---|---|
| Band | `<scope>_sub`, or `client_box` / `incloud_box` | `corp_sub`, `conn_sub` |
| Band header | `<band>_mg_icon` / `_mg_text`, `_sub_icon` / `_sub_text`, `_rg_icon` / `_rg_text` | `corp_mg_icon` |
| VNet / its icon | `<scope>_vnet`, `<scope>_vnet_icon` | `corp_vnet` |
| Subnet / its icon | `snet_<purpose>`, `snet_<purpose>_subnet_icon` | `snet_pe` |
| Resource | `icon_<name>` + `text_<name>` | `icon_kv`, `text_kv` |
| Private endpoint | `icon_pe_<target>` + `text_pe_<target>` | `icon_pe_kv` |
| NSG | `icon_nsg_<snet>` + `text_nsg_<snet>` | `icon_nsg_pe` |
| DNS zone | `icon_pdns_<service>` + `text_pdns_<service>` | `icon_pdns_kv` |
| Edge | `arr_<from>_<to>` | `arr_peer_hub_corp` |
| Notes | `notes_header`, `notes_<category>` | `notes_dns` |

### Edges

Edges use `source`/`target` cell IDs and need `edge="1" parent="1"`. Styles are in
`reference/styles.md`.

- **HTTPS ingress** — `client_box` → `online_gw_vnet`, label `HTTPS`.
- **VNet peering** — band to band, `exitX=0.5;exitY=1` → `entryX=0.5;entryY=0`, label
  `VNet peering`. Between *adjacent* bands this needs no waypoints.
- **Peering that skips a band** — when `online_wl` sits between `online_gw` and `conn`, the
  AGW→hub peering must route around it down the **left** lane at `x=-790`
  (`exitX=0;exitY=1`, waypoints `(-790, …)`, `entryX=0;entryY=0`). Never route it right: the
  notes panel occupies `x=400…940`.
- **Direct Link** — `icon_vpng` ↔ `incloud_box`, double-headed, label `Direct Link / S2S VPN`,
  routed down the outer left lane at `x=-900` so it clears the peering lane.
- **Do not draw PE → PaaS arrows.** The PE label (`PE → kv-proj-prod`) already states the
  relationship, and the arrows turn the diagram into spaghetti.

### Notes panel

Fixed at `x=400, y=180, w=540`, independent of which bands exist. A header cell (`Notes`,
height 40) then one cell per category, each `y = previous_y + previous_height + 5`.

Generate **all eight** categories, omitting only #8 when `incloud=No`:

1. **Network** — region, CIDR ranges per subnet, peering topology, NSG rules, private endpoints
2. **SKU choices** — a justified SKU for every service drawn
3. **Backup/DR** — backup policies, soft-delete + purge protection, geo-replication, AZ, RTO/RPO
4. **Identity/Auth** — MI role assignments (`AcrPull`, `Key Vault Secrets User`), certificate
   strategy, OAuth/OIDC; flag any secret or service principal here
5. **DNS** — every `privatelink.*` zone, InCloud DNS integration or resolver rulesets, and the
   `<custom_domain>` → `pip-agw-shared-<env>` A-record
6. **AGW and certificates** — WAF policy version, backend pool, custom domain, and the
   certificate chain: issued by **Intility ACME** → stored in `kv-cert-<env>` in `<cc>-management`
   → read by AGW (and by any private service with a custom domain) via managed identity with
   *Key Vault Secrets User*. App Service Managed Certificates are **not** usable here
7. **Open questions** — pending decisions and assumptions you made
8. **Intility InCloud** — server names, ports/protocols, required NSG/firewall rules

---

## Step 6b: Write the file

Write to `<customercode>-<projectname>-<environment>.drawio` in the working directory, not to
chat. State the path afterwards. Only paste raw XML into the conversation if the user explicitly
asks for it.

## Step 7: Validate — mandatory

```bash
python3 scripts/validate_drawio.py <file>.drawio
```

Fix every `ERROR` and re-run until clean; read each `warn` and decide. The validator catches
malformed escaping, missing `parent="1"`, dangling edge endpoints, non-existent icon paths,
labels on icon cells, overlapping bands or icons, and boxes that overflow their band.

## Step 8: Verify the architecture against Microsoft Learn — mandatory

Step 7 proves the file is well-formed. This proves the architecture is *true*:

```bash
python3 scripts/verify_facts.py <file>.drawio
```

It extracts every private DNS zone, subnet size, delegation and SKU assertion from the labels and
cross-checks them against `reference/dns-zones.md` and `reference/verified-claims.md`.

Act on the output:

- **GAP** — a real defect. The commonest is a private endpoint drawn without its DNS zone, which
  produces a diagram that looks correct and resolves to a public IP. Fix the spec and re-emit.
- **NEEDS LOOKUP** — the script cannot settle it locally. **Look each one up with the
  `microsoft-learn` MCP** (`microsoft_docs_search`), then:
  - a zone or subnet rule → add it to `reference/dns-zones.md`
  - a SKU or product claim → add a row to `reference/verified-claims.md` with the verdict, the
    date and the source URL
  so the next diagram resolves it without a lookup.
- **ok** — already verified; the date it was checked is shown.

Two rules about this step:

1. **Never silence a NEEDS LOOKUP by deleting the claim from the diagram.** Either verify it or
   mark it unverified in the notes panel.
2. **Never present an unverified claim to a customer as fact.** If the MCP is unavailable, say so
   and flag the item in the notes panel instead of guessing.

Zone names do not follow a guessable pattern — Container Apps and AKS are region-scoped while Key
Vault is not, Event Hub shares Service Bus's zone, and Container Registry's regional data endpoint
is a record *inside* the main zone rather than a zone of its own. Inference is how wrong diagrams
get shipped.

## Step 9: Render it and actually look at it

The validator checks structure; only a render shows you the diagram. If the draw.io desktop app
is installed, this is the strongest check available — do it every time:

```bash
drawio -x -f png --scale 2 -o /tmp/preview.png <file>.drawio
```

Then **open the PNG and inspect it.** Look for:

- grey broken-image placeholders where an icon should be → run `scripts/check_icons.py <file>`
- labels overlapping each other, an icon, or a box border
- text running past the right edge of its band
- boxes with wildly uneven empty space, which usually means a row count was wrong
- edges cutting through a band instead of routing down a lane

A diagram that validates but renders badly is still a broken diagram. Fix and re-render.
If `drawio` is not on PATH, say so rather than silently skipping this step.

Then self-check what neither the validator nor the render can show:

- [ ] Every PaaS resource has a private endpoint **and** a matching zone in `conn`
- [ ] Region-scoped zones include the region (ACA, AKS)
- [ ] Every subnet has an NSG icon + label, except `GatewaySubnet` / `AzureFirewallSubnet`
- [ ] `custom_domain` appears on the AGW and on each internet-facing resource
- [ ] Any custom domain ⇒ a `management` band with the Intility ACME certificate Key Vault is drawn, and every consumer's label names it
- [ ] The `management` band has **no** VNet/subnet/private endpoint, and the public-endpoint exception is stated in the notes
- [ ] `vpng` / `GatewaySubnet` drawn only if there's a hybrid requirement
- [ ] The AGW band declares a direct peering to the VNet holding its backend pool
- [ ] Resolver inbound and outbound are in **separate** subnets
- [ ] All eight notes categories present (seven if `incloud=No`), in one consistent language
- [ ] Title reads `<cc>-<proj>-<env>` and the region appears in the title or notes

Tell the user what you assumed or inferred — especially resources you added that they never
mentioned.
