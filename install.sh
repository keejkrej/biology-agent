#!/usr/bin/env zsh

set -e  # Exit on error

echo "🧬 Biology Agent - Claude Code Plugin Installer"
echo "================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the script's directory (source location)
SCRIPT_DIR="$( cd "$( dirname "${(%):-%x}" )" && pwd )"
SOURCE_DIR="$SCRIPT_DIR/biology-microscopy"
INSTALL_DIR="$HOME/.claude/plugins/repos/biology-microscopy"

echo "📍 Source: $SOURCE_DIR"
echo "📍 Install to: $INSTALL_DIR"
echo ""

# Step 1: Check for uv
echo "1️⃣  Checking for uv..."
if ! command -v uv &> /dev/null; then
    echo "${RED}❌ uv not found${NC}"
    echo "   Install uv first: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi
echo "${GREEN}✓${NC} uv found: $(which uv)"
echo ""

# Step 2: Check Python version
echo "2️⃣  Checking Python version..."
if ! uv python list | grep -q "3.12"; then
    echo "${YELLOW}⚠️  Python 3.12 not found, installing...${NC}"
    uv python install 3.12
fi
echo "${GREEN}✓${NC} Python 3.12 available"
echo ""

# Step 3: Copy plugin files
echo "3️⃣  Copying plugin files..."
mkdir -p "$INSTALL_DIR"

# Remove old installation if it exists
if [ -d "$INSTALL_DIR" ]; then
    echo "   Removing old installation..."
    rm -rf "$INSTALL_DIR"
    mkdir -p "$INSTALL_DIR"
fi

echo "   Copying .claude-plugin/..."
cp -r "$SOURCE_DIR/.claude-plugin" "$INSTALL_DIR/"

echo "   Copying mcp-server/..."
cp -r "$SOURCE_DIR/mcp-server" "$INSTALL_DIR/"

echo "   Copying scripts/..."
cp -r "$SOURCE_DIR/scripts" "$INSTALL_DIR/"

echo "   Copying .mcp.json..."
cp "$SOURCE_DIR/.mcp.json" "$INSTALL_DIR/"

echo "${GREEN}✓${NC} Plugin files copied to $INSTALL_DIR"
echo ""

# Step 4: Create virtual environment
echo "4️⃣  Setting up virtual environment..."
cd "$INSTALL_DIR"
echo "   Creating new venv..."
uv venv --python 3.12
echo "${GREEN}✓${NC} Virtual environment ready"
echo ""

# Step 5: Install dependencies
echo "5️⃣  Installing dependencies..."
cd "$INSTALL_DIR"
uv pip install -r mcp-server/requirements.txt
echo "${GREEN}✓${NC} Dependencies installed"
echo ""

# Step 6: Make scripts executable
echo "6️⃣  Making CLI scripts executable..."
chmod +x "$INSTALL_DIR/scripts/microscopy-info"
chmod +x "$INSTALL_DIR/scripts/batch-convert-metadata"
chmod +x "$INSTALL_DIR/scripts/validate-formats"
echo "${GREEN}✓${NC} Scripts are executable"
echo ""

# Step 7: Register MCP server with Claude Code
echo "7️⃣  Registering MCP server with Claude Code..."

# Remove old entry if exists
claude mcp remove biology 2>/dev/null || true

# Add MCP server globally
claude mcp add biology --global -- "$INSTALL_DIR/.venv/bin/python" "$INSTALL_DIR/mcp-server/server.py"
echo "${GREEN}✓${NC} MCP server registered"
echo ""

# Step 8: Copy skills to Claude skills directory
echo "8️⃣  Setting up skills..."
SKILLS_DIR="$HOME/.claude/skills"
mkdir -p "$SKILLS_DIR"

# Copy each skill from the plugin
for skill_dir in "$SOURCE_DIR/skills"/*/; do
    if [ -d "$skill_dir" ]; then
        skill_name=$(basename "$skill_dir")
        echo "   Installing skill: $skill_name"
        cp -r "$skill_dir" "$SKILLS_DIR/"
    fi
done
echo "${GREEN}✓${NC} Skills installed to $SKILLS_DIR"
echo ""

# Final instructions
echo "✅ ${GREEN}Installation Complete!${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Next Steps:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. ${YELLOW}Restart Claude Code${NC} (fully quit and reopen)"
echo ""
echo "2. The biology MCP server will be available"
echo ""
echo "3. Available MCP tools:"
echo "   • read_microscopy_metadata"
echo "   • get_image_info"
echo "   • validate_microscopy_file"
echo "   • get_channel_info"
echo "   • get_physical_dimensions"
echo "   • list_scenes"
echo ""
echo "4. Available skills:"
ls "$SKILLS_DIR" 2>/dev/null | sed 's/^/   • /' || echo "   (check ~/.claude/skills/)"
echo ""
echo "5. CLI tools are available at:"
echo "   $INSTALL_DIR/scripts/"
echo ""
echo "6. Optional: Add scripts to PATH in ~/.zshrc:"
echo "   export PATH=\"$INSTALL_DIR/scripts:\$PATH\""
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🧪 Test the installation:"
echo "   Ask Claude: 'List available MCP servers'"
echo "   Then: 'Analyze /path/to/microscopy-file.tif'"
echo ""
