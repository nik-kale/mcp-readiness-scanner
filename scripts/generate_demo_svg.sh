#!/usr/bin/env bash
set -euo pipefail

###############################################################################
# MCP Readiness Scanner - Demo SVG Generator
#
# This script generates an animated SVG demonstration of the MCP readiness
# scanner. This is an alternative to generate_demo.sh that produces SVG
# instead of GIF format, which may be more convenient for some users.
#
# Requirements:
#   - termtosvg (pip install termtosvg)
#   - mcp-readiness-scanner installed
#
# Usage:
#   ./scripts/generate_demo_svg.sh
#
# Output:
#   demos/mcp-readiness-demo.svg
###############################################################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DEMOS_DIR="$PROJECT_ROOT/demos"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

check_dependencies() {
    log_info "Checking dependencies..."

    if ! command -v termtosvg &> /dev/null; then
        log_error "termtosvg is not installed"
        echo ""
        echo "Installation:"
        echo "  pip install termtosvg"
        echo ""
        return 1
    fi

    if ! command -v mcp-readiness &> /dev/null; then
        log_error "mcp-readiness is not installed"
        echo ""
        echo "Installation:"
        echo "  pip install -e .  # From repo"
        echo "  pip install mcp-readiness-scanner  # From PyPI"
        echo ""
        return 1
    fi

    log_success "All dependencies are installed"
}

main() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║       MCP Readiness Scanner - Demo SVG Generator                ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo ""

    if ! check_dependencies; then
        exit 1
    fi

    mkdir -p "$DEMOS_DIR"

    local output_file="$DEMOS_DIR/mcp-readiness-demo.svg"

    log_info "Recording demo session..."

    cd "$PROJECT_ROOT"

    # Create demo script
    cat > "$DEMOS_DIR/temp_demo.sh" << 'DEMO'
#!/usr/bin/env bash
clear
echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║           MCP Readiness Scanner - Demo                          ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
sleep 1

echo "Scanning a poorly designed tool..."
echo "$ mcp-readiness scan-tool --tool examples/sample_tool_definitions/bad_tool.json"
sleep 0.5
mcp-readiness scan-tool --tool examples/sample_tool_definitions/bad_tool.json
sleep 2

echo ""
echo "Scanning a production-ready tool..."
echo "$ mcp-readiness scan-tool --tool examples/sample_tool_definitions/good_tool.json"
sleep 0.5
mcp-readiness scan-tool --tool examples/sample_tool_definitions/good_tool.json
sleep 2

DEMO

    chmod +x "$DEMOS_DIR/temp_demo.sh"

    # Record with termtosvg
    termtosvg "$output_file" -c "$DEMOS_DIR/temp_demo.sh" -t window_frame

    # Cleanup
    rm -f "$DEMOS_DIR/temp_demo.sh"

    log_success "Demo SVG created: $output_file"
    echo ""
    echo "You can embed this in your README:"
    echo ""
    echo "  ![Demo](demos/mcp-readiness-demo.svg)"
    echo ""
}

main "$@"
