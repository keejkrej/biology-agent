# Quick Start Guide

Get up and running with the Biology Agent in 5 minutes!

## 1. Install Dependencies (1 minute)

```bash
cd ~/workspace/biology-agent

# Install Python 3.12 and create venv
uv python install 3.12
uv venv --python 3.12

# Install packages
uv pip install -r mcp-server/requirements.txt
```

✅ **Done!** You should see ~126 packages installed.

## 2. Test the MCP Server (1 minute)

```bash
# Activate the virtual environment
source .venv/bin/activate

# Test the server starts without errors
python mcp-server/server.py
```

You should see the FastMCP server starting. Press **Ctrl+C** to stop.

✅ **Server works!**

## 3. Test CLI Tools (1 minute)

Create a test file or use an existing one:

```bash
# Test with microscopy-info
scripts/microscopy-info /path/to/your/image.ome.tiff

# Or validate a folder
scripts/validate-formats /path/to/folder/
```

✅ **CLI tools work!**

## 4. Configure Claude Code (2 minutes)

### Find your username:
```bash
echo $HOME
# Output: /Users/YOUR_USERNAME
```

### Edit Claude Code config:

Open `~/.config/claude/config.json` and add:

```json
{
  "mcpServers": {
    "biology": {
      "command": "/Users/YOUR_USERNAME/workspace/biology-agent/.venv/bin/python",
      "args": ["/Users/YOUR_USERNAME/workspace/biology-agent/mcp-server/server.py"]
    }
  }
}
```

**Replace `YOUR_USERNAME` with your actual username!**

### Restart Claude Code

```bash
# Close and reopen Claude Code, or:
claude restart
```

✅ **Claude Code configured!**

## 5. Try It Out! (1 minute)

Open Claude Code and ask:

```
Read metadata from /path/to/your/image.ome.tiff
```

Claude should use the `read_microscopy_metadata` tool!

Or use a skill:

```
/analyze-microscopy-file
```

## 🎉 You're Done!

### Next Steps:

1. **Read the full README.md** for detailed usage
2. **Try the CLI scripts** for batch processing
3. **Explore the skills** available in `skills/`
4. **Add more format support** if needed (e.g., `uv pip install bioio-czi`)

### Common Issues:

**Q: Server not found in Claude Code**
- Check the config path is correct
- Use absolute paths (not `~`)
- Restart Claude Code

**Q: Module not found errors**
- Make sure virtual environment is activated
- Reinstall: `uv pip install -r mcp-server/requirements.txt`

**Q: Permission denied on scripts**
- Run: `chmod +x scripts/*`

## Need Help?

Check the **Troubleshooting** section in README.md!
