"""JSON AI MCP Server — JSON manipulation and validation tools."""

import sys, os
sys.path.insert(0, os.path.expanduser('~/clawd/meok-labs-engine/shared'))
from auth_middleware import check_access

import json
import time
from typing import Any
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("json-ai-mcp")
_calls: dict[str, list[float]] = {}
DAILY_LIMIT = 50

def _rate_check(tool: str) -> bool:
    now = time.time()
    _calls.setdefault(tool, [])
    _calls[tool] = [t for t in _calls[tool] if t > now - 86400]
    if len(_calls[tool]) >= DAILY_LIMIT:
        return False
    _calls[tool].append(now)
    return True

@mcp.tool()
def validate_json(json_string: str, strict: bool = True, api_key: str = "") -> dict[str, Any]:
    """Validate JSON and report structure details."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    if not _rate_check("validate_json"):
        return {"error": "Rate limit exceeded (50/day)"}
    try:
        data = json.loads(json_string, strict=strict)
    except json.JSONDecodeError as e:
        return {"valid": False, "error": str(e), "line": e.lineno, "column": e.colno, "position": e.pos}
    def analyze(obj, depth=0):
        info = {"type": type(obj).__name__, "depth": depth}
        if isinstance(obj, dict):
            info["key_count"] = len(obj)
            info["keys"] = list(obj.keys())
        elif isinstance(obj, list):
            info["length"] = len(obj)
            info["element_types"] = list(set(type(x).__name__ for x in obj))
        return info
    return {"valid": True, "structure": analyze(data), "size_bytes": len(json_string), "pretty": json.dumps(data, indent=2)[:2000]}

@mcp.tool()
def transform_json(json_string: str, operation: str, path: str = "", value: str = "", api_key: str = "") -> dict[str, Any]:
    """Transform JSON. Operations: sort_keys, minify, prettify, remove_nulls, add_field, remove_field, get_path."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    if not _rate_check("transform_json"):
        return {"error": "Rate limit exceeded (50/day)"}
    try:
        data = json.loads(json_string)
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON: {e}"}
    if operation == "sort_keys":
        result = json.dumps(data, sort_keys=True, indent=2)
    elif operation == "minify":
        result = json.dumps(data, separators=(",", ":"))
    elif operation == "prettify":
        result = json.dumps(data, indent=2)
    elif operation == "remove_nulls":
        def strip_nulls(obj):
            if isinstance(obj, dict):
                return {k: strip_nulls(v) for k, v in obj.items() if v is not None}
            if isinstance(obj, list):
                return [strip_nulls(i) for i in obj if i is not None]
            return obj
        result = json.dumps(strip_nulls(data), indent=2)
    elif operation == "get_path":
        parts = path.strip(".").split(".") if path else []
        current = data
        for p in parts:
            if isinstance(current, dict) and p in current:
                current = current[p]
            elif isinstance(current, list) and p.isdigit():
                current = current[int(p)]
            else:
                return {"error": f"Path '{path}' not found"}
        result = json.dumps(current, indent=2)
    elif operation == "add_field":
        if not path:
            return {"error": "Path required for add_field"}
        try:
            val = json.loads(value)
        except json.JSONDecodeError:
            val = value
        parts = path.strip(".").split(".")
        current = data
        for p in parts[:-1]:
            current = current[p] if isinstance(current, dict) else current[int(p)]
        current[parts[-1]] = val
        result = json.dumps(data, indent=2)
    elif operation == "remove_field":
        if not path:
            return {"error": "Path required"}
        parts = path.strip(".").split(".")
        current = data
        for p in parts[:-1]:
            current = current[p] if isinstance(current, dict) else current[int(p)]
        if isinstance(current, dict) and parts[-1] in current:
            del current[parts[-1]]
        result = json.dumps(data, indent=2)
    else:
        return {"error": f"Unknown operation: {operation}. Use: sort_keys, minify, prettify, remove_nulls, add_field, remove_field, get_path"}
    return {"operation": operation, "result": result, "original_size": len(json_string), "result_size": len(result)}

@mcp.tool()
def diff_json(json_a: str, json_b: str, api_key: str = "") -> dict[str, Any]:
    """Compare two JSON objects and find differences."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    if not _rate_check("diff_json"):
        return {"error": "Rate limit exceeded (50/day)"}
    try:
        a = json.loads(json_a)
        b = json.loads(json_b)
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON: {e}"}
    diffs = []
    def compare(obj_a, obj_b, path="$"):
        if type(obj_a) != type(obj_b):
            diffs.append({"path": path, "type": "type_change", "from": type(obj_a).__name__, "to": type(obj_b).__name__})
            return
        if isinstance(obj_a, dict):
            for k in set(list(obj_a.keys()) + list(obj_b.keys())):
                if k not in obj_a:
                    diffs.append({"path": f"{path}.{k}", "type": "added", "value": obj_b[k]})
                elif k not in obj_b:
                    diffs.append({"path": f"{path}.{k}", "type": "removed", "value": obj_a[k]})
                else:
                    compare(obj_a[k], obj_b[k], f"{path}.{k}")
        elif isinstance(obj_a, list):
            for i in range(max(len(obj_a), len(obj_b))):
                if i >= len(obj_a):
                    diffs.append({"path": f"{path}[{i}]", "type": "added", "value": obj_b[i]})
                elif i >= len(obj_b):
                    diffs.append({"path": f"{path}[{i}]", "type": "removed", "value": obj_a[i]})
                else:
                    compare(obj_a[i], obj_b[i], f"{path}[{i}]")
        elif obj_a != obj_b:
            diffs.append({"path": path, "type": "changed", "from": obj_a, "to": obj_b})
    compare(a, b)
    return {"identical": len(diffs) == 0, "differences": diffs, "diff_count": len(diffs)}

@mcp.tool()
def flatten_json(json_string: str, separator: str = ".", max_depth: int = 10, api_key: str = "") -> dict[str, Any]:
    """Flatten nested JSON to single-level with dot-notation keys."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    if not _rate_check("flatten_json"):
        return {"error": "Rate limit exceeded (50/day)"}
    try:
        data = json.loads(json_string)
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON: {e}"}
    flat: dict[str, Any] = {}
    def flatten(obj, prefix="", depth=0):
        if depth > max_depth:
            flat[prefix] = obj
            return
        if isinstance(obj, dict):
            for k, v in obj.items():
                key = f"{prefix}{separator}{k}" if prefix else k
                flatten(v, key, depth + 1)
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                key = f"{prefix}{separator}{i}" if prefix else str(i)
                flatten(v, key, depth + 1)
        else:
            flat[prefix] = obj
    flatten(data)
    return {"flattened": flat, "key_count": len(flat), "separator": separator, "original_size": len(json_string)}

if __name__ == "__main__":
    mcp.run()
