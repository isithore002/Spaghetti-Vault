import asyncio
import json
import os
from typing import AsyncGenerator, Optional

import httpx
import websockets
from solders.keypair import Keypair

from .signing import build_market_order_payload

BASE_URL = (
    os.getenv("PACIFICA_TESTNET_URL", "https://test-api.pacifica.fi/api/v1")
    if os.getenv("PACIFICA_ENV", "testnet") == "testnet"
    else os.getenv("PACIFICA_MAINNET_URL", "https://api.pacifica.fi/api/v1")
)

WS_URL = (
    os.getenv("PACIFICA_WS_TESTNET", "wss://test-stream.pacifica.fi")
    if os.getenv("PACIFICA_ENV", "testnet") == "testnet"
    else os.getenv("PACIFICA_WS_MAINNET", "wss://stream.pacifica.fi")
)


class PacificaClient:
    def __init__(self, vault_keypair: Keypair, builder_code: str):
        self.keypair = vault_keypair
        self.builder_code = builder_code
        self.http = httpx.AsyncClient(base_url=BASE_URL, timeout=10.0)

    async def _get(self, endpoint: str, params: dict | None = None) -> dict:
        response = await self.http.get(endpoint, params=params)
        response.raise_for_status()
        return response.json()

    async def _post(self, endpoint: str, payload: dict) -> dict:
        response = await self.http.post(endpoint, json=payload)
        response.raise_for_status()
        return response.json()

    async def get_funding_rate(self, symbol: str = "SOL") -> float:
        data = await self._get("/info/prices")
        markets = data.get("data", [])
        for market in markets:
            if market.get("symbol") == symbol:
                return float(market.get("funding", 0))
        return 0.0

    async def get_mark_price(self, symbol: str = "SOL") -> float:
        data = await self._get("/info/prices")
        markets = data.get("data", [])
        for market in markets:
            if market.get("symbol") == symbol:
                return float(market.get("mark", 0))
        return 0.0

    async def get_market_info(self, symbol: str = "SOL") -> Optional[dict]:
        data = await self._get("/info")
        markets = data.get("data", [])
        for market in markets:
            if market.get("symbol") == symbol:
                return market
        return None

    async def get_all_prices(self) -> list:
        data = await self._get("/info/prices")
        return data.get("data", [])

    async def get_account(self, account: str) -> dict:
        data = await self._get("/account/info", params={"account": account})
        return data.get("data", {})

    async def get_positions(self, account: str) -> list:
        data = await self._get("/account/positions", params={"account": account})
        return data.get("data", [])

    async def get_position(self, account: str, symbol: str) -> Optional[dict]:
        positions = await self.get_positions(account)
        for pos in positions:
            if pos.get("symbol") == symbol:
                return pos
        return None

    async def get_account_funding_history(self, account: str, limit: int = 50) -> list:
        data = await self._get("/account/funding", params={"account": account, "limit": limit})
        return data.get("data", [])

    async def get_trade_history(self, account: str, limit: int = 100) -> list:
        data = await self._get(
            "/account/trades",
            params={"account": account, "builder_code": self.builder_code, "limit": limit},
        )
        return data.get("data", [])

    async def check_builder_approval(self, account: str) -> bool:
        if not self._is_pacifica_account(account):
            return False
        data = await self._get("/account/builder_codes/approvals", params={"account": account})
        approvals = data if isinstance(data, list) else data.get("data", [])
        return any(a.get("builder_code") == self.builder_code for a in approvals)

    @staticmethod
    def _is_pacifica_account(account: str) -> bool:
        if account.startswith("0x"):
            return False
        allowed = set("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz")
        return 32 <= len(account) <= 44 and all(ch in allowed for ch in account)

    async def open_short(self, user_account: str, symbol: str, amount: str) -> dict:
        payload = build_market_order_payload(
            vault_keypair=self.keypair,
            user_account=user_account,
            symbol=symbol,
            side="ask",
            amount=amount,
            builder_code=self.builder_code,
            slippage_percent="0.5",
            reduce_only=False,
        )
        return await self._post("/orders/create_market", payload)

    async def close_position(self, user_account: str, symbol: str, amount: str) -> dict:
        payload = build_market_order_payload(
            vault_keypair=self.keypair,
            user_account=user_account,
            symbol=symbol,
            side="bid",
            amount=amount,
            builder_code=self.builder_code,
            slippage_percent="0.5",
            reduce_only=True,
        )
        return await self._post("/orders/create_market", payload)

    async def stream_funding_rate(self, symbol: str = "SOL") -> AsyncGenerator[float, None]:
        try:
            uri = f"{WS_URL}/ws"
            async with websockets.connect(uri) as ws:
                await ws.send(
                    json.dumps(
                        {
                            "method": "subscribe",
                            "params": {"channel": "prices", "symbol": symbol},
                        }
                    )
                )
                async for message in ws:
                    data = json.loads(message)
                    if "funding" in data:
                        yield float(data["funding"])
        except Exception:
            while True:
                rate = await self.get_funding_rate(symbol)
                yield rate
                await asyncio.sleep(30)

    async def close(self):
        await self.http.aclose()
