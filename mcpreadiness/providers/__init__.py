"""
Inspection providers for MCP Readiness Scanner.

Providers analyze MCP tool definitions and configurations to detect
operational readiness issues.

Supports custom providers via entry points:
  [project.entry-points."mcp_readiness.providers"]
  my_provider = "my_package.providers:MyProvider"
"""

import sys

from mcpreadiness.providers.base import InspectionProvider
from mcpreadiness.providers.heuristic_provider import HeuristicProvider
from mcpreadiness.providers.llm_judge_provider import LLMJudgeProvider

# Plugin discovery
if sys.version_info >= (3, 10):
    from importlib.metadata import entry_points
else:
    from importlib_metadata import entry_points  # type: ignore

# Conditional imports for optional providers
_yara_available = False
_opa_available = False

try:
    from mcpreadiness.providers.yara_provider import YaraProvider

    _yara_available = True
except ImportError:
    YaraProvider = None  # type: ignore

try:
    from mcpreadiness.providers.opa_provider import OpaProvider

    _opa_available = True
except ImportError:
    OpaProvider = None  # type: ignore

__all__ = [
    "InspectionProvider",
    "HeuristicProvider",
    "YaraProvider",
    "OpaProvider",
    "LLMJudgeProvider",
]


def get_default_providers() -> list["InspectionProvider"]:
    """
    Get all available providers with default configuration.

    Returns providers that are available (dependencies installed, etc.)
    """
    providers: list[InspectionProvider] = []

    # Heuristic provider is always available (no external deps)
    providers.append(HeuristicProvider())

    # YARA provider if yara-python is installed
    if YaraProvider is not None:
        yara = YaraProvider()
        if yara.is_available():
            providers.append(yara)

    # OPA provider if opa binary is in PATH
    if OpaProvider is not None:
        opa = OpaProvider()
        if opa.is_available():
            providers.append(opa)

    # LLM provider is disabled by default, not included here

    return providers


def get_all_provider_classes() -> list[type]:
    """Get all provider classes (including unavailable ones)."""
    classes: list[type] = [HeuristicProvider]
    if YaraProvider is not None:
        classes.append(YaraProvider)
    if OpaProvider is not None:
        classes.append(OpaProvider)
    classes.append(LLMJudgeProvider)
    return classes


def discover_custom_providers() -> dict[str, type[InspectionProvider]]:
    """
    Discover custom providers via entry points.

    Returns:
        Dictionary mapping provider names to provider classes
    """
    custom_providers: dict[str, type[InspectionProvider]] = {}

    try:
        # Python 3.10+ API
        if hasattr(entry_points(), "select"):
            eps = entry_points().select(group="mcp_readiness.providers")
        else:
            # Python 3.9 API
            eps = entry_points().get("mcp_readiness.providers", [])

        for ep in eps:
            try:
                provider_class = ep.load()
                # Validate it's a subclass of InspectionProvider
                if isinstance(provider_class, type) and issubclass(
                    provider_class, InspectionProvider
                ):
                    custom_providers[ep.name] = provider_class
                else:
                    import warnings

                    warnings.warn(
                        f"Custom provider '{ep.name}' is not a subclass of InspectionProvider"
                    )
            except Exception as e:
                import warnings

                warnings.warn(f"Failed to load custom provider '{ep.name}': {e}")

    except Exception as e:
        import warnings

        warnings.warn(f"Failed to discover custom providers: {e}")

    return custom_providers


def get_all_providers_with_plugins() -> list[InspectionProvider]:
    """
    Get all available providers including custom plugins.

    Returns providers that are available (dependencies installed, etc.)
    """
    providers: list[InspectionProvider] = get_default_providers()

    # Add custom providers
    custom_providers = discover_custom_providers()
    for name, provider_class in custom_providers.items():
        try:
            provider = provider_class()
            if provider.is_available():
                providers.append(provider)
        except Exception:
            # Skip providers that fail to instantiate
            pass

    return providers
