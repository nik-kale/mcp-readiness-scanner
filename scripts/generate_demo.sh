#!/usr/bin/env bash
set -euo pipefail

###############################################################################
# MCP Readiness Scanner - Demo GIF Generator
#
# This script generates an animated GIF demonstration of the MCP readiness
# scanner in action. It records terminal sessions showing scans of both
# "bad" and "good" tool definitions, then converts them to GIF format.
#
# Requirements:
#   - asciinema (for recording terminal sessions)
#   - agg (asciinema-gif-generator, for converting to GIF)
#   - mcp-readiness-scanner installed
#
# Usage:
#   ./scripts/generate_demo.sh
#
# Output:
#   demos/mcp-readiness-demo.gif
###############################################################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DEMOS_DIR="$PROJECT_ROOT/demos"
TEMP_DIR="$DEMOS_DIR/temp"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Demo configuration
DEMO_SPEED=1.5  # Playback speed multiplier
DEMO_WIDTH=120  # Terminal width in characters
DEMO_HEIGHT=30  # Terminal height in lines

###############################################################################
# Helper Functions
###############################################################################

log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

check_dependencies() {
    log_info "Checking dependencies..."

    local missing_deps=()

    if ! command -v asciinema &> /dev/null; then
        missing_deps+=("asciinema")
    fi

    if ! command -v agg &> /dev/null; then
        missing_deps+=("agg")
    fi

    if ! command -v mcp-readiness &> /dev/null; then
        missing_deps+=("mcp-readiness")
    fi

    if [ ${#missing_deps[@]} -gt 0 ]; then
        log_error "Missing required dependencies: ${missing_deps[*]}"
        echo ""
        echo "Installation instructions:"
        echo ""

        for dep in "${missing_deps[@]}"; do
            case $dep in
                asciinema)
                    echo "  asciinema:"
                    echo "    macOS:   brew install asciinema"
                    echo "    Ubuntu:  sudo apt-get install asciinema"
                    echo "    Arch:    sudo pacman -S asciinema"
                    echo "    pip:     pip install asciinema"
                    echo ""
                    ;;
                agg)
                    echo "  agg (asciinema-gif-generator):"
                    echo "    cargo:   cargo install agg"
                    echo "    GitHub:  https://github.com/asciinema/agg"
                    echo ""
                    ;;
                mcp-readiness)
                    echo "  mcp-readiness-scanner:"
                    echo "    From repo:  pip install -e ."
                    echo "    From PyPI:  pip install mcp-readiness-scanner"
                    echo ""
                    ;;
            esac
        done

        return 1
    fi

    log_success "All dependencies are installed"
}

setup_directories() {
    log_info "Setting up directories..."
    mkdir -p "$DEMOS_DIR"
    mkdir -p "$TEMP_DIR"
    log_success "Directories created"
}

cleanup() {
    log_info "Cleaning up temporary files..."
    rm -rf "$TEMP_DIR"
    log_success "Cleanup complete"
}

###############################################################################
# Recording Functions
###############################################################################

record_demo_session() {
    log_info "Recording demo session..."

    local cast_file="$TEMP_DIR/demo.cast"

    # Create the recording script that will be executed
    cat > "$TEMP_DIR/demo_script.sh" << 'DEMO_SCRIPT'
#!/usr/bin/env bash

# Add delays to make the demo more readable
type_command() {
    local cmd="$1"
    local delay="${2:-0.05}"

    # Print prompt
    echo -ne "\033[1;32m$\033[0m "

    # Type out the command character by character
    for (( i=0; i<${#cmd}; i++ )); do
        echo -n "${cmd:$i:1}"
        sleep "$delay"
    done

    echo ""
    sleep 0.3
}

pause() {
    sleep "${1:-1.5}"
}

# Clear screen and show banner
clear
echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║           MCP Readiness Scanner - Demo                          ║"
echo "║      Production Readiness for MCP Tools & AI Agents             ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
pause 2

# Demo 1: Scan a bad tool
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Demo 1: Scanning a poorly designed tool"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
pause 1

type_command "mcp-readiness scan-tool --tool examples/sample_tool_definitions/bad_tool.json --format markdown"
mcp-readiness scan-tool --tool examples/sample_tool_definitions/bad_tool.json --format markdown
pause 3

# Demo 2: Scan a good tool
echo ""
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Demo 2: Scanning a production-ready tool"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
pause 1

type_command "mcp-readiness scan-tool --tool examples/sample_tool_definitions/good_tool.json --format markdown"
mcp-readiness scan-tool --tool examples/sample_tool_definitions/good_tool.json --format markdown
pause 3

# Demo 3: List providers
echo ""
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Demo 3: Available inspection providers"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
pause 1

type_command "mcp-readiness list-providers"
mcp-readiness list-providers
pause 2

echo ""
echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                    Demo Complete!                                ║"
echo "║                                                                  ║"
echo "║  Get started: pip install mcp-readiness-scanner                  ║"
echo "║  Learn more:  github.com/mcp-readiness/scanner                   ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
pause 2

DEMO_SCRIPT

    chmod +x "$TEMP_DIR/demo_script.sh"

    # Record the session
    cd "$PROJECT_ROOT"
    COLUMNS=$DEMO_WIDTH LINES=$DEMO_HEIGHT asciinema rec \
        --overwrite \
        --command "$TEMP_DIR/demo_script.sh" \
        --title "MCP Readiness Scanner Demo" \
        "$cast_file"

    log_success "Demo session recorded to $cast_file"
    echo "$cast_file"
}

convert_to_gif() {
    local cast_file="$1"
    local output_file="$DEMOS_DIR/mcp-readiness-demo.gif"

    log_info "Converting recording to GIF..."

    agg \
        --font-size 14 \
        --speed "$DEMO_SPEED" \
        --cols "$DEMO_WIDTH" \
        --rows "$DEMO_HEIGHT" \
        --theme monokai \
        "$cast_file" \
        "$output_file"

    log_success "GIF created: $output_file"

    # Get file size
    local size=$(du -h "$output_file" | cut -f1)
    log_info "File size: $size"

    echo "$output_file"
}

###############################################################################
# Main Script
###############################################################################

main() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║        MCP Readiness Scanner - Demo GIF Generator               ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo ""

    # Check dependencies
    if ! check_dependencies; then
        exit 1
    fi

    # Setup
    setup_directories

    # Record demo
    cast_file=$(record_demo_session)

    # Convert to GIF
    output_file=$(convert_to_gif "$cast_file")

    # Cleanup
    cleanup

    echo ""
    log_success "Demo GIF generation complete!"
    echo ""
    echo "  Output: $output_file"
    echo ""
    echo "You can now add this GIF to your README or documentation:"
    echo ""
    echo "  ![MCP Readiness Scanner Demo](demos/mcp-readiness-demo.gif)"
    echo ""
}

# Run main function
main "$@"
