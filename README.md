# Agentic Security Hands-On Lab

A comprehensive hands-on lab demonstrating enterprise-grade security patterns for AI agents using OAuth token exchange, policy-based access control, and dynamic secrets management.

## 🎯 Learning Objectives

By completing this lab, you will understand:

1. **OAuth Token Exchange (RFC 8693)** - Securely propagate user identity to AI agents
2. **Policy-Based Access Control** - Enforce fine-grained permissions with HashiCorp Vault
3. **External Group Mapping** - Map identity provider groups to Vault policies
4. **Dynamic Secrets** - Generate short-lived database credentials on-demand
5. **Complete Audit Trails** - Maintain compliance-ready audit logs

## 🏗️ Architecture

```
User → IBM Verify (SSO) → JWT Token → AskHR Frontend
                                            │
                                            ▼
                                    Langflow HR Agent
                                            │
                              ┌─────────────┴─────────────┐
                              ▼                           ▼
                        Vault Tool               Database Tool
                              │                           │
                              ▼                           ▼
                      HashiCorp Vault           PostgreSQL (employee_db)
                    (JWT Auth + Policies)
                    (Dynamic Credentials)
                    (Audit Logging)
```

### Components

- **IBM Verify**: Identity Provider & OAuth Server (SSO + Token Exchange)
- **HashiCorp Vault**: Policy enforcement & dynamic secrets (configured via Terraform)
- **PostgreSQL**: Employee database (2 tables with different access levels)
- **Langflow**: AI agent platform with visual flow builder and custom tools
- **AskHR Frontend**: React + IBM Carbon Design chatbot with embedded Langflow widget
- **AskHR Backend**: Flask API handling IBM Verify SSO authentication
- **Jupyter Notebooks**: Step-by-step interactive lab interface

## 📋 Prerequisites

### Required Software

- **Podman** (v4.0+) or **Docker**
- **Podman Compose** (v1.0+) or **Docker Compose**
- **Python** (v3.9+)
- **Terraform** (v1.0+) — for Vault configuration
- **Git**
- **Web Browser** (Chrome, Firefox, or Safari)

### Required Accounts

- **IBM Verify Tenant Access** (provided by instructor)

### Technical Skills

- Basic Python programming
- Understanding of REST APIs
- Familiarity with Podman/Docker containers
- Basic SQL knowledge
- Understanding of OAuth/JWT concepts (helpful but not required)

## 🚀 Getting Started

Follow the step-by-step Jupyter notebooks to complete this lab. The notebooks provide an interactive learning experience with detailed explanations and executable code cells.

**Start here:** Open `notebooks/01-introduction-and-setup.ipynb` in Jupyter or VS Code

All setup, configuration, testing, and troubleshooting instructions are included in the notebooks.

## 📚 Lab Structure

### Directory Layout

```
agentic-security-incubation/
├── docker-compose.yml              # Infrastructure definition (Podman compatible)
├── .env.template                   # Environment configuration template
├── requirements.txt                # Python dependencies
│
├── notebooks/                      # Step-by-step Jupyter lab notebooks
│   ├── 01-introduction-and-setup.ipynb
│   ├── 02-vault-configuration.ipynb
│   ├── 03-langflow-setup.ipynb
│   ├── 04-demo-app-walkthrough.ipynb
│   └── README.md
│
├── infrastructure/
│   ├── vault/
│   │   ├── policies/               # Vault policy HCL files
│   │   │   ├── hr-basic-policy.hcl
│   │   │   └── hr-admin-policy.hcl
│   │   └── terraform/              # Terraform-based Vault configuration
│   │       ├── main.tf
│   │       ├── variables.tf
│   │       ├── outputs.tf
│   │       ├── terraform.tfvars.example
│   │       └── README.md
│   │
│   └── database/
│       ├── 01-init-schema.sql      # Database schema
│       └── 02-seed-data.sql        # Sample data
│
├── demo-app/                       # AskHR demo application
│   ├── backend/                    # Flask API (IBM Verify SSO)
│   │   ├── app.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── frontend/                   # React + IBM Carbon Design chatbot
│   │   ├── src/
│   │   │   ├── App.tsx
│   │   │   └── components/
│   │   │       └── ChatWidget.tsx  # Embedded Langflow chat widget
│   │   └── Dockerfile
│   ├── tools/                      # Custom Langflow tools
│   │   ├── vault_credentials_tool.py  # JWT → Vault → dynamic credentials
│   │   ├── vault_tool.py
│   │   ├── database_tool.py        # PostgreSQL query tool
│   │   └── token_exchange_tool.py  # OAuth token exchange
│   ├── langflow-flows/
│   │   └── AskHR-Agent.json        # Pre-built Langflow agent flow
│   └── README.md
│
├── agents/
│   ├── base.py                     # Agent framework interface
│   └── adapters/
│       └── langflow_adapter.py
│
└── docs/
    ├── IBM_VERIFY_SETUP.md
    ├── IBM_VERIFY_THREE_CLIENT_SETUP.md
    ├── IBM_VERIFY_ACTOR_TOKEN_SETUP.md
    └── IBM_VERIFY_INSTRUCTOR_GUIDE.md
```

## 🎓 Lab Notebooks

The lab is organized into sequential Jupyter notebooks:

| # | Notebook | Duration | Topics |
|---|----------|----------|--------|
| 1 | `01-introduction-and-setup.ipynb` | 30 min | Core concepts, OAuth token exchange, architecture, environment setup |
| 2 | `02-vault-configuration.ipynb` | 20 min | JWT auth, database secrets engine, policies, external group mapping |
| 3 | `03-langflow-setup.ipynb` | 25 min | Import agent flow, configure custom tools, test security flow |
| 4 | `04-demo-app-walkthrough.ipynb` | 30–40 min | End-to-end demo with AskHR app, access control scenarios, audit logs |

**Total Duration**: ~2 hours (core lab)

> Start with `notebooks/01-introduction-and-setup.ipynb` and proceed in order.

## 🔐 Security Scenarios

### Scenario 1: HR Employee (Basic Access)

**User**: Alice (`hr-employee@company.com`)  
**Groups**: `hr-basic`  
**Access**: Can query `employee_basic_info` table  
**Denied**: Cannot access `employee_salary_info` table

### Scenario 2: HR Manager (Admin Access)

**User**: Bob (`hr-manager@company.com`)  
**Groups**: `hr-admin`  
**Access**: Can query both `employee_basic_info` and `employee_salary_info` tables

### Security Flow (per request)

1. User logs in → IBM Verify returns JWT token
2. User asks question → Frontend sends query + JWT to Langflow via chat widget
3. Langflow agent determines it needs database access
4. **Vault Credentials Tool** receives user JWT, authenticates with Vault
5. Vault validates JWT, checks user's group policy, generates dynamic PostgreSQL credentials
6. **Database Tool** connects to PostgreSQL with dynamic credentials
7. Query executes with permissions scoped to the user's role
8. Agent formats and returns response; credentials expire after TTL

## 📊 Database Schema

### employee_basic_info (Non-Sensitive)

| Column | Type |
|--------|------|
| employee_id | INTEGER |
| first_name, last_name | VARCHAR |
| email | VARCHAR |
| department, job_title | VARCHAR |
| hire_date | DATE |
| office_location, phone_number | VARCHAR |

### employee_salary_info (Sensitive)

| Column | Type |
|--------|------|
| salary_id, employee_id | INTEGER |
| annual_salary | NUMERIC |
| bonus_percentage | NUMERIC |
| stock_options | INTEGER |
| salary_grade | VARCHAR |
| performance_rating | NUMERIC |

## 🔧 Configuration

### IBM Verify — Three Client Setup

This lab uses three IBM Verify OAuth clients:

| Client | Grant Type | Purpose |
|--------|-----------|---------|
| **Frontend Client** | Authorization Code | User SSO login, returns user JWT |
| **Agent Client** | Client Credentials | Bot identity (actor token) |
| **Tool/Exchange Client** | Token Exchange | Delegated token with `act` claim for Vault |

> See [docs/IBM_VERIFY_THREE_CLIENT_SETUP.md](docs/IBM_VERIFY_THREE_CLIENT_SETUP.md) for full setup instructions.

### Vault Policies

**hr-basic-policy**: Access to basic employee information only
```hcl
path "database/creds/hr-basic-reader" {
  capabilities = ["read"]
}
```

**hr-admin-policy**: Access to all employee information
```hcl
path "database/creds/hr-basic-reader" {
  capabilities = ["read"]
}
path "database/creds/hr-admin-reader" {
  capabilities = ["read"]
}
```

### External Group Mapping

```
IBM Verify Group → Vault External Group → Vault Policy
hr-basic         → hr-basic-group       → hr-basic-policy
hr-admin         → hr-admin-group       → hr-admin-policy
```

### Vault Configuration (Terraform)

Vault is configured using Terraform (`infrastructure/vault/terraform/`):

```bash
cd infrastructure/vault/terraform
cp terraform.tfvars.example terraform.tfvars
terraform init && terraform apply
```

Resources created:
- JWT Auth Backend (IBM Verify OIDC)
- Database Secrets Engine (PostgreSQL)
- `hr-basic-policy` and `hr-admin-policy`
- `hr-basic-reader` and `hr-admin-reader` database roles
- External identity groups with IBM Verify group aliases
- Audit logging to `/vault/logs/audit.log`


## 📖 Additional Resources

### Documentation

- **[IBM Verify Setup Guide](docs/IBM_VERIFY_SETUP.md)** - Complete guide for configuring IBM Verify
- **[Three Client Setup](docs/IBM_VERIFY_THREE_CLIENT_SETUP.md)** - Frontend, Agent, and Tool client configuration
- **[Actor Token Setup](docs/IBM_VERIFY_ACTOR_TOKEN_SETUP.md)** - Configuring `act` claim for token exchange
- **[Instructor Guide](docs/IBM_VERIFY_INSTRUCTOR_GUIDE.md)** - Lab facilitation guide
- **[Vault Terraform README](infrastructure/vault/terraform/README.md)** - Terraform configuration details
- **[Demo App README](demo-app/README.md)** - AskHR application details
- **[Langflow Chat Integration](demo-app/LANGFLOW_CHAT_INTEGRATION.md)** - Chat widget integration guide

### External Resources

- [OAuth 2.0 Token Exchange (RFC 8693)](https://datatracker.ietf.org/doc/html/rfc8693)
- [HashiCorp Vault Documentation](https://developer.hashicorp.com/vault/docs)
- [Terraform Vault Provider](https://registry.terraform.io/providers/hashicorp/vault/latest/docs)
- [IBM Verify Documentation](https://www.ibm.com/docs/en/security-verify)
- [Langflow Documentation](https://docs.langflow.org/)
- [IBM Carbon Design System](https://carbondesignsystem.com/)
- [HashiCorp Validated Pattern: AI Agent Identity](https://developer.hashicorp.com/validated-patterns/vault/ai-agent-identity-with-hashicorp-vault)

## 🤝 Support

For questions or issues:

1. Check the [Troubleshooting](#-troubleshooting) section above
2. Review the [Instructor Guide](docs/IBM_VERIFY_INSTRUCTOR_GUIDE.md)
3. Contact your lab instructor
4. Create an issue in the repository

## 📝 License

This lab is provided for educational purposes.

## 🙏 Acknowledgments

- HashiCorp for Vault and Terraform
- IBM for IBM Verify and Carbon Design System
- Langflow team for the agent platform
- The open-source community

## 👥 Contributors

- @eddy.kim
- @rachel.chua

---

**Version**: 2.0.0
**Last Updated**: 2026-03-02
**Maintainer**: steven.dirjayanto