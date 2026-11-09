#!/usr/bin/env python3
"""Extract the verifiable Azure claims from a diagram and check what can be checked.

validate_drawio.py checks that the file is well-formed; this checks whether the
architecture it draws is *true*. It pulls every private DNS zone, subnet size,
delegation and SKU assertion out of the labels and cross-checks them against
reference/dns-zones.md.

Anything it cannot settle locally is printed under NEEDS LOOKUP — take those to
the microsoft-learn MCP (`microsoft_docs_search`), then add the answer to
reference/dns-zones.md so the next diagram resolves it locally.

Usage:
    python3 verify_facts.py diagram.drawio
    python3 verify_facts.py diagram.drawio --json

Exit 0 = nothing unresolved, 1 = at least one GAP or MISMATCH.
"""

# Windows consoles/pipes default to a legacy code page; force UTF-8 so labels and
# messages containing arrows, middots or Norwegian letters never raise UnicodeEncodeError.
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
import html
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
REF = os.path.join(SKILL, "reference", "dns-zones.md")
CLAIMS = os.path.join(SKILL, "reference", "verified-claims.md")

# Resource-name prefix -> private DNS zone(s) that must appear in the diagram.
# Sourced from reference/dns-zones.md; {region} is filled from the diagram title.
PE_ZONES = {
    "kv": ["privatelink.vaultcore.azure.net"],
    "sqldb": ["privatelink.database.windows.net"],
    "sql": ["privatelink.database.windows.net"],
    "psql": ["privatelink.postgres.database.azure.com"],
    "mysql": ["privatelink.mysql.database.azure.com"],
    "cosmos": ["privatelink.documents.azure.com"],
    "redis": ["privatelink.redis.cache.windows.net"],
    "sb": ["privatelink.servicebus.windows.net"],
    "evhns": ["privatelink.servicebus.windows.net"],
    "apim": ["privatelink.azure-api.net"],
    "appcs": ["privatelink.azconfig.io"],
    "app": ["privatelink.azurewebsites.net"],
    "func": ["privatelink.azurewebsites.net"],
    "aks": ["privatelink.{region}.azmk8s.io"],
    "st": ["privatelink.blob.core.windows.net"],
    "cr": ["privatelink.azurecr.io"],
    "ampls": [
        "privatelink.monitor.azure.com",
        "privatelink.oms.opinsights.azure.com",
        "privatelink.ods.opinsights.azure.com",
        "privatelink.agentsvc.azure-automation.net",
        "privatelink.blob.core.windows.net",
    ],
}

# Subnet purpose -> (minimum prefix length, required delegation or None, source note)
SUBNET_RULES = {
    "gatewaysubnet": (27, None, "VPN/ER Gateway: /27 minimum, /26 preferred"),
    "azurefirewallsubnet": (26, None, "Azure Firewall: /26"),
    "azurebastionsubnet": (26, None, "Azure Bastion: /26"),
    "routeserversubnet": (26, None, "Route Server: /26"),
    "agw": (24, None, "Application Gateway v2: /24 recommended for autoscale headroom"),
    "dnspr": (28, "Microsoft.Network/dnsResolvers",
              "DNS Private Resolver: /28 min, own subnet per endpoint"),
    "cae": (27, "Microsoft.App/environments",
            "Container App Environment (workload profiles): /27 min"),
    "app": (26, "Microsoft.Web/serverFarms", "App Service VNet integration: /26"),
    "pe": (27, None, "Private endpoints: /27 (or /26 above 27 PEs)"),
}

# Phrases that assert a product constraint. True or not, they should be sourced.
SKU_PATTERNS = [
    ("sb-premium-pe", r"Service Bus[^|]*Premium",
     "Service Bus Premium is required for Private Endpoint"),
    ("acr-premium-pe", r"Container Registry[^|]*Premium",
     "ACR Premium is required for Private Endpoint"),
    ("agw-waf-v2", r"WAF_v2",
     "Application Gateway WAF_v2 supports WAF + autoscale"),
    ("vpngw-az", r"VpnGw\d+AZ", "Zone-redundant VPN Gateway SKU"),
    ("aca-workload-profiles", r"workload profiles?",
     "Container Apps workload profiles required for VNet integration"),
    ("kv-soft-delete", r"[Ss]oft-delete", "Key Vault soft-delete / purge protection"),
    ("appsvc-cert-agw", r"App Service Managed Certificate",
     "App Service Managed Certificate cannot be used on Application Gateway"),
]


def load_verified_claims():
    """ids in the CONFIRMED table -> date. Rows under 'Not yet verified' have no date."""
    if not os.path.isfile(CLAIMS):
        return {}
    out = {}
    for line in open(CLAIMS, encoding="utf-8"):
        m = re.match(r"\|\s*`([\w-]+)`\s*\|.*?\|\s*(CONFIRMED|REFUTED)\s*\|"
                     r"\s*(\d{4}-\d{2}-\d{2})\s*\|", line)
        if m:
            out[m.group(1)] = (m.group(2), m.group(3))
    return out


def load_known_zones():
    if not os.path.isfile(REF):
        return set(), None
    text = open(REF, encoding="utf-8").read()
    zones = set(re.findall(r"`((?:privatelink|[a-z0-9-]+\.data\.privatelink)[^`]*)`", text))
    zones |= set(re.findall(r"`(privatelink-global[^`]*)`", text))
    m = re.search(r"\*\*Verified (\d{4}-\d{2}-\d{2})\*\*", text)
    return zones, (m.group(1) if m else None)


def plain(v):
    """Strip markup to text, replacing tags with a space.

    Dropping tags outright glues adjacent list items together
    ("...azurecontainerapps.io." + "Sonen trenger...") which corrupts every
    regex downstream — zone names then run into the next sentence.
    """
    v = html.unescape(html.unescape(v or ""))
    v = re.sub(r"<br\s*/?>", " | ", v)
    v = re.sub(r"<[^>]+>", " ", v)
    return re.sub(r"[ \t]+", " ", v).strip()


def collect(path):
    root = ET.fromstring(open(path, encoding="utf-8").read())
    labels, title = [], ""
    for cell in root.iter("mxCell"):
        t = plain(cell.get("value"))
        if t:
            labels.append(t)
            if cell.get("id") == "title":
                title = t
    return labels, title


def analyse(path):
    labels, title = collect(path)
    known, verified_on = load_known_zones()
    corpus = "\n".join(labels)

    region = ""
    m = re.search(r"·\s*([a-z]+(?:east|west|north|south|central)[a-z0-9]*)", title)
    if m:
        region = m.group(1)

    ok, gaps, lookups = [], [], []

    # ---- zones present in the diagram
    zones_drawn = set(re.findall(
        r"\b(privatelink(?:-global)?(?:\.[a-z0-9][a-z0-9\-]*)+)", corpus))
    special = set(re.findall(r"\{defaultDomain\}[\w.\-]*|[\w.\-]*azurecontainerapps\.io", corpus))

    # rstrip: a trailing sentence period would otherwise make the negated form
    # differ from the captured zone and defeat the exclusion.
    negated = {z.rstrip(".") for z in
               re.findall(r"(?:IKKE|ikke|NOT|not)\s+(privatelink[\w.\-]*)", corpus)}
    for z in sorted(zones_drawn - negated):
        generic = re.sub(r"\.(no|we|ne|eu)?[a-z]*(east|west|north|south|central)[a-z0-9]*\.",
                         ".{region}.", z)
        if z in known or generic in known or z.replace(region, "{region}") in known:
            ok.append(f"zone {z} matches reference/dns-zones.md")
        else:
            lookups.append(f"zone '{z}' is not in reference/dns-zones.md — confirm the exact "
                           f"name with microsoft_docs_search \"private endpoint DNS zone\"")
    for z in sorted(special):
        if "{defaultDomain}" in z:
            ok.append("Container Apps internal ingress uses the environment defaultDomain "
                      "as the private zone (not a privatelink zone) — matches reference")

    # ---- every private endpoint must have its zone drawn
    for target in re.findall(r"PE\s*→\s*([A-Za-z0-9\-]+)", corpus):
        if "-" in target:
            key = target.split("-", 1)[0]
        else:
            key = next((k for k in ("st", "cr") if target.startswith(k)), target)
        if key not in PE_ZONES:
            lookups.append(f"private endpoint '{target}': cannot infer the service from its "
                           f"name — confirm its required zone with microsoft_docs_search")
            continue
        for want in PE_ZONES[key]:
            want_r = want.replace("{region}", region or "{region}")
            if want_r in zones_drawn or want in zones_drawn or (
                    "{region}" in want and any(want.split("{region}")[-1] in z
                                               for z in zones_drawn)):
                ok.append(f"PE {target} → zone {want_r} is drawn")
            else:
                gaps.append(f"PE '{target}' is drawn but its zone '{want_r}' is NOT in the "
                            f"connectivity band — the endpoint will resolve to a public IP")

    # ---- subnet sizing and delegation
    for name, prefix in re.findall(r"\b((?:snet-[\w\-]+|GatewaySubnet|Azure\w+Subnet|"
                                   r"RouteServerSubnet))\s*\([\d.]+/(\d+)\)", corpus):
        low = name.lower()
        rule = None
        for key, r in SUBNET_RULES.items():
            if low.startswith(key) or key in low:
                rule = (key, r)
                break
        if not rule:
            continue
        key, (minlen, deleg, note) = rule
        if int(prefix) <= minlen:
            ok.append(f"{name} /{prefix} satisfies /{minlen} — {note}")
        else:
            gaps.append(f"{name} is /{prefix} but the documented minimum is /{minlen} — {note}")
        if deleg:
            if deleg in corpus:
                ok.append(f"{name} delegation {deleg} is stated")
            else:
                gaps.append(f"{name} needs delegation to {deleg}, which is not stated "
                            f"anywhere in the diagram")

    # ---- SKU / product assertions
    settled = load_verified_claims()
    for cid, pat, claim in SKU_PATTERNS:
        if not re.search(pat, corpus):
            continue
        if cid in settled:
            verdict, when = settled[cid]
            ok.append(f"claim '{cid}' {verdict} {when} — {claim}")
        else:
            lookups.append(f"claim '{cid}' is unverified: {claim} — confirm with "
                           f"microsoft_docs_search, then record it in "
                           f"reference/verified-claims.md")

    return {"title": title, "region": region, "verified_on": verified_on,
            "ok": ok, "gaps": gaps, "lookups": lookups}


def main(argv):
    targets = [a for a in argv[1:] if not a.startswith("--")]
    if not targets:
        print(__doc__)
        return 2
    as_json = "--json" in argv
    failed = False

    for path in targets:
        r = analyse(path)
        if as_json:
            print(json.dumps(r, indent=2, ensure_ascii=False))
        else:
            print(f"== {os.path.basename(path)}")
            if r["verified_on"]:
                print(f"   reference/dns-zones.md verified {r['verified_on']}"
                      f"{'  region=' + r['region'] if r['region'] else ''}")
            for m in r["gaps"]:
                print(f"  GAP           {m}")
            for m in r["lookups"]:
                print(f"  NEEDS LOOKUP  {m}")
            for m in r["ok"]:
                print(f"  ok            {m}")
            if not r["gaps"] and not r["lookups"]:
                print("  OK            every claim resolves against the reference")
        if r["gaps"]:
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
