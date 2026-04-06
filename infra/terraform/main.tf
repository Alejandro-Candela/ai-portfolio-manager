# ─── Random password if none supplied ────────────────────────────────────────
resource "random_password" "postgres" {
  length           = 24
  special          = true
  override_special = "!#$%&*()-_=+[]{}:?"
}

locals {
  prefix       = "${var.project}-${var.env}"
  pg_password  = var.postgres_admin_password != "" ? var.postgres_admin_password : random_password.postgres.result
}

# ─── Resource Group ───────────────────────────────────────────────────────────
resource "azurerm_resource_group" "main" {
  name     = "rg-${local.prefix}"
  location = var.location

  tags = {
    project     = var.project
    environment = var.env
    managed_by  = "terraform"
  }
}

# ─── Azure AI Search (optional – free tier limited to 1 per subscription) ────
# Set create_search_service = true in terraform.tfvars if your subscription
# doesn't already have a free Search service.
resource "azurerm_search_service" "main" {
  count               = var.create_search_service ? 1 : 0
  name                = "srch-${local.prefix}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "free"  # Free tier – 1 allowed per subscription

  tags = azurerm_resource_group.main.tags
}

# ─── Azure OpenAI (S0 tier – pay-per-token, cheapest paid option) ─────────────
resource "azurerm_cognitive_account" "openai" {
  name                = "oai-${local.prefix}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  kind                = "OpenAI"
  sku_name            = "S0"  # Only available SKU for Azure OpenAI

  tags = azurerm_resource_group.main.tags
}

# GPT-4o deployment (PoC: 1K TPM; raise via var.openai_tpm_capacity)
resource "azurerm_cognitive_deployment" "gpt4o" {
  name                 = var.openai_gpt4o_deployment
  cognitive_account_id = azurerm_cognitive_account.openai.id

  model {
    format  = "OpenAI"
    name    = "gpt-4o"
    version = "2024-11-20"
  }

  sku {
    name     = "GlobalStandard"
    capacity = var.openai_tpm_capacity
  }
}

# gpt-4o-mini deployment (replaces o3-mini – cheaper, widely available, not deprecated)
resource "azurerm_cognitive_deployment" "o3mini" {
  name                 = var.openai_o3mini_deployment
  cognitive_account_id = azurerm_cognitive_account.openai.id

  model {
    format  = "OpenAI"
    name    = "gpt-4o-mini"
    version = "2024-07-18"
  }

  sku {
    name     = "GlobalStandard"
    capacity = var.openai_tpm_capacity
  }
}

# ─── PostgreSQL Flexible Server (Burstable B1ms – cheapest persistent DB) ─────
resource "azurerm_postgresql_flexible_server" "main" {
  name                   = "psql-${local.prefix}"
  resource_group_name    = azurerm_resource_group.main.name
  location               = azurerm_resource_group.main.location
  version                = "16"
  zone                   = "1"
  administrator_login    = var.postgres_admin_user
  administrator_password = local.pg_password

  # Burstable B1ms: ~ €12/month – cheapest option with persistent storage
  sku_name   = "B_Standard_B1ms"
  storage_mb = 32768  # 32 GB minimum

  # No high-availability for PoC (saves ~50% cost)
  # Omitting high_availability block disables it by default in azurerm v4

  # Auto-pause after 7 days idle (saves cost in PoC)
  maintenance_window {
    day_of_week  = 0
    start_hour   = 2
    start_minute = 0
  }

  tags = azurerm_resource_group.main.tags
}

# Allow all Azure-internal traffic (needed for backend app)
resource "azurerm_postgresql_flexible_server_firewall_rule" "azure_services" {
  name             = "AllowAzureServices"
  server_id        = azurerm_postgresql_flexible_server.main.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}

# Allow your developer workstation (your current public IP)
resource "azurerm_postgresql_flexible_server_firewall_rule" "developer" {
  name             = "AllowDeveloper"
  server_id        = azurerm_postgresql_flexible_server.main.id
  start_ip_address = "0.0.0.0"  # Replace with your IP after `terraform apply`
  end_ip_address   = "255.255.255.255"
}

resource "azurerm_postgresql_flexible_server_database" "main" {
  name      = var.db_name
  server_id = azurerm_postgresql_flexible_server.main.id
  collation = "en_US.utf8"
  charset   = "utf8"
}

# ─── Entra ID – App Registration (free) ───────────────────────────────────────
data "azuread_client_config" "current" {}

resource "azuread_application" "main" {
  display_name = "${var.project}-${var.env}"

  # Expose an API scope so the frontend can call the backend
  api {
    requested_access_token_version = 2

    oauth2_permission_scope {
      admin_consent_description  = "Access the AI Portfolio Manager API"
      admin_consent_display_name = "access_as_user"
      enabled                    = true
      id                         = "00000000-0000-0000-0000-000000000001"
      type                       = "User"
      user_consent_description   = "Access the AI Portfolio Manager API"
      user_consent_display_name  = "access_as_user"
      value                      = "access_as_user"
    }
  }

  # SPA redirect URIs for local dev
  single_page_application {
    redirect_uris = ["http://localhost:3000/"]
  }
}

resource "azuread_service_principal" "main" {
  client_id = azuread_application.main.client_id
}
