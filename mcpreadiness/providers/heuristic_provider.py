"""
Heuristic Provider - Zero-dependency operational readiness checks.

This is the highest priority provider as it requires no external
dependencies. It performs static analysis of tool definitions and
configurations using Python heuristics.

Implements 20 core heuristic rules (HEUR-001 through HEUR-020) as specified
in the MVP requirements.
"""

import re
from typing import Any

from mcpreadiness.core.models import Finding, OperationalRiskCategory, Severity
from mcpreadiness.providers.base import InspectionProvider


class HeuristicProvider(InspectionProvider):
    """
    Heuristic-based inspection provider.

    Performs zero-dependency operational readiness checks on tool
    definitions and configurations. Implements 20 core heuristic rules:

    Timeout Guards (HEUR-001, HEUR-002):
    - Missing timeout configuration
    - Timeout values too long (>5 minutes)

    Retry Configuration (HEUR-003, HEUR-004, HEUR-005):
    - No retry limit defined
    - Unlimited or excessive retries
    - Missing backoff strategy

    Error Handling (HEUR-006, HEUR-007, HEUR-008):
    - Missing error schema
    - Error schema without error code field
    - Missing output schema

    Description Quality (HEUR-009, HEUR-010):
    - Vague or missing descriptions
    - Overloaded tool scope indicators

    Input Validation (HEUR-011, HEUR-012):
    - No required fields defined
    - Missing input validation hints

    Operational Config (HEUR-013, HEUR-014, HEUR-015):
    - No rate limiting
    - Missing version information
    - No observability configuration

    Resource Management (HEUR-016, HEUR-017):
    - Resource cleanup not documented
    - No idempotency indication

    Safety (HEUR-018, HEUR-019, HEUR-020):
    - Dangerous operation keywords
    - No authentication context
    - Circular dependency risk
    """

    def __init__(
        self,
        max_capabilities: int = 10,
        min_description_length: int = 20,
    ) -> None:
        """
        Initialize the heuristic provider.

        Args:
            max_capabilities: Maximum allowed capabilities before warning
            min_description_length: Minimum description length before warning
        """
        self.max_capabilities = max_capabilities
        self.min_description_length = min_description_length

    @property
    def name(self) -> str:
        return "heuristic"

    @property
    def description(self) -> str:
        return (
            "Zero-dependency heuristic checks for timeout, retry, "
            "scope, error handling, and description quality (20 core rules)"
        )

    async def analyze_tool(self, tool_definition: dict[str, Any]) -> list[Finding]:
        """
        Analyze a tool definition for operational readiness issues.

        Runs all 20 heuristic rules against the tool definition.

        Args:
            tool_definition: Dictionary containing the tool definition

        Returns:
            List of findings from all applicable rules
        """
        findings: list[Finding] = []
        tool_name = tool_definition.get("name", "unknown")

        # Timeout Guards
        findings.extend(self._check_missing_timeout(tool_definition, tool_name))
        findings.extend(self._check_timeout_too_long(tool_definition, tool_name))

        # Retry Configuration
        findings.extend(self._check_no_retry_limit(tool_definition, tool_name))
        findings.extend(self._check_unlimited_retries(tool_definition, tool_name))
        findings.extend(self._check_no_backoff_strategy(tool_definition, tool_name))

        # Error Handling
        findings.extend(self._check_missing_error_schema(tool_definition, tool_name))
        findings.extend(self._check_error_schema_missing_code(tool_definition, tool_name))
        findings.extend(self._check_no_output_schema(tool_definition, tool_name))

        # Description Quality
        findings.extend(self._check_vague_description(tool_definition, tool_name))
        findings.extend(self._check_too_many_capabilities(tool_definition, tool_name))

        # Input Validation
        findings.extend(self._check_no_required_fields(tool_definition, tool_name))
        findings.extend(self._check_no_input_validation_hints(tool_definition, tool_name))

        # Operational Config
        findings.extend(self._check_no_rate_limit(tool_definition, tool_name))
        findings.extend(self._check_no_version(tool_definition, tool_name))
        findings.extend(self._check_no_observability(tool_definition, tool_name))

        # Resource Management
        findings.extend(self._check_resource_cleanup_not_documented(tool_definition, tool_name))
        findings.extend(self._check_no_idempotency_indication(tool_definition, tool_name))

        # Safety
        findings.extend(self._check_dangerous_operation_keywords(tool_definition, tool_name))
        findings.extend(self._check_no_authentication_context(tool_definition, tool_name))
        findings.extend(self._check_circular_dependency_risk(tool_definition, tool_name))

        return findings

    async def analyze_config(self, config: dict[str, Any]) -> list[Finding]:
        """
        Analyze an MCP configuration for operational readiness issues.

        Checks performed:
        - Server-level timeout configurations
        - Environment variable security (warnings for sensitive patterns)
        - Missing server configurations
        """
        findings: list[Finding] = []

        mcp_servers = config.get("mcpServers", {})

        if not mcp_servers:
            findings.append(
                Finding(
                    category=OperationalRiskCategory.SILENT_FAILURE_PATH,
                    severity=Severity.INFO,
                    title="No MCP servers configured",
                    description="Configuration file contains no MCP server definitions",
                    location="mcpServers",
                    provider=self.name,
                    rule_id="HEUR-CFG-001",
                )
            )
            return findings

        for server_name, server_config in mcp_servers.items():
            findings.extend(self._check_server_config(server_name, server_config))

        return findings

    # ===================================================================
    # HEUR-001: Missing timeout (HIGH)
    # ===================================================================
    def _check_missing_timeout(
        self, tool_def: dict[str, Any], tool_name: str
    ) -> list[Finding]:
        """
        HEUR-001: Check for missing timeout configuration.

        Timeout fields checked: timeout, timeoutMs, timeout_ms, timeoutSeconds
        """
        findings: list[Finding] = []

        timeout_fields = ["timeout", "timeoutMs", "timeout_ms", "timeoutSeconds"]
        has_timeout = any(field in tool_def for field in timeout_fields)

        # Also check nested config
        config = tool_def.get("config", {})
        has_timeout = has_timeout or any(field in config for field in timeout_fields)

        if not has_timeout:
            findings.append(
                Finding(
                    category=OperationalRiskCategory.MISSING_TIMEOUT_GUARD,
                    severity=Severity.HIGH,
                    title="No timeout configuration",
                    description=(
                        f"Tool '{tool_name}' does not specify a timeout. "
                        "Operations may hang indefinitely if external services "
                        "become unresponsive."
                    ),
                    location=f"tool.{tool_name}",
                    provider=self.name,
                    remediation=(
                        "Add a 'timeout' or 'timeoutMs' field with a reasonable "
                        "value (e.g., 30000 for 30 seconds)"
                    ),
                    rule_id="HEUR-001",
                )
            )

        return findings

    # ===================================================================
    # HEUR-002: Timeout too long (MEDIUM)
    # ===================================================================
    def _check_timeout_too_long(
        self, tool_def: dict[str, Any], tool_name: str
    ) -> list[Finding]:
        """
        HEUR-002: Check if timeout is greater than 300000ms (5 minutes).
        """
        findings: list[Finding] = []

        timeout_fields = ["timeout", "timeoutMs", "timeout_ms"]
        config = tool_def.get("config", {})

        for field in timeout_fields:
            timeout_value = tool_def.get(field) or config.get(field)
            if timeout_value is not None and timeout_value > 300000:
                findings.append(
                    Finding(
                        category=OperationalRiskCategory.MISSING_TIMEOUT_GUARD,
                        severity=Severity.MEDIUM,
                        title="Timeout too long",
                        description=(
                            f"Tool '{tool_name}' has {field}={timeout_value}ms "
                            "(over 5 minutes). Long timeouts can cause extended hangs "
                            "and poor user experience."
                        ),
                        location=f"tool.{tool_name}.{field}",
                        evidence={"field": field, "value": timeout_value},
                        provider=self.name,
                        remediation="Consider reducing timeout to 30-60 seconds for better responsiveness",
                        rule_id="HEUR-002",
                    )
                )

        return findings

    # ===================================================================
    # HEUR-003: No retry limit (MEDIUM)
    # ===================================================================
    def _check_no_retry_limit(
        self, tool_def: dict[str, Any], tool_name: str
    ) -> list[Finding]:
        """
        HEUR-003: Check for missing retry limit configuration.
        """
        findings: list[Finding] = []

        retry_fields = [
            "maxRetries", "retries", "max_retries", "retryCount", 
            "retryLimit", "retry_limit"
        ]
        has_retries = any(field in tool_def for field in retry_fields)

        config = tool_def.get("config", {})
        has_retries = has_retries or any(field in config for field in retry_fields)
        
        # Also check for retryPolicy object
        retry_policy = tool_def.get("retryPolicy") or config.get("retryPolicy")
        if retry_policy and isinstance(retry_policy, dict):
            has_retries = has_retries or any(field in retry_policy for field in retry_fields)

        if not has_retries:
            findings.append(
                Finding(
                    category=OperationalRiskCategory.UNSAFE_RETRY_LOOP,
                    severity=Severity.MEDIUM,
                    title="No retry limit configured",
                    description=(
                        f"Tool '{tool_name}' does not specify a retry limit. "
                        "Without limits, retry logic may cause resource exhaustion "
                        "or infinite loops."
                    ),
                    location=f"tool.{tool_name}",
                    provider=self.name,
                    remediation=(
                        "Add a 'maxRetries' or 'retryLimit' field with a "
                        "reasonable value (e.g., 3)"
                    ),
                    rule_id="HEUR-003",
                )
            )

        return findings

    # ===================================================================
    # HEUR-004: Unlimited retries (HIGH)
    # ===================================================================
    def _check_unlimited_retries(
        self, tool_def: dict[str, Any], tool_name: str
    ) -> list[Finding]:
        """
        HEUR-004: Check for unlimited retries (maxRetries == -1 or > 10).
        """
        findings: list[Finding] = []

        retry_fields = ["maxRetries", "retries", "max_retries", "retryLimit"]
        config = tool_def.get("config", {})
        retry_policy = tool_def.get("retryPolicy") or config.get("retryPolicy") or {}

        for field in retry_fields:
            retry_value = (
                tool_def.get(field) 
                or config.get(field) 
                or (retry_policy.get(field) if isinstance(retry_policy, dict) else None)
            )
            
            if retry_value is not None:
                if retry_value == -1:
                    findings.append(
                        Finding(
                            category=OperationalRiskCategory.UNSAFE_RETRY_LOOP,
                            severity=Severity.HIGH,
                            title="Unlimited retries configured",
                            description=(
                                f"Tool '{tool_name}' has {field}=-1, indicating unlimited retries. "
                                "This can cause infinite loops and resource exhaustion."
                            ),
                            location=f"tool.{tool_name}.{field}",
                            evidence={"field": field, "value": retry_value},
                            provider=self.name,
                            remediation="Set a finite retry limit (recommended: 3-5 retries)",
                            rule_id="HEUR-004",
                        )
                    )
                elif retry_value > 10:
                    findings.append(
                        Finding(
                            category=OperationalRiskCategory.UNSAFE_RETRY_LOOP,
                            severity=Severity.HIGH,
                            title="Excessive retry limit",
                            description=(
                                f"Tool '{tool_name}' has {field}={retry_value}. "
                                "Very high retry limits may cause extended delays during outages."
                            ),
                            location=f"tool.{tool_name}.{field}",
                            evidence={"field": field, "value": retry_value},
                            provider=self.name,
                            remediation="Consider reducing retry limit to 3-5",
                            rule_id="HEUR-004",
                        )
                    )

        return findings

    # ===================================================================
    # HEUR-005: No backoff strategy (LOW)
    # ===================================================================
    def _check_no_backoff_strategy(
        self, tool_def: dict[str, Any], tool_name: str
    ) -> list[Finding]:
        """
        HEUR-005: Check for missing backoff strategy when retries are configured.
        """
        findings: list[Finding] = []

        # First check if retries are configured
        retry_fields = ["maxRetries", "retries", "max_retries", "retryLimit"]
        config = tool_def.get("config", {})
        retry_policy = tool_def.get("retryPolicy") or config.get("retryPolicy") or {}
        
        has_retries = any(
            (tool_def.get(field) or config.get(field) or 
             (retry_policy.get(field) if isinstance(retry_policy, dict) else None))
            for field in retry_fields
        )

        if has_retries:
            # Check for backoff configuration
            backoff_fields = [
                "backoff", "backoffMs", "exponentialBackoff", "backoffStrategy",
                "retryDelay", "retryBackoff"
            ]
            has_backoff = any(field in tool_def for field in backoff_fields)
            has_backoff = has_backoff or any(field in config for field in backoff_fields)
            has_backoff = has_backoff or (
                isinstance(retry_policy, dict) and 
                any(field in retry_policy for field in backoff_fields)
            )

            if not has_backoff:
                findings.append(
                    Finding(
                        category=OperationalRiskCategory.UNSAFE_RETRY_LOOP,
                        severity=Severity.LOW,
                        title="No backoff strategy for retries",
                        description=(
                            f"Tool '{tool_name}' has retry logic but no backoff strategy. "
                            "Without backoff, rapid retries can overwhelm failing services."
                        ),
                        location=f"tool.{tool_name}",
                        provider=self.name,
                        remediation=(
                            "Add exponential backoff configuration (e.g., backoffMs, "
                            "exponentialBackoff) to avoid thundering herd problems"
                        ),
                        rule_id="HEUR-005",
                    )
                )

        return findings

    # ===================================================================
    # HEUR-006: Missing error schema (MEDIUM)
    # ===================================================================
    def _check_missing_error_schema(
        self, tool_def: dict[str, Any], tool_name: str
    ) -> list[Finding]:
        """
        HEUR-006: Check for missing error response schema.
        """
        findings: list[Finding] = []

        error_schema_fields = ["errorSchema", "error_schema", "errors", "errorResponse"]
        has_error_schema = any(field in tool_def for field in error_schema_fields)

        if not has_error_schema:
            findings.append(
                Finding(
                    category=OperationalRiskCategory.MISSING_ERROR_SCHEMA,
                    severity=Severity.MEDIUM,
                    title="No error response schema",
                    description=(
                        f"Tool '{tool_name}' does not define an error response schema. "
                        "Without structured error responses, agents cannot "
                        "programmatically handle failures."
                    ),
                    location=f"tool.{tool_name}",
                    provider=self.name,
                    remediation=(
                        "Add an 'errorSchema' field defining the structure of "
                        "error responses with error codes and messages"
                    ),
                    rule_id="HEUR-006",
                )
            )

        return findings

    # ===================================================================
    # HEUR-007: Error schema missing code field (LOW)
    # ===================================================================
    def _check_error_schema_missing_code(
        self, tool_def: dict[str, Any], tool_name: str
    ) -> list[Finding]:
        """
        HEUR-007: Check if error schema exists but lacks a 'code' property.
        """
        findings: list[Finding] = []

        error_schema_fields = ["errorSchema", "error_schema", "errors", "errorResponse"]
        
        for field in error_schema_fields:
            error_schema = tool_def.get(field)
            if error_schema and isinstance(error_schema, dict):
                properties = error_schema.get("properties", {})
                if "code" not in properties and "errorCode" not in properties:
                    findings.append(
                        Finding(
                            category=OperationalRiskCategory.MISSING_ERROR_SCHEMA,
                            severity=Severity.LOW,
                            title="Error schema missing error code field",
                            description=(
                                f"Tool '{tool_name}' has an error schema but it doesn't "
                                "include a 'code' or 'errorCode' property. Error codes are "
                                "essential for programmatic error handling."
                            ),
                            location=f"tool.{tool_name}.{field}.properties",
                            provider=self.name,
                            remediation="Add a 'code' property to the error schema (e.g., string enum of error codes)",
                            rule_id="HEUR-007",
                        )
                    )
                break  # Only check the first error schema found

        return findings

    # ===================================================================
    # HEUR-008: No output schema (LOW)
    # ===================================================================
    def _check_no_output_schema(
        self, tool_def: dict[str, Any], tool_name: str
    ) -> list[Finding]:
        """
        HEUR-008: Check for missing output/response schema.
        """
        findings: list[Finding] = []

        output_schema_fields = ["outputSchema", "output_schema", "responseSchema", "response_schema"]
        has_output_schema = any(field in tool_def for field in output_schema_fields)

        if not has_output_schema:
            findings.append(
                Finding(
                    category=OperationalRiskCategory.MISSING_ERROR_SCHEMA,
                    severity=Severity.LOW,
                    title="No output schema defined",
                    description=(
                        f"Tool '{tool_name}' does not define an output schema. "
                        "Agents cannot reliably parse responses without knowing "
                        "the expected structure."
                    ),
                    location=f"tool.{tool_name}",
                    provider=self.name,
                    remediation="Add an 'outputSchema' field defining the structure of successful responses",
                    rule_id="HEUR-008",
                )
            )

        return findings

    # ===================================================================
    # HEUR-009: Vague description (MEDIUM)
    # ===================================================================
    def _check_vague_description(
        self, tool_def: dict[str, Any], tool_name: str
    ) -> list[Finding]:
        """
        HEUR-009: Check if description is missing or too short (<20 chars)
        or contains only generic words.
        """
        findings: list[Finding] = []

        description = tool_def.get("description", "")

        if not description:
            findings.append(
                Finding(
                    category=OperationalRiskCategory.OVERLOADED_TOOL_SCOPE,
                    severity=Severity.MEDIUM,
                    title="Missing description",
                    description=(
                        f"Tool '{tool_name}' has no description. "
                        "Agents rely on descriptions to understand tool capabilities "
                        "and select the appropriate tool for tasks."
                    ),
                    location=f"tool.{tool_name}.description",
                    provider=self.name,
                    remediation="Add a clear, detailed description explaining what the tool does",
                    rule_id="HEUR-009",
                )
            )
        elif len(description) < 20:
            findings.append(
                Finding(
                    category=OperationalRiskCategory.OVERLOADED_TOOL_SCOPE,
                    severity=Severity.MEDIUM,
                    title="Vague description",
                    description=(
                        f"Tool '{tool_name}' has a very short description "
                        f"({len(description)} characters, minimum 20 recommended). "
                        "Brief descriptions may not provide enough context for agents."
                    ),
                    location=f"tool.{tool_name}.description",
                    evidence={"length": len(description), "minimum": 20},
                    provider=self.name,
                    remediation="Expand the description to explain the tool's purpose, inputs, and expected outputs",
                    rule_id="HEUR-009",
                )
            )
        else:
            # Check for generic-only words
            generic_words = ["tool", "utility", "helper", "function", "method"]
            words = description.lower().split()
            non_generic_words = [w for w in words if w not in generic_words]
            
            if len(non_generic_words) < 3:
                findings.append(
                    Finding(
                        category=OperationalRiskCategory.OVERLOADED_TOOL_SCOPE,
                        severity=Severity.MEDIUM,
                        title="Generic description",
                        description=(
                            f"Tool '{tool_name}' description contains only generic words. "
                            "Add specific details about what the tool does."
                        ),
                        location=f"tool.{tool_name}.description",
                        provider=self.name,
                        remediation="Replace generic terms with specific details about functionality",
                        rule_id="HEUR-009",
                    )
                )

        return findings

    # ===================================================================
    # HEUR-010: Too many capabilities (HIGH)
    # ===================================================================
    def _check_too_many_capabilities(
        self, tool_def: dict[str, Any], tool_name: str
    ) -> list[Finding]:
        """
        HEUR-010: Check if description mentions >5 verbs or words like
        "any", "all", "everything".
        """
        findings: list[Finding] = []

        description = tool_def.get("description", "").lower()

        # Check for overload keywords
        overload_keywords = ["any", "all", "everything", "anything", "whatever"]
        found_overload_keywords = [kw for kw in overload_keywords if kw in description]

        if found_overload_keywords:
            findings.append(
                Finding(
                    category=OperationalRiskCategory.OVERLOADED_TOOL_SCOPE,
                    severity=Severity.HIGH,
                    title="Overloaded tool scope indicated",
                    description=(
                        f"Tool '{tool_name}' description contains scope-overload keywords: "
                        f"{', '.join(found_overload_keywords)}. Tools that do 'everything' "
                        "are difficult to test, maintain, and use reliably."
                    ),
                    location=f"tool.{tool_name}.description",
                    evidence={"keywords": found_overload_keywords},
                    provider=self.name,
                    remediation=(
                        "Split into multiple focused tools, each with a specific, "
                        "well-defined purpose"
                    ),
                    rule_id="HEUR-010",
                )
            )

        # Check for too many action verbs
        action_verbs = [
            "create", "read", "write", "update", "delete", "get", "set",
            "fetch", "send", "post", "put", "patch", "remove", "add",
            "list", "find", "search", "query", "execute", "run", "start",
            "stop", "restart", "pause", "resume", "cancel", "retry"
        ]
        
        found_verbs = [verb for verb in action_verbs if verb in description]
        
        if len(found_verbs) > 5:
            findings.append(
                Finding(
                    category=OperationalRiskCategory.OVERLOADED_TOOL_SCOPE,
                    severity=Severity.HIGH,
                    title="Too many capabilities",
                    description=(
                        f"Tool '{tool_name}' description mentions {len(found_verbs)} action verbs "
                        f"(found: {', '.join(found_verbs[:5])}...). Tools with many capabilities "
                        "are harder to test, secure, and maintain."
                    ),
                    location=f"tool.{tool_name}.description",
                    evidence={"verb_count": len(found_verbs), "verbs": found_verbs},
                    provider=self.name,
                    remediation="Consider splitting into multiple focused tools with specific responsibilities",
                    rule_id="HEUR-010",
                )
            )

        return findings

    # ===================================================================
    # HEUR-011: No required fields (LOW)
    # ===================================================================
    def _check_no_required_fields(
        self, tool_def: dict[str, Any], tool_name: str
    ) -> list[Finding]:
        """
        HEUR-011: Check if inputSchema exists but no 'required' array is defined.
        """
        findings: list[Finding] = []

        input_schema = tool_def.get("inputSchema")

        if input_schema and isinstance(input_schema, dict):
            properties = input_schema.get("properties", {})
            required = input_schema.get("required", [])
            
            # Only flag if there are properties but no required fields
            if properties and not required:
                findings.append(
                    Finding(
                        category=OperationalRiskCategory.SILENT_FAILURE_PATH,
                        severity=Severity.LOW,
                        title="No required fields specified",
                        description=(
                            f"Tool '{tool_name}' has an input schema with {len(properties)} properties "
                            "but doesn't specify which fields are required. This may lead to "
                            "missing input errors at runtime."
                        ),
                        location=f"tool.{tool_name}.inputSchema.required",
                        evidence={"property_count": len(properties)},
                        provider=self.name,
                        remediation="Add a 'required' array listing mandatory input fields",
                        rule_id="HEUR-011",
                    )
                )

        return findings

    # ===================================================================
    # HEUR-012: No input validation hints (INFO)
    # ===================================================================
    def _check_no_input_validation_hints(
        self, tool_def: dict[str, Any], tool_name: str
    ) -> list[Finding]:
        """
        HEUR-012: Check if inputSchema properties lack validation keywords
        like 'pattern', 'minLength', 'enum', 'minimum', 'maximum', etc.
        """
        findings: list[Finding] = []

        input_schema = tool_def.get("inputSchema")

        if input_schema and isinstance(input_schema, dict):
            properties = input_schema.get("properties", {})
            
            if properties:
                validation_keywords = [
                    "pattern", "minLength", "maxLength", "minimum", "maximum",
                    "enum", "format", "minItems", "maxItems"
                ]
                
                properties_without_validation = []
                for prop_name, prop_def in properties.items():
                    if isinstance(prop_def, dict):
                        has_validation = any(kw in prop_def for kw in validation_keywords)
                        if not has_validation:
                            properties_without_validation.append(prop_name)
                
                if properties_without_validation and len(properties_without_validation) >= len(properties) * 0.5:
                    findings.append(
                        Finding(
                            category=OperationalRiskCategory.SILENT_FAILURE_PATH,
                            severity=Severity.INFO,
                            title="Missing input validation hints",
                            description=(
                                f"Tool '{tool_name}' input schema has {len(properties_without_validation)} "
                                f"properties (out of {len(properties)}) without validation constraints "
                                "(pattern, minLength, enum, etc.). This may allow invalid inputs."
                            ),
                            location=f"tool.{tool_name}.inputSchema.properties",
                            evidence={
                                "properties_without_validation": properties_without_validation[:5],
                                "total_properties": len(properties)
                            },
                            provider=self.name,
                            remediation=(
                                "Add validation constraints to input properties (e.g., pattern for strings, "
                                "minimum/maximum for numbers, enum for limited choices)"
                            ),
                            rule_id="HEUR-012",
                        )
                    )

        return findings

    # ===================================================================
    # HEUR-013: No rate limit (LOW)
    # ===================================================================
    def _check_no_rate_limit(
        self, tool_def: dict[str, Any], tool_name: str
    ) -> list[Finding]:
        """
        HEUR-013: Check for missing rate limit configuration.
        """
        findings: list[Finding] = []

        rate_limit_fields = [
            "rateLimit", "rate_limit", "rateLimitPerMinute", 
            "throttle", "maxCallsPerSecond"
        ]
        has_rate_limit = any(field in tool_def for field in rate_limit_fields)

        config = tool_def.get("config", {})
        has_rate_limit = has_rate_limit or any(field in config for field in rate_limit_fields)

        if not has_rate_limit:
            findings.append(
                Finding(
                    category=OperationalRiskCategory.UNSAFE_RETRY_LOOP,
                    severity=Severity.LOW,
                    title="No rate limit configuration",
                    description=(
                        f"Tool '{tool_name}' does not specify rate limits. "
                        "Without rate limits, rapid repeated calls may overwhelm "
                        "external services or exhaust resources."
                    ),
                    location=f"tool.{tool_name}",
                    provider=self.name,
                    remediation="Add a 'rateLimit' field specifying maximum calls per time period",
                    rule_id="HEUR-013",
                )
            )

        return findings

    # ===================================================================
    # HEUR-014: No version (LOW)
    # ===================================================================
    def _check_no_version(
        self, tool_def: dict[str, Any], tool_name: str
    ) -> list[Finding]:
        """
        HEUR-014: Check for missing version information.
        """
        findings: list[Finding] = []

        version_fields = ["version", "apiVersion", "api_version", "schemaVersion"]
        has_version = any(field in tool_def for field in version_fields)

        if not has_version:
            findings.append(
                Finding(
                    category=OperationalRiskCategory.NO_OBSERVABILITY_HOOKS,
                    severity=Severity.LOW,
                    title="No version information",
                    description=(
                        f"Tool '{tool_name}' does not specify a version. "
                        "Versioning helps track changes and ensure compatibility "
                        "when tools evolve over time."
                    ),
                    location=f"tool.{tool_name}",
                    provider=self.name,
                    remediation="Add a 'version' field (e.g., '1.0.0') following semantic versioning",
                    rule_id="HEUR-014",
                )
            )

        return findings

    # ===================================================================
    # HEUR-015: No observability config (LOW)
    # ===================================================================
    def _check_no_observability(
        self, tool_def: dict[str, Any], tool_name: str
    ) -> list[Finding]:
        """
        HEUR-015: Check for missing observability/monitoring configuration.
        """
        findings: list[Finding] = []

        observability_fields = [
            "observability", "logging", "metrics", "telemetry", "tracing",
            "monitoring", "instrumentation", "logger"
        ]
        has_observability = any(field in tool_def for field in observability_fields)

        config = tool_def.get("config", {})
        has_observability = has_observability or any(
            field in config for field in observability_fields
        )

        if not has_observability:
            findings.append(
                Finding(
                    category=OperationalRiskCategory.NO_OBSERVABILITY_HOOKS,
                    severity=Severity.LOW,
                    title="No observability configuration",
                    description=(
                        f"Tool '{tool_name}' does not configure observability hooks "
                        "(logging, metrics, tracing). Without observability, "
                        "debugging production issues becomes extremely difficult."
                    ),
                    location=f"tool.{tool_name}",
                    provider=self.name,
                    remediation=(
                        "Add logging, metrics, or tracing configuration to enable "
                        "monitoring and debugging in production"
                    ),
                    rule_id="HEUR-015",
                )
            )

        return findings

    # ===================================================================
    # HEUR-016: Resource cleanup not documented (MEDIUM)
    # ===================================================================
    def _check_resource_cleanup_not_documented(
        self, tool_def: dict[str, Any], tool_name: str
    ) -> list[Finding]:
        """
        HEUR-016: Check if description mentions resources but not cleanup.
        """
        findings: list[Finding] = []

        description = tool_def.get("description", "").lower()

        # Check if tool appears to use resources that need cleanup
        resource_indicators = [
            "connection", "file", "stream", "socket", "handle",
            "session", "lock", "transaction", "database", "network"
        ]
        uses_resources = any(indicator in description for indicator in resource_indicators)

        if uses_resources:
            # Check if cleanup is documented
            cleanup_indicators = ["close", "cleanup", "release", "dispose", "free", "disconnect"]
            has_cleanup_doc = any(indicator in description for indicator in cleanup_indicators)

            if not has_cleanup_doc:
                found_resources = [ind for ind in resource_indicators if ind in description]
                findings.append(
                    Finding(
                        category=OperationalRiskCategory.SILENT_FAILURE_PATH,
                        severity=Severity.MEDIUM,
                        title="Resource cleanup not documented",
                        description=(
                            f"Tool '{tool_name}' appears to use resources ({', '.join(found_resources[:3])}) "
                            "but doesn't document cleanup procedures. "
                            "Resource leaks can cause production instability."
                        ),
                        location=f"tool.{tool_name}.description",
                        evidence={"resources": found_resources},
                        provider=self.name,
                        remediation=(
                            "Document how resources are cleaned up (e.g., 'connections are automatically "
                            "closed', 'call cleanup() to release resources')"
                        ),
                        rule_id="HEUR-016",
                    )
                )

        return findings

    # ===================================================================
    # HEUR-017: No idempotency indication (INFO)
    # ===================================================================
    def _check_no_idempotency_indication(
        self, tool_def: dict[str, Any], tool_name: str
    ) -> list[Finding]:
        """
        HEUR-017: Check if tool appears to modify state but doesn't
        document idempotency.
        """
        findings: list[Finding] = []

        description = tool_def.get("description", "").lower()

        # Check if tool appears to be state-changing
        state_changing_verbs = [
            "create", "delete", "update", "modify", "remove", "insert",
            "write", "post", "put", "patch", "drop", "truncate"
        ]
        is_state_changing = any(verb in description for verb in state_changing_verbs)

        if is_state_changing:
            # Check if idempotency is documented
            idempotency_indicators = [
                "idempotent", "safe to retry", "can be retried", 
                "idempotency", "duplicate", "repeat"
            ]
            has_idempotency_doc = any(indicator in description for indicator in idempotency_indicators)

            if not has_idempotency_doc:
                findings.append(
                    Finding(
                        category=OperationalRiskCategory.NON_DETERMINISTIC_RESPONSE,
                        severity=Severity.INFO,
                        title="No idempotency indication",
                        description=(
                            f"Tool '{tool_name}' appears to perform state-changing operations "
                            "but doesn't indicate whether it's idempotent. This is important "
                            "for retry logic - non-idempotent operations may cause duplicates."
                        ),
                        location=f"tool.{tool_name}.description",
                        provider=self.name,
                        remediation=(
                            "Document whether the operation is idempotent and safe to retry. "
                            "If not idempotent, consider adding idempotency keys or documenting this clearly."
                        ),
                        rule_id="HEUR-017",
                    )
                )

        return findings

    # ===================================================================
    # HEUR-018: Dangerous operation keywords (HIGH)
    # ===================================================================
    def _check_dangerous_operation_keywords(
        self, tool_def: dict[str, Any], tool_name: str
    ) -> list[Finding]:
        """
        HEUR-018: Check for dangerous keywords in name/description like
        'delete', 'drop', 'truncate', 'exec', 'eval'.
        """
        findings: list[Finding] = []

        name = tool_def.get("name", "").lower()
        description = tool_def.get("description", "").lower()
        combined = f"{name} {description}"

        dangerous_keywords = [
            ("delete", "deletion operations"),
            ("drop", "drop/destroy operations"),
            ("truncate", "truncate operations"),
            ("exec", "code execution"),
            ("eval", "code evaluation"),
            ("rm ", "file removal"),
            ("remove", "removal operations"),
            ("destroy", "destruction operations"),
            ("purge", "purge operations"),
            ("wipe", "wipe operations"),
        ]

        found_dangerous = []
        for keyword, meaning in dangerous_keywords:
            if keyword in combined:
                found_dangerous.append((keyword, meaning))

        if found_dangerous:
            findings.append(
                Finding(
                    category=OperationalRiskCategory.OVERLOADED_TOOL_SCOPE,
                    severity=Severity.HIGH,
                    title="Dangerous operation keywords detected",
                    description=(
                        f"Tool '{tool_name}' contains dangerous operation keywords: "
                        f"{', '.join(k for k, _ in found_dangerous)}. "
                        "Tools performing destructive operations require extra safeguards."
                    ),
                    location=f"tool.{tool_name}",
                    evidence={"keywords": [k for k, m in found_dangerous]},
                    provider=self.name,
                    remediation=(
                        "Add safeguards: require explicit confirmation, implement dry-run mode, "
                        "add audit logging, or provide undo/rollback mechanisms"
                    ),
                    rule_id="HEUR-018",
                )
            )

        return findings

    # ===================================================================
    # HEUR-019: No authentication context (INFO)
    # ===================================================================
    def _check_no_authentication_context(
        self, tool_def: dict[str, Any], tool_name: str
    ) -> list[Finding]:
        """
        HEUR-019: Check if tool accesses external resources but has no
        authentication configuration documented.
        """
        findings: list[Finding] = []

        auth_fields = ["auth", "authentication", "credentials", "apiKey", "api_key", "token"]
        has_auth = any(field in tool_def for field in auth_fields)

        config = tool_def.get("config", {})
        has_auth = has_auth or any(field in config for field in auth_fields)

        # Check if description mentions external services
        description = tool_def.get("description", "").lower()
        external_indicators = [
            "api", "service", "endpoint", "http", "rest", "request",
            "external", "remote", "third-party", "cloud", "server"
        ]
        mentions_external = any(indicator in description for indicator in external_indicators)

        if mentions_external and not has_auth:
            findings.append(
                Finding(
                    category=OperationalRiskCategory.SILENT_FAILURE_PATH,
                    severity=Severity.INFO,
                    title="No authentication context documented",
                    description=(
                        f"Tool '{tool_name}' appears to interact with external services "
                        "but does not document authentication requirements. This may lead "
                        "to authorization failures at runtime."
                    ),
                    location=f"tool.{tool_name}",
                    provider=self.name,
                    remediation=(
                        "Document authentication requirements (e.g., 'requires API_KEY environment variable', "
                        "'auth' field, or credential configuration)"
                    ),
                    rule_id="HEUR-019",
                )
            )

        return findings

    # ===================================================================
    # HEUR-020: Circular dependency risk (MEDIUM)
    # ===================================================================
    def _check_circular_dependency_risk(
        self, tool_def: dict[str, Any], tool_name: str
    ) -> list[Finding]:
        """
        HEUR-020: Check if tool references itself or common circular patterns.
        """
        findings: list[Finding] = []

        description = tool_def.get("description", "").lower()
        
        # Check if tool name appears in its own description (potential self-reference)
        if tool_name and tool_name.lower() in description:
            findings.append(
                Finding(
                    category=OperationalRiskCategory.UNSAFE_RETRY_LOOP,
                    severity=Severity.MEDIUM,
                    title="Potential circular dependency",
                    description=(
                        f"Tool '{tool_name}' references itself in its description. "
                        "Self-referencing tools can cause infinite loops in agent workflows."
                    ),
                    location=f"tool.{tool_name}.description",
                    provider=self.name,
                    remediation=(
                        "Ensure the tool does not call itself recursively. "
                        "If recursive calls are necessary, implement depth limits and termination conditions."
                    ),
                    rule_id="HEUR-020",
                )
            )
        
        # Check for circular dependency patterns
        circular_patterns = [
            ("calls itself", "self-referencing"),
            ("recursive", "recursion"),
            ("loop", "looping behavior"),
            ("repeat until", "unbounded repetition"),
        ]
        
        for pattern, meaning in circular_patterns:
            if pattern in description:
                findings.append(
                    Finding(
                        category=OperationalRiskCategory.UNSAFE_RETRY_LOOP,
                        severity=Severity.MEDIUM,
                        title="Circular dependency risk pattern detected",
                        description=(
                            f"Tool '{tool_name}' description mentions {meaning}. "
                            "Ensure proper termination conditions to avoid infinite loops."
                        ),
                        location=f"tool.{tool_name}.description",
                        evidence={"pattern": pattern, "meaning": meaning},
                        provider=self.name,
                        remediation=(
                            "Add explicit termination conditions, maximum iteration counts, "
                            "or depth limits to prevent infinite loops"
                        ),
                        rule_id="HEUR-020",
                    )
                )
                break  # Only report once

        return findings

    # ===================================================================
    # Config Checking (Server-level)
    # ===================================================================
    def _check_server_config(
        self, server_name: str, server_config: dict[str, Any]
    ) -> list[Finding]:
        """Check server-level configuration."""
        findings: list[Finding] = []

        # Check for missing command
        if "command" not in server_config:
            findings.append(
                Finding(
                    category=OperationalRiskCategory.SILENT_FAILURE_PATH,
                    severity=Severity.HIGH,
                    title="Missing server command",
                    description=(
                        f"Server '{server_name}' does not specify a command. "
                        "The server cannot be started without a command."
                    ),
                    location=f"mcpServers.{server_name}.command",
                    provider=self.name,
                    rule_id="HEUR-CFG-002",
                )
            )

        # Check for env vars that might contain secrets
        env_vars = server_config.get("env", {})
        sensitive_patterns = ["key", "secret", "token", "password", "credential"]
        for env_name in env_vars:
            if any(p in env_name.lower() for p in sensitive_patterns):
                findings.append(
                    Finding(
                        category=OperationalRiskCategory.NO_OBSERVABILITY_HOOKS,
                        severity=Severity.INFO,
                        title="Sensitive environment variable",
                        description=(
                            f"Server '{server_name}' has environment variable "
                            f"'{env_name}' that may contain sensitive data. "
                            "Ensure this is not logged or exposed."
                        ),
                        location=f"mcpServers.{server_name}.env.{env_name}",
                        provider=self.name,
                        rule_id="HEUR-CFG-003",
                    )
                )

        # Check for timeout at server level
        if "timeout" not in server_config:
            findings.append(
                Finding(
                    category=OperationalRiskCategory.MISSING_TIMEOUT_GUARD,
                    severity=Severity.MEDIUM,
                    title="No server timeout",
                    description=(
                        f"Server '{server_name}' does not specify a timeout. "
                        "Server initialization may hang indefinitely."
                    ),
                    location=f"mcpServers.{server_name}",
                    provider=self.name,
                    remediation="Add a 'timeout' field for server initialization",
                    rule_id="HEUR-CFG-004",
                )
            )

        return findings
