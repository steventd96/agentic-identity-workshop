"""
Agentic Security Lab - Agent Framework Module
=============================================

This module provides a modular architecture for integrating different
agent frameworks (Langflow, CrewAI, LangGraph, LangChain) with consistent
security patterns.
"""

from .base import AgentFrameworkAdapter, AgentConfig, AgentResponse

__all__ = ['AgentFrameworkAdapter', 'AgentConfig', 'AgentResponse']
__version__ = '1.0.0'

# Made with Bob
