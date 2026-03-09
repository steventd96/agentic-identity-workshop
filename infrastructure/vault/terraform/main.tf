# ============================================================================
# Vault Configuration using Terraform for Agentic Security Lab
# ============================================================================
# This Terraform configuration sets up HashiCorp Vault with:
# - JWT authentication for IBM Verify
# - Database secrets engine for PostgreSQL
# - Policies for hr-basic and hr-admin groups
# - External group mappings
# ============================================================================

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    vault = {
      source  = "hashicorp/vault"
      version = "~> 4.0"
    }
  }
}

provider "vault" {
  address = var.vault_addr
  token   = var.vault_token
}

# ============================================================================
# Audit Logging
# ============================================================================

resource "vault_audit" "file" {
  type = "file"

  options = {
    file_path = "/vault/logs/audit.log"
  }
}

# ============================================================================
# JWT Authentication Method
# ============================================================================

resource "vault_jwt_auth_backend" "ibm_verify" {
  description        = "JWT auth backend for IBM Verify"
  path               = "jwt"
  oidc_discovery_url = var.ibm_verify_oidc_url
  bound_issuer       = var.ibm_verify_oidc_url
  default_role       = "agent-role"
}

resource "vault_jwt_auth_backend_role" "agent_role" {
  backend         = vault_jwt_auth_backend.ibm_verify.path
  role_name       = "agent-role"
  role_type       = "jwt"
  bound_audiences = ["vault", "a7ffd6ef-50a6-4f08-91d5-c08b37424f2f"]  # Accept both vault and agent client ID
  user_claim      = "sub"
  groups_claim    = "groupIds"  # IBM Verify uses groupIds instead of groups
  token_ttl       = 3600   # 1 hour
  token_max_ttl   = 86400  # 24 hours
  
  # Token policies - base policies for all authenticated users
  token_policies  = ["default"]
}

# ============================================================================
# Vault Policies
# ============================================================================

resource "vault_policy" "hr_basic" {
  name   = "hr-basic-policy"
  policy = file("${path.module}/../policies/hr-basic-policy.hcl")
}

resource "vault_policy" "hr_admin" {
  name   = "hr-admin-policy"
  policy = file("${path.module}/../policies/hr-admin-policy.hcl")
}

# ============================================================================
# Database Secrets Engine
# ============================================================================

resource "vault_database_secrets_mount" "db" {
  path = "database"

  postgresql {
    name              = "employee-db"
    username          = var.postgres_user
    password          = var.postgres_password
    connection_url    = "postgresql://{{username}}:{{password}}@${var.postgres_host}:${var.postgres_port}/${var.postgres_db}?sslmode=disable"
    verify_connection = true
    allowed_roles = [
      "hr-basic-reader",
      "hr-admin-reader"
    ]
  }
}

# ============================================================================
# Database Roles
# ============================================================================

resource "vault_database_secret_backend_role" "hr_basic_reader" {
  backend             = vault_database_secrets_mount.db.path
  name                = "hr-basic-reader"
  db_name             = "employee-db"
  default_ttl         = 3600  # 1 hour
  max_ttl             = 86400 # 24 hours
  
  creation_statements = [
    "CREATE USER \"{{name}}\" WITH PASSWORD '{{password}}' VALID UNTIL '{{expiration}}';",
    "GRANT CONNECT ON DATABASE ${var.postgres_db} TO \"{{name}}\";",
    "GRANT USAGE ON SCHEMA public TO \"{{name}}\";",
    "GRANT SELECT ON employee_basic_info TO \"{{name}}\";"
  ]
}

resource "vault_database_secret_backend_role" "hr_admin_reader" {
  backend             = vault_database_secrets_mount.db.path
  name                = "hr-admin-reader"
  db_name             = "employee-db"
  default_ttl         = 3600  # 1 hour
  max_ttl             = 86400 # 24 hours
  
  creation_statements = [
    "CREATE USER \"{{name}}\" WITH PASSWORD '{{password}}' VALID UNTIL '{{expiration}}';",
    "GRANT CONNECT ON DATABASE ${var.postgres_db} TO \"{{name}}\";",
    "GRANT USAGE ON SCHEMA public TO \"{{name}}\";",
    "GRANT SELECT ON employee_basic_info TO \"{{name}}\";",
    "GRANT SELECT ON employee_salary_info TO \"{{name}}\";"
  ]
}

# ============================================================================
# Identity Groups and External Group Mappings
# ============================================================================
# Maps IBM Verify groups (from groupIds claim) to Vault internal groups
# which then apply policies
# ============================================================================

# Internal group for hr-basic
# Users in this group get only hr-basic policy (limited access)
resource "vault_identity_group" "hr_basic" {
  name     = "hr-basic-group"
  type     = "external"
  policies = [
    vault_policy.hr_basic.name
  ]
  
  metadata = {
    description = "Basic HR staff with access to employee basic info only"
    source      = "IBM Verify groupIds claim"
  }
}

# External group alias for hr-basic
# Maps IBM Verify's "hr-basic" group to Vault's hr-basic-group
resource "vault_identity_group_alias" "hr_basic" {
  name           = "hr-basic"  # Must match groupIds value from IBM Verify
  mount_accessor = vault_jwt_auth_backend.ibm_verify.accessor
  canonical_id   = vault_identity_group.hr_basic.id
}

# Internal group for hr-admin
# Users in this group get only hr-admin policy.
# hr-admin-policy already grants access to both basic and salary data,
# so hr-basic-policy is not needed here.
resource "vault_identity_group" "hr_admin" {
  name     = "hr-admin-group"
  type     = "external"
  policies = [
    vault_policy.hr_admin.name
  ]
  
  metadata = {
    description = "HR administrators with full access to employee data including salary"
    source      = "IBM Verify groupIds claim"
  }
}

# External group alias for hr-admin
# Maps IBM Verify's "hr-admin" group to Vault's hr-admin-group
resource "vault_identity_group_alias" "hr_admin" {
  name           = "hr-admin"  # Must match groupIds value from IBM Verify
  mount_accessor = vault_jwt_auth_backend.ibm_verify.accessor
  canonical_id   = vault_identity_group.hr_admin.id
}