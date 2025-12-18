---
name: 🧪 Add Test Coverage
about: Add or improve test coverage for existing code (Good First Issue)
title: '[TEST] Add tests for '
labels: ['testing', 'good-first-issue']
assignees: ''
---

## 🧪 Add Test Coverage

### Module/Function to Test
<!-- Which file or function needs more test coverage? -->

**File:** `mcpreadiness/`
**Function/Class:**

### Current Coverage Gap
<!-- What scenarios are not currently tested? -->

- [ ] Happy path (basic functionality)
- [ ] Edge cases
- [ ] Error handling
- [ ] Invalid inputs
- [ ] Async behavior
- [ ] Configuration options
- [ ] Other:

### Test Scenarios Needed
<!-- List specific test cases that should be added -->

1.
2.
3.

### Expected Behavior
<!-- What should happen in each test scenario? -->


---

### For Contributors

This is a **good first issue**! Here's how to get started:

1. **Setup your environment:**
   ```bash
   git clone https://github.com/mcp-readiness/scanner
   cd scanner
   pip install -e ".[dev]"
   ```

2. **Check current coverage:**
   ```bash
   pytest tests/ --cov=mcpreadiness --cov-report=term-missing
   ```

3. **Add your tests:**
   - Create or edit test files in `tests/`
   - Follow existing test patterns using `pytest`
   - For async functions, use `@pytest.mark.asyncio`

4. **Run your tests:**
   ```bash
   pytest tests/test_your_file.py -v
   pytest --cov=mcpreadiness --cov-report=html
   ```

5. **Submit a PR:**
   - Reference this issue in your PR
   - Include coverage report showing improvement

**Testing Tips:**
- Look at existing test files for patterns to follow
- Use `pytest.raises()` for testing exceptions
- Use `pytest.mark.parametrize()` for multiple test cases
- Keep tests simple and focused on one thing

**Need help?** Comment on this issue and the maintainers will assist you!
