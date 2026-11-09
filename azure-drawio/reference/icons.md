# Icon Paths & Sizes

Paths resolve against draw.io's built-in shape libraries. They are **case- and
singular/plural-sensitive** — a wrong path renders as a broken-image placeholder, which is the
most common silent failure in generated diagrams. Copy paths verbatim from this file; never
guess a path by analogy.

Every path in this file has been verified against the icons bundled in draw.io. Re-check after a
draw.io upgrade with:

```bash
python3 scripts/check_icons.py
```

Known traps — the library is not organised the way the Azure portal is, so the "obvious" folder
is often wrong:
- `DNS_Private_Resolver.svg` is **singular**. `DNS_Private_Resolvers.svg` does not exist.
- Function Apps live under `compute/`, **not** `app_services/`.
- Event Hubs live under `analytics/`, **not** `integration/`.
- Redis is `databases/Cache_Redis.svg` — there is no `Azure_Cache_Redis.svg`.
  (`Azure_Managed_Redis.svg` is the separate Azure Managed Redis product.)
- Resource Group, DNS, and DNS Private Zones live under `mscae/`, not `azure2/`.

## Structural / header

| Resource | Path | W | H |
|---|---|---|---|
| Management Group | `img/lib/azure2/general/Management_Groups.svg` | 20 | 19.39 |
| Subscription | `img/lib/azure2/general/Subscriptions.svg` | 14 | 22.59 |
| Resource Group | `img/lib/mscae/ResourceGroup.svg` | 20 | 16 |
| Virtual Network (header) | `img/lib/azure2/networking/Virtual_Networks.svg` | 27 | 16.12 |
| Subnet (header) | `img/lib/azure2/networking/Subnet.svg` | 18 | 10.78 |

## Networking

| Resource | Path | W | H |
|---|---|---|---|
| Application Gateway | `img/lib/azure2/networking/Application_Gateways.svg` | 30 | 30 |
| Public IP | `img/lib/azure2/networking/Public_IP_Addresses.svg` | 30 | 30 |
| Private Endpoint | `img/lib/azure2/networking/Private_Endpoint.svg` | 30 | 27.5 |
| VPN / VNet Gateway | `img/lib/azure2/networking/Virtual_Network_Gateways.svg` | 24 | 31.85 |
| NSG | `img/lib/azure2/networking/Network_Security_Groups.svg` | 16 | 19.43 |
| Route Table | `img/lib/azure2/networking/Route_Tables.svg` | 30 | 30 |
| Firewall | `img/lib/azure2/networking/Firewalls.svg` | 30 | 30 |
| WAF Policy | `img/lib/azure2/networking/Web_Application_Firewall_Policies_WAF.svg` | 30 | 30 |
| Load Balancer | `img/lib/azure2/networking/Load_Balancers.svg` | 30 | 30 |
| Front Door | `img/lib/azure2/networking/Front_Doors.svg` | 30 | 30 |
| DNS Private Resolver | `img/lib/azure2/networking/DNS_Private_Resolver.svg` | 30 | 30 |
| DNS Private Zone | `img/lib/mscae/DNS_Private_Zones.svg` | 22 | 22 |
| DNS Zone (generic / InCloud) | `img/lib/mscae/DNS.svg` | 30 | 30 |

## Compute & containers

| Resource | Path | W | H |
|---|---|---|---|
| App Service | `img/lib/azure2/app_services/App_Services.svg` | 30 | 30 |
| App Service Plan | `img/lib/azure2/app_services/App_Service_Plans.svg` | 30 | 30 |
| Function App | `img/lib/azure2/compute/Function_Apps.svg` | 30 | 30 |
| Container App | `img/lib/azure2/other/Worker_Container_App.svg` | 30 | 30 |
| Container App Environment | `img/lib/azure2/other/Container_App_Environments.svg` | 30 | 30 |
| Container Registry | `img/lib/azure2/containers/Container_Registries.svg` | 38 | 38 |
| AKS | `img/lib/azure2/compute/Kubernetes_Services.svg` | 38 | 38 |
| Virtual Machine | `img/lib/azure2/compute/Virtual_Machine.svg` | 30 | 30 |

## Databases

| Resource | Path | W | H |
|---|---|---|---|
| SQL Database | `img/lib/azure2/databases/SQL_Database.svg` | 38 | 38 |
| SQL Server | `img/lib/azure2/databases/SQL_Server.svg` | 38 | 38 |
| Cosmos DB | `img/lib/azure2/databases/Azure_Cosmos_DB.svg` | 38 | 38 |
| PostgreSQL | `img/lib/azure2/databases/Azure_Database_PostgreSQL_Server.svg` | 38 | 38 |
| Redis Cache | `img/lib/azure2/databases/Cache_Redis.svg` | 38 | 38 |

## Storage, security, integration, monitoring

| Resource | Path | W | H |
|---|---|---|---|
| Storage Account | `img/lib/azure2/storage/Storage_Accounts.svg` | 38 | 38 |
| Key Vault | `img/lib/azure2/security/Key_Vaults.svg` | 38 | 38 |
| Certificate (Intility ACME) | `img/lib/mscae/Certificate.svg` | 38 | 38 |
| Managed Identity | `img/lib/azure2/identity/Managed_Identities.svg` | 30 | 30 |
| Service Bus | `img/lib/azure2/integration/Service_Bus.svg` | 38 | 38 |
| Event Hub | `img/lib/azure2/analytics/Event_Hubs.svg` | 38 | 38 |
| Event Grid | `img/lib/azure2/integration/Event_Grid_Topics.svg` | 38 | 38 |
| API Management | `img/lib/azure2/integration/API_Management_Services.svg` | 38 | 38 |
| App Configuration | `img/lib/azure2/integration/App_Configuration.svg` | 38 | 38 |
| Application Insights | `img/lib/azure2/management_governance/Application_Insights.svg` | 30 | 42.95 |
| Log Analytics Workspace | `img/lib/azure2/management_governance/Log_Analytics_Workspaces.svg` | 43 | 43 |
| Monitor | `img/lib/azure2/management_governance/Monitor.svg` | 38 | 38 |

## Icon cell style

One style string for every icon; only `image=` and the geometry change:

```
image;aspect=fixed;html=1;points=[];align=center;fontSize=12;image=<PATH>;
```

`ResourceGroup.svg` additionally takes `sketch=0`:

```
image;sketch=0;aspect=fixed;html=1;points=[];align=center;fontSize=12;image=img/lib/mscae/ResourceGroup.svg;
```
