# Vault Terraform Configuration

This directory contains Terraform configuration for setting up HashiCorp Vault for the Agentic Security Lab.

## Overview

The Terraform configuration automates the setup of:

- **JWT Authentication** - Integration with IBM Verify for user authentication
- **Database Secrets Engine** - Dynamic credential generation for PostgreSQL
- **Vault Policies** - Fine-grained access control (hr-basic-policy, hr-admin-policy)
- **External Group Mapping** - Map IBM Verify groups to Vault policies
- **Database Roles** - Two roles with different permission levels
- **Audit Logging** - Complete audit trail of all Vault operations

## Prerequisites

1. **Terraform** - Install Terraform >= 1.0
   ```bash
   # macOS
   brew install terraform
   
   # Linux
   wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
   unzip terraform_1.6.0_linux_amd64.zip
   sudo mv terraform /usr/local/bin/
   ```

2. **Vault Running** - Ensure Vault container is running
   ```bash
   docker-compose up -d vault
   ```

3. **Environment Variables** - Set up your `.env` file in the project root

## Quick Start

### 1. Configure Variables

Copy the example variables file and update with your values:

```bash
cd infrastructure/vault/terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` with your actual configuration:

```hcl
vault_addr  = "http://localhost:8200"
vault_token = "root"

postgres_host     = "postgres"
postgres_port     = 5432
postgres_db       = "employee_db"
postgres_user     = "vault"
postgres_password = "vault-password"

ibm_verify_tenant   = "your-actual-tenant"
ibm_verify_oidc_url = "https://your-actual-tenant.verify.ibm.com/oidc/endpoint/default"
```

### 2. Initialize Terraform

```bash
terraform init
```

This downloads the required Vault provider.

### 3. Review the Plan

```bash
terraform plan
```

This shows what resources will be created without making any changes.

### 4. Apply Configuration

```bash
terraform apply
```

Type `yes` when prompted to confirm.

### 5. Verify Configuration

```bash
# View outputs
terraform output

# Check Vault status
vault status

# List auth methods
vault auth list

# List secrets engines
vault secrets list

# List policies
vault policy list
```

## Configuration Details

### Resources Created

1. **Audit Device** (`vault_audit.file`)
   - Logs all Vault operations to `/vault/logs/audit.log`

2. **JWT Auth Backend** (`vault_jwt_auth_backend.ibm_verify`)
   - Enables JWT authentication
   - Configured to trust IBM Verify OIDC endpoint

3. **JWT Auth Role** (`vault_jwt_auth_backend_role.agent_role`)
   - Role for agent authentication
   - Maps JWT claims to Vault tokens

4. **Policies** (`vault_policy.hr_basic`, `vault_policy.hr_admin`)
   - hr-basic-policy: Access to basic employee info only
   - hr-admin-policy: Access to all employee info including salary

5. **Database Secrets Mount** (`vault_database_secrets_mount.db`)
   - Enables database secrets engine
   - Configures PostgreSQL connection

6. **Database Roles** (`vault_database_secret_backend_role.*`)
   - hr-basic-reader: SELECT on basic tables
   - hr-admin-reader: SELECT on all tables including salary

7. **Identity Groups** (`vault_identity_group.*`)
   - hr-basic-group: External group for basic users
   - hr-admin-group: External group for admin users

8. **Group Aliases** (`vault_identity_group_alias.*`)
   - Maps IBM Verify groups to Vault internal groups

## Using Environment Variables

Instead of `terraform.tfvars`, you can use environment variables:

```bash
export TF_VAR_vault_addr="http://localhost:8200"
export TF_VAR_vault_token="root"
export TF_VAR_postgres_host="postgres"
export TF_VAR_postgres_port="5432"
export TF_VAR_postgres_db="employee_db"
export TF_VAR_postgres_user="vault"
export TF_VAR_postgres_password="vault-password"
export TF_VAR_ibm_verify_tenant="your-tenant"
export TF_VAR_ibm_verify_oidc_url="https://your-tenant.verify.ibm.com/oidc/endpoint/default"

terraform apply
```

## Updating Configuration

To update the configuration:

1. Modify the Terraform files
2. Run `terraform plan` to review changes
3. Run `terraform apply` to apply changes

## Destroying Resources

To remove all Vault configuration:

```bash
terraform destroy
```

**Warning:** This will remove all policies, auth methods, and secrets engines configured by Terraform.

## Troubleshooting

### Vault Connection Issues

```bash
# Check Vault is running
docker ps | grep vault

# Check Vault status
vault status

# Verify VAULT_ADDR
echo $VAULT_ADDR
```

### Authentication Issues

```bash
# Verify token
vault token lookup

# Check auth methods
vault auth list
```

### Database Connection Issues

```bash
# Test database connection
vault read database/config/employee-db

# Check database roles
vault list database/roles
```

### Policy Issues

```bash
# List policies
vault policy list

# Read policy
vault policy read hr-basic-policy
```

## Comparison with Bash Script

### Advantages of Terraform:

1. **Declarative** - Define desired state, not steps
2. **Idempotent** - Safe to run multiple times
3. **State Management** - Tracks what's been created
4. **Plan Before Apply** - Preview changes before making them
5. **Version Control** - Easy to track configuration changes
6. **Modular** - Can be split into modules for reuse
7. **Provider Ecosystem** - Integrates with many services

### Migration from Bash Script:

The Terraform configuration replaces `configure-vault.sh` with equivalent functionality:

| Bash Script | Terraform Resource |
|-------------|-------------------|
| `vault audit enable file` | `vault_audit.file` |
| `vault auth enable jwt` | `vault_jwt_auth_backend.ibm_verify` |
| `vault write auth/jwt/config` | `vault_jwt_auth_backend.ibm_verify` |
| `vault write auth/jwt/role/agent-role` | `vault_jwt_auth_backend_role.agent_role` |
| `vault policy write` | `vault_policy.*` |
| `vault secrets enable database` | `vault_database_secrets_mount.db` |
| `vault write database/config` | `vault_database_secrets_mount.db.postgresql` |
| `vault write database/roles` | `vault_database_secret_backend_role.*` |
| `vault write identity/group` | `vault_identity_group.*` |
| `vault write identity/group-alias` | `vault_identity_group_alias.*` |

## Files

- `main.tf` - Main Terraform configuration
- `variables.tf` - Variable definitions
- `outputs.tf` - Output definitions
- `terraform.tfvars.example` - Example variables file
- `README.md` - This file

## Additional Resources

- [Terraform Vault Provider Documentation](https://registry.terraform.io/providers/hashicorp/vault/latest/docs)
- [HashiCorp Vault Documentation](https://www.vaultproject.io/docs)
- [Terraform Best Practices](https://www.terraform.io/docs/cloud/guides/recommended-practices/index.html)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Terraform and Vault logs
3. Consult the instructor guide
4. Refer to official documentation