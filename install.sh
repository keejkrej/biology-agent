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
SOURCE_DIR="$SCRIPT_DIR/plugin"
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

echo "   Copying skills/..."
cp -r "$SOURCE_DIR/skills" "$INSTALL_DIR/"

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

# Step 7: Create custom marketplace for auto-discovery
echo "7️⃣  Setting up custom marketplace (keejkrej) for auto-discovery..."
MARKETPLACE_DIR="$HOME/.claude/plugins/marketplaces/keejkrej"
mkdir -p "$MARKETPLACE_DIR/.claude-plugin"

# Copy plugin files to marketplace
echo "   Copying plugin to marketplace..."
cp -r "$INSTALL_DIR"/* "$MARKETPLACE_DIR"/

# Create marketplace.json for discovery
echo "   Creating marketplace.json..."
python3 - "$MARKETPLACE_DIR" << 'PYEOF'
import json
import os
import sys

marketplace_dir = sys.argv[1]
plugin_name = "biology-microscopy"

marketplace_json = {
    "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
    "name": "keejkrej",
    "description": "Biology microscopy analysis toolkit",
    "owner": {
        "name": "Biology Research Community"
    },
    "plugins": [
        {
            "name": plugin_name,
            "description": "Microscopy data analysis toolkit with bioio. Read metadata, validate files, and analyze microscopy images (OME-TIFF, ND2, CZI, etc.).",
            "version": "1.0.0",
            "author": {
                "name": "Biology Research Community"
            },
            "source": f"./{plugin_name}",
            "category": "science"
        }
    ]
}

with open(os.path.join(marketplace_dir, ".claude-plugin", "marketplace.json"), "w") as f:
    json.dump(marketplace_json, f, indent=2)
    f.write("\n")

print("   ✓ marketplace.json created")
PYEOF

echo "${GREEN}✓${NC} Marketplace plugin ready at $MARKETPLACE_DIR"
echo ""

# Step 8: Update known_marketplaces.json
echo "8️⃣  Registering custom marketplace (keejkrej)..."
KNOWN_MARKETPLACES="$HOME/.claude/plugins/known_marketplaces.json"
MARKETPLACE_DIR="$HOME/.claude/plugins/marketplaces/keejkrej"

if [ -f "$KNOWN_MARKETPLACES" ]; then
    # Check if keejkrej already exists
    if grep -q '"keejkrej"' "$KNOWN_MARKETPLACES" 2>/dev/null; then
        echo "   keejkrej marketplace already registered, updating timestamp..."
        # Use python for safe JSON manipulation
        python3 << PYEOF
import json
import os
from datetime import datetime, timezone

with open(os.path.expanduser("$KNOWN_MARKETPLACES"), 'r') as f:
    data = json.load(f)

data["keejkrej"] = {
    "source": {
        "source": "github",
        "repo": "keejkrej/biology-agent"
    },
    "installLocation": os.path.expanduser("$MARKETPLACE_DIR"),
    "lastUpdated": datetime.now(timezone.utc).isoformat()
}

with open(os.path.expanduser("$KNOWN_MARKETPLACES"), 'w') as f:
    json.dump(data, f, indent=2)
    f.write('\n')
PYEOF
        echo "${GREEN}✓${NC} Updated keejkrej entry"
    else
        # Add new entry to existing file
        python3 << PYEOF
import json
import os
from datetime import datetime, timezone

with open(os.path.expanduser("$KNOWN_MARKETPLACES"), 'r') as f:
    data = json.load(f)

data["keejkrej"] = {
    "source": {
        "source": "github",
        "repo": "keejkrej/biology-agent"
    },
    "installLocation": os.path.expanduser("$MARKETPLACE_DIR"),
    "lastUpdated": datetime.now(timezone.utc).isoformat()
}

with open(os.path.expanduser("$KNOWN_MARKETPLACES"), 'w') as f:
    json.dump(data, f, indent=2)
    f.write('\n')
PYEOF
        echo "${GREEN}✓${NC} Added keejkrej to known_marketplaces.json"
    fi
else
    echo "${YELLOW}⚠️  known_marketplaces.json not found, creating...${NC}"
    mkdir -p "$(dirname "$KNOWN_MARKETPLACES")"
    python3 << PYEOF
import json
import os
from datetime import datetime, timezone

data = {
    "keejkrej": {
        "source": {
            "source": "github",
            "repo": "keejkrej/biology-agent"
        },
        "installLocation": os.path.expanduser("$MARKETPLACE_DIR"),
        "lastUpdated": datetime.now(timezone.utc).isoformat()
    }
}

with open(os.path.expanduser("$KNOWN_MARKETPLACES"), 'w') as f:
    json.dump(data, f, indent=2)
    f.write('\n')
PYEOF
    echo "${GREEN}✓${NC} Created known_marketplaces.json"
fi
echo ""

# Step 9: Clean up old manual MCP config if it exists (compatibility)
echo "9️⃣  Checking for old manual MCP configuration..."
if claude mcp list 2>/dev/null | grep -q "biology"; then
    echo "${YELLOW}   Found manual biology MCP entry, removing for clean auto-discovery...${NC}"
    claude mcp remove biology 2>/dev/null || true
    echo "${GREEN}✓${NC} Removed manual configuration"
else
    echo "   No manual configuration found"
fi
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
echo "2. The biology MCP server will be auto-discovered"
echo "   via the custom 'keejkrej' marketplace"
echo ""
echo "3. Available MCP tools:"
echo "   • read_microscopy_metadata"
echo "   • get_image_info"
echo "   • validate_microscopy_file"
echo "   • get_channel_info"
echo "   • get_physical_dimensions"
echo "   • list_scenes"
echo ""
echo "4. CLI tools are available at:"
echo "   $INSTALL_DIR/scripts/"
echo ""
echo "5. Optional: Add scripts to PATH in ~/.zshrc:"
echo "   export PATH=\"$INSTALL_DIR/scripts:\$PATH\""
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🧪 Test the installation:"
echo "   Ask Claude: 'List available MCP servers'"
echo "   Then: 'Analyze /path/to/microscopy-file.tif'"
echo ""
