from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from config import BUILDER_CODE
from vault.db import VaultDB
from vault.manager import VaultManager

router = APIRouter()
db = VaultDB()
manager = VaultManager(db)


class DepositRequest(BaseModel):
    wallet_address: str
    amount_usdc: float


class WithdrawRequest(BaseModel):
    wallet_address: str


@router.post("/deposit")
async def deposit(req: DepositRequest):
    if req.amount_usdc <= 0:
        raise HTTPException(400, "Amount must be positive")

    manager.register_deposit(req.wallet_address, req.amount_usdc)
    return {
        "success": True,
        "wallet": req.wallet_address,
        "amount_usdc": req.amount_usdc,
        "builder_code": BUILDER_CODE,
        "message": "Deposit registered. Now authorize the vault builder code.",
    }


@router.post("/withdraw")
async def withdraw(req: WithdrawRequest):
    result = manager.withdraw(req.wallet_address)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("reason", "Withdraw failed"))
    return result


@router.get("/status")
async def status(account: str):
    users = {u["wallet_address"]: u for u in db.get_active_users()}
    if account not in users:
        return {"active": False}

    return {
        "active": True,
        "deposit_usdc": users[account]["deposit_usdc"],
        "builder_code": BUILDER_CODE,
    }
