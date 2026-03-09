"""
Custom Langflow Tools for Agentic Security Demo

This package contains custom Langflow components for the HR Agent demo:
- TokenExchangeToolComponent: Exchanges user JWT token for agent JWT token
- VaultToolComponent: Gets dynamic database credentials from HashiCorp Vault
- DatabaseToolComponent: Queries PostgreSQL using dynamic credentials
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from lfx.components._importing import import_mod

if TYPE_CHECKING:
    from hands_on_lab.demo_app.tools.token_exchange_tool import TokenExchangeToolComponent
    from hands_on_lab.demo_app.tools.vault_tool import VaultToolComponent
    from hands_on_lab.demo_app.tools.database_tool import DatabaseToolComponent

_dynamic_imports = {
    "TokenExchangeToolComponent": "token_exchange_tool",
    "VaultToolComponent": "vault_tool",
    "DatabaseToolComponent": "database_tool",
}

__all__ = [
    "TokenExchangeToolComponent",
    "VaultToolComponent",
    "DatabaseToolComponent",
]


def __getattr__(attr_name: str) -> Any:
    """Lazily import tool components on attribute access."""
    if attr_name not in _dynamic_imports:
        msg = f"module '{__name__}' has no attribute '{attr_name}'"
        raise AttributeError(msg)
    try:
        result = import_mod(attr_name, _dynamic_imports[attr_name], __spec__.parent)
    except (ModuleNotFoundError, ImportError, AttributeError) as e:
        msg = f"Could not import '{attr_name}' from '{__name__}': {e}"
        raise AttributeError(msg) from e
    globals()[attr_name] = result
    return result


def __dir__() -> list[str]:
    return list(__all__)

# Made with Bob
