# ============================================================================
# Terraform Outputs for Vault Configuration
# ============================================================================

output "jwt_auth_path" {
  description = "Path where JWT auth method is mounted"
  value       = vault_jwt_auth_backend.ibm_verify.path
}

output "jwt_accessor" {
  description = "Accessor for JWT auth method"
  value       = vault_jwt_auth_backend.ibm_verify.accessor
}

output "database_mount_path" {
  description = "Path where database secrets engine is mounted"
  value       = vault_database_secrets_mount.db.path
}

output "hr_basic_group_id" {
  description = "ID of hr-basic internal group"
  value       = vault_identity_group.hr_basic.id
}

output "hr_admin_group_id" {
  description = "ID of hr-admin internal group"
  value       = vault_identity_group.hr_admin.id
}

output "group_mappings" {
  description = "External group to internal group mappings"
  value = {
    "hr-basic" = vault_identity_group.hr_basic.name
    "hr-admin" = vault_identity_group.hr_admin.name
  }
}

output "policies_created" {
  description = "List of policies created"
  value = [
    vault_policy.hr_basic.name,
    vault_policy.hr_admin.name
  ]
}

output "database_roles_created" {
  description = "List of database roles created"
  value = [
    vault_database_secret_backend_role.hr_basic_reader.name,
    vault_database_secret_backend_role.hr_admin_reader.name
  ]
}

output "configuration_summary" {
  description = "Summary of Vault configuration"
  value = {
    jwt_auth_enabled         = true
    jwt_groups_claim         = "groupIds"
    jwt_bound_audiences      = ["vault", "a7ffd6ef-50a6-4f08-91d5-c08b37424f2f"]
    database_secrets_enabled = true
    policies                 = [vault_policy.hr_basic.name, vault_policy.hr_admin.name]
    database_roles           = [vault_database_secret_backend_role.hr_basic_reader.name, vault_database_secret_backend_role.hr_admin_reader.name]
    external_group_mappings  = {
      "hr-basic (IBM Verify)" = "hr-basic-group (Vault) → hr-basic-policy"
      "hr-admin (IBM Verify)" = "hr-admin-group (Vault) → hr-admin-policy"
    }
  }
}