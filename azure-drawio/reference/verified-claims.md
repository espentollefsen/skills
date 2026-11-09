# Verified Product Claims

Standing assertions the diagrams make about Azure behaviour. `verify_facts.py` reads this file:
a claim listed here with a `verified` date is reported as settled; anything else surfaces as
NEEDS LOOKUP on every diagram until someone checks it and records the result here.

Add a row only after actually reading the Microsoft Learn page — not from memory. Re-check a
claim when it is older than about a year, or when it decides something expensive.

| id | Claim | Verdict | Verified | Source |
|---|---|---|---|---|
| `sb-premium-pe` | Service Bus requires the **Premium** tier for Private Endpoint | CONFIRMED | 2026-09-11 | `learn.microsoft.com/azure/service-bus-messaging/private-link-service` — "This feature is supported with the premium tier of Azure Service Bus" |
| `acr-premium-pe` | Container Registry requires the **Premium** SKU for Private Endpoint | CONFIRMED | 2026-09-11 | `learn.microsoft.com/azure/container-registry/container-registry-skus` — SKU table: "Private link with private endpoints — Basic N/A, Standard N/A, Premium Supported" |
| `appsvc-cert-agw` | An App Service **Managed Certificate** cannot be used on Application Gateway | CONFIRMED | 2026-09-11 | `learn.microsoft.com/troubleshoot/azure/app-service/connection-issues-with-ssl-or-tls/use-azure-app-service-certificate-with-application-gateway` — AGW accepts only `.pfx` with private key; App Service certs are "Direct use ❌ Not supported" and must be exported via Key Vault. Managed Certificates are not exportable at all, so Key Vault integration is the only route |
| `peering-nontransitive` | VNet peering is **non-transitive** — two spokes peered to the same hub cannot reach each other without UDR-through-NVA or direct peering. AGW must peer directly to its backend VNet | CONFIRMED | 2026-09-11 | `learn.microsoft.com/azure/networking/design-guide/hub-spoke` — "VNet peering is non-transitive. Spokes can reach the hub, but spokes can't reach each other directly through the hub unless you configure routing or direct peering between them." Documents "hub-and-spoke with direct peering" as a supported variant, noting such traffic bypasses central firewall inspection |
| `aca-pe-preview` | Container Apps **private endpoint** requires a workload-profile environment and is **Public Preview** | CONFIRMED | 2026-09-11 | `learn.microsoft.com/azure/private-link/availability` — "Azure Container Apps … Supported for workload profile environments … Public Preview" |
| `agw-waf-v2` | WAF_v2 (and Standard_v2) is the Application Gateway SKU family that provides autoscaling, and gateways are zone-redundant across ≥2 AZs **by default** on this SKU | CONFIRMED | 2026-09-21 | `learn.microsoft.com/azure/reliability/reliability-application-gateway-v2` — "When you deploy a new gateway, it's zone-redundant by default" (Standard_v2/WAF_v2 only) |
| `vpngw-az` | `VpnGw*AZ` SKUs are the zone-redundant VPN Gateway SKUs; all VPN Gateway tiers except **Basic** support zone redundancy when using an AZ SKU | CONFIRMED | 2026-09-21 | `learn.microsoft.com/azure/reliability/reliability-virtual-network-gateway` — "All tiers of VPN Gateway support zone redundancy except the Basic SKU" |
| `kv-soft-delete` | Key Vault **soft-delete** is enabled by default on every new vault (since Sept 2019) and cannot be disabled; **purge protection** is a separate setting and is **NOT enabled by default** — it must be turned on explicitly and, once on, cannot be turned off | CONFIRMED | 2026-09-21 | `learn.microsoft.com/azure/key-vault/general/soft-delete-overview` — "When creating a new key vault, soft-delete is on by default"; "Purge protection is an optional Key Vault behavior and is not enabled by default" |
| `psql-flexible-pe` | Azure Database for PostgreSQL Flexible Server supports **Private Endpoint** (Private Link) as an alternative to VNet-integration (private access); the two networking modes are mutually exclusive per server — a server created with VNet integration cannot add a private endpoint | CONFIRMED | 2026-09-21 | `learn.microsoft.com/azure/postgresql/network/concepts-networking-private-link` — "The use of private endpoints isn't currently supported on servers created with virtual network integration" |
| `aca-subnet-sizing` | Container Apps subnet delegation requirements differ by environment type: **Consumption-only** needs a **non-delegated** `/23`-minimum subnet; **Workload profiles** needs a subnet delegated to `Microsoft.App/environments` with a **/27 minimum**. Internal ingress and VNet integration work on both types — workload profiles are required only for UDR-based egress control and (in Public Preview) private endpoints, not for internal ingress itself | CONFIRMED | 2026-09-21 | `learn.microsoft.com/azure/container-apps/custom-virtual-networks#subnet`, `learn.microsoft.com/azure/container-apps/networking` |
| `agw-backend-aca-no-pe` | An Application Gateway backend pool can target an internal-ingress Container Apps Environment directly by FQDN (or the environment's static internal IP) over VNet peering, without the Container App needing a private endpoint — this requires the AGW to resolve the environment's private DNS zone | CONFIRMED | 2026-09-21 | `learn.microsoft.com/azure/container-apps/waf-app-gateway` — backend pool "Target type: IP address or FQDN", using the Container App's Application URL; `learn.microsoft.com/answers/a/2609173` — "if they're in different vnets, u need peering... if using private container app, u need private dns zones" |

## Not yet verified

These are asserted in diagrams but have **not** been checked against Microsoft Learn in this
skill. They will keep appearing as NEEDS LOOKUP, which is intended — verify and move them up.

| id | Claim |
|---|---|
