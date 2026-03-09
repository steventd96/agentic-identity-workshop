# IBM Verify Setup Guide for Agentic Security Labs

This guide provides step-by-step instructions for setting up IBM Verify as the identity provider for the Agentic Security hands-on labs.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [IBM Verify Tenant Setup](#ibm-verify-tenant-setup)
4. [Application Registration](#application-registration)
5. [User and Group Configuration](#user-and-group-configuration)
6. [OAuth Configuration](#oauth-configuration)
7. [Testing the Setup](#testing-the-setup)
8. [Environment Configuration](#environment-configuration)
9. [Troubleshooting](#troubleshooting)

---

## Overview

IBM Verify serves as the OAuth 2.0 identity provider for this lab, providing:

- **User Authentication**: Secure login for lab participants
- **Group Management**: Role-based access control (hr-basic, hr-admin)
- **JWT Token Issuance**: Tokens for OAuth 2.0 Token Exchange
- **Claims Mapping**: User attributes and group memberships in tokens

### Architecture Flow

```
User Login → IBM Verify → JWT Token → Token Exchange → Vault → Dynamic Credentials
```

---

## Prerequisites

### Required Access

- **IBM Verify Tenant**: Access to an IBM Verify tenant (trial or production)
- **Admin Privileges**: Ability to create applications and manage users
- **Domain Access**: Optional custom domain for production use

### Technical Requirements

- Web browser (Chrome, Firefox, or Safari)
- Basic understanding of OAuth 2.0 and OIDC
- Access to the lab environment

---

## IBM Verify Tenant Setup

### Step 1: Access Your IBM Verify Tenant

1. Navigate to your IBM Verify admin console:
   ```
   https://[your-tenant-name].verify.ibm.com/ui/admin
   ```

2. Log in with your administrator credentials

3. Note your tenant name (e.g., `my-company` from `my-company.verify.ibm.com`)

### Step 2: Verify Tenant Configuration

1. Go to **Settings** → **General**
2. Confirm the following settings:
   - **Tenant Status**: Active
   - **OIDC Endpoint**: Enabled
   - **Token Lifetime**: Default (3600 seconds recommended)

---

## Application Registration

### Step 1: Create a New Application

> **Note**: This lab uses a **single application** approach where one IBM Verify application serves multiple components (AskHR Frontend and Langflow UI). This simplifies configuration management as all components share the same client credentials and can be managed centrally.
>
> **Alternative**: You could create separate applications for each component if you need:
> - Different token lifetimes per component
> - Separate audit trails per application
> - Independent credential rotation schedules
> - Different security policies per component
>
> For this lab, one application is sufficient and easier to manage.

1. Navigate to **Applications** in the left sidebar
2. Click **Add application**
3. Select **Custom Application**
4. Choose **OpenID Connect** as the protocol

### Step 2: Configure Application Settings

#### Basic Information

- **Application Name**: `Agentic Security Lab`
- **Description**: `OAuth provider for agentic security hands-on lab`
- **Application Type**: `Web Application`

#### Authentication Settings

1. **Redirect URIs**: Add the following URIs:
   ```
   http://localhost:3000/callback    # AskHR Frontend (React app)
   http://localhost:7860/callback    # Langflow UI
   ```
   
   > **Note**:
   > - Port 3000: AskHR frontend application (main demo UI)
   > - Port 7860: Langflow agent platform UI (agent configuration)
   > - Jupyter Notebook (port 8888) is used for lab exercises but doesn't require OAuth redirect
   > - Add your production URLs if deploying to a server

2. **Grant Types**: Enable the following:
   - ✅ Authorization Code
   - ✅ Refresh Token
   - ✅ Token Exchange (RFC 8693)
   - ✅ Implicit (required for response type options)

   > **Important**: While Implicit grant is generally deprecated for security reasons, IBM Verify requires it to be enabled to access certain response types (`token` and `id_token`) needed for token exchange and OpenID Connect flows. The lab uses Authorization Code flow for user authentication, not Implicit flow.

3. **Response Types**: Select:
   - ✅ code (for Authorization Code flow)
   - ✅ token (enables token exchange capabilities)
   - ✅ id_token (for OpenID Connect ID tokens)

#### Token Configuration

1. **Access Token Lifetime**: `3600` seconds (1 hour)
2. **Refresh Token Lifetime**: `86400` seconds (24 hours)
3. **ID Token Lifetime**: `3600` seconds (1 hour)

#### Advanced Settings

1. **Token Exchange**: Enable token exchange
   - Subject Token Type: `urn:ietf:params:oauth:token-type:access_token`
   - Requested Token Type: `urn:ietf:params:oauth:token-type:jwt`

2. **Claims Mapping**: Configure the following claims:
   ```json
   {
     "sub": "user.id",
     "email": "user.email",
     "name": "user.displayName",
     "groups": "user.groups",
     "preferred_username": "user.userName"
   }
   ```

### Step 3: Save and Note Credentials

1. Click **Save**
2. Copy and securely store:
   - **Client ID**: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
   - **Client Secret**: `yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy`

> ⚠️ **Security Warning**: Never commit these credentials to version control!

---

## User and Group Configuration

### Step 1: Create User Groups

1. Navigate to **Users & Groups** → **Groups**
2. Create the following groups:

#### HR Basic Group

- **Group Name**: `hr-basic`
- **Description**: `Basic HR employees with read-only access to employee information`
- **Type**: `Security Group`

#### HR Admin Group

- **Group Name**: `hr-admin`
- **Description**: `HR administrators with full access to employee and salary information`
- **Type**: `Security Group`

### Step 2: Create Test Users

Create the following test users for the lab:

#### User 1: HR Employee (Basic Access)

- **Username**: `alice.employee`
- **Email**: `alice.employee@company.com`
- **First Name**: `Alice`
- **Last Name**: `Employee`
- **Password**: Set a secure password
- **Groups**: Add to `hr-basic` group
- **Status**: Active

#### User 2: HR Manager (Admin Access)

- **Username**: `bob.manager`
- **Email**: `bob.manager@company.com`
- **First Name**: `Bob`
- **Last Name**: `Manager`
- **Password**: Set a secure password
- **Groups**: Add to `hr-admin` group
- **Status**: Active

#### User 3: Regular Employee (No Access)

- **Username**: `charlie.user`
- **Email**: `charlie.user@company.com`
- **First Name**: `Charlie`
- **Last Name**: `User`
- **Password**: Set a secure password
- **Groups**: None (for testing unauthorized access)
- **Status**: Active

### Step 3: Assign Groups to Application

1. Go to **Applications** → **Agentic Security Lab**
2. Navigate to the **Entitlements** tab
3. Click **Add entitlement**
4. Add both groups:
   - `hr-basic`
   - `hr-admin`
5. Save changes

---

## OAuth Configuration

### Step 1: Configure OIDC Endpoints

Verify the following endpoints are accessible:

```
Authorization Endpoint:
https://[tenant].verify.ibm.com/oidc/endpoint/default/authorize

Token Endpoint:
https://[tenant].verify.ibm.com/oidc/endpoint/default/token

Token Exchange Endpoint:
https://[tenant].verify.ibm.com/oidc/endpoint/default/token

UserInfo Endpoint:
https://[tenant].verify.ibm.com/oidc/endpoint/default/userinfo

JWKS URI:
https://[tenant].verify.ibm.com/oidc/endpoint/default/jwks
```

### Step 2: Configure Scopes

Ensure the following scopes are enabled for your application:

- `openid` - Required for OIDC
- `profile` - User profile information
- `email` - User email address
- `groups` - User group memberships

### Step 3: Configure Token Exchange

1. Navigate to **Applications** → **Agentic Security Lab** → **Token Exchange**
2. Enable **Token Exchange (RFC 8693)**
3. Configure exchange parameters:

   **Subject Token Type**: `urn:ietf:params:oauth:token-type:access_token`
   - The type of token being exchanged (user's access token)
   
   **Requested Token Type**: `urn:ietf:params:oauth:token-type:jwt`
   - The type of token being requested (JWT for Vault)
   
   **Audience**: `vault`
   - The intended recipient of the exchanged token
   
   **Scope**: `openid profile email groups`
   - Claims to include in the exchanged token
   
   **Actor Token Type** (Optional): `urn:ietf:params:oauth:token-type:access_token`
   - If using actor tokens, this represents the agent's identity token
   - The actor token represents the party (AI agent) acting on behalf of the user
   - Leave empty if not using delegation scenarios

   > **Note on Actor Tokens**: Actor tokens enable delegation scenarios where an AI agent acts on behalf of a user. The exchanged token will contain both the user's identity (subject) and the agent's identity (actor), allowing Vault to enforce policies based on both identities. This lab focuses on subject token exchange; actor tokens are optional for advanced scenarios.

---

## Testing the Setup

### Step 1: Test OIDC Discovery

```bash
curl https://[tenant].verify.ibm.com/oidc/endpoint/default/.well-known/openid-configuration
```

Expected response should include:
- `authorization_endpoint`
- `token_endpoint`
- `userinfo_endpoint`
- `jwks_uri`

### Step 2: Test User Authentication

1. Open a browser and navigate to:
   ```
   https://[tenant].verify.ibm.com/oidc/endpoint/default/authorize?
     client_id=[CLIENT_ID]&
     response_type=code&
     scope=openid%20profile%20email%20groups&
     redirect_uri=http://localhost:3000/callback
   ```

2. Log in with test user credentials (e.g., `alice.employee`)

3. Verify you receive an authorization code in the redirect

### Step 3: Test Token Exchange

Use the following Python script to test token exchange:

```python
import requests
import os

# Configuration
tenant = os.getenv('IBM_VERIFY_TENANT')
client_id = os.getenv('IBM_VERIFY_CLIENT_ID')
client_secret = os.getenv('IBM_VERIFY_CLIENT_SECRET')
token_endpoint = f"https://{tenant}.verify.ibm.com/oidc/endpoint/default/token"

# Exchange authorization code for tokens
def exchange_code(auth_code):
    response = requests.post(
        token_endpoint,
        data={
            'grant_type': 'authorization_code',
            'code': auth_code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': 'http://localhost:3000/callback'
        }
    )
    return response.json()

# Test token exchange
def test_token_exchange(access_token):
    response = requests.post(
        token_endpoint,
        data={
            'grant_type': 'urn:ietf:params:oauth:grant-type:token-exchange',
            'subject_token': access_token,
            'subject_token_type': 'urn:ietf:params:oauth:token-type:access_token',
            'requested_token_type': 'urn:ietf:params:oauth:token-type:jwt',
            'audience': 'vault',
            'client_id': client_id,
            'client_secret': client_secret
        }
    )
    return response.json()

# Run tests
if __name__ == '__main__':
    # Replace with actual authorization code
    auth_code = 'YOUR_AUTH_CODE_HERE'
    
    # Get tokens
    tokens = exchange_code(auth_code)
    print("Access Token:", tokens.get('access_token')[:50] + '...')
    
    # Test token exchange
    exchanged = test_token_exchange(tokens['access_token'])
    print("Exchanged Token:", exchanged.get('access_token')[:50] + '...')
```

### Step 4: Verify JWT Claims

Decode the JWT token at [jwt.io](https://jwt.io) and verify it contains:

```json
{
  "sub": "user-id",
  "email": "alice.employee@company.com",
  "name": "Alice Employee",
  "groups": ["hr-basic"],
  "preferred_username": "alice.employee",
  "iss": "https://[tenant].verify.ibm.com/oidc/endpoint/default",
  "aud": "vault",
  "exp": 1234567890,
  "iat": 1234567890
}
```

---

## Environment Configuration

### Step 1: Update .env File

Copy the template and fill in your IBM Verify credentials:

```bash
cd agentic-security-incubation
cp .env.template .env
```

Edit `.env` with your values:

```bash
# IBM Verify Configuration
IBM_VERIFY_TENANT=your-tenant-name
IBM_VERIFY_OIDC_URL=https://your-tenant-name.verify.ibm.com/oidc/endpoint/default
IBM_VERIFY_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
IBM_VERIFY_CLIENT_SECRET=yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy

# Redirect URI for frontend
IBM_VERIFY_REDIRECT_URI=http://localhost:3000/callback
```

### Step 2: Verify Configuration

Run the configuration test:

```bash
python -c "from security.config import SecurityConfig; config = SecurityConfig.from_env(); print(config)"
```

Expected output:
```
SecurityConfig(ibm_verify_tenant='your-tenant-name', vault_addr='http://localhost:8200', postgres_host='localhost')
```

---

## Troubleshooting

### Issue: "Invalid Client" Error

**Symptoms**: Error when exchanging authorization code for tokens

**Solutions**:
1. Verify `CLIENT_ID` and `CLIENT_SECRET` are correct
2. Check that redirect URI matches exactly (including protocol and port)
3. Ensure application is active in IBM Verify

### Issue: "Groups Not in Token"

**Symptoms**: JWT token doesn't contain `groups` claim

**Solutions**:
1. Verify users are assigned to groups
2. Check groups are entitled to the application
3. Ensure `groups` scope is requested
4. Verify claims mapping includes `groups`

### Issue: "Token Exchange Not Supported"

**Symptoms**: Error when attempting token exchange

**Solutions**:
1. Verify token exchange is enabled in application settings
2. Check grant type includes `urn:ietf:params:oauth:grant-type:token-exchange`
3. Ensure IBM Verify version supports RFC 8693

### Issue: "CORS Errors in Browser"

**Symptoms**: Browser console shows CORS errors

**Solutions**:
1. Add allowed origins in IBM Verify application settings
2. Use backend proxy for token exchange (recommended)
3. Verify redirect URIs are correctly configured

### Issue: "Token Expired"

**Symptoms**: Token validation fails with expiration error

**Solutions**:
1. Check token lifetime settings in IBM Verify
2. Implement token refresh logic
3. Verify system clocks are synchronized

### Issue: "Cannot Access OIDC Endpoints"

**Symptoms**: Network errors when accessing IBM Verify URLs

**Solutions**:
1. Verify tenant name is correct
2. Check network connectivity and firewall rules
3. Ensure IBM Verify tenant is active
4. Try accessing discovery endpoint in browser

---

## Additional Resources

### IBM Verify Documentation

- [IBM Verify Documentation](https://www.ibm.com/docs/en/security-verify)
- [OIDC Configuration Guide](https://www.ibm.com/docs/en/security-verify?topic=applications-openid-connect)
- [Token Exchange Guide](https://www.ibm.com/docs/en/security-verify?topic=tokens-token-exchange)

### OAuth 2.0 Standards

- [RFC 8693: OAuth 2.0 Token Exchange](https://datatracker.ietf.org/doc/html/rfc8693)
- [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0.html)
- [OAuth 2.0 Authorization Framework](https://datatracker.ietf.org/doc/html/rfc6749)

### Lab Resources

- [Main Lab README](../README.md)
- [Vault Configuration Guide](../infrastructure/vault/README.md)
- [Demo App Installation](../demo-app/INSTALLATION.md)

---

## Support

For issues specific to IBM Verify setup:

1. Check the [Troubleshooting](#troubleshooting) section above
2. Review IBM Verify documentation
3. Contact your IBM Verify administrator
4. Reach out to the lab instructor

For lab-specific issues:

1. Check the main [README.md](../README.md)
2. Review the [FAQ](./faq.md)
3. Contact the lab support team

---

**Document Version**: 1.0.0  
**Last Updated**: 2026-02-19  
**Maintained By**: IBM Security Team