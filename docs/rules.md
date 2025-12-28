# Heuristic Rules Reference

This document describes all 20 heuristic rules (HEUR-001 through HEUR-020) used by the MCP Readiness Scanner to detect operational readiness issues in MCP tool definitions.

## Overview

The heuristic provider performs zero-dependency static analysis of tool definitions using Python. All checks are fast (<1 second) and require no external services.

### Rule Categories

- **Timeout Guards** (HEUR-001, HEUR-002): Prevent indefinite hangs
- **Retry Configuration** (HEUR-003, HEUR-004, HEUR-005): Safe retry patterns
- **Error Handling** (HEUR-006, HEUR-007, HEUR-008): Structured error responses
- **Description Quality** (HEUR-009, HEUR-010): Clear tool documentation
- **Input Validation** (HEUR-011, HEUR-012): Input contract enforcement
- **Operational Config** (HEUR-013, HEUR-014, HEUR-015): Production settings
- **Resource Management** (HEUR-016, HEUR-017): Cleanup and idempotency
- **Safety** (HEUR-018, HEUR-019, HEUR-020): Dangerous operations

---

## HEUR-001: Missing Timeout

**Severity**: HIGH  
**Category**: `missing_timeout_guard`

### Description

Tool does not specify a timeout configuration. Operations may hang indefinitely if external services become unresponsive.

### Detection

Checks for presence of any of these fields:
- `timeout`
- `timeoutMs`
- `timeout_ms`
- `timeoutSeconds`

Also checks nested `config` object.

### Example - FAIL

```json
{
  "name": "fetch_data",
  "description": "Fetches data from external API"
}
```

### Example - PASS

```json
{
  "name": "fetch_data",
  "description": "Fetches data from external API",
  "timeout": 30000
}
```

### Remediation

Add a `timeout` or `timeoutMs` field with a reasonable value (e.g., 30000 for 30 seconds). Choose timeout based on expected operation duration:
- Fast operations (< 5s): 5000ms
- Normal operations (5-30s): 30000ms
- Long operations (30s-2min): 120000ms

---

## HEUR-002: Timeout Too Long

**Severity**: MEDIUM  
**Category**: `missing_timeout_guard`

### Description

Timeout is set to more than 300,000ms (5 minutes). Long timeouts can cause extended hangs and poor user experience.

### Detection

Checks if any timeout field exceeds 300000 (5 minutes).

### Example - FAIL

```json
{
  "name": "batch_process",
  "timeout": 600000
}
```

### Example - PASS

```json
{
  "name": "batch_process",
  "timeout": 120000,
  "description": "Processes batch in 2 minutes or less"
}
```

### Remediation

Reduce timeout to 30-120 seconds. If operations truly take longer, consider:
- Breaking into smaller operations
- Implementing progress callbacks
- Using async patterns with status polling

---

## HEUR-003: No Retry Limit

**Severity**: MEDIUM  
**Category**: `unsafe_retry_loop`

### Description

Tool does not specify a retry limit. Without limits, retry logic may cause resource exhaustion or infinite loops.

### Detection

Checks for presence of any of these fields:
- `maxRetries`
- `retries`
- `max_retries`
- `retryLimit`
- `retry_limit`
- `retryPolicy.maxRetries`

### Example - FAIL

```json
{
  "name": "api_call",
  "description": "Calls external API with retry"
}
```

### Example - PASS

```json
{
  "name": "api_call",
  "description": "Calls external API with retry",
  "maxRetries": 3
}
```

### Remediation

Add a `maxRetries` field with a reasonable value:
- Network calls: 3-5 retries
- Database operations: 2-3 retries
- File operations: 1-2 retries

---

## HEUR-004: Unlimited Retries

**Severity**: HIGH  
**Category**: `unsafe_retry_loop`

### Description

Retry limit is set to -1 (unlimited) or excessively high (>10). This can cause infinite loops and resource exhaustion.

### Detection

Checks if retry fields are:
- Equal to -1 (often means unlimited)
- Greater than 10

### Example - FAIL

```json
{
  "name": "persistent_call",
  "maxRetries": -1
}
```

### Example - PASS

```json
{
  "name": "persistent_call",
  "maxRetries": 5
}
```

### Remediation

Set a finite retry limit (recommended: 3-5 retries). If persistence is required, implement:
- Circuit breaker pattern
- Exponential backoff with max attempts
- Manual retry triggers

---

## HEUR-005: No Backoff Strategy

**Severity**: LOW  
**Category**: `unsafe_retry_loop`

### Description

Tool has retry logic but no backoff strategy. Without backoff, rapid retries can overwhelm failing services.

### Detection

If retries are configured, checks for presence of:
- `backoff`
- `backoffMs`
- `exponentialBackoff`
- `backoffStrategy`
- `retryDelay`
- `retryBackoff`

### Example - FAIL

```json
{
  "name": "api_call",
  "maxRetries": 3
}
```

### Example - PASS

```json
{
  "name": "api_call",
  "maxRetries": 3,
  "backoffMs": 1000,
  "exponentialBackoff": true
}
```

### Remediation

Add exponential backoff configuration:
```json
{
  "backoffMs": 1000,
  "exponentialBackoff": true
}
```

Or linear backoff:
```json
{
  "retryDelay": 2000
}
```

---

## HEUR-006: Missing Error Schema

**Severity**: MEDIUM  
**Category**: `missing_error_schema`

### Description

Tool does not define an error response schema. Without structured error responses, agents cannot programmatically handle failures.

### Detection

Checks for presence of:
- `errorSchema`
- `error_schema`
- `errors`
- `errorResponse`

### Example - FAIL

```json
{
  "name": "create_user",
  "description": "Creates a new user"
}
```

### Example - PASS

```json
{
  "name": "create_user",
  "description": "Creates a new user",
  "errorSchema": {
    "type": "object",
    "properties": {
      "code": { "type": "string" },
      "message": { "type": "string" }
    }
  }
}
```

### Remediation

Define a structured error schema with at minimum:
- Error code (for programmatic handling)
- Error message (for human readability)
- Optional: details, context, stack trace

---

## HEUR-007: Error Schema Missing Code Field

**Severity**: LOW  
**Category**: `missing_error_schema`

### Description

Error schema exists but doesn't include a 'code' or 'errorCode' property. Error codes are essential for programmatic error handling.

### Detection

If `errorSchema` exists, checks if properties include:
- `code`
- `errorCode`

### Example - FAIL

```json
{
  "errorSchema": {
    "type": "object",
    "properties": {
      "message": { "type": "string" }
    }
  }
}
```

### Example - PASS

```json
{
  "errorSchema": {
    "type": "object",
    "properties": {
      "code": { 
        "type": "string",
        "enum": ["VALIDATION_ERROR", "NOT_FOUND", "INTERNAL_ERROR"]
      },
      "message": { "type": "string" }
    }
  }
}
```

### Remediation

Add a `code` property to error schema, preferably with enum of possible error codes.

---

## HEUR-008: No Output Schema

**Severity**: LOW  
**Category**: `missing_error_schema`

### Description

Tool does not define an output schema. Agents cannot reliably parse responses without knowing the expected structure.

### Detection

Checks for presence of:
- `outputSchema`
- `output_schema`
- `responseSchema`
- `response_schema`

### Example - FAIL

```json
{
  "name": "get_user",
  "description": "Retrieves user information"
}
```

### Example - PASS

```json
{
  "name": "get_user",
  "description": "Retrieves user information",
  "outputSchema": {
    "type": "object",
    "properties": {
      "id": { "type": "string" },
      "name": { "type": "string" },
      "email": { "type": "string" }
    }
  }
}
```

### Remediation

Define an `outputSchema` using JSON Schema describing the structure of successful responses.

---

## HEUR-009: Vague Description

**Severity**: MEDIUM  
**Category**: `overloaded_tool_scope`

### Description

Tool description is missing, too short (<20 characters), or contains only generic words. Agents rely on descriptions to understand tool capabilities.

### Detection

Checks for:
- Missing description
- Length < 20 characters
- Contains only generic words (tool, utility, helper, function, method)

### Example - FAIL

```json
{
  "name": "process_data",
  "description": "Tool"
}
```

### Example - PASS

```json
{
  "name": "process_data",
  "description": "Processes customer data by validating fields, enriching with external data sources, and formatting for downstream systems. Returns processed records with validation status."
}
```

### Remediation

Write a clear, detailed description (50-200 characters) that explains:
- What the tool does
- What inputs it expects
- What outputs it produces
- Any important constraints or side effects

---

## HEUR-010: Too Many Capabilities

**Severity**: HIGH  
**Category**: `overloaded_tool_scope`

### Description

Tool description mentions too many action verbs (>5) or scope-overload keywords ("any", "all", "everything"). Tools with many capabilities are harder to test, secure, and maintain.

### Detection

Checks for:
- Overload keywords: "any", "all", "everything", "anything", "whatever"
- More than 5 action verbs from a predefined list

### Example - FAIL

```json
{
  "name": "data_tool",
  "description": "Can create, read, update, delete, search, filter, sort, validate, transform, export, import, and process any data"
}
```

### Example - PASS

```json
{
  "name": "user_fetcher",
  "description": "Retrieves user information by ID or email from the user database"
}
```

### Remediation

Split into multiple focused tools, each with a specific, well-defined purpose. Follow Single Responsibility Principle.

---

## HEUR-011: No Required Fields

**Severity**: LOW  
**Category**: `silent_failure_path`

### Description

Input schema exists with properties but doesn't specify which fields are required. This may lead to missing input errors at runtime.

### Detection

If `inputSchema.properties` exists, checks for presence of `inputSchema.required` array.

### Example - FAIL

```json
{
  "inputSchema": {
    "type": "object",
    "properties": {
      "userId": { "type": "string" },
      "action": { "type": "string" }
    }
  }
}
```

### Example - PASS

```json
{
  "inputSchema": {
    "type": "object",
    "properties": {
      "userId": { "type": "string" },
      "action": { "type": "string" }
    },
    "required": ["userId"]
  }
}
```

### Remediation

Add a `required` array listing mandatory input fields.

---

## HEUR-012: No Input Validation Hints

**Severity**: INFO  
**Category**: `silent_failure_path`

### Description

Input schema properties lack validation constraints (pattern, minLength, enum, etc.). This may allow invalid inputs.

### Detection

If `inputSchema.properties` exists, checks if properties have validation keywords:
- `pattern`
- `minLength` / `maxLength`
- `minimum` / `maximum`
- `enum`
- `format`
- `minItems` / `maxItems`

Flags if >50% of properties lack validation.

### Example - FAIL

```json
{
  "inputSchema": {
    "properties": {
      "email": { "type": "string" },
      "age": { "type": "integer" }
    }
  }
}
```

### Example - PASS

```json
{
  "inputSchema": {
    "properties": {
      "email": { 
        "type": "string",
        "format": "email",
        "pattern": "^[^@]+@[^@]+\\.[^@]+$"
      },
      "age": { 
        "type": "integer",
        "minimum": 0,
        "maximum": 150
      }
    }
  }
}
```

### Remediation

Add validation constraints to input properties appropriate to their types.

---

## HEUR-013: No Rate Limit

**Severity**: LOW  
**Category**: `unsafe_retry_loop`

### Description

Tool does not specify rate limits. Without rate limits, rapid repeated calls may overwhelm external services or exhaust resources.

### Detection

Checks for presence of:
- `rateLimit`
- `rate_limit`
- `rateLimitPerMinute`
- `throttle`
- `maxCallsPerSecond`

### Example - FAIL

```json
{
  "name": "send_notification",
  "description": "Sends push notification to user"
}
```

### Example - PASS

```json
{
  "name": "send_notification",
  "description": "Sends push notification to user",
  "rateLimit": {
    "maxCallsPerSecond": 10,
    "maxCallsPerMinute": 100
  }
}
```

### Remediation

Add rate limit configuration specifying maximum calls per time period.

---

## HEUR-014: No Version

**Severity**: LOW  
**Category**: `no_observability_hooks`

### Description

Tool does not specify a version. Versioning helps track changes and ensure compatibility when tools evolve over time.

### Detection

Checks for presence of:
- `version`
- `apiVersion`
- `api_version`
- `schemaVersion`

### Example - FAIL

```json
{
  "name": "calculate",
  "description": "Performs calculation"
}
```

### Example - PASS

```json
{
  "name": "calculate",
  "description": "Performs calculation",
  "version": "1.2.0"
}
```

### Remediation

Add a `version` field following semantic versioning (MAJOR.MINOR.PATCH).

---

## HEUR-015: No Observability Config

**Severity**: LOW  
**Category**: `no_observability_hooks`

### Description

Tool does not configure observability hooks (logging, metrics, tracing). Without observability, debugging production issues becomes extremely difficult.

### Detection

Checks for presence of:
- `observability`
- `logging`
- `metrics`
- `telemetry`
- `tracing`
- `monitoring`
- `instrumentation`
- `logger`

### Example - FAIL

```json
{
  "name": "process_order",
  "description": "Processes customer order"
}
```

### Example - PASS

```json
{
  "name": "process_order",
  "description": "Processes customer order",
  "observability": {
    "logging": {
      "level": "info",
      "includeRequestId": true
    },
    "metrics": {
      "counters": ["orders_processed", "orders_failed"],
      "histograms": ["order_processing_duration"]
    }
  }
}
```

### Remediation

Add logging, metrics, or tracing configuration to enable monitoring and debugging in production.

---

## HEUR-016: Resource Cleanup Not Documented

**Severity**: MEDIUM  
**Category**: `silent_failure_path`

### Description

Tool description mentions resources (connections, files, etc.) but doesn't document cleanup procedures. Resource leaks can cause production instability.

### Detection

Checks if description mentions resource indicators:
- connection, file, stream, socket, handle, session, lock, transaction, database, network

But doesn't mention cleanup indicators:
- close, cleanup, release, dispose, free, disconnect

### Example - FAIL

```json
{
  "description": "Opens a database connection and executes query"
}
```

### Example - PASS

```json
{
  "description": "Opens a database connection, executes query, and automatically closes the connection. Resources are cleaned up even on error."
}
```

### Remediation

Document how resources are cleaned up. Ensure proper cleanup in error paths and add timeout-based cleanup.

---

## HEUR-017: No Idempotency Indication

**Severity**: INFO  
**Category**: `non_deterministic_response`

### Description

Tool appears to perform state-changing operations but doesn't indicate whether it's idempotent. This is important for retry logic.

### Detection

If description contains state-changing verbs (create, delete, update, etc.), checks for idempotency indicators:
- idempotent, safe to retry, can be retried, idempotency

### Example - FAIL

```json
{
  "description": "Creates a new user account"
}
```

### Example - PASS

```json
{
  "description": "Creates a new user account. Idempotent - calling with the same email will return existing user."
}
```

Or:

```json
{
  "description": "Creates a new user account",
  "idempotent": false,
  "idempotencyKey": "requestId"
}
```

### Remediation

Document whether the operation is idempotent and safe to retry. If not idempotent, consider adding idempotency keys.

---

## HEUR-018: Dangerous Operation Keywords

**Severity**: HIGH  
**Category**: `overloaded_tool_scope`

### Description

Tool name or description contains dangerous operation keywords (delete, drop, truncate, exec, eval). Tools performing destructive operations require extra safeguards.

### Detection

Checks for keywords:
- delete, drop, truncate, exec, eval, rm, remove, destroy, purge, wipe

### Example - FAIL

```json
{
  "name": "delete_all_data",
  "description": "Deletes all data from the system"
}
```

### Example - PASS

```json
{
  "name": "delete_user",
  "description": "Deletes a single user by ID with confirmation. Requires admin role and audit logging. Soft delete with 30-day recovery period.",
  "requiresConfirmation": true,
  "auditLog": true
}
```

### Remediation

Add safeguards:
- Require explicit confirmation
- Implement dry-run mode
- Add audit logging
- Provide undo/rollback mechanisms
- Use soft deletes with recovery periods

---

## HEUR-019: No Authentication Context

**Severity**: INFO  
**Category**: `silent_failure_path`

### Description

Tool appears to interact with external services but does not document authentication requirements. This may lead to authorization failures at runtime.

### Detection

If description mentions external indicators (api, service, endpoint, etc.) but doesn't have auth fields:
- `auth`, `authentication`, `credentials`, `apiKey`, `token`

### Example - FAIL

```json
{
  "description": "Calls external API to retrieve data"
}
```

### Example - PASS

```json
{
  "description": "Calls external API to retrieve data. Requires API_KEY environment variable.",
  "auth": {
    "type": "apiKey",
    "location": "env",
    "name": "API_KEY"
  }
}
```

### Remediation

Document authentication requirements explicitly.

---

## HEUR-020: Circular Dependency Risk

**Severity**: MEDIUM  
**Category**: `unsafe_retry_loop`

### Description

Tool references itself or contains patterns suggesting circular dependencies. Self-referencing tools can cause infinite loops in agent workflows.

### Detection

Checks if:
- Tool name appears in its own description
- Description contains circular patterns: "calls itself", "recursive", "loop", "repeat until"

### Example - FAIL

```json
{
  "name": "process_recursively",
  "description": "Processes data recursively by calling process_recursively on nested items"
}
```

### Example - PASS

```json
{
  "name": "process_nested",
  "description": "Processes nested data up to maximum depth of 10 levels. Returns error if depth exceeded.",
  "maxRecursionDepth": 10
}
```

### Remediation

- Avoid self-referencing tools
- If recursion is necessary, implement depth limits and termination conditions
- Add maximum iteration counts
- Document termination conditions clearly

---

## Score Impact

Each rule deducts points from the readiness score based on severity:

- **CRITICAL**: -25 points
- **HIGH**: -15 points
- **MEDIUM**: -8 points
- **LOW**: -3 points
- **INFO**: -1 point

Starting score is 100. Minimum score is 0.

## Ignoring Rules

To ignore specific rules, use the `--ignore-rule` flag:

```bash
mcp-readiness scan-tool --tool my_tool.json --ignore-rule HEUR-013 --ignore-rule HEUR-014
```

Or in GitHub Action:

```yaml
- uses: nik-kale/mcp-readiness-scanner@v1
  with:
    tool: my_tool.json
    ignore-rules: 'HEUR-013,HEUR-014'
```

