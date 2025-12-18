---
name: 📝 Add Example
about: Add a new example tool definition or use case (Good First Issue)
title: '[EXAMPLE] Add example for '
labels: ['documentation', 'good-first-issue', 'examples']
assignees: ''
---

## 📝 Add Example

### Example Type
<!-- What kind of example would you like to add? -->

- [ ] Good tool definition (production-ready example)
- [ ] Bad tool definition (anti-pattern example)
- [ ] Real-world use case
- [ ] Integration example
- [ ] Configuration example
- [ ] Other:

### Use Case
<!-- What scenario or pattern does this example demonstrate? -->


### Example Description
<!-- Describe what this example will show -->


### Key Learning Points
<!-- What should users learn from this example? -->

1.
2.
3.

### Proposed File Location
<!-- Where should this example be added? -->

- Directory: `examples/`
- Filename:

---

### For Contributors

This is a **good first issue**! Here's how to get started:

1. **Setup your environment:**
   ```bash
   git clone https://github.com/mcp-readiness/scanner
   cd scanner
   pip install -e ".[dev]"
   ```

2. **Create your example:**
   - Add a new JSON file in `examples/sample_tool_definitions/`
   - Or add a new example in `examples/use_cases/`
   - Follow the MCP tool definition schema

3. **Test your example:**
   ```bash
   # For tool definitions:
   mcp-readiness scan-tool --tool examples/your_example.json --format markdown

   # Verify it produces expected findings
   ```

4. **Document your example:**
   - Add a comment header explaining the purpose
   - If it's in a subdirectory, update the README
   - Explain what makes it a good/bad example

5. **Submit a PR:**
   - Reference this issue in your PR
   - Include scan output showing the example works

**Example Template:**
```json
{
  "name": "example_tool",
  "description": "Clear description of what this tool does",
  "inputSchema": {
    "type": "object",
    "properties": {
      // Define parameters
    },
    "required": []
  },
  "timeout": 30000,
  // Add other relevant fields
}
```

**Need help?** Comment on this issue and the maintainers will guide you!
