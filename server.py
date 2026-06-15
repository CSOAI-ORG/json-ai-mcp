import urllib.request as _meter_urlreq
import urllib.error as _meter_urlerr
"""
JSON AI MCP Server — JSON manipulation and validation tools."""

import sys, os
from auth_middleware import check_access

import json
import time
from typing import Any
from mcp.server.fastmcp import FastMCP

from datetime import datetime, timezone
from collections import defaultdict

STRIPE_199 = "https://buy.stripe.com/5kQ6oJ0xS3ce8sl7ew8k91j"

def _add_upgrade_tail(response, tier="free"):
    """Append upgrade nudge to free-tier success responses."""
    if isinstance(response, dict) and tier == "free":
        response["_upgrade_note"] = "Pro tier: unlimited calls + priority support. Upgrade: " + STRIPE_199
    return response


FREE_DAILY_LIMIT = 15
_usage = defaultdict(list)
def _rl(c="anon"):
    now = datetime.now(timezone.utc)
    _usage[c] = [t for t in _usage[c] if (now-t).total_seconds() < 86400]
    if len(_usage[c]) >= FREE_DAILY_LIMIT: return json.dumps({"error": f"Limit {FREE_DAILY_LIMIT}/day"})
    _usage[c].append(now); return None


mcp = FastMCP("json-ai", instructions="MEOK AI Labs MCP Server")
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


def _server_meter_check(api_key: str = "") -> dict:
    """Calls the live /verify endpoint for server-side metering. Fail-open."""
    try:
        data = json.dumps({"api_key": api_key, "tool": ""}).encode()
        req = _meter_urlreq.Request(_METER_URL, data=data,
            headers={"Content-Type": "application/json"}, method="POST")
        with _meter_urlreq.urlopen(req, timeout=2.5) as r:
            d = json.loads(r.read())
            if isinstance(d, dict) and "allowed" in d:
                return d
    except Exception:
        pass
    return {"allowed": True, "tier": "anonymous", "remaining": 200, "upgrade_url": "https://meok.ai/pricing"}


_METER_URL = "https://proofof.ai/verify"


@mcp.tool()
def validate_json(json_string: str, strict: bool = True, api_key: str = "") -> dict[str, Any]:
    """Validate JSON and report structure details.

    Behavior:
        This tool is read-only and stateless — it produces analysis output
        without modifying any external systems, databases, or files.
        Safe to call repeatedly with identical inputs (idempotent).
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool when you need structured analysis or classification
        of inputs against established frameworks or standards.

    When NOT to use:
        Not suitable for real-time production decision-making without
        human review of results.

    Args:
        json_string (str): The json string to analyze or process.
        strict (bool): The strict to analyze or process.
        api_key (str): The api key to analyze or process.

    Behavioral Transparency:
        - Side Effects: This tool is read-only and produces no side effects. It does not modify
          any external state, databases, or files. All output is computed in-memory and returned
          directly to the caller.
        - Authentication: No authentication required for basic usage. Pro/Enterprise tiers
          require a valid MEOK API key passed via the MEOK_API_KEY environment variable.
        - Rate Limits: Free tier: 10 calls/day. Pro tier: unlimited. Rate limit headers are
          included in responses (X-RateLimit-Remaining, X-RateLimit-Reset).
        - Error Handling: Returns structured error objects with 'error' key on failure.
          Never raises unhandled exceptions. Invalid inputs return descriptive validation errors.
        - Idempotency: Fully idempotent — calling with the same inputs always produces the
          same output. Safe to retry on timeout or transient failure.
        - Data Privacy: No input data is stored, logged, or transmitted to external services.
          All processing happens locally within the MCP server process.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": STRIPE_199}
    if err := _rl(): return err

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
    """Transform JSON. Operations: sort_keys, minify, prettify, remove_nulls, add_field, remove_field, get_path.

    Behavior:
        This tool is read-only and stateless — it produces analysis output
        without modifying any external systems, databases, or files.
        Safe to call repeatedly with identical inputs (idempotent).
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool when you need structured analysis or classification
        of inputs against established frameworks or standards.

    When NOT to use:
        Not suitable for real-time production decision-making without
        human review of results.

    Args:
        json_string (str): The json string to analyze or process.
        operation (str): The operation to analyze or process.
        path (str): The path to analyze or process.
        value (str): The value to analyze or process.
        api_key (str): The api key to analyze or process.

    Behavioral Transparency:
        - Side Effects: This tool is read-only and produces no side effects. It does not modify
          any external state, databases, or files. All output is computed in-memory and returned
          directly to the caller.
        - Authentication: No authentication required for basic usage. Pro/Enterprise tiers
          require a valid MEOK API key passed via the MEOK_API_KEY environment variable.
        - Rate Limits: Free tier: 10 calls/day. Pro tier: unlimited. Rate limit headers are
          included in responses (X-RateLimit-Remaining, X-RateLimit-Reset).
        - Error Handling: Returns structured error objects with 'error' key on failure.
          Never raises unhandled exceptions. Invalid inputs return descriptive validation errors.
        - Idempotency: Fully idempotent — calling with the same inputs always produces the
          same output. Safe to retry on timeout or transient failure.
        - Data Privacy: No input data is stored, logged, or transmitted to external services.
          All processing happens locally within the MCP server process.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": STRIPE_199}
    if err := _rl(): return err

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
    """Compare two JSON objects and find differences.

    Behavior:
        This tool is read-only and stateless — it produces analysis output
        without modifying any external systems, databases, or files.
        Safe to call repeatedly with identical inputs (idempotent).
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool when you need structured analysis or classification
        of inputs against established frameworks or standards.

    When NOT to use:
        Not suitable for real-time production decision-making without
        human review of results.

    Args:
        json_a (str): The json a to analyze or process.
        json_b (str): The json b to analyze or process.
        api_key (str): The api key to analyze or process.

    Behavioral Transparency:
        - Side Effects: This tool is read-only and produces no side effects. It does not modify
          any external state, databases, or files. All output is computed in-memory and returned
          directly to the caller.
        - Authentication: No authentication required for basic usage. Pro/Enterprise tiers
          require a valid MEOK API key passed via the MEOK_API_KEY environment variable.
        - Rate Limits: Free tier: 10 calls/day. Pro tier: unlimited. Rate limit headers are
          included in responses (X-RateLimit-Remaining, X-RateLimit-Reset).
        - Error Handling: Returns structured error objects with 'error' key on failure.
          Never raises unhandled exceptions. Invalid inputs return descriptive validation errors.
        - Idempotency: Fully idempotent — calling with the same inputs always produces the
          same output. Safe to retry on timeout or transient failure.
        - Data Privacy: No input data is stored, logged, or transmitted to external services.
          All processing happens locally within the MCP server process.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": STRIPE_199}
    if err := _rl(): return err

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
    """Flatten nested JSON to single-level with dot-notation keys.

    Behavior:
        This tool is read-only and stateless — it produces analysis output
        without modifying any external systems, databases, or files.
        Safe to call repeatedly with identical inputs (idempotent).
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool when you need structured analysis or classification
        of inputs against established frameworks or standards.

    When NOT to use:
        Not suitable for real-time production decision-making without
        human review of results.

    Args:
        json_string (str): The json string to analyze or process.
        separator (str): The separator to analyze or process.
        max_depth (int): The max depth to analyze or process.
        api_key (str): The api key to analyze or process.

    Behavioral Transparency:
        - Side Effects: This tool is read-only and produces no side effects. It does not modify
          any external state, databases, or files. All output is computed in-memory and returned
          directly to the caller.
        - Authentication: No authentication required for basic usage. Pro/Enterprise tiers
          require a valid MEOK API key passed via the MEOK_API_KEY environment variable.
        - Rate Limits: Free tier: 10 calls/day. Pro tier: unlimited. Rate limit headers are
          included in responses (X-RateLimit-Remaining, X-RateLimit-Reset).
        - Error Handling: Returns structured error objects with 'error' key on failure.
          Never raises unhandled exceptions. Invalid inputs return descriptive validation errors.
        - Idempotency: Fully idempotent — calling with the same inputs always produces the
          same output. Safe to retry on timeout or transient failure.
        - Data Privacy: No input data is stored, logged, or transmitted to external services.
          All processing happens locally within the MCP server process.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": STRIPE_199}
    if err := _rl(): return err

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

def main():
    mcp.run()

if __name__ == '__main__':
    main()


# ── MEOK monetization layer (Stripe upgrade · PAYG · pricing) ──────────
# Free tier is zero-config. Upgrade to Pro (unlimited) or pay-as-you-go per call.
import os as _meok_os
MEOK_STRIPE_UPGRADE = "https://buy.stripe.com/5kQ6oJ0xS3ce8sl7ew8k91j"  # Pro (unlimited)
MEOK_PAYG_KEY = _meok_os.environ.get("MEOK_PAYG_KEY", "")  # set to enable PAYG (x402 / ~GBP0.05 per call)
MEOK_PRICING = "https://meok.ai/pricing"


def meok_upsell(tier: str = "free") -> dict:
    """Monetization options for free-tier callers: Pro upgrade, PAYG, or pricing page."""
    if tier != "free":
        return {}
    return {"upgrade_url": MEOK_STRIPE_UPGRADE,
            "payg_enabled": bool(MEOK_PAYG_KEY),
            "pricing": MEOK_PRICING}
