from config import PERFORMANCE_FEE_PCT
from vault.db import VaultDB


class VaultManager:
    """Simple manager for vault accounting actions."""

    def __init__(self, db: VaultDB):
        self.db = db

    def register_deposit(self, wallet: str, amount_usdc: float) -> None:
        self.db.register_deposit(wallet, amount_usdc)

    def withdraw(self, wallet: str) -> dict:
        user = self.db.get_user(wallet)
        if not user:
            return {"success": False, "reason": "User has no active deposit"}

        principal = float(user["deposit_usdc"])
        pnl = 0.0
        gross = principal + pnl
        fee = max(pnl, 0.0) * PERFORMANCE_FEE_PCT
        net = gross - fee

        self.db.deactivate_user(wallet)
        self.db.record_event(wallet, "withdraw", f"net={net:.4f},fee={fee:.4f}")

        return {
            "success": True,
            "wallet": wallet,
            "principal_usdc": principal,
            "pnl_usdc": pnl,
            "performance_fee_usdc": fee,
            "net_withdraw_usdc": net,
        }
