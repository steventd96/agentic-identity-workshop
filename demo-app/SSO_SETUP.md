# SSO Login and Token Exchange Setup Guide

This guide explains how to set up and use the SSO login feature with token exchange in the AskHR demo application.

## Overview

The demo app now includes:
1. **Frontend SSO Login**: React app with IBM Verify OAuth integration
2. **Backend API**: Flask server handling OAuth flow
3. **Token Exchange Tool**: Langflow component for exchanging user tokens to agent tokens

## Architecture Flow

```
User → Frontend (Login Button) → Backend API → IBM Verify (OAuth)
                                      ↓
                                  User JWT Token
                                      ↓
                            Langflow Token Exchange Tool
                                      ↓
                                  Agent JWT Token
                                      ↓
                              Vault Authentication
                                      ↓
                            Dynamic DB Credentials
```

## Prerequisites

1. IBM Verify tenant configured (see [IBM_VERIFY_SETUP.md](../docs/IBM_VERIFY_SETUP.md))
2. Environment variables set in `.env` file
3. Node.js and npm installed (for frontend)
4. Python 3.8+ installed (for backend)

## Installation

### 1. Backend Setup

```bash
# Navigate to backend directory
cd agentic-security-incubation/demo-app/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export IBM_VERIFY_TENANT="your-tenant-name"
export IBM_VERIFY_CLIENT_ID="your-client-id"
export IBM_VERIFY_CLIENT_SECRET="your-client-secret"
export IBM_VERIFY_REDIRECT_URI="http://localhost:3000/callback"
export FLASK_SECRET_KEY="your-secret-key"  # Generate with: python -c "import secrets; print(secrets.token_hex(32))"

# Start backend server
python app.py
```

The backend will start on `http://localhost:5000`

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd agentic-security-incubation/demo-app/frontend

# Install dependencies
npm install

# Create .env file
echo "REACT_APP_BACKEND_URL=http://localhost:5000" > .env

# Start frontend
npm start
```

The frontend will start on `http://localhost:3000`

### 3. Langflow Tool Setup

The Token Exchange Tool is automatically available in Langflow after copying the tools to the Langflow components directory:

```bash
# Copy tools to Langflow
cp -r agentic-security-incubation/demo-app/tools/* /path/to/langflow/components/custom/
```

Or add the tools directory to your `LANGFLOW_COMPONENTS_PATH`:

```bash
export LANGFLOW_COMPONENTS_PATH="agentic-security-incubation/demo-app/tools"
```

## Usage

### Step 1: Login with SSO

1. Open the demo app at `http://localhost:3000`
2. Click the **"🔐 Login with SSO"** button
3. You'll be redirected to IBM Verify
4. Enter your credentials (e.g., `alice.employee` or `bob.manager`)
5. After successful authentication, you'll be redirected back to the app

### Step 2: Copy Your JWT Token

1. After login, you'll see your user information
2. Your JWT token is displayed in the "Your JWT Token" section
3. Click the **"📋 Copy Token"** button to copy it to clipboard

### Step 3: Use Token in Langflow

1. Open Langflow at `http://localhost:7860`
2. Create or open a flow
3. Add the **Token Exchange Tool** component
4. Configure the tool:
   - **User JWT Token**: Paste the token you copied
   - **Token Endpoint**: `https://your-tenant.verify.ibm.com/oidc/endpoint/default/token`
   - **Client ID**: Your IBM Verify client ID
   - **Client Secret**: Your IBM Verify client secret
   - **Audience**: `vault` (or your target audience)
   - **Scope**: `openid profile email groups`

5. Run the tool - it will return an agent JWT token

### Step 4: Use Agent Token with Vault Tool

1. Connect the Token Exchange Tool output to the Vault Tool
2. The Vault Tool will use the agent token to authenticate with Vault
3. Vault will return dynamic database credentials based on the user's groups

## API Endpoints

### Backend API

- `GET /health` - Health check
- `GET /api/auth/login` - Initiate OAuth login
- `POST /api/auth/callback` - Handle OAuth callback
- `GET /api/auth/user` - Get current user info
- `POST /api/auth/logout` - Logout user
- `POST /api/auth/refresh` - Refresh access token

## Token Exchange Tool Configuration

### Inputs

| Parameter | Description | Default | Required |
|-----------|-------------|---------|----------|
| user_jwt_token | JWT token from IBM Verify | - | Yes |
| token_endpoint | OAuth token endpoint URL | - | Yes |
| client_id | OAuth client ID | - | Yes |
| client_secret | OAuth client secret | - | Yes |
| audience | Target audience for token | vault | No |
| scope | Requested scopes | openid profile email groups | No |

### Outputs

The tool returns a Data object with:

```json
{
  "status": "success",
  "agent_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "audience": "vault",
  "user_email": "alice.employee@company.com",
  "user_groups": ["hr-basic"]
}
```

## Security Considerations

### Backend Security

1. **CSRF Protection**: State parameter validates OAuth callback
2. **Secure Sessions**: Flask sessions with secure secret key
3. **CORS**: Configured for specific origins only
4. **HTTPS**: Use HTTPS in production
5. **Token Storage**: Tokens stored in secure HTTP-only cookies

### Frontend Security

1. **No Token Storage**: Tokens not stored in localStorage
2. **Secure Communication**: All API calls use credentials
3. **Token Display**: Only shows truncated token preview
4. **Auto-logout**: Session expires with backend

### Token Exchange Security

1. **Client Authentication**: Requires client credentials
2. **Audience Validation**: Tokens scoped to specific audience
3. **Short-lived Tokens**: Tokens expire after configured time
4. **Group-based Access**: Vault policies based on user groups

## Troubleshooting

### Backend Issues

**Error: "Missing required IBM Verify configuration"**
- Solution: Ensure all environment variables are set

**Error: "Invalid state parameter"**
- Solution: Clear browser cookies and try again

**Error: "Token exchange failed"**
- Solution: Verify client credentials and token endpoint URL

### Frontend Issues

**Error: "Failed to initiate login"**
- Solution: Check backend is running on port 5000

**Error: "Authentication failed"**
- Solution: Check browser console for detailed error

**CORS Errors**
- Solution: Ensure backend CORS is configured for `http://localhost:3000`

### Langflow Tool Issues

**Error: "Invalid JWT token format"**
- Solution: Ensure you copied the complete token

**Error: "Token exchange failed: 401"**
- Solution: Verify client credentials in tool configuration

**Error: "Network error"**
- Solution: Check token endpoint URL is accessible

## Environment Variables Reference

### Backend (.env)

```bash
# IBM Verify Configuration
IBM_VERIFY_TENANT=your-tenant-name
IBM_VERIFY_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
IBM_VERIFY_CLIENT_SECRET=yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy
IBM_VERIFY_OIDC_URL=https://your-tenant.verify.ibm.com/oidc/endpoint/default
IBM_VERIFY_REDIRECT_URI=http://localhost:3000/callback

# Flask Configuration
FLASK_SECRET_KEY=your-secret-key-here
FLASK_DEBUG=False
PORT=5000
```

### Frontend (.env)

```bash
REACT_APP_BACKEND_URL=http://localhost:5000
```

## Testing

### Test User Login

1. Use test users created in IBM Verify:
   - `alice.employee` (hr-basic group)
   - `bob.manager` (hr-admin group)
   - `charlie.user` (no groups - should fail Vault auth)

### Test Token Exchange

```bash
# Test with curl
curl -X POST http://localhost:5000/api/auth/callback \
  -H "Content-Type: application/json" \
  -d '{"code": "AUTH_CODE", "state": "STATE_VALUE"}'
```

### Test Langflow Tool

1. Copy a valid user JWT token
2. Run the Token Exchange Tool in Langflow
3. Verify the output contains an agent token
4. Use the agent token with Vault Tool
5. Verify dynamic credentials are returned

## Production Deployment

### Backend

1. Use production WSGI server (gunicorn, uWSGI)
2. Enable HTTPS
3. Set secure session cookies
4. Use environment-specific configuration
5. Enable logging and monitoring

### Frontend

1. Build production bundle: `npm run build`
2. Serve with nginx or similar
3. Enable HTTPS
4. Configure proper CORS origins
5. Set production backend URL

### Security Checklist

- [ ] HTTPS enabled for all services
- [ ] Secure session secret key
- [ ] CORS configured for production domains
- [ ] Token expiration configured appropriately
- [ ] Logging and monitoring enabled
- [ ] Rate limiting implemented
- [ ] Security headers configured
- [ ] Regular security updates applied

## Additional Resources

- [IBM Verify Setup Guide](../docs/IBM_VERIFY_SETUP.md)
- [OAuth 2.0 Token Exchange (RFC 8693)](https://datatracker.ietf.org/doc/html/rfc8693)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/2.3.x/security/)
- [React Security Best Practices](https://reactjs.org/docs/security.html)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the IBM Verify setup guide
3. Check backend and frontend logs
4. Contact the lab support team

---

**Version**: 1.0.0  
**Last Updated**: 2026-02-20  
**Maintained By**: IBM Security Team

<!-- Made with Bob -->