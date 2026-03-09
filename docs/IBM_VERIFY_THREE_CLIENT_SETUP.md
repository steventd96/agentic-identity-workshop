# IBM Verify Three-Client Architecture Setup

## Overview

This guide describes the **recommended 3-client architecture** for implementing RFC 8693 Token Exchange with proper delegation semantics using IBM Verify.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     IBM Verify (IdP)                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │  Frontend Client │  │   Agent Client   │  │ Exchange     │  │
│  │  (User SSO)      │  │  (Bot Identity)  │  │ Client       │  │
│  ├──────────────────┤  ├──────────────────┤  ├──────────────┤  │
│  │ Grant Type:      │  │ Grant Type:      │  │ Grant Type:  │  │
│  │ - Auth Code      │  │ - Client Creds   │  │ - Token Exch │  │
│  │                  │  │                  │  │              │  │
│  │ Returns:         │  │ Returns:         │  │ Returns:     │  │
│  │ - Access Token   │  │ - Access Token   │  │ - Access Tkn │  │
│  │   (JWT format)   │  │   (JWT format)   │  │   (JWT)      │  │
│  │   → Subject      │  │   → Actor        │  │   → Vault    │  │
│  └──────────────────┘  └──────────────────┘  └──────────────┘  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
    User Token              Agent Token          Delegated Token
    (Subject)               (Actor)              (with 'act' claim)
```

## Why Three Clients?

### Previous 2-Client Approach (Problems):
- ❌ Frontend Client provided both subject and actor tokens
- ❌ Actor token was just another user token (no clear agent identity)
- ❌ Difficult to distinguish between user and agent actions
- ❌ No clear separation of concerns

### New 3-Client Approach (Benefits):
- ✅ **Frontend Client**: User authentication (subject token)
- ✅ **Agent Client**: Bot/agent identity (actor token via client credentials)
- ✅ **Exchange Client**: Token exchange service (produces delegated token)
- ✅ Clear separation: User identity vs Agent identity vs Exchange service
- ✅ Proper RFC 8693 delegation semantics with `act` claim
- ✅ Agent has its own identity (not impersonating user)

## Client Configuration

### Client 1: Frontend Client (User SSO)

**Purpose**: Authenticate end users via SSO

**Configuration**:
```yaml
Name: HR Frontend App
Client ID: 72ba65a6-f5d0-45f3-b19c-21fbdfe7646a
Grant Types:
  - Authorization Code
  - Refresh Token
Response Types:
  - code
  - token ✅ (Required for access token in authorization response)
Redirect URIs:
  - http://localhost:3000/callback
  - http://localhost:3000
Token Settings:
  - Access token format: JWT ✅
Scopes:
  - openid
  - profile
  - email
  - groups
```

**Critical: Introspect Endpoint Configuration**

This configuration is **REQUIRED** to authorize the agent to act on behalf of users.

1. **Navigate to**: Frontend Client → Sign-on → Endpoint configuration → Introspect

2. **Add Attribute Mapping for `may_act`**:
   - **Attribute name**: `may_act`
   - **Source**: Custom rule
   - **Rule format**: JSON
   - **Rule**:
     ```json
     {
       "client_id": "caf77fa3-5873-403e-900e-d8b0c2a8e540"
     }
     ```
   - **Purpose**: Authorizes the agent client (with this client_id) to act on behalf of users
   - **Note**: Replace `caf77fa3-5873-403e-900e-d8b0c2a8e540` with your actual Agent Client ID

3. **Add Attribute Mapping for `groupIds`**:
   - **Attribute name**: `groupIds`
   - **Source**: Attribute mapping
   - **Mapping**: `groupIds` → `groupIds`
   - **Purpose**: Include user groups in the access token

**Why `may_act` is Critical**:

Without this configuration, you'll get the error:
```
"The actor or client is not authorized to act on behalf of the subject"
```

The `may_act` claim in the subject token explicitly authorizes which clients can act on behalf of the user. This is IBM Verify's security mechanism for delegation.

**Returns**:
- **Access Token** (JWT format) - Used as **Subject Token** in exchange
- ID Token - For user info display
- Refresh Token - For token renewal

**Access Token Claims** (with `may_act`):
```json
{
  "aud": ["72ba65a6-f5d0-45f3-b19c-21fbdfe7646a"],
  "sub": "643006RHZC",
  "email": "user@example.com",
  "groupIds": ["hr-admin", "admin"],
  "may_act": {
    "client_id": "caf77fa3-5873-403e-900e-d8b0c2a8e540"
  },
  "grant_type": "authorization_code",
  "scope": "openid profile email groups",
  "iat": 1771988834,
  "exp": 1771992434
}
```

---

### Client 2: Agent Client (Bot Identity)

**Purpose**: Provide agent/bot identity for delegation

**Configuration**:
```yaml
Name: HR Agent Bot
Client ID: a7ffd6ef-50a6-4f08-91d5-c08b37424f2f
Client Secret: <secure-secret>
Grant Types:
  - Client Credentials ✅
Token Settings:
  - Access token format: JWT ✅
Scopes:
  - agent.act (custom scope for acting on behalf)
```

**Usage**:
```bash
# Get agent token via client credentials
curl -X POST https://automation.verify.ibm.com/oidc/endpoint/default/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials" \
  -d "client_id=a7ffd6ef-50a6-4f08-91d5-c08b37424f2f" \
  -d "client_secret=<secret>" \
  -d "scope=agent.act"
```

**Returns**:
- **Access Token** (JWT format) - Used as **Actor Token** in exchange

**Access Token Claims**:
```json
{
  "aud": ["a7ffd6ef-50a6-4f08-91d5-c08b37424f2f"],
  "sub": "a7ffd6ef-50a6-4f08-91d5-c08b37424f2f",
  "client_id": "a7ffd6ef-50a6-4f08-91d5-c08b37424f2f",
  "grant_type": "client_credentials",
  "scope": "agent.act",
  "iat": 1771988834,
  "exp": 1771992434
}
```

---

### Client 3: Exchange Client (Token Exchange Service)

**Purpose**: Perform RFC 8693 token exchange with delegation

**Configuration**:
```yaml
Name: Token Exchange Service
Client ID: <exchange-client-id>
Client Secret: <secure-secret>
Grant Types:
  - Token Exchange (urn:ietf:params:oauth:grant-type:token-exchange) ✅
Token Settings:
  - Access token format: JWT ✅
```

**Critical: Introspect Endpoint Configuration**

1. **Navigate to**: Exchange Client → Sign-on → Endpoint configuration → Introspect

2. **Add Attribute Mapping for `act`** (RFC 8693 delegation):
   - **Attribute name**: `act`
   - **Source**: Custom rule
   - **Rule**: `requestContext.actor_token`
   - **Purpose**: Includes the actor token information in the `act` claim of the exchanged token

3. **Add Attribute Mapping for `groupIds`** (preserve user groups):
   - **Attribute name**: `groupIds`
   - **Source**: Attribute mapping
   - **Mapping**: `groupIds` → `groupIds`
   - **Purpose**: Preserve user groups from subject token in the exchanged token

**Usage**:
```bash
# Exchange tokens with delegation
curl -X POST https://automation.verify.ibm.com/oidc/endpoint/default/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=urn:ietf:params:oauth:grant-type:token-exchange" \
  -d "subject_token=<user-access-token>" \
  -d "subject_token_type=urn:ietf:params:oauth:token-type:access_token" \
  -d "actor_token=<agent-access-token>" \
  -d "actor_token_type=urn:ietf:params:oauth:token-type:access_token" \
  -d "requested_token_type=urn:ietf:params:oauth:token-type:access_token" \
  -d "client_id=<exchange-client-id>" \
  -d "client_secret=<exchange-secret>" \
  -d "audience=vault" \
  -d "scope=openid profile email groups"
```

**Returns**:
- **Access Token** (JWT format) - Used for **Vault JWT Auth**

**Access Token Claims** (with delegation):
```json
{
  "aud": ["vault"],
  "sub": "643006RHZC",
  "email": "user@example.com",
  "groupIds": ["hr-admin", "admin"],
  "act": {
    "sub": "a7ffd6ef-50a6-4f08-91d5-c08b37424f2f",
    "client_id": "a7ffd6ef-50a6-4f08-91d5-c08b37424f2f"
  },
  "scope": "openid profile email groups",
  "iat": 1771988834,
  "exp": 1771992434
}
```

## Token Flow

```
1. User Login (Frontend Client)
   ↓
   User Access Token (Subject)
   
2. Agent Authentication (Agent Client)
   ↓
   Agent Access Token (Actor)
   
3. Token Exchange (Exchange Client)
   Subject Token + Actor Token
   ↓
   Delegated Token (with 'act' claim)
   
4. Vault Authentication
   Delegated Token
   ↓
   Vault Access (with user context + agent attribution)
```

## Critical Configuration Requirements

### ✅ All Three Clients MUST Have:

1. **Access Token Format = JWT**
   - Location: Sign-on → Token settings → Access token format
   - Value: `JWT` (not `Default` or `Opaque`)

2. **Proper Grant Types**
   - Frontend: Authorization Code
   - Agent: Client Credentials
   - Exchange: Token Exchange

### ✅ Exchange Client MUST Have:

1. **Introspect Endpoint Configuration**
   - Navigate to: Sign-on → Endpoint configuration → Introspect
   - Add attribute mapping:
     - Attribute: `act`
     - Source: Custom rule
     - Rule: `requestContext.actor_token`

2. **Token Exchange Grant Enabled**
   - Navigate to: Sign-on → Grant types
   - Enable: `Token exchange`

## Implementation in Token Exchange Tool

The tool should:

1. **Accept user access token** (from frontend) as subject
2. **Obtain agent token** via client credentials (Agent Client)
3. **Perform token exchange** using Exchange Client credentials
4. **Return delegated token** with `act` claim for Vault

```python
# Pseudo-code
def exchange_token(user_access_token):
    # Step 1: Get agent token via client credentials
    agent_token = get_agent_token(
        client_id=AGENT_CLIENT_ID,
        client_secret=AGENT_CLIENT_SECRET
    )
    
    # Step 2: Exchange tokens
    delegated_token = exchange_tokens(
        subject_token=user_access_token,
        actor_token=agent_token,
        client_id=EXCHANGE_CLIENT_ID,
        client_secret=EXCHANGE_CLIENT_SECRET,
        audience="vault"
    )
    
    return delegated_token
```

## Verification

### Check Frontend Client Token:
```bash
# Decode user access token
echo "<user-access-token>" | cut -d. -f2 | base64 -d | jq
```

Expected:
- ✅ `grant_type: "authorization_code"`
- ✅ `scope` includes groups
- ✅ `groupIds` array present

### Check Agent Client Token:
```bash
# Get and decode agent token
curl -X POST ... | jq -r '.access_token' | cut -d. -f2 | base64 -d | jq
```

Expected:
- ✅ `grant_type: "client_credentials"`
- ✅ `client_id` matches Agent Client ID
- ✅ `sub` equals `client_id`

### Check Exchanged Token:
```bash
# Decode delegated token
echo "<delegated-token>" | cut -d. -f2 | base64 -d | jq
```

Expected:
- ✅ `sub` matches user ID (from subject token)
- ✅ `groupIds` from user token
- ✅ `act.sub` matches agent client ID
- ✅ `act.client_id` matches agent client ID
- ✅ `aud` matches requested audience ("vault")

## Troubleshooting

### Issue: "The actor or client is not authorized to act on behalf of the subject"

**Cause**: Missing `may_act` configuration in Frontend Client

**Fix**:
1. ✅ Navigate to Frontend Client → Sign-on → Endpoint configuration → Introspect
2. ✅ Add `may_act` attribute with JSON rule containing agent client_id
3. ✅ Ensure the client_id in `may_act` matches your Agent Client ID
4. ✅ Save and test again

**Example `may_act` rule**:
```json
{
  "client_id": "caf77fa3-5873-403e-900e-d8b0c2a8e540"
}
```

This explicitly authorizes the agent client to act on behalf of users authenticated by the frontend client.

### Issue: `act` claim not appearing

**Check**:
1. ✅ Exchange Client has JWT access token format
2. ✅ Exchange Client Introspect endpoint has `act` attribute mapping with rule: `requestContext.actor_token`
3. ✅ Using `access_token` type (not `id_token`)
4. ✅ Actor token is provided in exchange request

### Issue: "authorization_grant of type user_code does not exist"

**Cause**: Token type mismatch

**Fix**:
- Ensure subject_token_type = `access_token`
- Ensure requested_token_type = `access_token`
- Ensure actor_token_type = `access_token`
- Don't use `id_token` types

### Issue: Groups not in token

**Check**:
1. ✅ User is assigned to groups in IBM Verify
2. ✅ Frontend Client requests `groups` scope
3. ✅ Frontend Client Introspect endpoint has `groupIds` attribute mapping
4. ✅ Exchange preserves claims from subject token

## Summary

| Client | Purpose | Grant Type | Token Use |
|--------|---------|------------|-----------|
| Frontend | User SSO | Authorization Code | Subject Token |
| Agent | Bot Identity | Client Credentials | Actor Token |
| Exchange | Token Exchange | Token Exchange | Delegated Token → Vault |

**Key Benefits**:
- ✅ Clear separation of identities
- ✅ Proper RFC 8693 delegation with `act` claim
- ✅ Agent has its own identity (not user impersonation)
- ✅ Audit trail shows both user and agent
- ✅ Vault policies can distinguish delegation from direct access
