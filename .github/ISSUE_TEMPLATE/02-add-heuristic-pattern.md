---
name: 🔍 Add Heuristic Pattern
about: Add a new detection pattern to the heuristic provider (Good First Issue)
title: '[HEURISTIC] Add pattern for '
labels: ['enhancement', 'good-first-issue', 'heuristic-provider']
assignees: ''
---

## 🔍 New Heuristic Pattern

### Pattern Description
<!-- What operational readiness issue should this pattern detect? -->


### Example Tool Definition
<!-- Provide an example MCP tool definition that should trigger this pattern -->

```json
{
  "name": "example_tool",
  "description": "...",
  // Add your example here
}
```

### Expected Finding
<!-- What should the scanner report when it detects this pattern? -->

**Severity:**
- [ ] Critical
- [ ] High
- [ ] Medium
- [ ] Low
- [ ] Info

**Category:**
<!-- Which operational risk category does this belong to? -->
- [ ] `missing_timeout_guard`
- [ ] `unsafe_retry_loop`
- [ ] `silent_failure_path`
- [ ] `non_deterministic_response`
- [ ] `no_observability_hooks`
- [ ] `overloaded_tool_scope`
- [ ] `no_fallback_contract`
- [ ] `missing_error_schema`
- [ ] Other (specify):

**Finding Message:**
<!-- What message should be shown to users? -->


### Implementation Guidance

**Files to modify:**
- `mcpreadiness/providers/heuristic_provider.py` - Add detection logic
- `tests/test_providers/test_heuristic.py` - Add test cases

**Pattern to follow:**
Look at existing patterns in `heuristic_provider.py` for examples:
- `_check_missing_timeout()`
- `_check_overloaded_scope()`
- `_check_silent_failures()`

---

### For Contributors

This is a **good first issue**! Here's how to get started:

1. **Setup your environment:**
   ```bash
   git clone https://github.com/mcp-readiness/scanner
   cd scanner
   pip install -e ".[dev]"
   ```

2. **Add your pattern:**
   - Edit `mcpreadiness/providers/heuristic_provider.py`
   - Add a new `_check_*()` method
   - Call it from the `scan()` method

3. **Add tests:**
   - Edit `tests/test_providers/test_heuristic.py`
   - Add test cases for both positive and negative matches

4. **Test your changes:**
   ```bash
   pytest tests/test_providers/test_heuristic.py -v
   ruff check mcpreadiness tests
   ```

5. **Submit a PR:**
   - Reference this issue in your PR
   - Include test output showing your pattern works

**Need help?** Comment on this issue and the maintainers will guide you!
