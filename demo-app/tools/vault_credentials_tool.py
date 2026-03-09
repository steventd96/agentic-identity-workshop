"""
Langflow Custom Component: Vault Credentials Tool (Combined)
Performs token exchange and gets dynamic database credentials from HashiCorp Vault

This tool combines:
1. Token Exchange: Exchanges user access token for delegated agent token (RFC 8693)
2. Vault Authentication: Uses agent token to authenticate with Vault
3. Credential Retrieval: Gets dynamic database credentials from Vault

Architecture:
- Frontend Client: User authentication (provides subject token)
- Agent Client: Bot identity via client credentials (provides actor token)
- Exchange Client: Token exchange service
- Vault: Dynamic credential generation
"""

from typing import Any, Optional
import requests
import json
import jwt

from lfx.custom import Component
from lfx.io import MessageTextInput, StrInput, SecretStrInput, BoolInput, Output
from lfx.schema import Data


class VaultCredentialsToolComponent(Component):
    display_name = "Vault Credentials Tool"
    description = "STEP 1: Call this tool FIRST to obtain database credentials from Vault. Exchanges user token and retrieves dynamic credentials. Returns a credentials object with username, password, and database_role. You MUST call this before using query_database tool."
    documentation = "https://developer.hashicorp.com/vault/docs/auth/jwt"
    icon = "Database"
    name = "vault_credentials_tool"
    
    inputs = [
        # Passthrough input — required for Langflow agent tool connection
        MessageTextInput(
            name="input_value",
            display_name="Input",
            info="Passthrough input used when the component is connected to an agent as a tool.",
            tool_mode=True,
        ),
        # User Token Input
        MessageTextInput(
            name="user_jwt_token",
            display_name="User Access Token",
            info="Access token (JWT format) from Frontend Client for the authenticated user",
            advanced=True,
        ),
        
        # Token Exchange Configuration
        StrInput(
            name="token_endpoint",
            display_name="Token Endpoint",
            info="OAuth token endpoint URL",
            value="https://automation.verify.ibm.com/oidc/endpoint/default/token",
            advanced=True,
        ),
        StrInput(
            name="exchange_client_id",
            display_name="Exchange Client ID",
            info="Client ID for the Token Exchange Client",
            value="",
            advanced=True,
        ),
        SecretStrInput(
            name="exchange_client_secret",
            display_name="Exchange Client Secret",
            info="Client secret for the Token Exchange Client",
            value="",
            advanced=True,
        ),
        StrInput(
            name="agent_client_id",
            display_name="Agent Client ID",
            info="Client ID for the Agent Bot (provides actor token)",
            value="",
            advanced=True,
        ),
        SecretStrInput(
            name="agent_client_secret",
            display_name="Agent Client Secret",
            info="Client secret for the Agent Bot",
            value="",
            advanced=True,
        ),
        StrInput(
            name="audience",
            display_name="Audience",
            info="Target audience for the exchanged token",
            value="vault",
            advanced=True,
        ),
        StrInput(
            name="scope",
            display_name="Scope",
            info="Requested scopes for the exchanged token",
            value="openid profile email groups",
            advanced=True,
        ),
        BoolInput(
            name="use_delegation",
            display_name="Use Delegation (RFC 8693)",
            info="Enable delegation semantics with 'act' claim",
            value=True,
            advanced=True,
        ),
        
        # Vault Configuration
        StrInput(
            name="vault_addr",
            display_name="Vault Address",
            info="HashiCorp Vault server address",
            value="http://vault:8200",
            advanced=True,
        ),
        StrInput(
            name="jwt_auth_path",
            display_name="JWT Auth Path",
            info="Vault JWT authentication path",
            value="auth/jwt/login",
            advanced=True,
        ),
        StrInput(
            name="jwt_role",
            display_name="JWT Role",
            info="Vault JWT role name for agent authentication",
            value="agent-role",
            advanced=True,
        ),
    ]
    
    outputs = [
        Output(
            display_name="Database Credentials",
            name="credentials",
            method="get_credentials",
        ),
    ]
    
    def get_credentials(self) -> Data:
        """
        Main method: Exchange token and get database credentials
        
        Flow:
        1. Validate user access token (subject)
        2. Obtain agent access token (actor) via client credentials
        3. Exchange tokens to get delegated token
        4. Authenticate with Vault using delegated token
        5. Request and return database credentials
        
        Returns:
            Data object with database credentials or error information
        """
        try:
            # ============================================================
            # STEP 1: Token Exchange
            # ============================================================
            self.log("=" * 60)
            self.log("STEP 1: TOKEN EXCHANGE")
            self.log("=" * 60)
            
            # Extract and validate user access token
            user_jwt = self._extract_token(self.user_jwt_token)
            
            if not user_jwt:
                error_msg = "User access token is required"
                self.log(f"❌ {error_msg}")
                self.status = "❌ Missing user token"
                return Data(data={"error": error_msg, "status": "failed"})
            
            if not self._is_valid_jwt_format(user_jwt):
                error_msg = f"Invalid JWT format. Token has {len(user_jwt.split('.'))} parts (expected 3)"
                self.log(f"❌ {error_msg}")
                self.status = "❌ Invalid token format"
                return Data(data={"error": error_msg, "status": "failed"})
            
            # Decode user token to inspect claims
            try:
                user_claims = jwt.decode(user_jwt, options={"verify_signature": False})
                user_email = user_claims.get('email', 'unknown')
                user_groups = user_claims.get('groupIds', [])
                self.log(f"📧 User: {user_email}")
                self.log(f"👥 Groups: {user_groups}")
            except Exception as e:
                self.log(f"⚠️  Could not decode user token: {e}")
                user_email = "unknown"
                user_groups = []
            
            # Get agent token via client credentials (if delegation enabled)
            actor_token = None
            if self.use_delegation:
                self.log("🤖 Obtaining agent token via client credentials...")
                actor_token = self._get_agent_token()
                
                if not actor_token:
                    error_msg = "Failed to obtain agent token via client credentials"
                    self.log(f"❌ {error_msg}")
                    self.status = "❌ Agent auth failed"
                    return Data(data={"error": error_msg, "status": "failed"})
                
                self.log("✓ Agent token obtained")
            
            # Perform token exchange
            self.log(f"🔄 Initiating token exchange for audience: {self.audience}")
            
            token_exchange_data = {
                'grant_type': 'urn:ietf:params:oauth:grant-type:token-exchange',
                'subject_token': user_jwt,
                'subject_token_type': 'urn:ietf:params:oauth:token-type:access_token',
                'requested_token_type': 'urn:ietf:params:oauth:token-type:access_token',
                'client_id': self.exchange_client_id,
                'client_secret': self.exchange_client_secret,
                'audience': self.audience,
                'scope': self.scope
            }
            
            # Add actor token for delegation semantics
            if actor_token:
                token_exchange_data['actor_token'] = actor_token
                token_exchange_data['actor_token_type'] = 'urn:ietf:params:oauth:token-type:access_token'
                self.log("🎭 Delegation mode: RFC 8693 with 'act' claim")
            
            response = requests.post(
                self.token_endpoint,
                data=token_exchange_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30
            )
            
            if response.status_code != 200:
                error_msg = f"Token exchange failed: {response.status_code} - {response.text}"
                self.log(f"❌ {error_msg}")
                self.status = "❌ Exchange failed"
                return Data(data={"error": error_msg, "status": "failed"})
            
            # Parse exchange response
            exchange_result = response.json()
            agent_token = exchange_result.get('access_token')
            
            if not agent_token:
                error_msg = "No access token in exchange response"
                self.log(f"❌ {error_msg}")
                self.status = "❌ Invalid response"
                return Data(data={"error": error_msg, "status": "failed"})
            
            # Verify agent token claims
            try:
                agent_claims = jwt.decode(agent_token, options={"verify_signature": False})
                agent_audience = agent_claims.get('aud', 'unknown')
                agent_subject = agent_claims.get('sub', 'unknown')
                
                if 'act' in agent_claims:
                    actor_info = agent_claims['act']
                    self.log(f"🎭 Delegation detected - Actor: {actor_info.get('sub', 'unknown')}")
                
                self.log(f"✓ Agent token obtained - Audience: {agent_audience}, Subject: {agent_subject}")
            except Exception as e:
                self.log(f"⚠️  Could not decode agent token: {e}")
            
            # ============================================================
            # STEP 2: Vault Authentication
            # ============================================================
            self.log("")
            self.log("=" * 60)
            self.log("STEP 2: VAULT AUTHENTICATION")
            self.log("=" * 60)
            
            self.log(f"🔐 Authenticating with Vault using agent JWT for role: {self.jwt_role}")
            
            auth_url = f"{self.vault_addr}/v1/{self.jwt_auth_path}"
            auth_payload = {
                "role": self.jwt_role,
                "jwt": agent_token
            }
            
            auth_response = requests.post(
                auth_url,
                json=auth_payload,
                timeout=10
            )
            
            if auth_response.status_code != 200:
                error_msg = f"Vault authentication failed: {auth_response.text}"
                self.log(f"❌ {error_msg}")
                self.status = "❌ Vault auth failed"
                return Data(data={"error": error_msg, "status": "failed"})
            
            vault_token = auth_response.json()["auth"]["client_token"]
            self.log("✓ Successfully authenticated with Vault")
            
            # ============================================================
            # STEP 3: Discover Database Role via Vault Capabilities
            # ============================================================
            self.log("")
            self.log("=" * 60)
            self.log("STEP 3: ROLE DISCOVERY")
            self.log("=" * 60)
            
            # Check which database credential paths this token can access.
            # The role is determined by the user's Vault identity (group membership),
            # not by the query type. Vault enforces the actual access boundary.
            headers = {"X-Vault-Token": vault_token}
            cap_response = requests.post(
                f"{self.vault_addr}/v1/sys/capabilities-self",
                headers=headers,
                json={"paths": ["database/creds/hr-admin-reader", "database/creds/hr-basic-reader"]},
                timeout=10
            )
            
            database_role = None
            if cap_response.status_code == 200:
                caps = cap_response.json()
                admin_caps = caps.get("database/creds/hr-admin-reader", ["deny"])
                basic_caps = caps.get("database/creds/hr-basic-reader", ["deny"])
                self.log(f"  hr-admin-reader capabilities : {admin_caps}")
                self.log(f"  hr-basic-reader capabilities : {basic_caps}")
                
                # Prefer hr-admin-reader if accessible; fall back to hr-basic-reader
                if "read" in admin_caps:
                    database_role = "hr-admin-reader"
                    self.log("✓ Role resolved: hr-admin-reader (admin access)")
                elif "read" in basic_caps:
                    database_role = "hr-basic-reader"
                    self.log("✓ Role resolved: hr-basic-reader (basic access)")
                else:
                    error_msg = "Access denied: user does not have permission to access any database role"
                    self.log(f"❌ {error_msg}")
                    self.status = "❌ Access denied"
                    return Data(data={"error": error_msg, "status": "failed"})
            else:
                # Capabilities check failed — fall back to hr-basic-reader
                self.log(f"⚠️  Could not check capabilities ({cap_response.status_code}), defaulting to hr-basic-reader")
                database_role = "hr-basic-reader"
            
            # ============================================================
            # STEP 4: Get Database Credentials
            # ============================================================
            self.log("")
            self.log("=" * 60)
            self.log("STEP 4: DATABASE CREDENTIALS")
            self.log("=" * 60)
            
            self.log(f"📊 Requesting credentials for database role: {database_role}")
            creds_url = f"{self.vault_addr}/v1/database/creds/{database_role}"
            
            creds_response = requests.get(
                creds_url,
                headers=headers,
                timeout=10
            )
            
            if creds_response.status_code != 200:
                error_msg = f"Failed to get credentials: {creds_response.text}"
                self.log(f"❌ {error_msg}")
                self.status = "❌ Credential request failed"
                return Data(data={"error": error_msg, "status": "failed"})
            
            creds_data = creds_response.json()["data"]
            
            # ============================================================
            # STEP 5: Return Credentials
            # ============================================================
            result = {
                "status": "success",
                "username": creds_data["username"],
                "password": creds_data["password"],
                "lease_duration": creds_data.get("lease_duration", 3600),
                "database_role": database_role,
                "user_email": user_email,
                "user_groups": user_groups
            }
            
            self.log("")
            self.log("=" * 60)
            self.log("✓ SUCCESS")
            self.log("=" * 60)
            self.log(f"✓ Database credentials obtained")
            self.log(f"  Username: {result['username']}")
            self.log(f"  Role    : {database_role}")
            self.log(f"  TTL     : {result['lease_duration']}s")
            self.log(f"  User    : {user_email}")
            self.log(f"  Groups  : {user_groups}")
            
            self.status = f"✓ Credentials for {database_role}"
            
            return Data(data=result)
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            self.log(f"❌ {error_msg}")
            self.status = "❌ Network error"
            return Data(data={"error": error_msg, "status": "failed"})
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.log(f"❌ {error_msg}")
            self.status = "❌ Unexpected error"
            return Data(data={"error": error_msg, "status": "failed"})
    
    def _is_valid_jwt_format(self, token: str) -> bool:
        """Check if token has valid JWT format (three base64 parts separated by dots)"""
        parts = token.split('.')
        return len(parts) == 3
    
    def _extract_token(self, token_input: Any) -> str:
        """Extract token string from various input types"""
        if not token_input:
            return ""
        
        if hasattr(token_input, 'text'):
            return token_input.text.strip()
        elif hasattr(token_input, 'data'):
            return str(token_input.data).strip()
        elif isinstance(token_input, dict):
            return token_input.get('token', token_input.get('access_token', str(token_input))).strip()
        else:
            token_str = str(token_input).strip()
            return "" if token_str == 'None' else token_str
    
    def _get_agent_token(self) -> Optional[str]:
        """
        Obtain agent access token via client credentials grant
        
        This implements the Agent Client in the 3-client architecture.
        The agent token represents the bot/agent identity and is used as the actor
        token in RFC 8693 token exchange.
        
        Returns:
            Agent access token (JWT format) or None if failed
        """
        try:
            self.log(f"🔐 Authenticating agent client: {self.agent_client_id[:20]}...")
            
            # Client credentials grant
            data = {
                'grant_type': 'client_credentials',
                'client_id': self.agent_client_id,
                'client_secret': self.agent_client_secret,
                'scope': 'agent.act'  # Custom scope for agent acting capability
            }
            
            response = requests.post(
                self.token_endpoint,
                data=data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30
            )
            
            if response.status_code != 200:
                self.log(f"❌ Agent auth failed: {response.status_code} - {response.text}")
                return None
            
            result = response.json()
            agent_token = result.get('access_token')
            
            if not agent_token:
                self.log("❌ No access token in agent auth response")
                return None
            
            # Verify it's a JWT
            if not self._is_valid_jwt_format(agent_token):
                self.log("❌ Agent token is not in JWT format")
                return None
            
            # Decode to verify claims
            try:
                agent_claims = jwt.decode(agent_token, options={"verify_signature": False})
                agent_client_id = agent_claims.get('client_id', 'unknown')
                self.log(f"✓ Agent authenticated: {agent_client_id}")
            except Exception as e:
                self.log(f"⚠️  Could not decode agent token: {e}")
            
            return agent_token
            
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Network error during agent authentication: {e}")
            return None
        except Exception as e:
            self.log(f"❌ Unexpected error during agent authentication: {e}")
            return None

# Made with Bob