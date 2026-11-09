# Naming Conventions

Format: `<abbreviation>-<projectname>-<environment>`
Hub/shared resources substitute `hub` or `shared` for `<projectname>`.

| Resource | Abbrev. | Example | Constraint |
|---|---|---|---|
| Virtual Network | `vnet` | `vnet-invoicing-corp-prod` | |
| Subnet | `snet` | `snet-app-invoicing-prod` | |
| NSG | `nsg` | `nsg-app-invoicing-prod` | |
| Route Table | `rt` | `rt-app-invoicing-prod` | |
| Application Gateway | `agw` | `agw-shared-prod` | always `shared` |
| WAF Policy | `waf` | `waf-shared-prod` | |
| Public IP | `pip` | `pip-agw-shared-prod` | |
| VPN Gateway | `vpng` | `vpng-hub-prod` | always `hub` |
| Local Network Gateway | `lgw` | `lgw-incloud-prod` | |
| Private Endpoint | `pe` | `pe-kv-invoicing-prod` | |
| DNS Private Resolver | `dnspr` | `dnspr-hub-prod` | |
| DNS Forwarding Ruleset | `dnsfrs` | `dnsfrs-hub-prod` | |
| Firewall | `afw` | `afw-hub-prod` | |
| App Service Plan | `asp` | `asp-invoicing-prod` | |
| App Service | `app` | `app-invoicing-prod` | |
| Function App | `func` | `func-invoicing-prod` | |
| Container App | `ca` | `ca-invoicing-prod` | |
| Container App Environment | `cae` | `cae-invoicing-prod` | |
| Container Registry | `cr` | `crinvoicingprod` | no hyphens, 5–50 chars, alphanumeric only, globally unique |
| AKS | `aks` | `aks-invoicing-prod` | |
| Virtual Machine | `vm` | `vm-invoicing-prod` | Windows name ≤15 chars |
| SQL Server (logical) | `sql` | `sql-invoicing-prod` | globally unique |
| SQL Database | `sqldb` | `sqldb-invoicing-prod` | |
| Cosmos DB | `cosmos` | `cosmos-invoicing-prod` | globally unique, lowercase |
| PostgreSQL Flexible | `psql` | `psql-invoicing-prod` | globally unique |
| MySQL Flexible | `mysql` | `mysql-invoicing-prod` | globally unique |
| Redis Cache | `redis` | `redis-invoicing-prod` | globally unique |
| Storage Account | `st` | `stinvoicingprod` | no hyphens, 3–24 chars, lowercase alphanumeric, globally unique |
| Key Vault | `kv` | `kv-invoicing-prod` | 3–24 chars, globally unique |
| Key Vault (certificates, shared) | `kv-cert` | `kv-cert-prod` | Lives in `<cc>-management`. Holds Intility ACME certificates for AGW and private custom domains. **Public endpoint** — ACME does not use private networking, so no private endpoint |
| Managed Identity | `id` | `id-invoicing-prod` | |
| Service Bus Namespace | `sb` | `sb-invoicing-prod` | globally unique |
| Event Hub Namespace | `evhns` | `evhns-invoicing-prod` | globally unique |
| Event Grid Topic | `evgt` | `evgt-invoicing-prod` | |
| API Management | `apim` | `apim-invoicing-prod` | globally unique |
| App Configuration | `appcs` | `appcs-invoicing-prod` | globally unique |
| Application Insights | `appi` | `appi-invoicing-prod` | |
| Log Analytics Workspace | `log` | `log-invoicing-prod` | |
| Monitor Private Link Scope | `ampls` | `ampls-invoicing-prod` | |
| Resource Group | `rg` | `rg-app-prod` | |

**Reserved subnet names — never rename:** `GatewaySubnet`, `AzureFirewallSubnet`,
`AzureFirewallManagementSubnet`, `AzureBastionSubnet`, `RouteServerSubnet`.

**Names with a `-corp-` / `-online-` infix:** only VNets and their subnets carry the
exposure-tier infix (`vnet-invoicing-online-prod`). PaaS resources do not.

## Resource groups — one per logical layer

| RG | Contains |
|---|---|
| `rg-network-<env>` | VNet, subnets, NSGs, route tables, private endpoints |
| `rg-app-<env>` | App Service plan, App Service, Functions, Container Apps, AKS |
| `rg-data-<env>` | SQL, Cosmos, PostgreSQL, Redis, Storage |
| `rg-shared-<env>` | Key Vault, Managed Identity, Container Registry |
| `rg-monitor-<env>` | Log Analytics, Application Insights, AMPLS |
| `rg-conn-<env>` | Hub VNet, VPN Gateway, DNS Private Resolver, private DNS zones (in `-connectivity`) |
| `rg-cert-<env>` | Certificate Key Vault written to by Intility ACME (in `-management`). No VNet — ACME uses the public endpoint |
| `rg-agw-network-<env>` | AGW VNet/subnet, AGW, public IP, WAF policy (in `-online`) |
