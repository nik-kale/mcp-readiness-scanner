"""
SARIF Report Generator for MCP Readiness Scanner.

Produces SARIF 2.1.0 output for GitHub Code Scanning integration
and other SARIF-compatible tools.

SARIF Specification: https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html
"""

import json
from typing import Any

from mcpreadiness import __version__
from mcpreadiness.core.models import Finding, ScanResult, Severity
from mcpreadiness.core.taxonomy import CATEGORY_DESCRIPTIONS, OperationalRiskCategory


# SARIF severity levels
SARIF_LEVELS = {
    Severity.CRITICAL: "error",
    Severity.HIGH: "error",
    Severity.MEDIUM: "warning",
    Severity.LOW: "note",
    Severity.INFO: "none",
}

# SARIF security severity for GitHub
SARIF_SECURITY_SEVERITY = {
    Severity.CRITICAL: "critical",
    Severity.HIGH: "high",
    Severity.MEDIUM: "medium",
    Severity.LOW: "low",
    Severity.INFO: "low",
}


def render_sarif(result: ScanResult) -> str:
    """
    Render a scan result as SARIF 2.1.0 JSON.

    Args:
        result: The scan result to render

    Returns:
        SARIF JSON string
    """
    sarif = _build_sarif(result)
    return json.dumps(sarif, indent=2)


def _build_sarif(result: ScanResult) -> dict[str, Any]:
    """Build the SARIF document structure."""
    return {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/sarif-2.1/schema/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [_build_run(result)],
    }


def _build_run(result: ScanResult) -> dict[str, Any]:
    """Build a SARIF run object."""
    return {
        "tool": _build_tool(),
        "results": [_build_result(f, i) for i, f in enumerate(result.findings)],
        "invocations": [
            {
                "executionSuccessful": True,
                "endTimeUtc": result.timestamp.isoformat() + "Z",
            }
        ],
        "properties": {
            "readinessScore": result.readiness_score,
            "isProductionReady": result.is_production_ready,
            "target": result.target,
            "providersUsed": result.providers_used,
        },
    }


def _build_tool() -> dict[str, Any]:
    """Build the SARIF tool object."""
    return {
        "driver": {
            "name": "mcp-readiness-scanner",
            "version": __version__,
            "informationUri": "https://github.com/mcp-readiness/scanner",
            "rules": _build_rules(),
            "properties": {
                "tags": ["mcp", "operational-readiness", "agentic-ai"],
            },
        }
    }


def _build_rules() -> list[dict[str, Any]]:
    """Build SARIF rule definitions from taxonomy."""
    rules = []

    for category in OperationalRiskCategory:
        desc = CATEGORY_DESCRIPTIONS.get(category, {})
        default_severity = desc.get("default_severity", Severity.MEDIUM)

        rule = {
            "id": category.value,
            "name": desc.get("name", category.value),
            "shortDescription": {
                "text": desc.get("short_description", "Operational readiness issue")
            },
            "fullDescription": {
                "text": desc.get("long_description", "").strip()[:1000]
            },
            "helpUri": f"https://github.com/mcp-readiness/scanner/blob/main/docs/taxonomy.md#{category.value}",
            "help": {
                "text": desc.get("remediation", "Review the finding and address the issue.").strip(),
                "markdown": desc.get("remediation", "Review the finding and address the issue.").strip(),
            },
            "defaultConfiguration": {
                "level": SARIF_LEVELS.get(default_severity, "warning"),
            },
            "properties": {
                "tags": ["operational-readiness", category.value],
                "security-severity": SARIF_SECURITY_SEVERITY.get(default_severity, "medium"),
            },
        }
        rules.append(rule)

    return rules


def _build_result(finding: Finding, index: int) -> dict[str, Any]:
    """Build a SARIF result object from a finding."""
    result: dict[str, Any] = {
        "ruleId": finding.category.value,
        "ruleIndex": list(OperationalRiskCategory).index(finding.category),
        "level": SARIF_LEVELS.get(finding.severity, "warning"),
        "message": {
            "text": f"{finding.title}: {finding.description}",
        },
        "locations": [],
        "properties": {
            "provider": finding.provider,
            "severity": finding.severity.value,
        },
    }

    # Add rule ID if present
    if finding.rule_id:
        result["properties"]["ruleId"] = finding.rule_id

    # Add location if present
    if finding.location:
        location = {
            "physicalLocation": {
                "artifactLocation": {
                    "uri": finding.location,
                    "uriBaseId": "%SRCROOT%",
                },
            },
            "logicalLocations": [
                {
                    "name": finding.location,
                    "kind": "object",
                }
            ],
        }
        result["locations"].append(location)

    # Add evidence as properties
    if finding.evidence:
        result["properties"]["evidence"] = finding.evidence

    # Add remediation as fix suggestion
    if finding.remediation:
        result["fixes"] = [
            {
                "description": {
                    "text": finding.remediation,
                },
            }
        ]

    return result


def render_sarif_summary(result: ScanResult) -> dict[str, Any]:
    """
    Generate a SARIF summary without full results.

    Useful for quick status in CI without full details.
    """
    return {
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "mcp-readiness-scanner",
                        "version": __version__,
                    }
                },
                "results": [],
                "properties": {
                    "readinessScore": result.readiness_score,
                    "isProductionReady": result.is_production_ready,
                    "findingsCount": len(result.findings),
                    "findingsBySeverity": result.finding_counts_by_severity,
                },
            }
        ],
    }
