"""
Agent Framework Base Classes
============================

Provides abstract base classes for implementing framework-agnostic
agent adapters that work with different AI agent frameworks.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class AgentFramework(Enum):
    """Supported agent frameworks."""
    LANGFLOW = "langflow"
    CREWAI = "crewai"
    LANGGRAPH = "langgraph"
    LANGCHAIN = "langchain"


@dataclass
class AgentConfig:
    """Configuration for agent initialization."""
    
    framework: AgentFramework
    name: str
    description: str
    tools: List[str]
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 2000
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'framework': self.framework.value,
            'name': self.name,
            'description': self.description,
            'tools': self.tools,
            'model': self.model,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'metadata': self.metadata or {}
        }


@dataclass
class AgentResponse:
    """Response from agent execution."""
    
    success: bool
    result: Any
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    execution_time: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        return {
            'success': self.success,
            'result': self.result,
            'error': self.error,
            'metadata': self.metadata or {},
            'execution_time': self.execution_time
        }


class AgentFrameworkAdapter(ABC):
    """
    Abstract base class for agent framework adapters.
    
    This class defines the interface that all framework-specific
    adapters must implement, ensuring consistent behavior across
    different agent frameworks.
    """
    
    def __init__(self, config: AgentConfig):
        """
        Initialize the agent adapter.
        
        Args:
            config: Agent configuration
        """
        self.config = config
        self._initialized = False
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the agent framework.
        
        Returns:
            bool: True if initialization successful
            
        Raises:
            Exception: If initialization fails
        """
        pass
    
    @abstractmethod
    def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """
        Execute a specific tool with given parameters.
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters
            context: Optional execution context (e.g., user token, session)
            
        Returns:
            AgentResponse: Tool execution result
            
        Raises:
            ValueError: If tool not found or parameters invalid
            Exception: If execution fails
        """
        pass
    
    @abstractmethod
    def run_agent(
        self,
        input_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """
        Run the agent with given input.
        
        Args:
            input_text: User input/query
            context: Optional execution context
            
        Returns:
            AgentResponse: Agent execution result
        """
        pass
    
    @abstractmethod
    def list_tools(self) -> List[str]:
        """
        List available tools for this agent.
        
        Returns:
            List[str]: Tool names
        """
        pass
    
    @abstractmethod
    def get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """
        Get information about a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            dict: Tool information including parameters and description
            
        Raises:
            ValueError: If tool not found
        """
        pass
    
    @abstractmethod
    def get_framework_name(self) -> str:
        """
        Get the name of the agent framework.
        
        Returns:
            str: Framework name
        """
        pass
    
    @abstractmethod
    def get_framework_version(self) -> str:
        """
        Get the version of the agent framework.
        
        Returns:
            str: Framework version
        """
        pass
    
    def is_initialized(self) -> bool:
        """
        Check if adapter is initialized.
        
        Returns:
            bool: True if initialized
        """
        return self._initialized
    
    def validate_context(self, context: Optional[Dict[str, Any]]) -> bool:
        """
        Validate execution context.
        
        Args:
            context: Execution context to validate
            
        Returns:
            bool: True if context is valid
        """
        if context is None:
            return True
        
        # Check for required security context
        required_keys = ['user_token', 'vault_token']
        return all(key in context for key in required_keys)
    
    def get_config(self) -> AgentConfig:
        """
        Get agent configuration.
        
        Returns:
            AgentConfig: Current configuration
        """
        return self.config
    
    def __repr__(self) -> str:
        """String representation of adapter."""
        return (
            f"{self.__class__.__name__}("
            f"framework={self.config.framework.value}, "
            f"name={self.config.name}, "
            f"initialized={self._initialized})"
        )


class ToolExecutionError(Exception):
    """Exception raised when tool execution fails."""
    
    def __init__(self, tool_name: str, message: str, details: Optional[Dict[str, Any]] = None):
        self.tool_name = tool_name
        self.message = message
        self.details = details or {}
        super().__init__(f"Tool '{tool_name}' execution failed: {message}")


class AgentInitializationError(Exception):
    """Exception raised when agent initialization fails."""
    
    def __init__(self, framework: str, message: str):
        self.framework = framework
        self.message = message
        super().__init__(f"Failed to initialize {framework}: {message}")

# Made with Bob
