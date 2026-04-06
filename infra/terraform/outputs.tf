# ─── Azure OpenAI ─────────────────────────────────────────────────────────────
output "openai_endpoint" {
  description = "Azure OpenAI endpoint URL"
  value       = azurerm_cognitive_account.openai.endpoint
}

output "openai_api_key" {
  description = "Azure OpenAI primary API key"
  value       = azurerm_cognitive_account.openai.primary_access_key
  sensitive   = true
}

# ─── Azure AI Search ──────────────────────────────────────────────────────────
output "search_endpoint" {
  description = "Azure AI Search endpoint (empty if not created)"
  value       = length(azurerm_search_service.main) > 0 ? "https://${azurerm_search_service.main[0].name}.search.windows.net" : ""
}

output "search_admin_key" {
  description = "Azure AI Search primary admin key (empty if not created)"
  value       = length(azurerm_search_service.main) > 0 ? azurerm_search_service.main[0].primary_key : ""
  sensitive   = true
}

# ─── PostgreSQL ───────────────────────────────────────────────────────────────
output "postgres_host" {
  description = "PostgreSQL FQDN"
  value       = azurerm_postgresql_flexible_server.main.fqdn
}

output "postgres_admin_user" {
  description = "PostgreSQL admin username"
  value       = var.postgres_admin_user
}

output "postgres_admin_password" {
  description = "PostgreSQL admin password (auto-generated if not provided)"
  value       = local.pg_password
  sensitive   = true
}

output "database_url" {
  description = "Full PostgreSQL connection string (with sslmode=require for Azure)"
  value       = "postgresql://${var.postgres_admin_user}:${local.pg_password}@${azurerm_postgresql_flexible_server.main.fqdn}:5432/${var.db_name}?sslmode=require"
  sensitive   = true
}

# ─── Entra ID ─────────────────────────────────────────────────────────────────
output "azure_ad_tenant_id" {
  description = "Azure AD Tenant ID"
  value       = data.azuread_client_config.current.tenant_id
}

output "azure_ad_client_id" {
  description = "Entra ID Application (client) ID"
  value       = azuread_application.main.client_id
}

output "azure_ad_audience" {
  description = "Token audience for JWT validation"
  value       = "api://${azuread_application.main.client_id}"
}

# ─── Resource Group ───────────────────────────────────────────────────────────
output "resource_group_name" {
  description = "Name of the resource group (useful for az CLI commands)"
  value       = azurerm_resource_group.main.name
}
