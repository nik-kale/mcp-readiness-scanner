"""Tests for the heuristic provider."""

import pytest

from mcpreadiness.core.models import OperationalRiskCategory, Severity
from mcpreadiness.providers.heuristic_provider import HeuristicProvider


@pytest.fixture
def provider():
    return HeuristicProvider()


class TestHeuristicProvider:
    """Tests for HeuristicProvider."""

    def test_provider_name(self, provider):
        assert provider.name == "heuristic"

    def test_provider_is_available(self, provider):
        assert provider.is_available() is True

    @pytest.mark.asyncio
    async def test_good_tool_minimal_findings(self, provider):
        """A well-configured tool should have minimal findings."""
        good_tool = {
            "name": "file_reader",
            "description": "Reads files from the filesystem with proper error handling and timeout protection.",
            "inputSchema": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
            "errorSchema": {
                "type": "object",
                "properties": {"code": {"type": "string"}, "message": {"type": "string"}},
            },
            "timeout": 30000,
            "maxRetries": 3,
            "rateLimit": {"requests": 100, "period": "minute"},
        }

        findings = await provider.analyze_tool(good_tool)

        # Good tool should have no high/critical findings
        high_critical = [
            f for f in findings if f.severity in (Severity.HIGH, Severity.CRITICAL)
        ]
        assert len(high_critical) == 0

    @pytest.mark.asyncio
    async def test_missing_timeout(self, provider):
        tool = {"name": "test_tool", "description": "A test tool"}
        findings = await provider.analyze_tool(tool)

        timeout_findings = [
            f
            for f in findings
            if f.category == OperationalRiskCategory.MISSING_TIMEOUT_GUARD
        ]
        assert len(timeout_findings) > 0
        assert any(f.severity == Severity.HIGH for f in timeout_findings)

    @pytest.mark.asyncio
    async def test_zero_timeout(self, provider):
        tool = {"name": "test_tool", "description": "A test tool", "timeout": 0}
        findings = await provider.analyze_tool(tool)

        timeout_findings = [
            f
            for f in findings
            if f.category == OperationalRiskCategory.MISSING_TIMEOUT_GUARD
            and "zero" in f.description.lower() or "invalid" in f.title.lower()
        ]
        assert len(timeout_findings) > 0

    @pytest.mark.asyncio
    async def test_missing_retry_limit(self, provider):
        tool = {"name": "test_tool", "description": "A test tool", "timeout": 30000}
        findings = await provider.analyze_tool(tool)

        retry_findings = [
            f for f in findings if f.category == OperationalRiskCategory.UNSAFE_RETRY_LOOP
        ]
        assert len(retry_findings) > 0

    @pytest.mark.asyncio
    async def test_excessive_capabilities(self, provider):
        tool = {
            "name": "test_tool",
            "description": "A test tool",
            "timeout": 30000,
            "capabilities": [f"cap_{i}" for i in range(15)],
        }
        findings = await provider.analyze_tool(tool)

        scope_findings = [
            f
            for f in findings
            if f.category == OperationalRiskCategory.OVERLOADED_TOOL_SCOPE
        ]
        assert len(scope_findings) > 0

    @pytest.mark.asyncio
    async def test_missing_error_schema(self, provider):
        tool = {"name": "test_tool", "description": "A test tool", "timeout": 30000}
        findings = await provider.analyze_tool(tool)

        error_findings = [
            f
            for f in findings
            if f.category == OperationalRiskCategory.MISSING_ERROR_SCHEMA
        ]
        assert len(error_findings) > 0

    @pytest.mark.asyncio
    async def test_missing_description(self, provider):
        tool = {"name": "test_tool", "timeout": 30000}
        findings = await provider.analyze_tool(tool)

        desc_findings = [f for f in findings if "description" in f.title.lower()]
        assert len(desc_findings) > 0
        assert any(f.severity == Severity.HIGH for f in desc_findings)

    @pytest.mark.asyncio
    async def test_short_description(self, provider):
        tool = {"name": "test_tool", "description": "Short", "timeout": 30000}
        findings = await provider.analyze_tool(tool)

        desc_findings = [f for f in findings if "vague" in f.title.lower()]
        assert len(desc_findings) > 0

    @pytest.mark.asyncio
    async def test_missing_input_schema(self, provider):
        tool = {"name": "test_tool", "description": "A test tool", "timeout": 30000}
        findings = await provider.analyze_tool(tool)

        schema_findings = [f for f in findings if "input" in f.title.lower()]
        assert len(schema_findings) > 0

    @pytest.mark.asyncio
    async def test_dangerous_phrases_best_effort(self, provider):
        tool = {
            "name": "test_tool",
            "description": "This tool uses best effort semantics",
            "timeout": 30000,
        }
        findings = await provider.analyze_tool(tool)

        phrase_findings = [
            f for f in findings if "dangerous phrase" in f.title.lower()
        ]
        assert len(phrase_findings) > 0

    @pytest.mark.asyncio
    async def test_dangerous_phrases_ignore_error(self, provider):
        tool = {
            "name": "test_tool",
            "description": "Errors are ignored when possible",
            "timeout": 30000,
        }
        findings = await provider.analyze_tool(tool)

        phrase_findings = [
            f for f in findings if "dangerous phrase" in f.title.lower()
        ]
        assert len(phrase_findings) > 0

    @pytest.mark.asyncio
    async def test_dangerous_phrases_fire_and_forget(self, provider):
        tool = {
            "name": "test_tool",
            "description": "This is a fire and forget operation",
            "timeout": 30000,
        }
        findings = await provider.analyze_tool(tool)

        phrase_findings = [
            f for f in findings if "dangerous phrase" in f.title.lower()
        ]
        assert len(phrase_findings) > 0

    @pytest.mark.asyncio
    async def test_config_missing_server_timeout(self, provider):
        config = {
            "mcpServers": {
                "test_server": {
                    "command": "node",
                    "args": ["server.js"],
                }
            }
        }
        findings = await provider.analyze_config(config)

        timeout_findings = [
            f
            for f in findings
            if f.category == OperationalRiskCategory.MISSING_TIMEOUT_GUARD
        ]
        assert len(timeout_findings) > 0

    @pytest.mark.asyncio
    async def test_config_missing_command(self, provider):
        config = {"mcpServers": {"test_server": {"args": ["--help"]}}}
        findings = await provider.analyze_config(config)

        command_findings = [f for f in findings if "command" in f.title.lower()]
        assert len(command_findings) > 0

    @pytest.mark.asyncio
    async def test_config_sensitive_env_vars(self, provider):
        config = {
            "mcpServers": {
                "test_server": {
                    "command": "node",
                    "env": {"API_KEY": "secret123"},
                }
            }
        }
        findings = await provider.analyze_config(config)

        env_findings = [f for f in findings if "environment" in f.title.lower()]
        assert len(env_findings) > 0
