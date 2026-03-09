# AskHR - Secure AI Agent Demo Application

This demo application showcases a production-ready implementation of agentic security with:
- **Frontend**: IBM Carbon Design chatbot with IBM Verify SSO
- **Agent**: Langflow HR agent with secure tools
- **Security**: OAuth token exchange + HashiCorp Vault dynamic secrets
- **Backend**: PostgreSQL with policy-based access control

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        AskHR Frontend                           │
│                  (IBM Carbon Design + React)                    │
│                                                                 │
│  ┌──────────────┐                                              │
│  │ IBM Verify   │  User Login (SSO)                            │
│  │ SSO          │  ↓                                            │
│  └──────────────┘  User JWT Token                              │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Langflow HR Agent                          │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Agent Flow:                                             │  │
│  │  1. Receive user query + JWT token                      │  │
│  │  2. Determine which tool to use                         │  │
│  │  3. Execute tool with user context                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────┐              ┌──────────────┐               │
│  │ Vault Tool   │              │ Database     │               │
│  │              │              │ Tool         │               │
│  │ • Get dynamic│──────────────▶│ • Use creds │               │
│  │   secrets    │   Pass creds │ • Query DB  │               │
│  └──────────────┘              └──────────────┘               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      HashiCorp Vault                            │
│                                                                 │
│  1. Validate JWT token                                         │
│  2. Check user policies (hr-basic vs hr-admin)                 │
│  3. Generate dynamic PostgreSQL credentials                    │
│  4. Return credentials with TTL                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      PostgreSQL Database                        │
│                                                                 │
│  • employee_basic_info (accessible to hr-basic)                │
│  • employee_salary_info (accessible to hr-admin only)          │
└─────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Frontend Application (`frontend/`)
- **Technology**: React + TypeScript + IBM Carbon Design System
- **Authentication**: IBM Verify SSO integration
- **Features**:
  - **Embedded Langflow Chat Widget**: Direct integration with Langflow flows
  - User authentication with IBM Verify
  - JWT token management and automatic passing to chat widget
  - Session handling
  - Responsive design for mobile and desktop

#### Langflow Chat Widget Integration

The frontend includes an embedded Langflow chat widget that:
- Loads dynamically from CDN (no additional dependencies)
- Automatically receives user JWT token via `tweaks` parameter
- Passes token to Langflow flow for authentication and authorization
- Provides seamless chat experience within the application

**Implementation Details**:
- **Component**: `frontend/src/components/ChatWidget.tsx`
- **Token Passing**: User JWT token from SSO login is passed via tweaks
- **Tweaks Format**: `{ "vault_credentials_tool-okuBC": { "user_jwt_token": "..." } }`
- **Configuration**: Environment variables for flow ID, host URL, API key, and component ID

**Environment Variables**:
```env
REACT_APP_LANGFLOW_API_KEY=your-langflow-api-key
REACT_APP_LANGFLOW_HOST_URL=http://localhost:7860
REACT_APP_LANGFLOW_FLOW_ID=6158c23c-7d05-49db-ba6e-0b3304f7df2a
REACT_APP_LANGFLOW_COMPONENT_ID=vault_credentials_tool-okuBC
```

See [`LANGFLOW_CHAT_INTEGRATION.md`](LANGFLOW_CHAT_INTEGRATION.md) for detailed integration documentation.

### 2. Langflow Agent (`langflow-flows/`)
- **Flow**: `hr-agent-flow.json`
- **Components**:
  - **Prompt Template**: Formats user queries
  - **Agent**: OpenAI-powered decision maker
  - **Vault Tool**: Custom tool for getting dynamic secrets
  - **Database Tool**: Custom tool for querying PostgreSQL

### 3. Custom Tools (`tools/`)
- **Vault Tool** (`vault_tool.py`):
  - Receives user JWT token
  - Authenticates with Vault
  - Requests dynamic database credentials
  - Returns credentials to agent

- **Database Tool** (`database_tool.py`):
  - Receives dynamic credentials from Vault Tool
  - Connects to PostgreSQL
  - Executes queries based on user permissions
  - Returns results to agent

## Setup Instructions

### Prerequisites
- Completed Parts 1-5 of the hands-on lab
- All infrastructure running (Vault, PostgreSQL, Langflow)
- IBM Verify configured
- Node.js 18+ installed

### Step 1: Install Frontend Dependencies

```bash
cd frontend
npm install
```

### Step 2: Configure Environment

Create `frontend/.env`:
```env
REACT_APP_IBM_VERIFY_CLIENT_ID=your_client_id
REACT_APP_IBM_VERIFY_AUTHORITY=https://your-tenant.verify.ibm.com
REACT_APP_LANGFLOW_URL=http://localhost:7007
REACT_APP_FLOW_ID=hr-agent-flow
```

### Step 3: Import Langflow Flow

1. Open Langflow UI: http://localhost:7007
2. Click "Import Flow"
3. Select `langflow-flows/hr-agent-flow.json`
4. Configure OpenAI API key in the Agent component

### Step 4: Deploy Custom Tools to Langflow

```bash
# Copy tools to Langflow's custom components directory
cp tools/*.py ~/.langflow/components/
```

### Step 5: Start the Frontend

```bash
cd frontend
npm start
```

The application will be available at http://localhost:3000

## Usage

### Using the Embedded Chat Widget

After logging in, you'll see the embedded Langflow chat widget in the authenticated section. The widget automatically:
1. Receives your JWT token from the SSO login
2. Passes it to the Langflow flow via the `tweaks` parameter
3. Enables the flow to perform token exchange and Vault authentication
4. Provides responses based on your permissions

### As Alice (HR Basic User)

1. **Login** with Alice's credentials via IBM Verify SSO
2. **Chat Widget Appears** - Your JWT token is automatically passed
3. **Ask**: "Show me all employees in the Engineering department"
   - ✅ Query succeeds - Alice can access basic employee info
4. **Ask**: "What is John Doe's salary?"
   - ❌ Query fails - Alice cannot access salary information

### As Bob (HR Admin User)

1. **Login** with Bob's credentials via IBM Verify SSO
2. **Chat Widget Appears** - Your JWT token is automatically passed
3. **Ask**: "Show me all employees in the Engineering department"
   - ✅ Query succeeds - Bob can access basic employee info
4. **Ask**: "What is John Doe's salary?"
   - ✅ Query succeeds - Bob can access salary information

### Chat Widget Features

- **Automatic Authentication**: No need to manually copy/paste tokens
- **Real-time Responses**: Instant feedback from the AI agent
- **Context Awareness**: Agent knows your identity and permissions
- **Secure Communication**: All requests use your authenticated session

## Security Flow

### Request Flow:
1. **User logs in** → IBM Verify returns JWT token
2. **User asks question** → Frontend sends query + JWT to Langflow
3. **Langflow agent** → Determines it needs database access
4. **Agent calls Vault Tool** → Passes user JWT token
5. **Vault Tool** → Authenticates with Vault using JWT
6. **Vault** → Validates token, checks policies, generates dynamic credentials
7. **Vault Tool** → Returns credentials to agent
8. **Agent calls Database Tool** → Passes dynamic credentials
9. **Database Tool** → Connects to PostgreSQL with dynamic credentials
10. **Database Tool** → Executes query, returns results
11. **Agent** → Formats response
12. **Frontend** → Displays answer to user

### Security Features:
- ✅ User authentication with IBM Verify
- ✅ JWT token validation
- ✅ Policy-based access control
- ✅ Dynamic database credentials (1-hour TTL)
- ✅ No long-lived secrets
- ✅ Complete audit trail
- ✅ Automatic credential revocation

## Testing

### Test Scenarios:

1. **Basic Access Test**:
   ```
   User: Alice
   Query: "List all employees"
   Expected: Success - Returns employee list
   ```

2. **Unauthorized Access Test**:
   ```
   User: Alice
   Query: "Show me salary information"
   Expected: Failure - Access denied
   ```

3. **Admin Access Test**:
   ```
   User: Bob
   Query: "Show me salary information"
   Expected: Success - Returns salary data
   ```

4. **Dynamic Credentials Test**:
   ```
   - Make query
   - Check Vault logs for credential generation
   - Wait 1 hour
   - Verify credentials are revoked
   ```

## Monitoring

### View Vault Audit Logs:
```bash
podman-compose logs vault | grep audit
```

### View Langflow Logs:
```bash
podman-compose logs langflow
```

### View Application Logs:
```bash
# Frontend logs in browser console
# Backend logs in terminal
```

## Troubleshooting

### Frontend won't start:
- Check Node.js version (18+)
- Verify `.env` file exists
- Run `npm install` again

### Langflow connection fails:
- Verify Langflow is running: `podman-compose ps`
- Check Langflow URL in `.env`
- Verify flow is imported

### Authentication fails:
- Check IBM Verify configuration
- Verify client ID and authority URL
- Check browser console for errors

### Database queries fail:
- Verify Vault is configured
- Check user policies in Vault
- Verify PostgreSQL is running

## Next Steps

1. **Customize the UI** - Modify Carbon Design components
2. **Add More Tools** - Extend agent capabilities
3. **Implement Caching** - Cache Vault credentials
4. **Add Monitoring** - Integrate with monitoring tools
5. **Deploy to Production** - Use production Vault cluster

## Resources

- [IBM Carbon Design System](https://carbondesignsystem.com/)
- [IBM Verify Documentation](https://www.ibm.com/docs/en/security-verify)
- [Langflow Documentation](https://docs.langflow.org/)
- [HashiCorp Vault Documentation](https://www.vaultproject.io/docs)

---

**This demo showcases production-ready agentic security patterns! 🔒🤖**