# Demo Application Installation Guide

This guide explains how to install and configure the custom Langflow tools for the AskHR demo application.

## Prerequisites

- Langflow installed (see main README.md for installation instructions)
- Infrastructure running (Vault, PostgreSQL, Langflow containers)
- Python 3.9+ with required dependencies

## Installation Steps

### 1. Install Custom Langflow Tools

The custom tools need to be placed in Langflow's components directory. There are two approaches:

#### Option A: Copy to Langflow Components Directory (Recommended for Development)

```bash
# Find your Langflow installation directory
python -c "import lfx; print(lfx.__file__)"

# This will show something like: /path/to/site-packages/lfx/__init__.py
# The components directory is at: /path/to/site-packages/lfx/components/

# Create a custom tools directory
mkdir -p /path/to/site-packages/lfx/components/custom_tools

# Copy the tools
cp hands-on-lab/demo-app/tools/*.py /path/to/site-packages/lfx/components/custom_tools/
```

#### Option B: Use LANGFLOW_COMPONENTS_PATH Environment Variable

```bash
# Set the environment variable to point to your custom tools directory
export LANGFLOW_COMPONENTS_PATH=/path/to/hands-on-lab/demo-app/tools

# Start Langflow with the custom components path
langflow run --port 7860 --env-file .env
```

### 2. Verify Tool Installation

1. Start Langflow:
   ```bash
   langflow run --port 7860
   ```

2. Open the Langflow UI at http://localhost:7860

3. Create a new flow

4. In the components sidebar, look for:
   - **Vault Tool** (under Custom Tools or Tools category)
   - **Database Tool** (under Custom Tools or Tools category)

5. If you see these components, the installation was successful!

### 3. Import the Pre-built HR Agent Flow

1. In Langflow UI, click **"Import"** or **"Load Flow"**

2. Select the file: `hands-on-lab/demo-app/langflow-flows/hr-agent-flow.json`

3. The flow will be imported with all components connected:
   - Chat Input
   - Prompt Template
   - Vault Tool
   - Database Tool
   - Agent
   - OpenAI LLM
   - Chat Output

### 4. Configure the Flow

#### Configure OpenAI LLM Component

1. Click on the **OpenAI** component
2. Enter your OpenAI API key
3. Select model: `gpt-4` or `gpt-3.5-turbo`

#### Configure Vault Tool Component

The Vault Tool should already have these default values:
- **Vault Address**: `http://vault:8200`
- **JWT Auth Path**: `auth/jwt/login`
- **JWT Role**: `hr-agent`

If running Vault on a different host, update the **Vault Address**.

#### Configure Database Tool Component

The Database Tool should already have these default values:
- **Database Host**: `localhost`
- **Database Port**: `5432`
- **Database Name**: `employee_db`

If running PostgreSQL in Podman, you may need to use `host.containers.internal` instead of `localhost`.

### 5. Test the Flow

1. Click the **"Play"** or **"Run"** button in Langflow

2. In the Chat Input, enter a test message with a mock JWT token:
   ```json
   {
     "message": "Show me employee basic information",
     "jwt_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
   }
   ```

3. The agent should:
   - Use the Vault Tool to get dynamic credentials
   - Use the Database Tool to query the database
   - Return the results in the Chat Output

## Troubleshooting

### Tools Not Appearing in Langflow UI

**Problem**: Custom tools don't appear in the components sidebar.

**Solutions**:
1. Verify the tools are in the correct directory
2. Check that `__init__.py` exists in the tools directory
3. Restart Langflow completely
4. Check Langflow logs for import errors:
   ```bash
   tail -f ~/.langflow/langflow.log
   ```

### Import Errors

**Problem**: `ImportError: cannot import name 'Component' from 'lfx.custom'`

**Solutions**:
1. Ensure Langflow is properly installed:
   ```bash
   pip install langflow --upgrade
   ```
2. Verify Langflow version:
   ```bash
   langflow --version
   ```
   (Should be 1.0.0 or higher)

### Connection Errors

**Problem**: Vault Tool fails with "Connection refused"

**Solutions**:
1. Verify Vault is running:
   ```bash
   podman ps | grep vault
   ```
2. Check Vault address in the tool configuration
3. If running in Podman, use the container name `vault` instead of `localhost`

**Problem**: Database Tool fails with "Connection refused"

**Solutions**:
1. Verify PostgreSQL is running:
   ```bash
   podman ps | grep postgres
   ```
2. Check database connection parameters
3. Verify dynamic credentials are valid (check Vault logs)

### Permission Errors

**Problem**: Database Tool returns "Permission denied for table"

**Expected Behavior**: This is correct! It demonstrates policy-based access control.

**Explanation**:
- Users with `hr-basic` role can only access `employee_basic_info` table
- Users with `hr-admin` role can access both tables
- The error proves that Vault policies are working correctly

## Podman Deployment

When running the entire stack in Podman:

1. Update `docker-compose.yml` to include Langflow with custom tools:

```yaml
services:
  langflow:
    image: langflowai/langflow:latest
    ports:
      - "7860:7860"
    volumes:
      - ./demo-app/tools:/app/custom_components/custom_tools
    environment:
      - LANGFLOW_COMPONENTS_PATH=/app/custom_components
    depends_on:
      - vault
      - postgres
```

2. Start the stack:
```bash
podman-compose up -d
```

## Next Steps

After successful installation:

1. **Test Basic Scenarios**: Try querying employee basic information
2. **Test Access Control**: Try querying salary information with different user roles
3. **Examine Logs**: Check Vault audit logs to see the security flow
4. **Customize the Agent**: Modify the prompt template or add new tools
5. **Build the Frontend**: Follow the frontend setup guide to create the AskHR UI

## Additional Resources

- [Langflow Documentation](https://docs.langflow.org/)
- [Custom Components Guide](https://docs.langflow.org/components-custom-components)
- [HashiCorp Vault Documentation](https://developer.hashicorp.com/vault/docs)
- [Main Lab README](../README.md)