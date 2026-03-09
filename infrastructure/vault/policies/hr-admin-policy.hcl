# ============================================================================
# HR Admin Policy - Full Access to All Employee Information
# ============================================================================
# This policy grants access to all employee information including sensitive data.
# Users in the hr-admin group can:
# - Read dynamic database credentials for admin (salary) info access only
# - Query both employee_basic_info and employee_salary_info tables
# - Full administrative access to employee data
#
# Note: hr-admin-reader credentials already include access to employee_basic_info,
# so there is no need to also grant hr-basic-reader access.
# ============================================================================

# Allow reading database credentials for salary info access (includes basic info)
path "database/creds/hr-admin-reader" {
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

# Allow listing database roles details
path "database/roles/*" {
  capabilities = ["read"]
}

# Allow reading metadata about the database connection
path "database/config/employee-db" {
  capabilities = ["read"]
}

# Allow reading static database roles configuration
path "database/static-roles/*" {
  capabilities = ["read"]
}