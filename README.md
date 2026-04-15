# JSON AI

> By [MEOK AI Labs](https://meok.ai) — JSON manipulation and validation tools

## Installation

```bash
pip install json-ai-mcp
```

## Usage

```bash
python server.py
```

## Tools

### `validate_json`
Validate JSON and report structure details including type, key count, and depth.

**Parameters:**
- `json_string` (str): JSON string to validate
- `strict` (bool): Strict parsing mode (default: True)

### `transform_json`
Transform JSON. Operations: sort_keys, minify, prettify, remove_nulls, add_field, remove_field, get_path.

**Parameters:**
- `json_string` (str): JSON string to transform
- `operation` (str): Transformation operation
- `path` (str): Dot-notation path for field operations
- `value` (str): Value for add_field operation

### `diff_json`
Compare two JSON objects and find differences including additions, removals, and changes.

**Parameters:**
- `json_a` (str): First JSON string
- `json_b` (str): Second JSON string

### `flatten_json`
Flatten nested JSON to single-level with dot-notation keys.

**Parameters:**
- `json_string` (str): JSON string to flatten
- `separator` (str): Key separator (default: ".")
- `max_depth` (int): Maximum nesting depth (default: 10)

## Authentication

Free tier: 15 calls/day. Upgrade at [meok.ai/pricing](https://meok.ai/pricing) for unlimited access.

## License

MIT — MEOK AI Labs
