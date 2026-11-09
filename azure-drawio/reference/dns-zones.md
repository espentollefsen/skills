# Private DNS Zones & Subnet Sizing

**Verified 2026-09-11** against Microsoft Learn
(`learn.microsoft.com/azure/private-link/private-endpoint-dns` and
`learn.microsoft.com/azure/networking/design-guide/vnets-subnets`).

This table is a snapshot and Azure moves. **If the workload uses a service that is not listed
here, do not infer a zone name from the pattern — look it up** with the `microsoft-learn` MCP
(`microsoft_docs_search` for "private endpoint DNS zone <service>"), then add it below. Guessing
zone names is how you ship a diagram whose private endpoints silently resolve to public IPs.

All `privatelink.*` zones live in `<customercode>-connectivity`, linked to every spoke VNet.
Never place them in a workload subscription.

## Zones by service

`{region}` = the Azure region short name, e.g. `norwayeast`. Zones marked **region-scoped**
MUST include it — a region-less zone name will not resolve.

| Service | Private DNS zone | Notes |
|---|---|---|
| App Service / Function App | `privatelink.azurewebsites.net` | Covers the `scm` site too |
| Container App Environment (private endpoint) | `privatelink.{region}.azurecontainerapps.io` | **region-scoped** |
| Container App Environment (internal, VNet-scope ingress, no PE) | `<unique-id>.{region}.azurecontainerapps.io` | Zone is the env's `defaultDomain`; add wildcard `*` A-record → env `staticIp`. NOT a `privatelink.` zone |
| AKS private cluster | `privatelink.{region}.azmk8s.io` | **region-scoped**. API-Server-VNet-Integration variant: `private.{region}.azmk8s.io` |
| Container Registry | `privatelink.azurecr.io` | Premium SKU only. The regional data endpoint (`{region}.data.privatelink.azurecr.io`) is **not** a separate zone when using Azure Private DNS — its records are added automatically to this zone. Only create it separately with custom DNS |
| Key Vault | `privatelink.vaultcore.azure.net` | |
| SQL Database | `privatelink.database.windows.net` | |
| SQL Managed Instance | `privatelink.{dnsPrefix}.database.windows.net` | |
| PostgreSQL Flexible Server | `privatelink.postgres.database.azure.com` | |
| MySQL Flexible Server | `privatelink.mysql.database.azure.com` | |
| Cosmos DB (SQL/Core) | `privatelink.documents.azure.com` | Per-API variants: `mongo.`, `cassandra.`, `gremlin.`, `table.cosmos.azure.com` |
| Redis Cache | `privatelink.redis.cache.windows.net` | Enterprise SKU: `privatelink.redisenterprise.cache.azure.net` |
| Service Bus **and** Event Hub | `privatelink.servicebus.windows.net` | Same zone for both — list it once |
| Event Grid | `privatelink.eventgrid.azure.net` | |
| API Management | `privatelink.azure-api.net` | |
| App Configuration | `privatelink.azconfig.io` | |
| Storage — blob | `privatelink.blob.core.windows.net` | One zone **per sub-resource in use** |
| Storage — file | `privatelink.file.core.windows.net` | |
| Storage — queue | `privatelink.queue.core.windows.net` | |
| Storage — table | `privatelink.table.core.windows.net` | |
| Storage — dfs (Data Lake Gen2) | `privatelink.dfs.core.windows.net` | |
| Storage — static website | `privatelink.web.core.windows.net` | |
| Azure OpenAI / AI Services | `privatelink.openai.azure.com`, `privatelink.cognitiveservices.azure.com`, `privatelink.services.ai.azure.com` | |
| Azure AI Search | `privatelink.search.windows.net` | |
| SignalR | `privatelink.service.signalr.net` | |
| Web PubSub | `privatelink.webpubsub.azure.com` | |
| Azure Relay | `privatelink.servicebus.windows.net` | Shares the Service Bus zone |
| Data Factory | `privatelink.datafactory.azure.net` **and** `privatelink.adf.azure.com` | Second zone is the portal/authoring endpoint |
| Synapse — SQL / SQL on-demand | `privatelink.sql.azuresynapse.net` | |
| Synapse — Dev | `privatelink.dev.azuresynapse.net` | |
| Synapse Studio | `privatelink.azuresynapse.net` | `privateLinkHubs` resource |
| Databricks | `privatelink.azuredatabricks.net` | `databricks_ui_api` + `browser_authentication` |
| Data Explorer (Kusto) | `privatelink.{region}.kusto.windows.net` + blob/queue/table zones | **region-scoped** |
| Static Web Apps | `privatelink.azurestaticapps.net` and `privatelink.{partitionId}.azurestaticapps.net` | |
| Batch | `privatelink.batch.azure.com` | Both `batchAccount` and `nodeManagement` |
| Recovery Services vault (Backup) | `privatelink.{geo}.backup.windowsazure.com` + blob and queue zones | `{geo}` is a region code (`ne`, `eus`), not the region name |
| Azure Virtual Desktop | `privatelink-global.wvd.microsoft.com` (global) and `privatelink.wvd.microsoft.com` (feed/connection) | |
| Machine Learning | `privatelink.api.azureml.ms`, `privatelink.notebooks.azure.net` | |

## Azure Monitor Private Link Scope (AMPLS)

Log Analytics and Application Insights do **not** get one zone each — they share a single AMPLS
private endpoint that needs **all five** of these zones. Listing only `monitor.azure.com` is a
common and breaking mistake:

- `privatelink.monitor.azure.com`
- `privatelink.oms.opinsights.azure.com`
- `privatelink.ods.opinsights.azure.com`
- `privatelink.agentsvc.azure-automation.net`
- `privatelink.blob.core.windows.net` (agent profile/solution-pack downloads)

In the diagram, draw **one** PE (`pe-ampls-<proj>-<env>`) labelled `PE → ampls-<proj>-<env>`,
and list all five zones in the connectivity band. If the workload already has a Storage blob PE,
`privatelink.blob.core.windows.net` is shared — list it once.

## Dedicated subnet requirements

| Service | Subnet name | Size | Delegation |
|---|---|---|---|
| Application Gateway v2 | any (`snet-agw-<env>`) | **/24 recommended** (min. formula-based; /26 works for ≤32 instances but Microsoft recommends /24 for autoscale headroom) | none — must be dedicated, no other resources |
| VPN / ExpressRoute Gateway | `GatewaySubnet` (reserved) | **/27 minimum**, /26 preferred | none |
| Azure Firewall | `AzureFirewallSubnet` (reserved) | **/26** | none |
| Azure Bastion | `AzureBastionSubnet` (reserved) | **/26** | none |
| Route Server | `RouteServerSubnet` (reserved) | **/26** | none |
| DNS Private Resolver — inbound | `snet-dnspr-in-<env>` | **/28 min**, /27–/24 for headroom | `Microsoft.Network/dnsResolvers` |
| DNS Private Resolver — outbound | `snet-dnspr-out-<env>` | **/28 min** | `Microsoft.Network/dnsResolvers` |
| App Service / Function VNet integration | `snet-app-<proj>-<env>` | /26 | `Microsoft.Web/serverFarms` |
| Container App Environment (workload profiles) | `snet-cae-<proj>-<env>` | **/27 min** | `Microsoft.App/environments` |
| Private Endpoints | `snet-pe-<proj>-<env>` | /27 (or /26 if >27 PEs) | none — PEs consume IPs from a normal subnet |

**DNS Private Resolver — critical:** inbound and outbound endpoints each require their **own**
dedicated subnet delegated to `Microsoft.Network/dnsResolvers`. They cannot share a subnet, and
no other resource may live in either. Draw two subnets when the customer needs both directions.
