import os

import httpx

BASE_URL = (
    os.getenv("PACIFICA_TESTNET_URL", "https://test-api.pacifica.fi/api/v1")
    if os.getenv("PACIFICA_ENV", "testnet") == "testnet"
    else os.getenv("PACIFICA_MAINNET_URL", "https://api.pacifica.fi/api/v1")
)


async def submit_approval(signed_payload: dict) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/account/builder_codes/approve", json=signed_payload
        )
        response.raise_for_status()
        return response.json()


async def submit_revocation(signed_payload: dict) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/account/builder_codes/revoke", json=signed_payload
        )
        response.raise_for_status()
        return response.json()


async def check_approval(account: str, builder_code: str) -> bool:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/account/builder_codes/approvals", params={"account": account}
        )
        response.raise_for_status()
        data = response.json()
        approvals = data if isinstance(data, list) else data.get("approvals", [])
        return any(a.get("builder_code") == builder_code for a in approvals)
