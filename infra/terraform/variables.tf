variable "subscription_id" {
  description = "Azure Subscription ID"
  type        = string
}

variable "location" {
  description = "Azure region for all resources"
  type        = string
  default     = "westeurope"
}

variable "project" {
  description = "Short project name used in resource naming (no spaces, lowercase)"
  type        = string
  default     = "aiportfolio"
}

variable "env" {
  description = "Environment tag (dev / staging / prod)"
  type        = string
  default     = "dev"
}

variable "postgres_admin_user" {
  description = "PostgreSQL administrator username"
  type        = string
  default     = "pgadmin"
}

variable "postgres_admin_password" {
  description = "PostgreSQL administrator password (leave empty to auto-generate)"
  type        = string
  default     = ""
  sensitive   = true
}

variable "db_name" {
  description = "Database name to create inside PostgreSQL"
  type        = string
  default     = "portfolio_manager"
}

variable "openai_gpt4o_deployment" {
  description = "Azure OpenAI deployment name for GPT-4o"
  type        = string
  default     = "gpt-4o"
}

variable "openai_o3mini_deployment" {
  description = "Azure OpenAI deployment name for o3-mini"
  type        = string
  default     = "o3-mini"
}

# Capacity in thousands of tokens per minute (TPM / 1000).
# 1 = 1 000 TPM, enough for a PoC. Increase to 10+ for real usage.
variable "openai_tpm_capacity" {
  description = "Azure OpenAI TPM capacity (x1000) per deployment"
  type        = number
  default     = 1
}

variable "create_search_service" {
  description = "Set to true to create a free Azure AI Search service. Limited to 1 per subscription."
  type        = bool
  default     = false
}
