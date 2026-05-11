from __future__ import annotations

import pytest

from services.llm_gateway import DisabledProvider


@pytest.mark.asyncio
async def test_disabled_llm_provider_returns_safe_result() -> None:
    result = await DisabledProvider().moderate("hello", {})

    assert result.action == "none"
    assert result.category == "safe"
    assert result.score == 0
