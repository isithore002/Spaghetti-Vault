import asyncio
import logging
import os

import base58
from solders.keypair import Keypair

from pacifica.client import PacificaClient
from strategy.risk import RiskEngine
from vault.db import VaultDB

logger = logging.getLogger("spaghettivault.strategy")

FUNDING_THRESHOLD = float(os.getenv("FUNDING_RATE_THRESHOLD", "0.0001"))
MAX_LEVERAGE = int(os.getenv("MAX_LEVERAGE", "3"))
LOOP_INTERVAL = int(os.getenv("LOOP_INTERVAL_SECONDS", "60"))
SYMBOL = "SOL"


class StrategyEngine:
    def __init__(self):
        private_key_b58 = os.getenv("VAULT_PRIVATE_KEY")
        if not private_key_b58:
            raise ValueError("VAULT_PRIVATE_KEY not set in environment")

        self.keypair = Keypair.from_bytes(base58.b58decode(private_key_b58))
        self.builder_code = os.getenv("VAULT_BUILDER_CODE", "SPAGHETTIVAULT1")
        self.client = PacificaClient(self.keypair, self.builder_code)
        self.risk = RiskEngine(self.client)
        self.db = VaultDB()
        self.running = False

    async def start(self):
        self.running = True
        logger.info("Strategy engine started")
        while self.running:
            try:
                await self._run_cycle()
            except Exception as exc:
                logger.error("Strategy cycle error: %s", exc, exc_info=True)
            await asyncio.sleep(LOOP_INTERVAL)

    def stop(self):
        self.running = False

    async def _run_cycle(self):
        funding_rate = await self.client.get_funding_rate(SYMBOL)
        mark_price = await self.client.get_mark_price(SYMBOL)

        logger.info("Funding rate: %.6f | Mark price: %.2f", funding_rate, mark_price)
        self.db.record_funding_rate(funding_rate)

        active_users = self.db.get_active_users()
        for user in active_users:
            await self._process_user(user, funding_rate, mark_price)

    async def _process_user(self, user: dict, funding_rate: float, mark_price: float):
        user_account = user["wallet_address"]
        deposit_usdc = float(user["deposit_usdc"])

        is_approved = await self.client.check_builder_approval(user_account)
        if not is_approved:
            logger.warning("Builder approval revoked for %s, skipping", user_account)
            self.db.deactivate_user(user_account)
            return

        position = await self.client.get_position(user_account, SYMBOL)
        should_close = await self.risk.should_close_position(
            user_account, SYMBOL, position, deposit_usdc
        )

        if should_close and position:
            logger.info("Risk trigger: closing position for %s", user_account)
            await self.client.close_position(user_account, SYMBOL, position["size"])
            self.db.record_event(user_account, "close", "risk_trigger")
            return

        if funding_rate > FUNDING_THRESHOLD:
            if not position:
                leverage = min(2, MAX_LEVERAGE)
                size_usd = deposit_usdc * leverage
                amount = str(round(size_usd / mark_price, 4)) if mark_price > 0 else "0"
                if amount == "0":
                    logger.warning("Mark price unavailable, skipping open for %s", user_account)
                    return
                logger.info("Opening short %s %s for %s", amount, SYMBOL, user_account)
                await self.client.open_short(user_account, SYMBOL, amount)
                self.db.record_event(user_account, "open", f"funding={funding_rate:.6f}")
            else:
                logger.info("Holding short for %s | funding=%.6f", user_account, funding_rate)
        elif position:
            logger.info("Funding negative: closing for %s", user_account)
            await self.client.close_position(user_account, SYMBOL, position["size"])
            self.db.record_event(user_account, "close", f"funding={funding_rate:.6f}")
