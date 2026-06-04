"""Food Data Central MCP client — USDA nutritional data.

Interfaces with the food-data-central-mcp-server (jlfwong/food-data-central-mcp-server).
"""

from __future__ import annotations

import json
from typing import Any

import httpx

from src.backend.core.config import settings

_TIMEOUT = 15.0


class FoodDataMCPClient:
    """HTTP client for the food-data-central MCP server."""

    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or settings.food_data_mcp_url).rstrip("/")

    async def _call_tool(self, tool_name: str, args: dict[str, Any]) -> Any:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": args},
        }
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                resp = await client.post(f"{self.base_url}/mcp", json=payload)
                resp.raise_for_status()
                data = resp.json()
                result = data.get("result", {})
                content = result.get("content", [])
                if content and isinstance(content, list):
                    texts = [c.get("text", "") for c in content if c.get("type") == "text"]
                    combined = "\n".join(texts)
                    try:
                        return json.loads(combined)
                    except json.JSONDecodeError:
                        return {"text": combined}
                return result
        except Exception as e:
            return {"error": str(e), "tool": tool_name}

    async def search_foods(self, query: str, page_size: int = 10) -> Any:
        """Search USDA FoodData Central for foods by keyword."""
        return await self._call_tool("search-foods", {
            "query": query, "pageSize": page_size,
        })
