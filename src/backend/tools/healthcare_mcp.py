"""Healthcare MCP client — FDA drugs, PubMed, clinical trials, ICD-10, medRxiv.

Interfaces with the healthcare-mcp server (Cicatriiz/healthcare-mcp-public).
"""

from __future__ import annotations

import json
from typing import Any

import httpx

from src.backend.core.config import settings

_TIMEOUT = 15.0


class HealthcareMCPClient:
    """HTTP client for the healthcare-mcp server."""

    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or settings.healthcare_mcp_url).rstrip("/")

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

    async def fda_drug_lookup(self, drug_name: str, search_type: str = "general") -> Any:
        """Search FDA database for drug info (general, label, adverse_events)."""
        return await self._call_tool("fda_drug_lookup", {
            "drug_name": drug_name, "search_type": search_type,
        })

    async def pubmed_search(self, query: str, max_results: int = 5) -> Any:
        """Search PubMed medical literature."""
        return await self._call_tool("pubmed_search", {
            "query": query, "max_results": max_results,
        })

    async def clinical_trials_search(
        self, condition: str, status: str = "recruiting", max_results: int = 5,
    ) -> Any:
        """Search ClinicalTrials.gov."""
        return await self._call_tool("clinical_trials_search", {
            "condition": condition, "status": status, "max_results": max_results,
        })

    async def lookup_icd_code(
        self, code: str | None = None, description: str | None = None,
    ) -> Any:
        """Look up ICD-10 codes by code or description."""
        args: dict[str, Any] = {}
        if code:
            args["code"] = code
        if description:
            args["description"] = description
        return await self._call_tool("lookup_icd_code", args)

    async def health_topics(self, topic: str) -> Any:
        """Access health info from Health.gov."""
        return await self._call_tool("health_topics", {"topic": topic})

    async def medrxiv_search(self, query: str, max_results: int = 5) -> Any:
        """Search medRxiv preprints."""
        return await self._call_tool("medrxiv_search", {
            "query": query, "max_results": max_results,
        })
