"""
Langflow Adapter Implementation
===============================

Adapter for integrating Langflow agent framework with the security lab.
"""

import requests
import logging
from typing import Dict, Any, Optional, List
import time

from ..base import (
    AgentFrameworkAdapter,
    AgentConfig,
    AgentResponse,
    AgentFramework,
    ToolExecutionError,
    AgentInitializationError
)


logger = logging.getLogger(__name__)


class LangflowAdapter(AgentFrameworkAdapter):
    """
    Adapter for Langflow agent framework.
    
    This adapter provides integration with Langflow's API, allowing
    execution of flows and tools with proper security context.
    """
    
    def __init__(
        self,
        config: AgentConfig,
        langflow_url: str = "http://localhost:7860",
        api_key: Optional[str] = None
    ):
        """
        Initialize Langflow adapter.
        
        Args:
            config: Agent configuration
            langflow_url: Langflow server URL
            api_key: Optional API key for authentication
        """
        super().__init__(config)
        self.langflow_url = langflow_url.rstrip('/')
        self.api_key = api_key
        self.flow_id = None
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}'
            })
        
        logger.info(f"Initialized LangflowAdapter for {langflow_url}")
    
    def initialize(self) -> bool:
        """
        Initialize connection to Langflow.
        
        Returns:
            bool: True if initialization successful
            
        Raises:
            AgentInitializationError: If initialization fails
        """
        try:
            # Check Langflow health
            response = self.session.get(f"{self.langflow_url}/health", timeout=10)
            response.raise_for_status()
            
            logger.info("Langflow health check passed")
            self._initialized = True
            return True
            
        except requests.RequestException as e:
            logger.error(f"Failed to connect to Langflow: {e}")
            raise AgentInitializationError("Langflow", str(e))
    
    def load_flow(self, flow_id: str) -> bool:
        """
        Load a specific flow by ID.
        
        Args:
            flow_id: Langflow flow ID
            
        Returns:
            bool: True if flow loaded successfully
        """
        try:
            # Verify flow exists
            response = self.session.get(
                f"{self.langflow_url}/api/v1/flows/{flow_id}",
                timeout=10
            )
            response.raise_for_status()
            
            self.flow_id = flow_id
            logger.info(f"Loaded flow: {flow_id}")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Failed to load flow {flow_id}: {e}")
            return False
    
    def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """
        Execute a specific tool in Langflow.
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters
            context: Optional execution context
            
        Returns:
            AgentResponse: Tool execution result
        """
        if not self._initialized:
            raise RuntimeError("Adapter not initialized. Call initialize() first.")
        
        if not self.flow_id:
            raise RuntimeError("No flow loaded. Call load_flow() first.")
        
        start_time = time.time()
        
        try:
            # Prepare request payload
            payload = {
                'tool': tool_name,
                'parameters': parameters,
                'context': context or {}
            }
            
            # Execute tool via Langflow API
            response = self.session.post(
                f"{self.langflow_url}/api/v1/flows/{self.flow_id}/execute",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            execution_time = time.time() - start_time
            
            logger.info(f"Tool '{tool_name}' executed successfully in {execution_time:.2f}s")
            
            return AgentResponse(
                success=True,
                result=result.get('output'),
                metadata={
                    'tool': tool_name,
                    'flow_id': self.flow_id
                },
                execution_time=execution_time
            )
            
        except requests.HTTPError as e:
            execution_time = time.time() - start_time
            error_msg = f"HTTP error executing tool '{tool_name}': {e}"
            logger.error(error_msg)
            
            return AgentResponse(
                success=False,
                result=None,
                error=error_msg,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Error executing tool '{tool_name}': {e}"
            logger.error(error_msg)
            
            return AgentResponse(
                success=False,
                result=None,
                error=error_msg,
                execution_time=execution_time
            )
    
    def run_agent(
        self,
        input_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """
        Run the Langflow agent with given input.
        
        Args:
            input_text: User input/query
            context: Optional execution context
            
        Returns:
            AgentResponse: Agent execution result
        """
        if not self._initialized:
            raise RuntimeError("Adapter not initialized. Call initialize() first.")
        
        if not self.flow_id:
            raise RuntimeError("No flow loaded. Call load_flow() first.")
        
        start_time = time.time()
        
        try:
            # Prepare request payload
            payload = {
                'input': input_text,
                'context': context or {}
            }
            
            # Run flow via Langflow API
            response = self.session.post(
                f"{self.langflow_url}/api/v1/flows/{self.flow_id}/run",
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            
            result = response.json()
            execution_time = time.time() - start_time
            
            logger.info(f"Agent executed successfully in {execution_time:.2f}s")
            
            return AgentResponse(
                success=True,
                result=result.get('output'),
                metadata={
                    'flow_id': self.flow_id,
                    'input': input_text
                },
                execution_time=execution_time
            )
            
        except requests.HTTPError as e:
            execution_time = time.time() - start_time
            error_msg = f"HTTP error running agent: {e}"
            logger.error(error_msg)
            
            return AgentResponse(
                success=False,
                result=None,
                error=error_msg,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Error running agent: {e}"
            logger.error(error_msg)
            
            return AgentResponse(
                success=False,
                result=None,
                error=error_msg,
                execution_time=execution_time
            )
    
    def list_tools(self) -> List[str]:
        """
        List available tools in the loaded flow.
        
        Returns:
            List[str]: Tool names
        """
        if not self.flow_id:
            return []
        
        try:
            response = self.session.get(
                f"{self.langflow_url}/api/v1/flows/{self.flow_id}/tools",
                timeout=10
            )
            response.raise_for_status()
            
            tools = response.json().get('tools', [])
            return [tool['name'] for tool in tools]
            
        except Exception as e:
            logger.error(f"Failed to list tools: {e}")
            return []
    
    def get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """
        Get information about a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            dict: Tool information
        """
        if not self.flow_id:
            raise ValueError("No flow loaded")
        
        try:
            response = self.session.get(
                f"{self.langflow_url}/api/v1/flows/{self.flow_id}/tools/{tool_name}",
                timeout=10
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.HTTPError:
            raise ValueError(f"Tool '{tool_name}' not found")
        except Exception as e:
            logger.error(f"Failed to get tool info: {e}")
            return {}
    
    def get_framework_name(self) -> str:
        """Get framework name."""
        return "Langflow"
    
    def get_framework_version(self) -> str:
        """Get framework version."""
        try:
            response = self.session.get(
                f"{self.langflow_url}/api/v1/version",
                timeout=5
            )
            response.raise_for_status()
            return response.json().get('version', 'unknown')
        except Exception:
            return "unknown"
    
    def list_flows(self) -> List[Dict[str, Any]]:
        """
        List all available flows in Langflow.
        
        Returns:
            List[dict]: Flow information
        """
        try:
            response = self.session.get(
                f"{self.langflow_url}/api/v1/flows",
                timeout=10
            )
            response.raise_for_status()
            
            return response.json().get('flows', [])
            
        except Exception as e:
            logger.error(f"Failed to list flows: {e}")
            return []
    
    def export_flow(self, flow_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Export a flow as JSON.
        
        Args:
            flow_id: Flow ID to export (uses loaded flow if not specified)
            
        Returns:
            dict: Flow JSON or None if export fails
        """
        target_flow_id = flow_id or self.flow_id
        if not target_flow_id:
            logger.error("No flow ID specified")
            return None
        
        try:
            response = self.session.get(
                f"{self.langflow_url}/api/v1/flows/{target_flow_id}/export",
                timeout=10
            )
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to export flow: {e}")
            return None

# Made with Bob
