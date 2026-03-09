# ============================================================================
# Terraform Variables for Vault Configuration
# ============================================================================

variable "vault_addr" {
  description = "Vault server address"
  type        = string
  default     = "http://localhost:8200"
}

variable "vault_token" {
  description = "Vault root token for initial configuration"
  type        = string
  default     = "root"
  sensitive   = true
}

variable "postgres_host" {
  description = "PostgreSQL host"
  type        = string
  default     = "postgres"
}

variable "postgres_port" {
  description = "PostgreSQL port"
  type        = number
  default     = 5432
}

variable "postgres_db" {
  description = "PostgreSQL database name"
  type        = string
  default     = "employee_db"
}

variable "postgres_user" {
  description = "PostgreSQL username for Vault connection"
  type        = string
  default     = "vault"
}

variable "postgres_password" {
  description = "PostgreSQL password for Vault connection"
  type        = string
  default     = "vault-password"
  sensitive   = true
}

variable "ibm_verify_tenant" {
  description = "IBM Verify tenant name"
  type        = string
  default     = "your-tenant"
}

variable "ibm_verify_oidc_url" {
  description = "IBM Verify OIDC discovery URL"
  type        = string
  default     = ""
}