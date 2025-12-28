# MCP Readiness Scanner - GitHub Action

[![GitHub Action](https://img.shields.io/badge/GitHub-Action-blue?logo=github-actions)](https://github.com/marketplace/actions/mcp-readiness-scan)

Production readiness scanner for MCP (Model Context Protocol) tools - detect operational issues before they reach production.

## Usage

### Quick Start

Add this one-liner to any workflow to scan your MCP tools:

```yaml
- uses: nik-kale/mcp-readiness-scanner@v1
  with:
    tool: 'tools/my_tool.json'
```

Results automatically appear in your **Security** → **Code scanning** tab! 🎉

### Full Example

```yaml
name: MCP Readiness Check

on: [push, pull_request]

jobs:
  scan:
    runs-on: ubuntu-latest
    permissions:
      security-events: write  # Required for SARIF upload
      contents: read
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Scan MCP Tool
        uses: nik-kale/mcp-readiness-scanner@v1
        with:
          tool: tools/my_tool.json
          min-score: 70
          fail-on: high
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `tool` | Path to single tool definition JSON file | No* | - |
| `config` | Path to MCP configuration file | No* | - |
| `tools` | Glob pattern for multiple tools | No* | - |
| `format` | Output format (`json`, `markdown`, `sarif`, `html`) | No | `sarif` |
| `min-score` | Minimum readiness score (0-100) to pass | No | `70` |
| `fail-on` | Fail on severity: `critical`, `high`, `medium`, `low`, `none` | No | `high` |
| `ignore-rules` | Comma-separated rule IDs to ignore (e.g., `HEUR-001,HEUR-003`) | No | - |
| `upload-sarif` | Upload results to GitHub Security tab | No | `true` |
| `output-file` | Path for output file | No | `mcp-readiness-results.sarif` |
| `providers` | Comma-separated providers to use | No | all available |
| `python-version` | Python version | No | `3.11` |

\* One of `tool`, `config`, or `tools` must be specified.

## Outputs

| Output | Description |
|--------|-------------|
| `score` | Readiness score (0-100) |
| `production-ready` | Whether tool is production ready (`true`/`false`) |
| `findings-count` | Number of findings detected |
| `sarif-file` | Path to generated SARIF file |
| `grade` | Readiness grade (`Excellent`/`Good`/`Acceptable`/`Poor`/`Critical`) |

## Examples

### Scan Single Tool

```yaml
- uses: nik-kale/mcp-readiness-scanner@v1
  with:
    tool: tools/my_tool.json
    min-score: 80
```

### Scan MCP Configuration

```yaml
- uses: nik-kale/mcp-readiness-scanner@v1
  with:
    config: .mcp/config.json
```

### Custom Format (Markdown)

```yaml
- uses: nik-kale/mcp-readiness-scanner@v1
  with:
    tool: tools/my_tool.json
    format: markdown
    output-file: results.md
    upload-sarif: false

- uses: actions/upload-artifact@v4
  with:
    name: scan-results
    path: results.md
```

### Ignore Specific Rules

```yaml
- uses: nik-kale/mcp-readiness-scanner@v1
  with:
    tool: tools/my_tool.json
    ignore-rules: 'HEUR-013,HEUR-014'  # Ignore rate limit and version warnings
```

### Use Outputs in Workflow

```yaml
- name: Scan Tool
  id: scan
  uses: nik-kale/mcp-readiness-scanner@v1
  with:
    tool: tools/my_tool.json

- name: Comment on PR
  if: github.event_name == 'pull_request'
  uses: actions/github-script@v7
  with:
    script: |
      github.rest.issues.createComment({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        body: `## MCP Readiness Scan Results
        
        📊 **Score:** ${{ steps.scan.outputs.score }}/100 (${{ steps.scan.outputs.grade }})
        🔍 **Findings:** ${{ steps.scan.outputs.findings-count }}
        ✅ **Production Ready:** ${{ steps.scan.outputs.production-ready }}`
      })
```

### Scan on Specific Paths

```yaml
on:
  push:
    paths:
      - 'tools/**/*.json'
      - '.mcp/config.json'
```

### Matrix Strategy (Multiple Tools)

```yaml
jobs:
  scan:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        tool:
          - tools/tool1.json
          - tools/tool2.json
          - tools/tool3.json
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: nik-kale/mcp-readiness-scanner@v1
        with:
          tool: ${{ matrix.tool }}
          min-score: 75
```

## What Gets Checked?

The scanner runs **20 heuristic rules** covering:

- ⏱️ **Timeout Guards**: Missing or excessive timeouts
- 🔄 **Retry Configuration**: Unsafe retry patterns, missing backoff
- ❌ **Error Handling**: Missing error/output schemas
- 📝 **Description Quality**: Vague or overloaded tool descriptions
- ✅ **Input Validation**: Missing required fields, validation hints
- ⚙️ **Operational Config**: Rate limits, versioning, observability
- 🧹 **Resource Management**: Cleanup documentation, idempotency
- ⚠️ **Safety**: Dangerous operations, authentication, circular dependencies

## Scoring

- **90-100**: Excellent ✨ - Production ready
- **80-89**: Good ✅ - Minor improvements recommended
- **70-79**: Acceptable ⚠️ - Address issues before production
- **50-69**: Poor ⚠️ - Significant issues detected
- **0-49**: Critical ❌ - Not recommended for production

## Security Tab Integration

When `upload-sarif: true` (default), results automatically appear in:

**Repository** → **Security** → **Code scanning**

This provides:
- 📊 Visual finding summaries
- 🔍 Inline annotations on code
- 📈 Historical trend tracking
- 🚨 PR check status

## Requirements

- **Permissions**: `security-events: write` for SARIF upload
- **Python**: 3.11+ (automatically installed)
- **GitHub**: Any plan (free tier supported)

## Complementary Tools

MCP Readiness Scanner focuses on **operational readiness**. For security scanning, use:

- [Cisco MCP Scanner](https://github.com/cisco-open/mcp-scanner) - Security vulnerability detection

## License

Apache-2.0

## Support

- 📖 [Documentation](https://github.com/nik-kale/mcp-readiness-scanner/tree/main/docs)
- 🐛 [Report Issues](https://github.com/nik-kale/mcp-readiness-scanner/issues)
- 💬 [Discussions](https://github.com/nik-kale/mcp-readiness-scanner/discussions)

