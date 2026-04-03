import logging
import os

logger = logging.getLogger("spaghettivault.risk")

STOP_LOSS_PCT = float(os.getenv("STOP_LOSS_PCT", "0.05"))
MARGIN_HEALTH_MIN = float(os.getenv("MARGIN_HEALTH_MIN", "0.25"))


class RiskEngine:
    def __init__(self, client):
        self.client = client

    async def should_close_position(
        self, account: str, symbol: str, position: dict | None, deposit_usdc: float
    ) -> bool:
        if not position:
            return False

        margin_ratio = await self._get_margin_ratio(account)
        if margin_ratio is not None and margin_ratio < MARGIN_HEALTH_MIN:
            logger.warning(
                "Margin ratio %.2f%% below threshold for %s", margin_ratio * 100, account
            )
            return True

        unrealised_pnl = float(position.get("unrealised_pnl", 0))
        drawdown_pct = abs(unrealised_pnl) / deposit_usdc if unrealised_pnl < 0 else 0
        if drawdown_pct > STOP_LOSS_PCT:
            logger.warning(
                "Drawdown %.2f%% exceeds stop loss for %s", drawdown_pct * 100, account
            )
            return True

        return False

    async def _get_margin_ratio(self, account: str) -> float | None:
        try:
            account_data = await self.client.get_account(account)
            equity = float(account_data.get("equity", 0))
            used_margin = float(account_data.get("used_margin", 0))
            if used_margin > 0:
                return equity / used_margin
        except Exception as exc:
            logger.error("Failed to fetch margin for %s: %s", account, exc)
        return None
