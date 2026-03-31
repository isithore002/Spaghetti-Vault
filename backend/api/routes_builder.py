from fastapi import APIRouter, HTTPException

from config import BUILDER_CODE
from pacifica.builder import check_approval, submit_approval, submit_revocation

router = APIRouter()


def _is_pacifica_account(account: str) -> bool:
    if account.startswith("0x"):
        return False
    allowed = set("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz")
    return 32 <= len(account) <= 44 and all(ch in allowed for ch in account)


@router.post("/approve")
async def approve_builder(payload: dict):
    try:
        result = await submit_approval(payload)
        return {"success": True, "result": result}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/revoke")
async def revoke_builder(payload: dict):
    try:
        result = await submit_revocation(payload)
        return {"success": True, "result": result}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/check")
async def check_approved(account: str):
    if not _is_pacifica_account(account):
        return {"account": account, "approved": False, "builder_code": BUILDER_CODE}

    try:
        approved = await check_approval(account, BUILDER_CODE)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"account": account, "approved": approved, "builder_code": BUILDER_CODE}
