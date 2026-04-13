# json-ai-mcp

MCP server for JSON manipulation and validation tools.

## Tools

- **validate_json** — Validate JSON with structure analysis
- **transform_json** — Transform JSON (sort, minify, prettify, remove nulls, etc.)
- **diff_json** — Compare two JSON objects and find differences
- **flatten_json** — Flatten nested JSON to dot-notation keys

## Usage

```bash
pip install mcp
python server.py
```

## Rate Limits

50 calls/day per tool (free tier).
