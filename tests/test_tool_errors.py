"""Regression tests for MCP tool error semantics."""

from __future__ import annotations

import asyncio

from fastmcp import Client


def test_service_exception_is_reported_as_mcp_tool_error(monkeypatch):
    """A helper failure must reach clients as isError=true, not successful text."""
    from winremote import services
    from winremote.__main__ import mcp

    def fail_ps(command: str, timeout: int = 30) -> str:
        raise RuntimeError("PowerShell unavailable")

    monkeypatch.setattr(services, "_ps", fail_ps)

    async def call_service_list():
        async with Client(mcp) as client:
            return await client.call_tool("ServiceList", {}, raise_on_error=False)

    result = asyncio.run(call_service_list())

    assert result.is_error is True
    assert "ServiceList" in result.content[0].text
    assert "PowerShell unavailable" in result.content[0].text
