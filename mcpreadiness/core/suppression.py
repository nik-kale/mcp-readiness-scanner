"""
Rule suppression logic for MCP Readiness Scanner.

Handles suppression of findings based on:
- Inline suppression in tool definitions
- CLI flags
- .mcp-readiness-ignore files
"""

from pathlib import Path
from typing import Any

from mcpreadiness.core.models import Finding


class SuppressionManager:
    """Manages rule suppression from multiple sources."""

    def __init__(
        self,
        cli_ignore_rules: list[str] | None = None,
        ignore_file_path: Path | str | None = None,
    ) -> None:
        """
        Initialize suppression manager.

        Args:
            cli_ignore_rules: Rules to ignore from CLI flags
            ignore_file_path: Path to .mcp-readiness-ignore file
        """
        self.cli_ignore_rules = set(cli_ignore_rules or [])
        self.ignore_file_rules: set[str] = set()

        if ignore_file_path:
            self._load_ignore_file(Path(ignore_file_path))

    def _load_ignore_file(self, path: Path) -> None:
        """
        Load rules from .mcp-readiness-ignore file.

        Format: One rule ID per line, comments start with #
        """
        if not path.exists():
            return

        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue
                self.ignore_file_rules.add(line)

    def is_suppressed(
        self,
        finding: Finding,
        tool_definition: dict[str, Any] | None = None,
    ) -> bool:
        """
        Check if a finding should be suppressed.

        Args:
            finding: The finding to check
            tool_definition: Optional tool definition with inline suppression

        Returns:
            True if the finding should be suppressed
        """
        # Check CLI flags
        if finding.rule_id and finding.rule_id in self.cli_ignore_rules:
            return True

        # Check ignore file
        if finding.rule_id and finding.rule_id in self.ignore_file_rules:
            return True

        # Check inline suppression in tool definition
        if tool_definition:
            inline_ignore = tool_definition.get("mcp-readiness-ignore", [])
            if finding.rule_id and finding.rule_id in inline_ignore:
                return True

        return False

    def filter_findings(
        self,
        findings: list[Finding],
        tool_definition: dict[str, Any] | None = None,
    ) -> tuple[list[Finding], list[Finding]]:
        """
        Filter findings into active and suppressed.

        Args:
            findings: List of findings to filter
            tool_definition: Optional tool definition with inline suppression

        Returns:
            Tuple of (active_findings, suppressed_findings)
        """
        active = []
        suppressed = []

        for finding in findings:
            if self.is_suppressed(finding, tool_definition):
                suppressed.append(finding)
            else:
                active.append(finding)

        return active, suppressed

    def get_all_suppressed_rules(self) -> set[str]:
        """Get all suppressed rule IDs from all sources."""
        return self.cli_ignore_rules | self.ignore_file_rules

