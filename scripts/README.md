# Demo Generation Scripts

This directory contains scripts for generating animated demonstrations of the MCP Readiness Scanner.

## Available Scripts

### 1. `generate_demo.sh` - GIF Generator (Recommended)

Generates a high-quality animated GIF demonstration.

**Requirements:**
- `asciinema` - Terminal session recorder
- `agg` - Asciinema GIF generator
- `mcp-readiness` - The scanner tool

**Installation:**

```bash
# macOS
brew install asciinema
cargo install agg

# Ubuntu/Debian
sudo apt-get install asciinema
cargo install agg

# Python (asciinema only)
pip install asciinema
cargo install agg  # agg requires Rust/Cargo
```

**Usage:**

```bash
./scripts/generate_demo.sh
```

**Output:** `demos/mcp-readiness-demo.gif`

### 2. `generate_demo_svg.sh` - SVG Generator (Alternative)

Generates an animated SVG demonstration. SVG files are resolution-independent and can be easily embedded in web pages.

**Requirements:**
- `termtosvg` - Terminal to SVG recorder
- `mcp-readiness` - The scanner tool

**Installation:**

```bash
pip install termtosvg
```

**Usage:**

```bash
./scripts/generate_demo_svg.sh
```

**Output:** `demos/mcp-readiness-demo.svg`

## Demo Content

Both scripts demonstrate:

1. **Scanning a poorly designed tool** - Shows the scanner identifying multiple issues in a tool with:
   - Missing timeout guards
   - Silent failure paths
   - Overloaded capabilities
   - No error schema

2. **Scanning a production-ready tool** - Shows a well-designed tool that passes all checks

3. **Listing available providers** - Shows the inspection providers available (Heuristic, YARA, OPA, LLM)

## Customization

You can customize the demo by editing the scripts:

- **Demo speed**: Adjust `DEMO_SPEED` in `generate_demo.sh` (default: 1.5x)
- **Terminal size**: Modify `DEMO_WIDTH` and `DEMO_HEIGHT` variables
- **Content**: Edit the demo script section to show different commands or examples
- **Theme**: Change the `--theme` parameter in the `agg` command

## Troubleshooting

### "Command not found" errors

Make sure all dependencies are installed:

```bash
# Check if tools are available
which asciinema
which agg
which termtosvg
which mcp-readiness
```

### mcp-readiness not found

Install the scanner from the repository:

```bash
pip install -e .
```

Or from PyPI:

```bash
pip install mcp-readiness-scanner
```

### Permission denied

Make the scripts executable:

```bash
chmod +x scripts/generate_demo.sh
chmod +x scripts/generate_demo_svg.sh
```

## Adding Demo to README

Once generated, add the demo to your README:

```markdown
## Demo

![MCP Readiness Scanner Demo](demos/mcp-readiness-demo.gif)

<!-- or for SVG -->
![MCP Readiness Scanner Demo](demos/mcp-readiness-demo.svg)
```

## Notes

- The GIF generator (`generate_demo.sh`) produces higher quality output but requires more dependencies
- The SVG generator (`generate_demo_svg.sh`) is easier to install but may have limited theme support
- Both scripts automatically create the `demos/` directory if it doesn't exist
- Generated files are not committed to the repository by default (check `.gitignore`)
