# IBM Verify Instructor Quick Reference Guide

This guide provides instructors with a quick checklist and reference for preparing IBM Verify for the Agentic Security hands-on labs.

## Pre-Lab Preparation Checklist

### 1. Tenant Setup (30 minutes before lab)

- [ ] Access IBM Verify admin console
- [ ] Verify tenant is active and accessible
- [ ] Confirm OIDC endpoints are enabled
- [ ] Test tenant connectivity

### 2. Application Configuration (15 minutes)

- [ ] Create "Agentic Security Lab" application
- [ ] Configure OAuth settings (see below)
- [ ] Enable token exchange (RFC 8693)
- [ ] Save client credentials securely
- [ ] Test OIDC discovery endpoint

### 3. User and Group Setup (20 minutes)

- [ ] Create `hr-basic` group
- [ ] Create `hr-admin` group
- [ ] Create test users (Alice, Bob, Charlie)
- [ ] Assign users to appropriate groups
- [ ] Entitle groups to application
- [ ] Test user login

### 4. Credentials Distribution (10 minutes)

- [ ] Prepare `.env` files for participants
- [ ] Share client credentials securely (encrypted email/vault)
- [ ] Provide test user credentials
- [ ] Share tenant information

---

## Quick Configuration Reference

### Application Settings

> **Recommended**: Create **ONE application** for simplified management. All components share the same client credentials.
>
> **Alternative**: Create separate applications if you need independent credential rotation, different token lifetimes, or separate audit trails per component.

```yaml
Application Name: Agentic Security Lab
Type: Web Application
Protocol: OpenID Connect

Redirect URIs:
  - http://localhost:3000/callback    # AskHR Frontend (main demo UI)
  - http://localhost:7860/callback    # Langflow UI (agent configuration)
  # Note: Jupyter Notebook (8888) doesn't need OAuth redirect

Grant Types:
  - Authorization Code
  - Refresh Token
  - Token Exchange (RFC 8693)
  - Implicit (required to enable token/id_token response types)

Response Types:
  - code (Authorization Code flow)
  - token (enables token exchange)
  - id_token (OpenID Connect)

Note: Implicit grant must be enabled in IBM Verify to access
token and id_token response types, even though the lab uses
Authorization Code flow for actual authentication.

Scopes:
  - openid
  - profile
  - email
  - groups

Token Lifetimes:
  Access Token: 3600s (1 hour)
  Refresh Token: 86400s (24 hours)
  ID Token: 3600s (1 hour)
```

### Groups Configuration

```yaml
Groups:
  - Name: hr-basic
    Description: Basic HR employees
    Members: alice.employee
    
  - Name: hr-admin
    Description: HR administrators
    Members: bob.manager
```

### Test Users

```yaml
Users:
  - Username: alice.employee
    Email: alice.employee@company.com
    Name: Alice Employee
    Groups: [hr-basic]
    Purpose: Test basic access (employee info only)
    
  - Username: bob.manager
    Email: bob.manager@company.com
    Name: Bob Manager
    Groups: [hr-admin]
    Purpose: Test admin access (all info)
    
  - Username: charlie.user
    Email: charlie.user@company.com
    Name: Charlie User
    Groups: []
    Purpose: Test unauthorized access
```

### Claims Mapping

```json
{
  "sub": "user.id",
  "email": "user.email",
  "name": "user.displayName",
  "groups": "user.groups",
  "preferred_username": "user.userName"
}
```

---

## Environment Template for Participants

Provide this template to participants:

```bash
# IBM Verify Configuration
IBM_VERIFY_TENANT=your-tenant-name
IBM_VERIFY_OIDC_URL=https://your-tenant-name.verify.ibm.com/oidc/endpoint/default
IBM_VERIFY_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
IBM_VERIFY_CLIENT_SECRET=yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy
IBM_VERIFY_REDIRECT_URI=http://localhost:3000/callback
```

---

## Pre-Lab Testing Script

Run this script to verify everything is working:

```bash
#!/bin/bash

# Configuration
TENANT="your-tenant-name"
CLIENT_ID="your-client-id"
CLIENT_SECRET="your-client-secret"

# Test 1: OIDC Discovery
echo "Testing OIDC Discovery..."
curl -s "https://${TENANT}.verify.ibm.com/oidc/endpoint/default/.well-known/openid-configuration" | jq .

# Test 2: JWKS Endpoint
echo "Testing JWKS Endpoint..."
curl -s "https://${TENANT}.verify.ibm.com/oidc/endpoint/default/jwks" | jq .

# Test 3: Client Credentials
echo "Testing Client Credentials..."
curl -s -X POST "https://${TENANT}.verify.ibm.com/oidc/endpoint/default/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials" \
  -d "client_id=${CLIENT_ID}" \
  -d "client_secret=${CLIENT_SECRET}" \
  -d "scope=openid" | jq .

echo "Pre-lab testing complete!"
```

---

## Common Issues and Quick Fixes

### Issue: Participants can't log in

**Quick Fix:**
1. Verify user status is "Active"
2. Check user has correct group membership
3. Confirm groups are entitled to application
4. Reset user password if needed

### Issue: Groups not in JWT token

**Quick Fix:**
1. Verify `groups` scope is requested
2. Check claims mapping includes `groups`
3. Ensure users are assigned to groups
4. Confirm groups are entitled to application

### Issue: Token exchange fails

**Quick Fix:**
1. Verify token exchange is enabled in app settings
2. Check grant type includes RFC 8693
3. Confirm IBM Verify version supports token exchange
4. Test with curl command (see testing section)

### Issue: Invalid redirect URI

**Quick Fix:**
1. Verify redirect URI matches exactly (protocol, host, port, path)
2. Check for trailing slashes
3. Ensure URI is added to application configuration
4. Test with exact URI from error message

---

## During Lab Support

### Monitoring Checklist

- [ ] Monitor IBM Verify admin console for errors
- [ ] Check application logs for authentication failures
- [ ] Watch for rate limiting issues
- [ ] Monitor token exchange requests

### Quick Diagnostics

```bash
# Check if user can authenticate
# Have participant try: https://[tenant].verify.ibm.com/oidc/endpoint/default/authorize?client_id=[CLIENT_ID]&response_type=code&scope=openid&redirect_uri=http://localhost:3000/callback

# Verify JWT token structure
# Use jwt.io to decode and inspect claims

# Test token exchange manually
curl -X POST "https://[tenant].verify.ibm.com/oidc/endpoint/default/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=urn:ietf:params:oauth:grant-type:token-exchange" \
  -d "subject_token=[ACCESS_TOKEN]" \
  -d "subject_token_type=urn:ietf:params:oauth:token-type:access_token" \
  -d "requested_token_type=urn:ietf:params:oauth:token-type:jwt" \
  -d "audience=vault" \
  -d "client_id=[CLIENT_ID]" \
  -d "client_secret=[CLIENT_SECRET]"
```

---

## Post-Lab Cleanup

### Optional Cleanup Steps

- [ ] Disable test users (or delete if not needed)
- [ ] Rotate client credentials
- [ ] Review audit logs
- [ ] Archive application configuration
- [ ] Document any issues encountered

### Audit Log Review

Check for:
- Successful authentications
- Failed login attempts
- Token exchange requests
- Group membership queries

---

## Troubleshooting Decision Tree

```
Participant reports authentication issue
│
├─ Can't access IBM Verify login page?
│  ├─ Check tenant URL
│  ├─ Verify network connectivity
│  └─ Confirm tenant is active
│
├─ Login fails?
│  ├─ Verify username/password
│  ├─ Check user status (Active)
│  └─ Reset password if needed
│
├─ Redirect fails?
│  ├─ Check redirect URI configuration
│  ├─ Verify exact match (protocol, host, port)
│  └─ Look for CORS errors in browser console
│
├─ Token exchange fails?
│  ├─ Verify token exchange is enabled
│  ├─ Check grant type configuration
│  ├─ Confirm access token is valid
│  └─ Test with curl command
│
└─ Groups not in token?
   ├─ Verify user group membership
   ├─ Check groups are entitled to app
   ├─ Confirm claims mapping
   └─ Ensure 'groups' scope is requested
```

---

## Contact Information

### IBM Verify Support

- **Documentation**: https://www.ibm.com/docs/en/security-verify
- **Support Portal**: [Your support portal URL]
- **Emergency Contact**: [Your emergency contact]

### Lab Support

- **Instructor**: [Your name and contact]
- **Backup Instructor**: [Backup contact]
- **Technical Support**: [Tech support contact]

---

## Additional Resources

### For Instructors

- [IBM Verify Admin Guide](https://www.ibm.com/docs/en/security-verify)
- [OAuth 2.0 Token Exchange (RFC 8693)](https://datatracker.ietf.org/doc/html/rfc8693)
- [OpenID Connect Specification](https://openid.net/specs/openid-connect-core-1_0.html)

### For Participants

- [IBM Verify Setup Guide](./IBM_VERIFY_SETUP.md)
- [Main Lab README](../README.md)
- [Troubleshooting Guide](./troubleshooting.md)

---

**Document Version**: 1.0.0  
**Last Updated**: 2026-02-19  
**Maintained By**: IBM Security Team

---

## Quick Command Reference

```bash
# Test OIDC Discovery
curl https://[tenant].verify.ibm.com/oidc/endpoint/default/.well-known/openid-configuration

# Test JWKS
curl https://[tenant].verify.ibm.com/oidc/endpoint/default/jwks

# Decode JWT (using jwt-cli)
jwt decode [TOKEN]

# Test with Python
python -c "from security.config import SecurityConfig; print(SecurityConfig.from_env())"

# Check Vault integration
export VAULT_ADDR=http://localhost:8200
export VAULT_TOKEN=root
vault read auth/jwt/config