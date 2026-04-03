import os
import asyncio
from typing import Any, cast

import base58
from fastapi import APIRouter
from solders.keypair import Keypair

from pacifica.client import PacificaClient
from vault.db import VaultDB

router = APIRouter()
db = VaultDB()

_kp_bytes = base58.b58decode(os.getenv("VAULT_PRIVATE_KEY", ""))
_keypair = Keypair.from_bytes(_kp_bytes) if _kp_bytes else None
_builder_code = os.getenv("VAULT_BUILDER_CODE", "SPAGHETTIVAULT1")
_client = PacificaClient(_keypair, _builder_code) if _keypair else None


@router.get("/summary")
async def dashboard_summary(account: str):
    if _client is None:
        return _safe_defaults(account)

    try:
        funding_rate_raw, position_raw, funding_history_raw_raw, trades_raw = await asyncio.gather(
            _client.get_funding_rate("SOL"),
            _client.get_position(account, "SOL"),
            _client.get_account_funding_history(account, limit=48),
            _client.get_trade_history(account, limit=100),
            return_exceptions=True,
        )

        if isinstance(funding_rate_raw, BaseException):
            funding_rate = 0.0
        else:
            funding_rate = float(cast(float | int, funding_rate_raw))

        position = None if isinstance(position_raw, BaseException) else position_raw

        if isinstance(funding_history_raw_raw, BaseException):
            funding_history_raw: list[dict[str, Any]] = []
        else:
            funding_history_raw = cast(list[dict[str, Any]], funding_history_raw_raw)

        if isinstance(trades_raw, BaseException):
            trades: list[dict[str, Any]] = []
        else:
            trades = cast(list[dict[str, Any]], trades_raw)

        if funding_rate != 0.0:
            db.record_funding_rate(funding_rate)

        total_funding_earned = sum(
            float(f.get("funding", 0))
            for f in funding_history_raw
            if float(f.get("funding", 0)) > 0
        )

        local_funding_history = db.get_funding_history(48)

        return {
            "account": account,
            "position": position,
            "current_funding_rate": funding_rate,
            "annualised_funding_apy": funding_rate * 24 * 365,
            "total_funding_earned_usdc": total_funding_earned,
            "trade_count": len(trades),
            "funding_history": local_funding_history,
            "on_chain_funding_history": funding_history_raw[:20],
        }
    except Exception as exc:
        return {**_safe_defaults(account), "error": str(exc)}


def _safe_defaults(account: str) -> dict:
    local_history = db.get_funding_history(48)
    return {
        "account": account,
        "position": None,
        "current_funding_rate": 0.0,
        "annualised_funding_apy": 0.0,
        "total_funding_earned_usdc": 0.0,
        "trade_count": 0,
        "funding_history": local_history,
        "on_chain_funding_history": [],
        "note": "Pacifica API unreachable, showing cached data only",
    }


@router.get("/funding_rate")
async def live_funding_rate():
    if _client is None:
        return {"symbol": "SOL", "rate": 0.0, "annualised_apy": 0.0, "mark_price": 0.0}

    try:
        prices = await _client.get_all_prices()
        sol = next((p for p in prices if p.get("symbol") == "SOL"), {})
        rate = float(sol.get("funding", 0))
        mark = float(sol.get("mark", 0))
        db.record_funding_rate(rate)

        return {
            "symbol": "SOL",
            "rate": rate,
            "next_rate": float(sol.get("next_funding", 0)),
            "annualised_apy": rate * 24 * 365,
            "mark_price": mark,
            "open_interest": sol.get("open_interest"),
        }
    except Exception as exc:
        return {"symbol": "SOL", "rate": 0.0, "annualised_apy": 0.0, "error": str(exc)}
