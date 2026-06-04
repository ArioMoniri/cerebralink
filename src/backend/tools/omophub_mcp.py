"""OMOPHub MCP client — OMOP CDM vocabulary mapping (SNOMED, ICD-10, RxNorm, LOINC).

Interfaces with the @omophub/omophub-mcp server.
"""

from __future__ import annotations

import json
from typing import Any

import httpx

from src.backend.core.config import settings

_TIMEOUT = 15.0


class OMOPHubMCPClient:
    """HTTP client for the OMOPHub MCP server."""

    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or settings.omophub_mcp_url).rstrip("/")

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

    async def search_concepts(self, query: str, limit: int = 10) -> Any:
        """Search for medical concepts by name across all vocabularies."""
        return await self._call_tool("search_concepts", {
            "query": query, "limit": limit,
        })

    async def get_concept_by_code(self, vocabulary_id: str, concept_code: str) -> Any:
        """Look up a concept using a vocabulary-specific code (e.g., ICD-10 E11.9)."""
        return await self._call_tool("get_concept_by_code", {
            "vocabulary_id": vocabulary_id, "concept_code": concept_code,
        })

    async def map_concept(self, concept_id: int, target_vocabulary: str | None = None) -> Any:
        """Map a concept to equivalent concepts in other vocabularies."""
        args: dict[str, Any] = {"concept_id": concept_id}
        if target_vocabulary:
            args["target_vocabulary_id"] = target_vocabulary
        return await self._call_tool("map_concept", args)

    async def explore_concept(self, concept_id: int) -> Any:
        """Get concept details, hierarchy, and cross-vocabulary mappings in one call."""
        return await self._call_tool("explore_concept", {"concept_id": concept_id})

    async def semantic_search(self, query: str, limit: int = 10) -> Any:
        """Search using natural language with neural embeddings."""
        return await self._call_tool("semantic_search", {
            "query": query, "limit": limit,
        })
