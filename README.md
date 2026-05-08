<div align="center">

# Json Ai MCP

**JSON AI MCP Server — JSON manipulation and validation tools.**

[![PyPI](https://img.shields.io/pypi/v/meok-json-ai-mcp)](https://pypi.org/project/meok-json-ai-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-MCP_Server-purple)](https://meok.ai)

</div>

## Overview

JSON AI MCP Server — JSON manipulation and validation tools.

## Tools

| Tool | Description |
|------|-------------|
| `validate_json` | Validate JSON and report structure details. |
| `transform_json` | Transform JSON. Operations: sort_keys, minify, prettify, remove_nulls, add_field |
| `diff_json` | Compare two JSON objects and find differences. |
| `flatten_json` | Flatten nested JSON to single-level with dot-notation keys. |

## Installation

```bash
pip install meok-json-ai-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "json-ai": {
      "command": "python",
      "args": ["-m", "meok_json_ai_mcp.server"]
    }
  }
}
```

## Usage with FastMCP

```python
from mcp.server.fastmcp import FastMCP

# This server exposes 4 tool(s) via MCP
# See server.py for full implementation
```

## License

MIT © [MEOK AI Labs](https://meok.ai)
