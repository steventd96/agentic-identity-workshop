# AskHR Demo App - Quick Start Guide

Complete guide to get the SSO login and token exchange working with your Podman setup.

## Prerequisites

- Podman and podman-compose installed
- IBM Verify tenant configured (see [IBM_VERIFY_SETUP.md](../docs/IBM_VERIFY_SETUP.md))
- Environment variables configured

## Step 1: Configure Environment Variables

Create or update your `.env` file in the `agentic-security-incubation` directory:

```bash
# IBM Verify Configuration
IBM_VERIFY_TENANT=your-tenant-name
IBM_VERIFY_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
IBM_VERIFY_CLIENT_SECRET=yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy
IBM_VERIFY_OIDC_URL=https://your-tenant-name.verify.ibm.com/oidc/endpoint/default
IBM_VERIFY_REDIRECT_URI=http://localhost:3000/callback

# Flask Backend Secret Key (generate with: python -c "import secrets; print(secrets.token_hex(32))")
FLASK_SECRET_KEY=your-generated-secret-key-here

# Langflow Database Configuration
LANGFLOW_POSTGRES_DB=langflow
LANGFLOW_POSTGRES_USER=langflow
LANGFLOW_POSTGRES_PASSWORD=langflow
LANGFLOW_SUPERUSER=admin
LANGFLOW_SUPERUSER_PASSWORD=admin
```

## Step 2: Start All Services

```bash
cd agentic-security-incubation

# Build and start all services
podman-compose up -d --build

# Check status
podman-compose ps
```

You should see these services running:
- ✅ `agentic-vault` (port 8200)
- ✅ `agentic-postgres` (port 5432)
- ✅ `langflow-postgres` (port 5433)
- ✅ `agentic-langflow` (port 7860)
- ✅ `agentic-askhr-backend` (port 5001) - **NEW!**
- ✅ `agentic-askhr-frontend` (port 3000)

## Step 3: Verify Services

### Check Backend API
```bash
curl http://localhost:5001/health
# Should return: {"status":"healthy","service":"askhr-backend","version":"1.0.0"}
```

### Check Frontend
```bash
curl http://localhost:3000
# Should return HTML content
```

### Check Langflow
```bash
curl http://localhost:7860/health
# Should return health status
```

## Step 4: Use the SSO Login

### 4.1 Open the Demo App

1. Open your browser to `http://localhost:3000`
2. You should see the AskHR welcome page with a **"🔐 Login with SSO"** button

### 4.2 Login with IBM Verify

1. Click the **"Login with SSO"** button
2. You'll be redirected to IBM Verify
3. Enter your credentials (e.g., `alice.employee` or `bob.manager`)
4. After successful authentication, you'll be redirected back to the app

### 4.3 Copy Your JWT Token

1. After login, you'll see your user information
2. Your JWT token is displayed in the "Your JWT Token" section
3. Click the **"📋 Copy Token"** button to copy it to clipboard

## Step 5: Use Token in Langflow

### 5.1 Open Langflow

1. Open `http://localhost:7860` in your browser
2. Login with credentials (default: admin/admin)

### 5.2 Create or Open a Flow

1. Create a new flow or open an existing one
2. You should see the custom tools in the sidebar:
   - **Token Exchange Tool** (NEW!)
   - **Vault Tool** (UPDATED!)
   - **Database Tool**

### 5.3 Build the Complete Flow

```
┌──────────────────────┐
│ Token Exchange Tool  │
│                      │
│ Input:               │
│ - User JWT Token     │ ← Paste token from demo app
│ - Token Endpoint     │
│ - Client ID          │
│ - Client Secret      │
│                      │
│ Output:              │
│ - agent_token        │
└──────────┬───────────┘
           │
           │ Connect output to input
           ↓
┌──────────────────────┐
│ Vault Tool           │
│                      │
│ Input:               │
│ - agent_token_data   │ ← Connected from Token Exchange
│ - database_role      │
│                      │
│ Output:              │
│ - credentials        │
└──────────┬───────────┘
           │
           │ Connect output to input
           ↓
┌──────────────────────┐
│ Database Tool        │
│                      │
│ Input:               │
│ - vault_credentials  │ ← Connected from Vault
│ - query_type         │
│                      │
│ Output:              │
│ - results            │
└──────────────────────┘
```

### 5.4 Configure Token Exchange Tool

- **User JWT Token**: Paste the token you copied from the demo app
- **Token Endpoint**: `https://your-tenant.verify.ibm.com/oidc/endpoint/default/token`
- **Client ID**: Your IBM Verify client ID
- **Client Secret**: Your IBM Verify client secret
- **Audience**: `vault`
- **Scope**: `openid profile email groups`

### 5.5 Configure Vault Tool

- **Agent Token Data**: Connect from Token Exchange Tool output (automatic)
- **Database Role**: `hr-basic-reader` or `hr-admin-reader`
- **Vault Address**: `http://vault:8200`
- **JWT Auth Path**: `auth/jwt/login`
- **JWT Role**: `hr-agent`

### 5.6 Configure Database Tool

- **Vault Credentials**: Connect from Vault Tool output (automatic)
- **Query Type**: `basic_info` or `salary_info`
- **Employee ID**: (optional) specific employee ID or leave empty for all

### 5.7 Run the Flow

1. Click the "Run" button
2. Watch the flow execute:
   - Token Exchange Tool exchanges user token for agent token
   - Vault Tool uses agent token to get dynamic DB credentials
   - Database Tool queries the database with those credentials

## Troubleshooting

### Issue: Backend not starting

**Check logs:**
```bash
podman logs agentic-askhr-backend
```

**Common causes:**
- Missing environment variables
- Invalid IBM Verify credentials
- Port 5000 already in use

### Issue: Frontend can't connect to backend

**Check:**
1. Backend is running: `curl http://localhost:5001/health`
2. CORS is configured correctly (already set in backend)
3. Browser console for errors

### Issue: Token Exchange Tool not appearing in Langflow

**Solution:**
```bash
# Restart Langflow to load new tools
podman-compose restart langflow

# Check if tools are mounted
podman exec -it agentic-langflow ls -la /app/custom_components/custom_tools/
```

### Issue: "Login with SSO" button not working

**Check:**
1. Backend is running and healthy
2. Environment variables are set correctly
3. IBM Verify redirect URI matches: `http://localhost:3000/callback`
4. Browser console for errors

### Issue: Vault Tool can't connect to Token Exchange output

**Solution:**
1. Make sure you're connecting the **output** of Token Exchange Tool
2. Connect to the **agent_token_data** input of Vault Tool
3. The connection should show a line between the components

## Viewing Logs

```bash
# All services
podman-compose logs -f

# Specific service
podman-compose logs -f askhr-backend
podman-compose logs -f askhr-frontend
podman-compose logs -f langflow
```

## Stopping Services

```bash
# Stop all services
podman-compose down

# Stop and remove volumes (clean slate)
podman-compose down -v
```

## Rebuilding After Changes

```bash
# Rebuild specific service
podman-compose up -d --build askhr-backend

# Rebuild all services
podman-compose up -d --build
```

## Testing the Complete Flow

### Test User: Alice (HR Basic)

1. Login as `alice.employee` (hr-basic group)
2. Copy JWT token
3. Use Token Exchange Tool in Langflow
4. Connect to Vault Tool with `hr-basic-reader` role
5. Should get credentials with access to `employee_basic_info` table only

### Test User: Bob (HR Admin)

1. Login as `bob.manager` (hr-admin group)
2. Copy JWT token
3. Use Token Exchange Tool in Langflow
4. Connect to Vault Tool with `hr-admin-reader` role
5. Should get credentials with access to both tables

### Test User: Charlie (No Access)

1. Login as `charlie.user` (no groups)
2. Copy JWT token
3. Use Token Exchange Tool in Langflow
4. Vault authentication should fail (no matching policy)

## Architecture Overview

```
┌─────────────────┐
│   User Browser  │
└────────┬────────┘
         │
         ↓
┌─────────────────┐      ┌──────────────┐
│  Frontend:3000  │─────→│ Backend:5001 │
└─────────────────┘      └──────┬───────┘
                                │
                                ↓
                         ┌──────────────┐
                         │ IBM Verify   │
                         │ (OAuth)      │
                         └──────────────┘
                                │
                                ↓ User JWT Token
                         ┌──────────────┐
                         │ Langflow     │
                         │ :7860        │
                         └──────┬───────┘
                                │
                    ┌───────────┴───────────┐
                    ↓                       ↓
            ┌───────────────┐      ┌──────────────┐
            │ Vault:8200    │      │ Postgres     │
            │ (Credentials) │      │ :5432        │
            └───────────────┘      └──────────────┘
```

## Next Steps

1. ✅ Services running
2. ✅ Login with SSO working
3. ✅ Token copied from demo app
4. ✅ Token Exchange Tool in Langflow
5. ✅ Vault Tool connected
6. ✅ Database Tool querying data

## Additional Resources

- [SSO Setup Guide](./SSO_SETUP.md) - Detailed SSO configuration
- [Langflow Tool Setup](./LANGFLOW_TOOL_SETUP.md) - Tool loading instructions
- [IBM Verify Setup](../docs/IBM_VERIFY_SETUP.md) - IBM Verify configuration

## Support

For issues:
1. Check logs: `podman-compose logs -f`
2. Verify environment variables
3. Check service health endpoints
4. Review troubleshooting section above

---

**Version**: 1.0.0  
**Last Updated**: 2026-02-21  
**Maintained By**: IBM Security Team

<!-- Made with Bob -->