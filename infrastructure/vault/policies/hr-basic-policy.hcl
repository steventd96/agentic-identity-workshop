# ============================================================================
# HR Basic Policy - Access to Non-Sensitive Employee Information
# ============================================================================
# This policy grants access to basic employee information only.
# Users in the hr-basic group can:
# - Read dynamic database credentials for basic info access
# - Query employee_basic_info table
# - Cannot access employee_salary_info table
#
# Note: Access to hr-admin-reader is simply not granted here.
# No explicit deny is needed — absence of permission is sufficient.
# ============================================================================

# Allow reading database credentials for basic info access
path "database/creds/hr-basic-reader" {
  capabilities = ["read"]
}

# Allow reading own token information
path "auth/token/lookup-self" {
  capabilities = ["read"]
}

# Allow renewing own token
path "auth/token/renew-self" {
  capabilities = ["update"]
}

# Allow revoking own token
path "auth/token/revoke-self" {
  capabilities = ["update"]
}

# Allow listing database roles (for discovery)
path "database/roles" {
  capabilities = ["list"]
}

# Allow reading metadata about the database connection
path "database/config/employee-db" {
  capabilities = ["read"]
}